# lesson-4-adding-agent-memory-with-python/demo/demo.py - Sports Analyst Agent Memory Management
"""
Sports Analyst Agent Memory Management with Short-Term Memory

This demo demonstrates:
- Semantic Kernel setup with sports tools
- Short-term memory implementation for sports analysis
- Memory persistence and context management
- Sports analyst agent with memory capabilities
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
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import KernelArguments
from tools.sports_scores import SportsScoresTools
from tools.player_stats import PlayerStatsTools
from models import SportsAnalysisResponse, GameResult, PlayerPerformance, TeamAnalysis, GameStatus, LeagueType, PlayerPosition
from memory import ShortTermMemory

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
        kernel.add_plugin(SportsScoresTools(), "sports_scores")
        logger.info("✅ SportsScoresTools plugin added successfully")
        
        kernel.add_plugin(PlayerStatsTools(), "player_stats")
        logger.info("✅ PlayerStatsTools plugin added successfully")
        
        logger.info("🎉 Semantic Kernel setup completed successfully!")
        return kernel
        
    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise


def create_sports_analysis_prompt() -> str:
    """Create a prompt that requests structured JSON output for sports analysis"""
    return """
You are an expert sports analyst with access to tools for sports scores and player statistics.

When a sports fan asks about games, players, or teams, use the appropriate tools and then provide a response in the following JSON format. ALL FIELDS ARE REQUIRED:

{
    "query_type": "game_scores" or "player_stats" or "team_analysis" or "general",
    "human_readable_response": "A helpful, engaging response for sports fans",
    "structured_data": {
        // Include relevant data based on query type - ALL FIELDS REQUIRED
    },
    "tools_used": ["list", "of", "tools", "used"],
    "confidence_score": 0.95,
    "follow_up_suggestions": ["suggestion1", "suggestion2"]
}

For game scores queries, the structured_data should match this format (ALL FIELDS REQUIRED):
{
    "home_team": "Lakers",
    "away_team": "Warriors",
    "home_score": 120,
    "away_score": 115,
    "game_date": "2024-01-15",
    "status": "completed",
    "league": "NBA",
    "season": "2023-24",
    "venue": "Crypto.com Arena",
    "highlights": ["LeBron's 30-point game", "Curry's clutch 3-pointer"]
}

For player stats queries, the structured_data should match this format (ALL FIELDS REQUIRED):
{
    "name": "LeBron James",
    "position": "SF",
    "team": "Lakers",
    "league": "NBA",
    "season": "2023-24",
    "games_played": 65,
    "points_per_game": 28.5,
    "rebounds_per_game": 8.2,
    "assists_per_game": 6.8,
    "field_goal_percentage": 0.485,
    "three_point_percentage": 0.382,
    "free_throw_percentage": 0.875,
    "plus_minus": 5.2,
    "efficiency_rating": 28.7
}

Always respond with valid JSON that matches these schemas exactly.
"""


def parse_and_validate_response(response_text: str, query_type: str) -> SportsAnalysisResponse:
    """Parse LLM response and validate against Pydantic models"""
    try:
        logger.info("🔍 Parsing and validating LLM response...")
        
        # Extract JSON from response (handle cases where LLM includes extra text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No valid JSON found in response")
        
        json_str = response_text[json_start:json_end]
        response_data = json.loads(json_str)
        
        logger.info("✅ JSON parsed successfully")
        
        # Ensure required fields have defaults if missing
        if "tools_used" not in response_data:
            response_data["tools_used"] = []
        if "confidence_score" not in response_data:
            response_data["confidence_score"] = 0.8
        if "follow_up_suggestions" not in response_data:
            response_data["follow_up_suggestions"] = []
        
        # Validate the main response structure
        sports_response = SportsAnalysisResponse(**response_data)
        
        # If there's structured data, validate it against the appropriate model
        if sports_response.structured_data:
            if query_type == "game_scores":
                # Add fallback values for game data to ensure all required fields are present
                game_data = sports_response.structured_data.copy()

                # Required string fields
                if game_data.get("game_id") is None:
                    game_data["game_id"] = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if game_data.get("home_team") is None:
                    game_data["home_team"] = "Unknown Team"
                if game_data.get("away_team") is None:
                    game_data["away_team"] = "Unknown Team"
                if game_data.get("date") is None:
                    # Try to get date from game_date or use current date
                    game_data["date"] = game_data.get("game_date") or datetime.now().strftime("%Y-%m-%d")

                # Required numeric fields
                if game_data.get("home_score") is None:
                    game_data["home_score"] = 0
                if game_data.get("away_score") is None:
                    game_data["away_score"] = 0

                # Handle status enum - map invalid values to valid ones
                status_value = game_data.get("status")
                if status_value is None:
                    game_data["status"] = "scheduled"
                elif status_value not in ["scheduled", "in_progress", "final", "postponed", "cancelled"]:
                    # Map common invalid values to valid enum values
                    status_mapping = {
                        "completed": "final",
                        "finished": "final",
                        "done": "final",
                        "live": "in_progress",
                        "playing": "in_progress",
                        "active": "in_progress"
                    }
                    game_data["status"] = status_mapping.get(status_value.lower(), "scheduled")

                # Handle league enum - ensure it's a valid LeagueType
                league_value = game_data.get("league")
                if league_value is None:
                    game_data["league"] = "NBA"
                elif league_value not in ["NBA", "NFL", "MLB", "NHL", "Premier League", "Champions League", "MLS"]:
                    game_data["league"] = "NBA"  # Default to NBA if invalid

                # Remove any fields not in GameResult model (like highlights)
                valid_fields = {
                    "game_id", "league", "date", "home_team", "away_team",
                    "home_score", "away_score", "status", "quarter_period",
                    "time_remaining", "venue", "attendance", "message"
                }
                game_data = {k: v for k, v in game_data.items() if k in valid_fields}

                game_result = GameResult(**game_data)
                logger.info(f"✅ Game data validated: {game_result.home_team} vs {game_result.away_team}")
                
            elif query_type == "player_stats":
                # Add fallback values for player data
                player_data = sports_response.structured_data.copy()
                # Map player_name to name if needed (model expects 'name')
                if "player_name" in player_data and "name" not in player_data:
                    player_data["name"] = player_data["player_name"]
                if player_data.get("name") is None:
                    player_data["name"] = "Unknown Player"
                # Required fields with defaults
                if player_data.get("player_id") is None:
                    player_data["player_id"] = f"player_{player_data.get('name', 'unknown').lower().replace(' ', '_')}"
                # Map position abbreviations/variations
                position = player_data.get("position", "Small Forward")
                position_mapping = {
                    "Forward": "Small Forward", "F": "Small Forward", "SF": "Small Forward",
                    "Guard": "Point Guard", "G": "Point Guard", "PG": "Point Guard"
                }
                player_data["position"] = position_mapping.get(position, position)
                if player_data.get("team") is None:
                    player_data["team"] = "Unknown Team"
                if player_data.get("league") is None:
                    player_data["league"] = "NBA"
                if player_data.get("season") is None:
                    player_data["season"] = "2023-24"
                if player_data.get("age") is None:
                    player_data["age"] = 25
                if player_data.get("height") is None:
                    player_data["height"] = "6'0\""
                if player_data.get("weight") is None:
                    player_data["weight"] = "200 lbs"
                if player_data.get("recent_form") is None:
                    player_data["recent_form"] = "Average"
                if player_data.get("injury_status") is None:
                    player_data["injury_status"] = "Healthy"
                # Build stats dict if needed
                if player_data.get("stats") is None:
                    player_data["stats"] = {
                        "points_per_game": player_data.get("points_per_game", 0.0),
                        "rebounds_per_game": player_data.get("rebounds_per_game", 0.0),
                        "assists_per_game": player_data.get("assists_per_game", 0.0)
                    }

                player_performance = PlayerPerformance(**player_data)
                logger.info(f"✅ Player data validated: {player_performance.name} - {player_performance.position}")
        
        logger.info("🎉 All Pydantic validation passed!")
        return sports_response
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        raise ValueError(f"Invalid JSON in response: {e}")
    except Exception as e:
        logger.error(f"❌ Pydantic validation failed: {e}")
        raise ValueError(f"Validation error: {e}")


async def process_sports_query_with_memory(kernel: Kernel, query: str, memory: ShortTermMemory) -> SportsAnalysisResponse:
    """Process a sports query using Semantic Kernel with memory context"""
    try:
        logger.info(f"🤖 Processing sports query with memory: {query}")
        
        # Add user query to memory
        memory.add_conversation("user", query)
        
        # Get conversation context for the prompt
        context = memory.get_context_window(max_tokens=1000)
        
        # Create the prompt with memory context
        prompt = f"""
{create_sports_analysis_prompt()}

Previous conversation context:
{context}

Current sports query: {query}
"""
        
        # Create chat history with memory context
        chat_history = ChatHistory()
        chat_history.add_system_message("You are an expert sports analyst with access to tools for sports scores and player statistics.")
        if context:
            chat_history.add_system_message(f"Previous conversation context:\n{context}")
        chat_history.add_user_message(f"{create_sports_analysis_prompt()}\n\nCurrent sports query: {query}")

        # Get chat completion service and enable automatic tool calling
        chat_service = kernel.get_service(type=ChatCompletionClientBase)
        execution_settings = kernel.get_prompt_execution_settings_from_service_id(
            service_id=chat_service.service_id
        )
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Execute with automatic tool invocation
        result = await chat_service.get_chat_message_contents(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel
        )
        response_text = str(result[0])
        
        logger.info("📝 Raw LLM response received")
        logger.debug(f"Response: {response_text}")
        
        # Determine query type for validation
        query_type = "general"
        if "game" in query.lower() or "score" in query.lower() or "match" in query.lower():
            query_type = "game_scores"
        elif "player" in query.lower() or "stats" in query.lower() or "statistics" in query.lower():
            query_type = "player_stats"
        elif "team" in query.lower() or "standings" in query.lower():
            query_type = "team_analysis"
        
        # Parse and validate the response
        validated_response = parse_and_validate_response(response_text, query_type)
        
        # Add assistant response to memory
        memory.add_conversation("assistant", validated_response.human_readable_response)

        # Extract actual tool calls from chat history
        for message in chat_history.messages:
            if hasattr(message, 'items') and message.items:
                for item in message.items:
                    tool_name = getattr(item, 'name', None)
                    if tool_name and tool_name in ['get_sports_scores', 'get_player_stats']:
                        # Extract input arguments
                        tool_input = getattr(item, 'arguments', {}) if hasattr(item, 'arguments') else {}
                        # Find corresponding result in next messages
                        tool_output = validated_response.structured_data if validated_response.structured_data else {}
                        # Add real tool call to memory
                        memory.add_tool_call(tool_name, tool_input, tool_output, success=True)
        
        return validated_response
        
    except Exception as e:
        logger.error(f"❌ Failed to process sports query: {e}")
        # Add error to memory
        memory.add_conversation("assistant", f"I apologize, but I encountered an error: {e}")
        # Return a fallback response
        return SportsAnalysisResponse(
            query_type="general",
            human_readable_response=f"I apologize, but I encountered an error processing your sports request: {e}",
            structured_data=None,
            tools_used=[],
            confidence_score=0.0,
            follow_up_suggestions=["Please try rephrasing your question", "Ask about specific games or players"],
            predictions=None,
            comparable_players=None,
            historical_context=None
        )


async def run_memory_demo(kernel: Kernel):
    """Run demo scenarios showcasing memory functionality"""
    demo_scenarios = [
        {
            "name": "Game Scores Query with Memory",
            "inputs": [
                "I want to check the Lakers game scores",
                "What about the Warriors game?",
                "Can you tell me more about those games?"
            ]
        },
        {
            "name": "Player Stats with Memory", 
            "inputs": [
                "I want to know about LeBron James' stats",
                "How about Stephen Curry?",
                "Can you compare their performances?"
            ]
        },
        {
            "name": "Mixed Sports Query with Memory Context",
            "inputs": [
                "I have a question about the Lakers",
                "I also want to know about LeBron James",
                "Can you give me a complete analysis of the Lakers and LeBron?"
            ]
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"🎭 Demo Scenario {i}: {scenario['name']}")
        logger.info(f"{'='*80}")
        
        # Create fresh memory for each scenario
        memory = ShortTermMemory(max_items=10, max_tokens=2000)
        logger.info(f"🧠 Created new memory: {memory}")
        
        for step, user_input in enumerate(scenario['inputs'], 1):
            logger.info(f"\n--- Step {step}: {user_input} ---")
            
            # Process the query with memory
            response = await process_sports_query_with_memory(kernel, user_input, memory)
            
            # Display response
            logger.info(f"📝 Agent Response:")
            logger.info(f"   {response.human_readable_response}")
            
            # Show memory state
            memory_summary = memory.get_memory_summary()
            logger.info(f"🧠 Memory State:")
            logger.info(f"   Items: {memory_summary['total_items']}")
            logger.info(f"   Tokens: {memory_summary['total_tokens']}")
            logger.info(f"   Usage: {memory_summary['memory_usage_percent']:.1f}%")
            
            # Show sports context
            sports_context = memory.get_sports_context()
            logger.info(f"🏀 Sports Context:")
            logger.info(f"   Teams: {sports_context['teams']}")
            logger.info(f"   Leagues: {sports_context['leagues']}")
            logger.info(f"   Players: {sports_context['players']}")
            logger.info(f"   Recent queries: {len(sports_context['recent_queries'])}")
            logger.info(f"   Tool calls: {len(sports_context['tool_calls'])}")
        
        # Final memory analysis
        logger.info(f"\n📊 Final Memory Analysis for Scenario {i}:")
        logger.info(f"   Total conversation items: {memory.get_memory_summary()['total_items']}")
        logger.info(f"   Total tokens used: {memory.get_memory_summary()['total_tokens']}")
        logger.info(f"   Memory efficiency: {memory.get_memory_summary()['memory_usage_percent']:.1f}%")
        
        # Show context window
        logger.info(f"\n📝 Context Window:")
        context_window = memory.get_context_window(max_tokens=500)
        logger.info(f"   {context_window}")
        
        # Demonstrate memory search
        logger.info(f"\n🔍 Memory Search Demo:")
        search_results = memory.search_memory("Lakers")
        logger.info(f"   Found {len(search_results)} items containing 'Lakers'")
        for result in search_results:
            logger.info(f"   - [{result['role']}] {result['content'][:50]}...")


def main():
    """Main function to demonstrate agent memory management"""
    import asyncio
    from datetime import datetime
    
    try:
        logger.info("=" * 80)
        logger.info("🎯 Starting Agent Memory Management Demo")
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
        
        logger.info("\n🧠 Memory Management Features:")
        logger.info("=" * 50)
        logger.info("  - Short-term memory for sports conversations")
        logger.info("  - Context window management")
        logger.info("  - Sports entity tracking (teams, players, leagues)")
        logger.info("  - Tool call history and success tracking")
        logger.info("  - Memory search and retrieval")
        logger.info("  - Automatic context extraction")
        
        logger.info("\n🎭 Running Memory Demo Scenarios")
        logger.info("=" * 50)
        
        # Run the memory demo
        asyncio.run(run_memory_demo(kernel))
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Memory Management Demo completed successfully!")
        logger.info("🎉 All memory features demonstrated!")
        logger.info("🧠 Agent memory capabilities showcased!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()