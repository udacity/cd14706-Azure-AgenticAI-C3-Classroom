# main.py (updated to focus on sports web search)

import os
import sys
import json
import logging
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.functions import KernelArguments
from tools.search import SearchTools

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_kernel():
    try:
        logger.info("🚀 Initializing Semantic Kernel with Bing Search tool...")

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

        # Register Bing sports search plugin
        kernel.add_plugin(SearchTools(), "sports_search")
        logger.info("✅ SearchTools plugin registered")

        return kernel

    except Exception as e:
        logger.error(f"❌ Kernel initialization failed: {e}")
        raise

async def test_sports_web_search(kernel: Kernel):
    logger.info("\n🌐 Testing Bing Sports Web Search")
    logger.info("=" * 60)

    try:
        search_function = kernel.plugins["sports_search"].functions["sports_web_search"]
        args = KernelArguments(query="latest NBA highlights", max_results=3)

        result = await kernel.invoke(search_function, args)

        # Handle FunctionResult.value if necessary
        if hasattr(result, "value"):
            result = result.value
        elif isinstance(result, str):
            result = json.loads(result)

        logger.info("\n🔎 Top Bing Sports Search Results:")
        for i, item in enumerate(result, 1):
            logger.info(f"{i}. {item.get('title')}")
            logger.info(f"   URL: {item.get('url')}")
            logger.info(f"   Snippet: {item.get('snippet')}\n")

    except Exception as e:
        logger.error(f"❌ Sports search test failed: {e}")

def main():
    try:
        logger.info("=" * 80)
        logger.info("🏀 Sports Analyst Bing Search Demo")
        logger.info("=" * 80)

        kernel = create_kernel()
        asyncio.run(test_sports_web_search(kernel))

        logger.info("\n✅ Sports search test completed successfully!")
        logger.info("🏆 Bing integration with Semantic Kernel is working!")

    except Exception as e:
        logger.error(f"❌ Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()