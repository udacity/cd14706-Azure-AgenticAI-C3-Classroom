# lesson-2-implementing-structured-outputs-with-pydantic/demo/main.py - Sports Analyst with Pydantic
"""
Sports Analyst with Structured Outputs and Pydantic Validation

This demo demonstrates:
- Semantic Kernel setup with sports analysis tools
- Pydantic model validation for sports data
- Structured JSON output generation
- AI-powered sports analysis with validated responses
"""

import os
import sys
import json
import logging
from typing import Optional
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

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_kernel():
    """Create and configure Semantic Kernel with Azure services and sports tools"""
    try:
        logger.info("🚀 Starting Semantic Kernel setup for Sports Analyst...")
        
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
        
        # Add sports tools as SK plugins
        logger.info("🏀 Adding sports analysis tools as Semantic Kernel plugins...")
        kernel.add_plugin(SportsScoresTools(), "sports_scores")
        logger.info("✅ SportsScoresTools plugin added successfully")
        
        kernel.add_plugin(PlayerStatsTools(), "player_stats")
        logger.info("✅ PlayerStatsTools plugin added successfully")
        
        logger.info("🎉 Sports Analyst setup completed successfully!")
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
You are an expert sports analyst with access to real-time sports data. You can get recent scores and player statistics.

When analyzing sports data, provide a response in the following JSON format. ALL FIELDS ARE REQUIRED:

{
    "query_type": "game_scores" or "player_stats" or "team_analysis" or "general",
    "human_readable_response": "A detailed, engaging analysis for sports fans",
    "structured_data": {
        // If query_type is "game_scores", include game details here
        // If query_type is "player_stats", include player details here
        // If query_type is "team_analysis", include team details here
        // Otherwise, this can be null
    },
    "tools_used": ["sports_scores", "player_stats"],
    "confidence_score": 0.95,
    "follow_up_suggestions": ["Ask about specific players", "Check recent games", "Compare teams"],
    "analysis_insights": ["Key statistical trends", "Performance highlights", "Strategic observations"],
    "predictions": ["Upcoming game predictions", "Season outlook"],
    "comparable_players": ["Similar players for comparison"],
    "historical_context": "Historical records or context"
}

For game scores queries, the structured_data should match this format:
{
    "game_id": "string",
    "league": "NBA|NFL|MLB|NHL|Premier League",
    "date": "2024-01-15",
    "home_team": "string",
    "away_team": "string",
    "home_score": 112,
    "away_score": 108,
    "status": "scheduled|in_progress|final|postponed|cancelled",
    "quarter_period": "4th or 3rd or 9th",
    "time_remaining": "0:00 or 5:23",
    "venue": "Stadium name",
    "attendance": 18997,
    "message": "string or null"
}

For player stats queries, the structured_data should match this format:
{
    "player_id": "string",
    "name": "string",
    "team": "string",
    "position": "Point Guard|Quarterback|Right Field|Center",
    "league": "NBA|NFL|MLB|NHL",
    "season": "2023-24",
    "age": 28,
    "height": "6'3\"",
    "weight": "230 lbs",
    "stats": {
        // League-specific statistics object
    },
    "recent_form": "string",
    "injury_status": "string",
    "salary": 45.0,
    "contract_years": 8,
    "message": "string or null"
}

Always respond with valid JSON that matches these schemas exactly. Provide insightful analysis, not just raw statistics.
"""


def parse_and_validate_response(response_text: str, query_type: str) -> SportsAnalysisResponse:
    """Parse LLM response and validate against Pydantic models"""
    try:
        logger.info("🔍 Parsing and validating sports analysis response...")
        
        # Extract JSON from response (handle cases where LLM includes extra text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
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
        if "analysis_insights" not in response_data:
            response_data["analysis_insights"] = []
        
        # Validate the main response structure
        sports_response = SportsAnalysisResponse(**response_data)
        
        # If there's structured data, validate it against the appropriate model
        if sports_response.structured_data:
            if query_type == "game_scores":
                game_data = GameResult(**sports_response.structured_data)
                logger.info(f"✅ Game data validated: {game_data.home_team} vs {game_data.away_team}")
            elif query_type == "player_stats":
                player_data = PlayerPerformance(**sports_response.structured_data)
                logger.info(f"✅ Player data validated: {player_data.name} - {player_data.team}")
            elif query_type == "team_analysis":
                team_data = TeamAnalysis(**sports_response.structured_data)
                logger.info(f"✅ Team data validated: {team_data.name} - {team_data.league}")
        
        logger.info("🎉 All Pydantic validation passed!")
        return sports_response
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        raise ValueError(f"Invalid JSON in response: {e}")
    except Exception as e:
        logger.error(f"❌ Pydantic validation failed: {e}")
        raise ValueError(f"Validation error: {e}")


async def process_sports_query(kernel: Kernel, query: str) -> SportsAnalysisResponse:
    """Process a sports query using Semantic Kernel and return validated response"""
    try:
        logger.info(f"🏀 Processing sports query: {query}")

        # Create chat history
        chat_history = ChatHistory()
        chat_history.add_system_message(create_sports_analysis_prompt())
        chat_history.add_user_message(query)

        # Get the chat completion service
        chat_service = kernel.get_service(type=ChatCompletionClientBase)

        # Configure execution settings with automatic function calling
        logger.info("🔧 Executing with automatic function calling enabled...")
        execution_settings = kernel.get_prompt_execution_settings_from_service_id(
            service_id=chat_service.service_id
        )
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Get the chat completion with automatic tool invocation
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
        if any(word in query.lower() for word in ["score", "game", "match", "result"]):
            query_type = "game_scores"
        elif any(word in query.lower() for word in ["player", "stats", "statistics", "performance"]):
            query_type = "player_stats"
        elif any(word in query.lower() for word in ["team", "standings", "record"]):
            query_type = "team_analysis"

        # Parse and validate the response
        validated_response = parse_and_validate_response(response_text, query_type)

        return validated_response
        
    except Exception as e:
        logger.error(f"❌ Failed to process sports query: {e}")
        # Return a fallback response
        return SportsAnalysisResponse(
            query_type="general",
            human_readable_response=f"I apologize, but I encountered an error processing your sports query: {e}",
            structured_data=None,
            tools_used=[],
            confidence_score=0.0,
            follow_up_suggestions=["Please try rephrasing your question", "Contact support if the issue persists"],
            analysis_insights=[],
            predictions=None,
            comparable_players=None,
            historical_context=None
        )


async def run_sports_demo_scenarios(kernel: Kernel):
    """Run demo scenarios showcasing structured outputs with Pydantic validation for sports"""
    demo_queries = [
        "What were the recent NBA scores?",
        "Tell me about LeBron James' performance this season",
        "How did the Kansas City Chiefs do in their last game?",
        "Compare Stephen Curry and Luka Doncic's stats",
        "What's the outlook for the Lakers this season?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"🏀 Demo Scenario {i}: {query}")
        logger.info(f"{'='*60}")
        
        try:
            # Process the query
            response = await process_sports_query(kernel, query)
            
            # Display results
            logger.info(f"📝 Human-readable analysis:")
            logger.info(f"   {response.human_readable_response}")
            
            logger.info(f"🔧 Tools used: {', '.join(response.tools_used)}")
            logger.info(f"📊 Confidence score: {response.confidence_score}")
            logger.info(f"💡 Follow-up suggestions: {', '.join(response.follow_up_suggestions)}")
            
            if response.analysis_insights:
                logger.info(f"🔍 Key insights: {', '.join(response.analysis_insights)}")
            
            if response.predictions:
                logger.info(f"🔮 Predictions: {', '.join(response.predictions)}")
            
            if response.comparable_players:
                logger.info(f"👥 Comparable players: {', '.join(response.comparable_players)}")
            
            if response.historical_context:
                logger.info(f"📚 Historical context: {response.historical_context}")
            
            if response.structured_data:
                logger.info(f"📋 Structured data:")
                logger.info(f"   {json.dumps(response.structured_data, indent=2)}")
            
            logger.info(f"✅ Scenario {i} completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Scenario {i} failed: {e}")


def main():
    """Main function to demonstrate structured outputs with Pydantic validation for sports"""
    import asyncio
    
    try:
        logger.info("=" * 60)
        logger.info("🏀 Starting Sports Analyst with Pydantic Validation Demo")
        logger.info("=" * 60)
        logger.info("📁 Loading environment variables from .env file...")
        
        # Create the kernel
        kernel = create_kernel()
        
        # List available plugins and functions
        logger.info("📋 Available sports analysis tools:")
        for plugin_name, plugin in kernel.plugins.items():
            logger.info(f"  🔌 Plugin: {plugin_name}")
            for function_name, function in plugin.functions.items():
                logger.info(f"    ⚙️  Function: {function_name}")
        
        # Run demo scenarios
        logger.info(f"\n{'='*60}")
        logger.info("🎭 Running Sports Analysis Demo Scenarios")
        logger.info(f"{'='*60}")
        
        asyncio.run(run_sports_demo_scenarios(kernel))
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ Sports Analyst Demo completed successfully!")
        logger.info("🏆 All Pydantic validations passed!")
        logger.info("🎯 Ready to provide validated sports analysis!")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()