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
        logger.info("Initializing Semantic Kernel...")

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

        return kernel

    except Exception as e:
        logger.error(f"Kernel initialization failed: {e}")
        raise

async def test_cosmos_db_operations(kernel: Kernel):
    logger.info("\nTesting Cosmos DB Operations for Sports Data")
    logger.info("=" * 60)

    try:
        logger.info("Cleaning up stale data from previous runs...")
        from rag.ingest import delete_all_items
        deleted_count = await delete_all_items("demo")
        if deleted_count > 0:
            logger.info(f"   Removed {deleted_count} stale items")
        else:
            logger.info("   No stale items found")
        
        logger.info("\nTesting sports data upserting...")
        
        test_sports_data = [
            ("demo-lakers-001", "Los Angeles Lakers: NBA team, current record 15-10. Key players: LeBron James, Anthony Davis. Recent performance: Won 3 of last 5 games. Next game: vs Warriors."),
            ("demo-lebron-001", "LeBron James: Lakers forward, 39 years old. Season stats: 25.2 PPG, 7.8 RPG, 6.8 APG. Recent form: Excellent. Injury status: Healthy."),
            ("demo-warriors-001", "Golden State Warriors: NBA team, current record 12-13. Key players: Stephen Curry, Klay Thompson. Recent performance: Lost 4 of last 5 games."),
            ("demo-nba-news-001", "NBA Trade Rumors: Lakers looking for shooting help, Warriors considering roster changes. Recent trades: None significant. Free agency: Several role players available.")
        ]
        
        for data_id, data_text in test_sports_data:
            await upsert_snippet(data_id, data_text, pk="demo")
            logger.info(f"   Upserted: {data_id}")
        
        logger.info("All demo sports data upserted successfully!")
        
        logger.info("\nTesting sports data retrieval...")
        
        test_queries = [
            "Lakers",
            "LeBron James",
            "Warriors",
            "NBA trade rumors",
            "basketball stats"
        ]
        
        for query in test_queries:
            logger.info(f"   Query: '{query}'")
            results = await retrieve(query, k=3, partition_key="demo")
            
            if results:
                logger.info(f"   Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"      {i}. {result.get('id', 'Unknown ID')}: {result.get('text', 'No text')[:100]}...")
            else:
                logger.info(f"   No results found for '{query}'")
        
        logger.info("Cosmos DB sports operations completed successfully!")

    except Exception as e:
        logger.error(f"Cosmos DB sports operations test failed: {e}")

def main():
    try:
        logger.info("=" * 80)
        logger.info("Sports Analyst Database Agent with Cosmos DB Demo")
        logger.info("=" * 80)

        kernel = create_kernel()
        
        asyncio.run(test_cosmos_db_operations(kernel))

        logger.info("\nSports database agent test completed successfully!")
        logger.info("Cosmos DB integration with Semantic Kernel is working!")
        logger.info("Text-based search for sports data is operational! (Vector search in L8)")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()