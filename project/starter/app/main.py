# app/main.py - Travel Concierge Agent with Semantic Kernel
import os
import json
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory
from app.state import AgentState
from app.memory import ShortTermMemory
from app.utils.config import validate_all_config
from app.utils.logger import setup_logger
from app.tools.weather import WeatherTools
from app.tools.fx import FxTools
from app.tools.search import SearchTools
from app.tools.card import CardTools
from app.tools.knowledge import KnowledgeTools
from app.models import TripPlan
import json as json_module

logger = setup_logger("travel_agent")





# ------------------------------
# KERNEL CREATION
# ------------------------------
def create_kernel():
    """
    Create and configure the Semantic Kernel instance.

    TODO: Implement kernel creation with:
    1. Azure OpenAI services (AzureChatCompletion, AzureTextEmbedding)
    2. Tool plugins (WeatherTools, FxTools, SearchTools, CardTools, KnowledgeTools)

    Hint: Use environment variables for credentials (AZURE_OPENAI_ENDPOINT, etc.)
    """
    # TODO: Implement kernel creation
    kernel = Kernel()

    # TODO: Add Azure OpenAI services and tool plugins

    return kernel


# -------------------------------
# MAIN REQUEST PIPELINE (AGENTIC LOOP)
# -------------------------------
async def run_request(user_input: str, memory: ShortTermMemory = None) -> str:
    try:
        validate_all_config()
        kernel = create_kernel()

        # Initialize state machine
        state = AgentState()
        logger.info(f"📍 State: {state.phase}")

        # Initialize or use existing short-term memory
        if memory is None:
            memory = ShortTermMemory(max_items=10, max_tokens=4000)
        memory.add_conversation("user", user_input)

        state.advance()
        logger.info(f"📍 State: {state.phase}")
        logger.info(f"Request: {user_input}")

        # Get chat service
        chat_service = kernel.get_service(type=ChatCompletionClientBase)

        # Create chat history
        chat_history = ChatHistory()

        # ------------------------------
        # SYSTEM MESSAGE PROMPT
        # ------------------------------
        # TODO: Write a system message prompt for the travel concierge agent.
        #
        # Your prompt should include:
        # 1. Agent role: Professional travel concierge with access to real-time tools
        # 2. Available tools and how to call them:
        #    - weather.get_weather(city="...") for weather forecasts
        #    - web_search for restaurants, hotels, attractions
        #    - convert_fx for currency conversion
        #    - recommend_card(category="...", country="...") for card recommendations
        #    - search_knowledge for credit card benefits
        # 3. Tool usage guidelines: When to call each tool for trip planning
        # 4. Output format: JSON matching the TripPlan Pydantic model structure
        # 5. Anti-hallucination rules:
        #    - Only include data actually obtained from tools
        #    - Use null for missing optional fields (weather, card_recommendation, etc.)
        #    - Use "N/A" for destination/dates if not a trip planning query
        #    - NEVER make up or guess data
        #
        # Hint: The output JSON should match the TripPlan model in app/models.py
        system_message = """You are a professional travel concierge agent.

TODO: Complete this system message prompt with:
- Available tools and their usage
- JSON output format matching TripPlan model
- Anti-hallucination instructions (use null/N/A for missing data)
"""

        chat_history.add_system_message(system_message)

        # Add conversation history from memory for context
        for item in memory.get_conversation_history():
            if item.get("role") == "user":
                chat_history.add_user_message(item.get("content", ""))
            elif item.get("role") == "assistant":
                chat_history.add_assistant_message(item.get("content", ""))

        chat_history.add_user_message(user_input)

        # Enable automatic function calling
        execution_settings = OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
            temperature=0.7,
            max_tokens=2000
        )

        state.advance()
        logger.info(f"📍 State: {state.phase}")
        logger.info("🤖 LLM will automatically call tools as needed...")

        # Let LLM automatically call tools
        response = await chat_service.get_chat_message_contents(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel
        )

        state.advance()
        logger.info(f"📍 State: {state.phase}")

        agent_response = response[0].content
        logger.info(f"✅ Agent response received: {len(agent_response)} chars")

        # Save assistant response to memory
        memory.add_conversation("assistant", agent_response[:500])

        # Parse and validate response with Pydantic (Lesson 2 pattern)
        try:
            # Extract JSON from response (handle cases where LLM includes extra text)
            json_start = agent_response.find('{')
            json_end = agent_response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = agent_response[json_start:json_end]
            response_data = json_module.loads(json_str)

            logger.info("✅ JSON parsed successfully")

            # Validate with TripPlan Pydantic model
            trip_plan = TripPlan(**response_data)
            logger.info(f"✅ Pydantic validation passed: {trip_plan.destination}")

            # Auto-populate citations from search results if empty
            if (not trip_plan.citations or trip_plan.citations == []) and trip_plan.results:
                trip_plan.citations = [r.url for r in trip_plan.results if r.url]
                logger.info(f"✅ Auto-populated {len(trip_plan.citations)} citations from results")

            state.advance()
            logger.info(f"📍 State: {state.phase}")

            # Return validated Pydantic model as JSON
            result = {
                "trip_plan": trip_plan.model_dump(),
                "metadata": {
                    "session_id": state.session_id,
                    "tools_called": ["automatic_via_llm"],
                    "data_quality": "validated_with_pydantic",
                    "memory_items": len(memory.get_conversation_history())
                }
            }

            return json.dumps(result, indent=2, default=str)

        except (json_module.JSONDecodeError, ValueError) as e:
            logger.warning(f"⚠️ JSON parsing failed: {e}")
            logger.warning("Falling back to raw agent response")

            # Fallback: return raw response if JSON parsing fails
            result = {
                "raw_response": agent_response,
                "metadata": {
                    "session_id": state.session_id,
                    "tools_called": ["automatic_via_llm"],
                    "data_quality": "unvalidated",
                    "parse_error": str(e)
                }
            }

            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            logger.error(f"❌ Pydantic validation failed: {e}")
            logger.warning("Falling back to raw agent response")

            # Fallback: return raw response if validation fails
            result = {
                "raw_response": agent_response,
                "metadata": {
                    "session_id": state.session_id,
                    "tools_called": ["automatic_via_llm"],
                    "data_quality": "validation_failed",
                    "validation_error": str(e)
                }
            }

            return json.dumps(result, indent=2, default=str)

    except Exception as e:
        logger.error(f"Request failed: {e}")
        return json.dumps({"error": str(e), "status": "failed"}, indent=2)



# -------------------------------
# CLI ENTRY POINT
# -------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Travel Concierge Agent")
    parser.add_argument("--input", help="User input for the agent")
    args = parser.parse_args()

    if args.input:
        result = asyncio.run(run_request(args.input))
        print(result)
    else:
        print("Travel Concierge Agent (type 'quit' to exit)")
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                result = asyncio.run(run_request(user_input))
                try:
                    data = json.loads(result)
                    if "plan" in data:
                        from app.utils.pretty_print import print_plan  # 👈 optional: factor out
                        print_plan(data["plan"])
                    else:
                        print(result)
                except Exception:
                    print(result)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()