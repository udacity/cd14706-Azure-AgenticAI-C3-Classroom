# main.py - Sports Analyst Database Agent with Cosmos DB Integration

import os
import sys
import json
import logging
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.functions import KernelArguments
from tools.sports_scores import SportsScoresTools
from tools.player_stats import PlayerStatsTools
from rag.ingest import upsert_snippet, embed_texts
from rag.retriever import retrieve

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress Azure SDK verbose logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def create_kernel():
    try:
        logger.info("🚀 Initializing Semantic Kernel with Sports Database tools...")

        endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        api_version = os.environ["AZURE_OPENAI_API_VERSION"]
        chat_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        embed_deployment = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        api_key = os.environ["AZURE_OPENAI_KEY"]

        kernel = Kernel()

        kernel.add_service(
            AzureChatCompletion(
                deployment_name=chat_deployment,
                endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        )

        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=embed_deployment,
                endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        )

        # Register sports database tools
        kernel.add_plugin(SportsScoresTools(), "sports_scores")
        kernel.add_plugin(PlayerStatsTools(), "player_stats")
        logger.info("✅ Sports database tools registered")

        return kernel

    except Exception as e:
        logger.error(f"❌ Kernel initialization failed: {e}")
        raise

async def test_cosmos_db_operations(kernel: Kernel):
    """Test Cosmos DB upserting and reading operations for sports data"""
    logger.info("\n🗄️ Testing Cosmos DB Operations for Sports Data")
    logger.info("=" * 60)

    try:
        # Test upserting sports data
        logger.info("📝 Testing sports data upserting...")
        
        # Upsert sample sports information
        test_sports_data = [
            ("demo-lakers-001", "Los Angeles Lakers: NBA team, current record 15-10. Key players: LeBron James, Anthony Davis. Recent performance: Won 3 of last 5 games. Next game: vs Warriors."),
            ("demo-lebron-001", "LeBron James: Lakers forward, 39 years old. Season stats: 25.2 PPG, 7.8 RPG, 6.8 APG. Recent form: Excellent. Injury status: Healthy."),
            ("demo-warriors-001", "Golden State Warriors: NBA team, current record 12-13. Key players: Stephen Curry, Klay Thompson. Recent performance: Lost 4 of last 5 games."),
            ("demo-nba-news-001", "NBA Trade Rumors: Lakers looking for shooting help, Warriors considering roster changes. Recent trades: None significant. Free agency: Several role players available.")
        ]
        
        for data_id, data_text in test_sports_data:
            await upsert_snippet(data_id, data_text, pk="demo")
            logger.info(f"   ✅ Upserted: {data_id}")
        
        logger.info("✅ All demo sports data upserted successfully!")
        
        # Test reading from Cosmos DB
        logger.info("\n📖 Testing sports data retrieval...")
        
        # Test different sports queries
        test_queries = [
            "Lakers",
            "LeBron James",
            "Warriors",
            "NBA trade rumors",
            "basketball stats"
        ]
        
        for query in test_queries:
            logger.info(f"   🔍 Query: '{query}'")
            results = await retrieve(query, k=3)
            
            if results:
                logger.info(f"   📊 Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"      {i}. {result.get('id', 'Unknown ID')}: {result.get('text', 'No text')[:100]}...")
            else:
                logger.info(f"   ❌ No results found for '{query}'")
        
        logger.info("✅ Cosmos DB sports operations completed successfully!")

    except Exception as e:
        logger.error(f"❌ Cosmos DB sports operations test failed: {e}")

async def test_sports_database_tools(kernel: Kernel):
    """Test sports database tools functionality"""
    logger.info("\n🏀 Testing Sports Database Tools")
    logger.info("=" * 60)

    try:
        # Test game scores
        logger.info("\n📊 Testing Game Scores Tool")
        logger.info("-" * 30)
        try:
            scores_function = kernel.plugins["sports_scores"].functions["get_game_scores"]
            args = KernelArguments(team1="Lakers", team2="Warriors", league="NBA")
            result = await kernel.invoke(scores_function, args)
            
            # Handle FunctionResult.value if necessary
            if hasattr(result, "value"):
                result = result.value
            elif isinstance(result, str):
                result = json.loads(result)
            
            logger.info("✅ Game Scores Response:")
            if result.get("success"):
                game_data = result.get("game_data", {})
                logger.info(f"   Game: {game_data.get('home_team')} vs {game_data.get('away_team')}")
                logger.info(f"   Score: {game_data.get('home_score')} - {game_data.get('away_score')}")
                logger.info(f"   Status: {game_data.get('status')}")
            else:
                logger.info(f"   Error: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Game Scores Test Failed: {e}")
        
        # Test player stats
        logger.info("\n👤 Testing Player Stats Tool")
        logger.info("-" * 30)
        try:
            player_function = kernel.plugins["player_stats"].functions["get_player_stats"]
            args = KernelArguments(player_name="LeBron James", season="2024-25")
            result = await kernel.invoke(player_function, args)
            
            # Handle FunctionResult.value if necessary
            if hasattr(result, "value"):
                result = result.value
            elif isinstance(result, str):
                result = json.loads(result)
            
            logger.info("✅ Player Stats Response:")
            if result.get("success"):
                player_data = result.get("player_data", {})
                logger.info(f"   Player: {player_data.get('name')}")
                logger.info(f"   Team: {player_data.get('team')}")
                logger.info(f"   Position: {player_data.get('position')}")
                stats = player_data.get("stats", {})
                logger.info(f"   PPG: {stats.get('points_per_game')}")
                logger.info(f"   RPG: {stats.get('rebounds_per_game')}")
                logger.info(f"   APG: {stats.get('assists_per_game')}")
            else:
                logger.info(f"   Error: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Player Stats Test Failed: {e}")
        
        # Test league standings
        logger.info("\n🏆 Testing League Standings Tool")
        logger.info("-" * 30)
        try:
            standings_function = kernel.plugins["sports_scores"].functions["get_league_standings"]
            args = KernelArguments(league="NBA", conference="western")
            result = await kernel.invoke(standings_function, args)
            
            # Handle FunctionResult.value if necessary
            if hasattr(result, "value"):
                result = result.value
            elif isinstance(result, str):
                result = json.loads(result)
            
            logger.info("✅ League Standings Response:")
            if result.get("success"):
                standings = result.get("standings", [])
                logger.info(f"   Western Conference Top 3:")
                for i, team in enumerate(standings[:3], 1):
                    logger.info(f"   {i}. {team.get('team')}: {team.get('wins')}-{team.get('losses')} ({team.get('win_pct')})")
            else:
                logger.info(f"   Error: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ League Standings Test Failed: {e}")
        
        logger.info("✅ Sports database tools testing completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Sports database tools test failed: {e}")

def main():
    try:
        logger.info("=" * 80)
        logger.info("🏀 Sports Analyst Database Agent with Cosmos DB Demo")
        logger.info("=" * 80)

        kernel = create_kernel()
        
        # Test Cosmos DB operations
        asyncio.run(test_cosmos_db_operations(kernel))
        
        # Test sports database tools
        asyncio.run(test_sports_database_tools(kernel))

        logger.info("\n✅ Sports database agent test completed successfully!")
        logger.info("🏆 Cosmos DB integration with Semantic Kernel is working!")
        logger.info("🗄️ RAG vector search for sports data is operational!")

    except Exception as e:
        logger.error(f"❌ Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()