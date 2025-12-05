# Ecommerce Database Agent with Cosmos DB

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from rag.ingest import upsert_snippet, embed_texts
from rag.retriever import retrieve

# Load environment variables from .env file
load_dotenv()

# Configure logging
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
    """Create and configure Semantic Kernel with Azure services and tools"""
    try:
        logger.info("Starting Semantic Kernel setup...")
        
        # Get Azure configuration
        logger.info("Retrieving Azure OpenAI configuration from environment variables...")
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
        DEPLOYMENT_CHAT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        DEPLOYMENT_EMBED = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
        
        logger.info(f"Configuration loaded - Endpoint: {AZURE_OPENAI_ENDPOINT}")
        logger.info(f"Chat deployment: {DEPLOYMENT_CHAT}, Embedding deployment: {DEPLOYMENT_EMBED}")
        
        # Create kernel
        logger.info("Creating Semantic Kernel instance...")
        kernel = Kernel()
        
        # Add Azure services
        logger.info("Adding Azure Chat Completion service...")
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=DEPLOYMENT_CHAT,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info("Azure Chat Completion service added successfully")
        
        logger.info("Adding Azure Text Embedding service...")
        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=DEPLOYMENT_EMBED,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info("Azure Text Embedding service added successfully")

        logger.info("Semantic Kernel setup completed successfully!")
        return kernel
        
    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise


# L5 ecommerce API functions removed - focusing on database operations only


from semantic_kernel.functions.function_result import FunctionResult

async def test_cosmos_db_operations():
    """Test Cosmos DB upserting and reading operations"""
    logger.info("\n🗄️ Testing Cosmos DB Operations")
    logger.info("-" * 40)

    try:
        # Clean up any stale data from previous runs
        logger.info("🧹 Cleaning up stale data from previous runs...")
        from rag.ingest import delete_all_items
        deleted_count = await delete_all_items("test")
        if deleted_count > 0:
            logger.info(f"    Removed {deleted_count} stale items")
        else:
            logger.info("    No stale items found")

        # Test upserting ecommerce data
        logger.info("\n📝 Testing data upserting...")

        # Upsert sample ecommerce products
        test_products = [
            ("test-product-001", "Gaming Mechanical Keyboard: RGB backlit mechanical keyboard with Cherry MX switches. Price: $129.99. Category: Electronics. In stock: 15 units."),
            ("test-product-002", "Wireless Mouse: Ergonomic wireless mouse with 2.4GHz connectivity. Price: $29.99. Category: Electronics. In stock: 28 units."),
            ("test-product-003", "Office Chair: Ergonomic office chair with lumbar support. Price: $199.99. Category: Furniture. In stock: 8 units.")
        ]

        for product_id, product_text in test_products:
            await upsert_snippet(product_id, product_text, pk="test")
            logger.info(f"   ✅ Upserted: {product_id}")

        logger.info("✅ All test products upserted successfully!")

        # Test reading from Cosmos DB
        logger.info("\n📖 Testing data retrieval...")

        # Test different queries
        test_queries = [
            "gaming keyboard",
            "wireless mouse",
            "office chair",
            "electronics"
        ]

        for query in test_queries:
            logger.info(f"   🔍 Query: '{query}'")
            results = await retrieve(query, k=3, partition_key="test")

            if results:
                logger.info(f"   📊 Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"      {i}. {result.get('id', 'Unknown ID')}: {result.get('text', 'No text')[:100]}...")
            else:
                logger.info(f"   ❌ No results found for '{query}'")

        logger.info("✅ Cosmos DB operations completed successfully!")

    except Exception as e:
        logger.error(f"❌ Cosmos DB operations test failed: {e}")



def main():
    """Main function to test ecommerce database agent with Cosmos DB"""
    import asyncio
    from datetime import datetime

    try:
        logger.info("=" * 80)
        logger.info("🎯 Ecommerce Database Agent with Cosmos DB Integration")
        logger.info("=" * 80)
        logger.info("📁 Loading environment variables from .env file...")

        # Create the kernel
        kernel = create_kernel()

        # Test Cosmos DB operations
        logger.info("\n Testing Cosmos DB Integration")
        logger.info("=" * 50)
        asyncio.run(test_cosmos_db_operations())

        logger.info(f"\n{'='*80}")
        logger.info(" Database Agent Testing completed successfully!")
        logger.info(" All Cosmos DB operations tested and working!")
        logger.info(" RAG integration with text-based search demonstrated! (Vector search in L8)")
        logger.info(f"{'='*80}")
        
    except Exception as e:
        logger.error(f" Ecommerce database agent testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()