# lesson-1-building-agents-with-tools-in-python/demo/main.py - Sports Analyst Bot
"""
Sports Analyst Bot with Semantic Kernel

This demo demonstrates:
- Semantic Kernel setup with sports analysis tools
- Sports scores and player statistics tools
- AI-powered sports analysis and insights
"""

import os
import sys
import logging
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from tools.sports_scores import SportsScoresTools
from tools.player_stats import PlayerStatsTools

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
        logger.info("🚀 Starting Semantic Kernel setup for Sports Analyst Bot...")
        
        # Get Azure configuration
        logger.info("📋 Retrieving Azure OpenAI configuration from environment variables...")
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"] # 2024-10-21
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
        
        logger.info("🎉 Sports Analyst Bot setup completed successfully!")
        return kernel
        
    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise


def create_sports_analysis_prompt() -> str:
    """Create a prompt for sports analysis"""
    return """
You are an expert sports analyst with access to real-time sports data. You can:

1. Get recent sports scores for various leagues (NBA, NFL, MLB, NHL, Premier League, etc.)
2. Look up detailed player statistics and performance data
3. Provide insights, analysis, and predictions based on the data

When analyzing sports data, consider:
- Recent performance trends
- Head-to-head matchups
- Statistical significance
- Context and circumstances
- Expert insights and predictions

Always provide thoughtful analysis backed by data, not just raw statistics.
"""


def main():
    """Main function to demonstrate the Sports Analyst Bot"""
    try:
        logger.info("=" * 60)
        logger.info("🏀 Starting Sports Analyst Bot Demo")
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
        
        # Demo scenarios
        logger.info(f"\n{'='*60}")
        logger.info("🎭 Sports Analysis Demo Scenarios")
        logger.info(f"{'='*60}")
        
        # Test sports scores tool
        logger.info("\n🏀 Testing NBA scores...")
        sports_tools = SportsScoresTools()
        nba_scores = sports_tools.get_sports_scores("NBA")
        logger.info(f"📊 Found {nba_scores['total_games']} NBA games")
        
        # Test player stats tool
        logger.info("\n👤 Testing player stats...")
        player_tools = PlayerStatsTools()
        lebron_stats = player_tools.get_player_stats("LeBron James", "NBA")
        logger.info(f"📈 {lebron_stats['name']} - {lebron_stats['team']}")
        logger.info(f"   PPG: {lebron_stats['stats']['points_per_game']}, RPG: {lebron_stats['stats']['rebounds_per_game']}")
        
        # Test team-specific scores
        logger.info("\n🏈 Testing NFL team scores...")
        chiefs_scores = sports_tools.get_sports_scores("NFL", "Chiefs")
        logger.info(f"📊 Chiefs games: {chiefs_scores['total_games']}")
        
        # Test player search
        logger.info("\n⚽ Testing player search...")
        mahomes_stats = player_tools.get_player_stats("Patrick Mahomes", "NFL")
        logger.info(f"🏈 {mahomes_stats['name']} - {mahomes_stats['team']}")
        logger.info(f"   Passing Yards: {mahomes_stats['stats']['passing_yards']}, TDs: {mahomes_stats['stats']['passing_touchdowns']}")
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ Sports Analyst Bot Demo completed successfully!")
        logger.info("🏆 Ready to analyze sports data and provide insights!")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
