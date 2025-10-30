# lesson-3-implementing-agent-state-management-with-python/exercises/solution/main.py - Agent State Management
"""
Agent State Management with State Machine

This demo demonstrates:
- Semantic Kernel setup with tools
- State machine implementation for agent workflow
- State transitions and tracking
- Customer service agent with state management
- Pydantic model validation
- Structured JSON output generation
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.functions import KernelArguments
from tools.order_status import OrderStatusTools
from tools.product_info import ProductInfoTools
from models import CustomerServiceResponse, OrderResponse, ProductResponse, OrderStatus, ProductAvailability
from state import AgentState, Phase

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_kernel():
    """Create and configure Semantic Kernel with Azure services and tools"""
    try:
        logger.info("🚀 Starting Semantic Kernel setup...")
        
        # Get Azure configuration
        logger.info("📋 Retrieving Azure OpenAI configuration from environment variables...")
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
        DEPLOYMENT_CHAT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        DEPLOYMENT_EMBED = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
        
        logger.info(f"✅ Configuration loaded - Endpoint: {AZURE_OPENAI_ENDPOINT}")
        logger.info(f"📊 Chat deployment: {DEPLOYMENT_CHAT}, Embedding deployment: {DEPLOYMENT_EMBED}")
        
        # Create kernel
        logger.info("🔧 Creating Semantic Kernel instance...")
        kernel = Kernel()
        
        # Add Azure services
        logger.info("🤖 Adding Azure Chat Completion service...")
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=DEPLOYMENT_CHAT,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info("✅ Azure Chat Completion service added successfully")
        
        logger.info("🧠 Adding Azure Text Embedding service...")
        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=DEPLOYMENT_EMBED,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info("✅ Azure Text Embedding service added successfully")
        
        # Add tools as SK plugins
        logger.info("🛠️ Adding custom tools as Semantic Kernel plugins...")
        kernel.add_plugin(OrderStatusTools(), "order_status")
        logger.info("✅ OrderStatusTools plugin added successfully")
        
        kernel.add_plugin(ProductInfoTools(), "product_info")
        logger.info("✅ ProductInfoTools plugin added successfully")
        
        logger.info("🎉 Semantic Kernel setup completed successfully!")
        return kernel
        
    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise


def create_state_aware_prompt(state: AgentState) -> str:
    """Create a state-aware prompt for the customer service agent"""
    base_prompt = """
You are a helpful customer service agent with access to tools for order status and product information.

Current session state:
- Phase: {phase}
- Phase Description: {phase_description}
- Session ID: {session_id}
- Data Completeness: {data_completeness:.1%}
- Tools Called: {tools_called}
- Issues: {issues}

Based on the current state, respond appropriately:
"""
    
    phase_specific_instructions = {
        Phase.Init: """
INIT PHASE: Welcome the customer and capture their initial request.
- Ask clarifying questions to understand their needs
- Identify if they need order status, product info, or general help
- Set up the session context
""",
        Phase.ClarifyRequirements: """
CLARIFY REQUIREMENTS PHASE: Ask targeted questions to gather missing information.
- Focus on required fields that are still missing
- Ask one clear, specific question at a time
- Avoid overwhelming the customer with multiple questions
""",
        Phase.PlanTools: """
PLAN TOOLS PHASE: Decide which tools to call based on the requirements.
- Determine if you need order_status or product_info tools
- Plan the sequence of tool calls
- Consider what parameters each tool needs
""",
        Phase.ExecuteTools: """
EXECUTE TOOLS PHASE: Call the planned tools and collect results.
- Use the appropriate tools based on the plan
- Handle any tool errors gracefully
- Collect and store all tool results
""",
        Phase.AnalyzeResults: """
ANALYZE RESULTS PHASE: Process tool outputs and validate data completeness.
- Review all tool results
- Check if the data is complete and accurate
- Identify any gaps or issues
""",
        Phase.ResolveIssues: """
RESOLVE ISSUES PHASE: Handle any problems or edge cases identified.
- Address any data gaps or errors
- Try alternative approaches if needed
- Escalate if issues cannot be resolved
""",
        Phase.ProduceStructuredOutput: """
PRODUCE STRUCTURED OUTPUT PHASE: Generate final response with validated data.
- Create Pydantic-validated JSON response
- Provide natural language summary
- Include all relevant information and citations
""",
        Phase.Done: """
DONE PHASE: Process is complete.
- Provide final summary
- Offer additional help if needed
- Close the session appropriately
"""
    }
    
    # Format the base prompt with current state
    formatted_prompt = base_prompt.format(
        phase=state.phase.value,
        phase_description=state.get_phase_description(),
        session_id=state.session_id,
        data_completeness=state.data_completeness,
        tools_called=', '.join(state.tools_called) if state.tools_called else 'None',
        issues=', '.join(state.issues) if state.issues else 'None'
    )
    
    # Add phase-specific instructions
    if state.phase in phase_specific_instructions:
        formatted_prompt += phase_specific_instructions[state.phase]
    
    # Add JSON response format
    formatted_prompt += """

Always respond with valid JSON in this format:
{
    "query_type": "order_status" or "product_info" or "general",
    "human_readable_response": "A helpful, friendly response to the customer",
    "structured_data": {
        // Include relevant data based on query type
    },
    "tools_used": ["list", "of", "tools", "used"],
    "confidence_score": 0.95,
    "follow_up_suggestions": ["suggestion1", "suggestion2"],
    "next_phase": "suggested_next_phase",
    "state_updates": {
        "requirements": {},
        "issues": [],
        "clarification_questions": []
    }
}
"""
    
    return formatted_prompt


def create_customer_service_prompt() -> str:
    """Create a prompt that requests structured JSON output"""
    return """
You are a helpful customer service agent. You have access to tools to check order status and product information.

When a customer asks about their order or a product, use the appropriate tools and then provide a response in the following JSON format:

{
    "query_type": "order_status" or "product_info" or "general",
    "human_readable_response": "A helpful, friendly response to the customer",
    "structured_data": {
        // If query_type is "order_status", include order details here
        // If query_type is "product_info", include product details here
        // Otherwise, this can be null
    },
    "tools_used": ["list", "of", "tools", "used"],
    "confidence_score": 0.95,
    "follow_up_suggestions": ["suggestion1", "suggestion2"]
}

For order status queries, the structured_data should match this format:
{
    "order_id": "string",
    "status": "processing|shipped|delivered|cancelled|not_found|error",
    "tracking_number": "string or null",
    "estimated_delivery": "string or null",
    "items": ["item1", "item2"],
    "message": "string or null"
}

For product info queries, the structured_data should match this format:
{
    "product_id": "string",
    "name": "string",
    "price": 99.99,
    "category": "string",
    "description": "string",
    "availability": "in_stock|out_of_stock|discontinued",
    "stock_quantity": 50,
    "rating": 4.5,
    "reviews_count": 128,
    "message": "string or null"
}

Always respond with valid JSON that matches these schemas exactly.
"""


def parse_and_validate_response(response_text: str, query_type: str) -> CustomerServiceResponse:
    """Parse LLM response and validate against Pydantic models"""
    try:
        logger.info("🔍 Parsing and validating LLM response...")
        
        # Extract JSON from response (handle cases where LLM includes extra text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response_text[json_start:json_end]
        response_data = json.loads(json_str)
        
        logger.info("✅ JSON parsed successfully")
        
        # Validate the main response structure
        customer_response = CustomerServiceResponse(**response_data)
        
        # If there's structured data, validate it against the appropriate model
        if customer_response.structured_data:
            if query_type == "order_status":
                order_data = OrderResponse(**customer_response.structured_data)
                logger.info(f"✅ Order data validated: {order_data.order_id} - {order_data.status}")
            elif query_type == "product_info":
                product_data = ProductResponse(**customer_response.structured_data)
                logger.info(f"✅ Product data validated: {product_data.product_id} - {product_data.name}")
        
        logger.info("🎉 All Pydantic validation passed!")
        return customer_response
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        raise ValueError(f"Invalid JSON in response: {e}")
    except Exception as e:
        logger.error(f"❌ Pydantic validation failed: {e}")
        raise ValueError(f"Validation error: {e}")


async def process_state_transition(kernel: Kernel, state: AgentState, user_input: str) -> Dict[str, Any]:
    """Process a state transition in the agent state machine"""
    try:
        logger.info(f"🔄 Processing state transition: {state.phase.value}")
        logger.info(f"📝 User input: {user_input}")
        
        # Create state-aware prompt
        prompt = create_state_aware_prompt(state)
        full_prompt = f"{prompt}\n\nCustomer input: {user_input}"
        
        # Create function from prompt
        state_function = kernel.add_function(
            function_name="state_processor",
            plugin_name="state_processor",
            prompt=full_prompt
        )
        
        # Execute the function
        result = await kernel.invoke(state_function)
        response_text = str(result)
        
        logger.info("📝 Raw LLM response received")
        logger.debug(f"Response: {response_text}")
        
        # Parse JSON response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response_text[json_start:json_end]
        response_data = json.loads(json_str)
        
        # Update state based on response
        await update_agent_state(state, response_data, user_input)
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Failed to process state transition: {e}")
        # Add error to state
        state.add_issue(f"State transition error: {e}")
        return {
            "query_type": "general",
            "human_readable_response": f"I apologize, but I encountered an error: {e}",
            "structured_data": None,
            "tools_used": [],
            "confidence_score": 0.0,
            "follow_up_suggestions": ["Please try again", "Contact support if the issue persists"],
            "next_phase": "ResolveIssues",
            "state_updates": {}
        }


async def update_agent_state(state: AgentState, response_data: Dict[str, Any], user_input: str) -> None:
    """Update agent state based on LLM response and user input"""
    try:
        # Extract query type and set required fields
        query_type = response_data.get("query_type", "general")
        state.set_required_fields_for_query_type(query_type)
        
        # Extract requirements from user input and structured data
        extracted_requirements = extract_requirements_from_input(user_input, response_data)
        if extracted_requirements:
            state.set_requirements(extracted_requirements)
        
        # Update requirements if provided in state_updates
        if "state_updates" in response_data:
            updates = response_data["state_updates"]
            
            if "requirements" in updates:
                state.set_requirements(updates["requirements"])
            
            if "issues" in updates:
                for issue in updates["issues"]:
                    state.add_issue(issue)
            
            if "clarification_questions" in updates:
                for question in updates["clarification_questions"]:
                    state.add_clarification_question(question)
        
        # Record tool usage
        if "tools_used" in response_data:
            for tool in response_data["tools_used"]:
                if tool not in state.tools_called:
                    state.add_tool_call(tool)
        
        # Determine next phase
        next_phase = response_data.get("next_phase", None)
        if next_phase:
            try:
                # Try to set specific phase
                phase_map = {p.value: p for p in Phase}
                if next_phase in phase_map:
                    state.phase = phase_map[next_phase]
                    state.updated_at = datetime.now()
                else:
                    # Advance to next phase if suggestion is invalid
                    state.advance()
            except:
                # Fallback to advancing phase
                state.advance()
        else:
            # Auto-advance based on current state
            advance_state_automatically(state, response_data)
        
        logger.info(f"✅ State updated - New phase: {state.phase.value}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update agent state: {e}")
        state.add_issue(f"State update error: {e}")


def extract_requirements_from_input(user_input: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract requirements from user input and response data"""
    requirements = {}
    
    # Extract order ID
    if "ORD-" in user_input.upper():
        import re
        order_match = re.search(r'ORD-\d+', user_input.upper())
        if order_match:
            requirements["order_id"] = order_match.group()
    
    # Extract product ID
    if "PROD-" in user_input.upper():
        import re
        product_match = re.search(r'PROD-\d+', user_input.upper())
        if product_match:
            requirements["product_id"] = product_match.group()
    
    # Extract from structured data
    if "structured_data" in response_data and response_data["structured_data"]:
        structured_data = response_data["structured_data"]
        if "order_id" in structured_data:
            requirements["order_id"] = structured_data["order_id"]
        if "product_id" in structured_data:
            requirements["product_id"] = structured_data["product_id"]
    
    return requirements


def advance_state_automatically(state: AgentState, response_data: Dict[str, Any]) -> None:
    """Automatically advance state based on current phase and response"""
    if state.phase == Phase.Init:
        # Move to clarify requirements if we have basic info
        if response_data.get("query_type") in ["order_status", "product_info"]:
            state.advance()
        else:
            # Stay in init to gather more info
            pass
    
    elif state.phase == Phase.ClarifyRequirements:
        # Move to plan tools if we have enough info or if user seems satisfied
        if state.data_completeness >= 0.7 or "thank" in response_data.get("human_readable_response", "").lower():
            state.advance()
        # Otherwise stay in clarify phase
    
    elif state.phase == Phase.PlanTools:
        # Move to execute tools
        state.advance()
    
    elif state.phase == Phase.ExecuteTools:
        # Move to analyze results
        state.advance()
    
    elif state.phase == Phase.AnalyzeResults:
        # Check if there are issues
        if state.has_issues():
            state.phase = Phase.ResolveIssues
        else:
            state.phase = Phase.ProduceStructuredOutput
    
    elif state.phase == Phase.ResolveIssues:
        # Move to produce output if issues resolved
        if not state.has_issues():
            state.phase = Phase.ProduceStructuredOutput
        # Otherwise stay in resolve issues
    
    elif state.phase == Phase.ProduceStructuredOutput:
        # Move to done
        state.advance()


async def execute_tools_for_state(kernel: Kernel, state: AgentState) -> None:
    """Execute tools based on current state and requirements"""
    try:
        logger.info(f"🔧 Executing tools for phase: {state.phase.value}")
        
        # Get tool instances
        order_tools = OrderStatusTools()
        product_tools = ProductInfoTools()
        
        # Execute tools based on requirements
        if "order_id" in state.requirements:
            order_id = state.requirements["order_id"]
            logger.info(f"📦 Getting order status for: {order_id}")
            result = order_tools.get_order_status(order_id)
            state.add_tool_call("order_status", result)
        
        if "product_id" in state.requirements:
            product_id = state.requirements["product_id"]
            logger.info(f"🛍️ Getting product info for: {product_id}")
            result = product_tools.get_product_info(product_id)
            state.add_tool_call("product_info", result)
        
        # Set analysis results
        state.set_analysis_results(state.tool_results)
        
        logger.info("✅ Tools executed successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to execute tools: {e}")
        state.add_issue(f"Tool execution error: {e}")


async def process_customer_query(kernel: Kernel, query: str) -> CustomerServiceResponse:
    """Process a customer query using Semantic Kernel and return validated response"""
    try:
        logger.info(f"🤖 Processing customer query: {query}")
        
        # Create the prompt with the customer query
        prompt = f"{create_customer_service_prompt()}\n\nCustomer query: {query}"
        
        # Create a function from the prompt
        customer_service_function = kernel.add_function(
            function_name="customer_service",
            plugin_name="customer_service",
            prompt=prompt
        )
        
        # Execute the function
        result = await kernel.invoke(customer_service_function)
        response_text = str(result)
        
        logger.info("📝 Raw LLM response received")
        logger.debug(f"Response: {response_text}")
        
        # Determine query type for validation
        query_type = "general"
        if "order" in query.lower() or "tracking" in query.lower():
            query_type = "order_status"
        elif "product" in query.lower() or "price" in query.lower():
            query_type = "product_info"
        
        # Parse and validate the response
        validated_response = parse_and_validate_response(response_text, query_type)
        
        return validated_response
        
    except Exception as e:
        logger.error(f"❌ Failed to process customer query: {e}")
        # Return a fallback response
        return CustomerServiceResponse(
            query_type="general",
            human_readable_response=f"I apologize, but I encountered an error processing your request: {e}",
            structured_data=None,
            tools_used=[],
            confidence_score=0.0,
            follow_up_suggestions=["Please try rephrasing your question", "Contact support if the issue persists"]
        )


async def run_state_machine_demo(kernel: Kernel):
    """Run demo scenarios showcasing the state machine workflow"""
    demo_scenarios = [
        {
            "name": "Order Status Query",
            "inputs": [
                "I need to check my order status",
                "My order number is ORD-001",
                "That's all I need to know"
            ]
        },
        {
            "name": "Product Information Query", 
            "inputs": [
                "I want to know about a product",
                "The product ID is PROD-002",
                "Thanks for the information"
            ]
        },
        {
            "name": "Complex Multi-Step Query",
            "inputs": [
                "I have a problem with my order",
                "Order ORD-003 is missing items",
                "Can you also tell me about product PROD-001?",
                "That helps, thank you"
            ]
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"🎭 Demo Scenario {i}: {scenario['name']}")
        logger.info(f"{'='*80}")
        
        # Create new agent state for this scenario
        state = AgentState()
        logger.info(f"🆕 Created new agent state - Session ID: {state.session_id}")
        
        # Process each input in the scenario
        for step, user_input in enumerate(scenario['inputs'], 1):
            logger.info(f"\n--- Step {step}: {user_input} ---")
            logger.info(f"🔄 Current State: {state.phase.value} - {state.get_phase_description()}")
            
            try:
                # Process the state transition
                response = await process_state_transition(kernel, state, user_input)
                
                # Display response
                logger.info(f"📝 Agent Response:")
                logger.info(f"   {response.get('human_readable_response', 'No response')}")
                
                # Show state updates
                logger.info(f"📊 State Summary:")
                status = state.get_status_summary()
                logger.info(f"   Phase: {status['phase']}")
                logger.info(f"   Data Completeness: {status['data_completeness']:.1%}")
                logger.info(f"   Tools Called: {', '.join(status['tools_called']) if status['tools_called'] else 'None'}")
                logger.info(f"   Issues: {', '.join(status['issues']) if status['issues'] else 'None'}")
                
                # Execute tools if in ExecuteTools phase
                if state.phase == Phase.ExecuteTools:
                    await execute_tools_for_state(kernel, state)
                
                # Show structured data if available
                if response.get('structured_data'):
                    logger.info(f"📋 Structured Data:")
                    logger.info(f"   {json.dumps(response['structured_data'], indent=2)}")
                
                # Check if we should advance to next phase
                if state.phase == Phase.Done:
                    logger.info(f"✅ Scenario {i} completed - Agent reached Done state")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Step {step} failed: {e}")
                state.add_issue(f"Step {step} error: {e}")
        
        # Final state summary
        logger.info(f"\n📊 Final State Summary for Scenario {i}:")
        final_status = state.get_status_summary()
        logger.info(f"   Final Phase: {final_status['phase']}")
        logger.info(f"   Total Tools Called: {len(final_status['tools_called'])}")
        logger.info(f"   Data Completeness: {final_status['data_completeness']:.1%}")
        logger.info(f"   Issues Resolved: {len(final_status['resolved_issues'])}")
        logger.info(f"   Has Structured Output: {final_status['has_structured_output']}")


def main():
    """Main function to demonstrate agent state management with state machine"""
    import asyncio
    from datetime import datetime
    
    try:
        logger.info("=" * 80)
        logger.info("🎯 Starting Agent State Management with State Machine Demo")
        logger.info("=" * 80)
        logger.info("📁 Loading environment variables from .env file...")
        
        # Create the kernel
        kernel = create_kernel()
        
        # List available plugins and functions
        logger.info("📋 Available plugins and functions:")
        for plugin_name, plugin in kernel.plugins.items():
            logger.info(f"  🔌 Plugin: {plugin_name}")
            for function_name, function in plugin.functions.items():
                logger.info(f"    ⚙️  Function: {function_name}")
        
        # Show state machine phases
        logger.info(f"\n{'='*80}")
        logger.info("🔄 Agent State Machine Phases")
        logger.info(f"{'='*80}")
        temp_state = AgentState()
        for phase in Phase:
            temp_state.phase = phase
            logger.info(f"  {phase.value}: {temp_state.get_phase_description()}")
        
        # Run state machine demo scenarios
        logger.info(f"\n{'='*80}")
        logger.info("🎭 Running State Machine Demo Scenarios")
        logger.info(f"{'='*80}")
        
        asyncio.run(run_state_machine_demo(kernel))
        
        logger.info(f"\n{'='*80}")
        logger.info("✅ State Machine Demo completed successfully!")
        logger.info("🎉 All state transitions processed!")
        logger.info("🏆 Agent state management demonstrated!")
        logger.info(f"{'='*80}")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()