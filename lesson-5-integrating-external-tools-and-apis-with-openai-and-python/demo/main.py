# lesson-5-integrating-external-tools-and-apis-with-openai-and-python/demo/main.py - Sports Analyst Agent with External APIs
"""
Sports Analyst Agent with External API Integration

This demo demonstrates:
- Semantic Kernel setup with sports tools and external APIs
- Short-term memory implementation for sports analysis
- External API integration for live sports data
- Sports analyst agent with memory and external data capabilities
- Pydantic model validation
- Structured JSON output generation with live data
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
from tools.sports_news import SportsNewsTools
from tools.team_standings import TeamStandingsTools
from tools.sports_analytics import SportsAnalyticsTools
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

# Reduce verbosity from noisy libraries
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('semantic_kernel').setLevel(logging.WARNING)
logging.getLogger('tools.sports_scores').setLevel(logging.WARNING)
logging.getLogger('tools.player_stats').setLevel(logging.WARNING)
logging.getLogger('tools.sports_news').setLevel(logging.WARNING)
logging.getLogger('tools.team_standings').setLevel(logging.WARNING)
logging.getLogger('tools.sports_analytics').setLevel(logging.WARNING)


def create_kernel():
    """Create and configure Semantic Kernel with Azure services and tools"""
    try:
        # Get Azure configuration
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
        DEPLOYMENT_CHAT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        DEPLOYMENT_EMBED = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]

        # Create kernel
        kernel = Kernel()

        # Add Azure services
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=DEPLOYMENT_CHAT,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )

        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=DEPLOYMENT_EMBED,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )

        # Add sports tools as SK plugins
        kernel.add_plugin(SportsScoresTools(), "sports_scores")
        kernel.add_plugin(PlayerStatsTools(), "player_stats")

        # Add external API tools
        kernel.add_plugin(SportsNewsTools(), "sports_news")
        kernel.add_plugin(TeamStandingsTools(), "team_standings")
        kernel.add_plugin(SportsAnalyticsTools(), "sports_analytics")

        logger.info("✅ Kernel initialized with 5 plugins")
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
You are an expert sports analyst with access to tools for sports scores, player statistics, team standings, sports news, and analytics.

When a sports fan asks about games, players, teams, or news, use the appropriate tools and then provide a response in the following JSON format. ALL FIELDS ARE REQUIRED:

{
    "query_type": "game_scores" or "player_stats" or "team_analysis" or "sports_news" or "general",
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
    "player_name": "LeBron James",
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
        # Extract JSON from response (handle cases where LLM includes extra text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("No valid JSON found in response")

        json_str = response_text[json_start:json_end]
        response_data = json.loads(json_str)
        
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
                # Add fallback values for game data
                game_data = sports_response.structured_data
                if game_data.get("home_team") is None:
                    game_data["home_team"] = "Unknown Team"
                if game_data.get("away_team") is None:
                    game_data["away_team"] = "Unknown Team"
                if game_data.get("home_score") is None:
                    game_data["home_score"] = 0
                if game_data.get("away_score") is None:
                    game_data["away_score"] = 0
                if game_data.get("status") is None:
                    game_data["status"] = "scheduled"
                if game_data.get("league") is None:
                    game_data["league"] = "NBA"
                if game_data.get("highlights") is None:
                    game_data["highlights"] = []
                
                game_result = GameResult(**game_data)
                
            elif query_type == "player_stats":
                # Add fallback values for player data
                player_data = sports_response.structured_data
                if player_data.get("player_name") is None:
                    player_data["player_name"] = "Unknown Player"
                if player_data.get("position") is None:
                    player_data["position"] = "SF"
                if player_data.get("team") is None:
                    player_data["team"] = "Unknown Team"
                if player_data.get("league") is None:
                    player_data["league"] = "NBA"
                if player_data.get("points_per_game") is None:
                    player_data["points_per_game"] = 0.0
                if player_data.get("rebounds_per_game") is None:
                    player_data["rebounds_per_game"] = 0.0
                if player_data.get("assists_per_game") is None:
                    player_data["assists_per_game"] = 0.0
                
                player_performance = PlayerPerformance(**player_data)

        return sports_response
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        raise ValueError(f"Invalid JSON in response: {e}")
    except Exception as e:
        logger.error(f"❌ Pydantic validation failed: {e}")
        raise ValueError(f"Validation error: {e}")


async def process_sports_query_with_memory_and_apis(kernel: Kernel, query: str, memory: ShortTermMemory) -> SportsAnalysisResponse:
    """Process a sports query using Semantic Kernel with memory context and external APIs"""
    try:
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
        chat_history.add_system_message("You are an expert sports analyst with access to tools for sports scores, player statistics, news, standings, and analytics.")
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
        
        logger.debug(f"Response: {response_text}")
        
        # Determine query type for validation
        query_type = "general"
        if "game" in query.lower() or "score" in query.lower() or "match" in query.lower():
            query_type = "game_scores"
        elif "player" in query.lower() or "stats" in query.lower() or "statistics" in query.lower():
            query_type = "player_stats"
        elif "team" in query.lower() or "standings" in query.lower():
            query_type = "team_analysis"
        elif "news" in query.lower() or "update" in query.lower():
            query_type = "sports_news"
        
        # Parse and validate the response
        validated_response = parse_and_validate_response(response_text, query_type)
        
        # Add assistant response to memory
        memory.add_conversation("assistant", validated_response.human_readable_response)

        # Tools are now automatically invoked by FunctionChoiceBehavior.Auto()
        if validated_response.tools_used:
            logger.info(f"✅ Tools used: {validated_response.tools_used}")

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
            follow_up_suggestions=["Please try rephrasing your question", "Ask about specific games or players"]
        )


async def test_external_sports_apis():
    """Test external API integrations"""
    # Initialize tools
    news_tools = SportsNewsTools()
    player_tools = PlayerStatsTools()

    # Test Sports News API (Real API)
    try:
        news_result = news_tools.get_latest_news("NBA", "Lakers")
        articles = len(news_result.get('news_data', {}).get('articles', []))
        logger.info(f"  📰 Sports News API: {articles} articles (Real API)")
    except Exception as e:
        logger.error(f"  ❌ Sports News API failed: {e}")

    # Test Player Stats API (Real API with fallback)
    try:
        player_result = player_tools.get_player_stats("LeBron James", "NBA")
        source = "Real API" if "Ball Don't Lie" in player_result.get("api_source", "") else "Mock Fallback"
        logger.info(f"  🏀 Player Stats API: {player_result.get('player_name', 'Unknown')} ({source})")
    except Exception as e:
        logger.error(f"  ❌ Player Stats API failed: {e}")


async def run_sports_demo_with_apis(kernel: Kernel):
    """Run demo scenarios showcasing sports analysis with external APIs"""
    demo_scenarios = [
        {
            "name": "Game Scores Query with External APIs",
            "inputs": [
                "I want to check the Lakers game scores",
                "What about the Warriors game?",
                "Can you get the latest news about these teams?",
                "Show me the current standings for both teams"
            ]
        },
        {
            "name": "Player Stats with External APIs", 
            "inputs": [
                "I want to know about LeBron James' stats",
                "How about Stephen Curry?",
                "Can you get recent news about these players?",
                "What's the analytics on their performance?"
            ]
        },
        {
            "name": "Comprehensive Sports Analysis with External APIs",
            "inputs": [
                "I'm interested in the Lakers",
                "Can you give me a complete analysis including scores, news, standings, and analytics?",
                "What are the latest insights about their performance?"
            ]
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"🎭 Demo Scenario {i}: {scenario['name']}")
        logger.info(f"{'='*80}")
        
        # Create fresh memory for each scenario
        memory = ShortTermMemory(max_items=10, max_tokens=2000)

        for step, user_input in enumerate(scenario['inputs'], 1):
            logger.info(f"\n--- Step {step}: {user_input} ---")
            
            # Process the query with memory and external APIs
            response = await process_sports_query_with_memory_and_apis(kernel, user_input, memory)
            
            # Display response
            logger.info(f"📝 Agent Response:")
            logger.info(f"   {response.human_readable_response}")
        
        # Final memory analysis
        summary = memory.get_memory_summary()
        logger.info(f"\n📊 Final Memory Analysis for Scenario {i}:")
        logger.info(f"   Total conversation items: {summary['total_items']}")
        logger.info(f"   Total tokens used: {summary['total_tokens']}")
        logger.info(f"   Memory efficiency: {summary['memory_usage_percent']:.1f}%")


def main():
    """Main function to demonstrate sports analyst agent with external APIs"""
    import asyncio
    from datetime import datetime
    
    try:
        logger.info("🎯 Sports Analyst Agent Demo")
        logger.info("=" * 80)

        # Create the kernel
        kernel = create_kernel()

        # Test external APIs
        logger.info("\n🧪 Testing External APIs")
        asyncio.run(test_external_sports_apis())

        # Run the sports demo with external APIs
        logger.info("\n🎭 Running Demo Scenarios")
        logger.info("=" * 80)
        asyncio.run(run_sports_demo_with_apis(kernel))

        logger.info("\n✅ Demo completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
