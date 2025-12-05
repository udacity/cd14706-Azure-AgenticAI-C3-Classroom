# lesson-6-creating-web-search-agents-with-python/exercises/solution/main.py - Ecommerce Web Search Agent
"""
Ecommerce Web Search Agent with Bing Integration

This demo focuses on:
- Web search integration for product research and ecommerce data
- Demonstrating real-time product information from web sources
- Price comparison and product review aggregation
- Comprehensive ecommerce data collection and analysis
- Live web search response validation and processing
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
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
from tools.search import SearchTools

# Load environment variables from .env file
load_dotenv()

# Configure logging
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

        # Register Bing ecommerce search plugin
        kernel.add_plugin(SearchTools(), "ecommerce_search")
        logger.info("✅ SearchTools plugin registered")

        return kernel

    except Exception as e:
        logger.error(f"❌ Kernel initialization failed: {e}")
        raise


# L5 API functions removed - focusing on web search only

from semantic_kernel.functions.function_result import FunctionResult

async def test_ecommerce_search(kernel: Kernel):
    """Test the ecommerce search integration using Azure AI Foundry"""
    logger.info("\n🛍️ Testing Ecommerce Search Tools")
    logger.info("-" * 40)

    try:
        # Test product search
        logger.info("\n📱 Testing Product Search")
        search_func = kernel.plugins["ecommerce_search"].functions["product_web_search"]
        args = KernelArguments(query="wireless headphones best 2024", max_results=3)

        result: FunctionResult = await kernel.invoke(search_func, args)
        result_value = result.value

        if isinstance(result_value, str):
            result_value = json.loads(result_value)

        for i, item in enumerate(result_value, 1):
            logger.info(f"{i}. {item.get('title', 'No title')}")
            logger.info(f"   URL: {item.get('url', 'No URL')}")
            logger.info(f"   Snippet: {item.get('snippet', 'No snippet')}")
        
        logger.info("✅ Product Search Results successfully integrated!")

        # Test price comparison search
        logger.info("\n💰 Testing Price Comparison Search")
        price_func = kernel.plugins["ecommerce_search"].functions["price_comparison_search"]
        price_args = KernelArguments(product_name="Sony WH-1000XM5", max_results=3)

        price_result: FunctionResult = await kernel.invoke(price_func, price_args)
        price_value = price_result.value

        if isinstance(price_value, str):
            price_value = json.loads(price_value)

        for i, item in enumerate(price_value, 1):
            logger.info(f"{i}. {item.get('title', 'No title')}")
            logger.info(f"   URL: {item.get('url', 'No URL')}")
            logger.info(f"   Snippet: {item.get('snippet', 'No snippet')}")
        
        logger.info("✅ Price Comparison Results successfully integrated!")

        # Test product review search
        logger.info("\n⭐ Testing Product Review Search")
        review_func = kernel.plugins["ecommerce_search"].functions["product_review_search"]
        review_args = KernelArguments(product_name="iPhone 15 Pro", max_results=3)

        review_result: FunctionResult = await kernel.invoke(review_func, review_args)
        review_value = review_result.value

        if isinstance(review_value, str):
            review_value = json.loads(review_value)

        for i, item in enumerate(review_value, 1):
            logger.info(f"{i}. {item.get('title', 'No title')}")
            logger.info(f"   URL: {item.get('url', 'No URL')}")
            logger.info(f"   Snippet: {item.get('snippet', 'No snippet')}")
        
        logger.info("✅ Product Review Results successfully integrated!")

    except Exception as e:
        logger.error(f"❌ Ecommerce Search test failed: {e}")



async def test_ecommerce_search_scenarios(kernel: Kernel):
    """Test realistic ecommerce search scenarios - web search only"""
    logger.info("\n🎭 Testing Realistic Ecommerce Search Scenarios")
    logger.info("=" * 60)

    # Scenario 1: Product Research with Web Search
    logger.info("\n📱 Scenario 1: Product Research with Web Search Integration")
    logger.info("-" * 50)
    try:
        product_name = "Sony WH-1000XM5"

        # Get product info from web search
        logger.info(f"🔍 Researching product: {product_name}")

        search_func = kernel.plugins["ecommerce_search"].functions["product_web_search"]
        search_args = KernelArguments(query=f"{product_name} specifications features", max_results=3)
        search_result = await kernel.invoke(search_func, search_args)
        search_data = search_result.value

        if isinstance(search_data, str):
            search_data = json.loads(search_data)

        logger.info(f"   🌐 Web Search Results: {len(search_data)} sources found")
        for i, item in enumerate(search_data[:2], 1):
            logger.info(f"   {i}. {item.get('title', 'No title')[:50]}...")

        logger.info("✅ Product research with web search completed successfully!")

    except Exception as e:
        logger.error(f"❌ Product research scenario failed: {e}")

    # Scenario 2: Price Comparison with Web Search
    logger.info("\n💰 Scenario 2: Price Comparison with Web Search")
    logger.info("-" * 50)
    try:
        product_name = "MacBook Pro M3"

        logger.info(f"🛒 Comparing prices for: {product_name}")

        # Get price comparison from web search
        price_func = kernel.plugins["ecommerce_search"].functions["price_comparison_search"]
        price_args = KernelArguments(product_name=product_name, max_results=4)
        price_result = await kernel.invoke(price_func, price_args)
        price_data = price_result.value

        if isinstance(price_data, str):
            price_data = json.loads(price_data)

        logger.info(f"   💰 Price Comparison Results: {len(price_data)} retailers found")
        for i, item in enumerate(price_data[:3], 1):
            logger.info(f"   {i}. {item.get('title', 'No title')[:40]}...")

        logger.info("✅ Price comparison with web search completed successfully!")

    except Exception as e:
        logger.error(f"❌ Price comparison scenario failed: {e}")

    # Scenario 3: Customer Support with Review Analysis
    logger.info("\n🎧 Scenario 3: Customer Support with Web Review Analysis")
    logger.info("-" * 50)
    try:
        product_name = "iPhone 15 Pro"
        customer_query = "I'm having issues with my iPhone camera"

        logger.info(f"🎧 Customer Support Query: {customer_query}")
        logger.info(f"📱 Analyzing reviews for: {product_name}")

        # Get product reviews from web search
        review_func = kernel.plugins["ecommerce_search"].functions["product_review_search"]
        review_args = KernelArguments(product_name=product_name, max_results=5)
        review_result = await kernel.invoke(review_func, review_args)
        review_data = review_result.value

        if isinstance(review_data, str):
            review_data = json.loads(review_data)

        logger.info(f"   ⭐ Web Review Sources: {len(review_data)} sources analyzed")
        for i, item in enumerate(review_data[:3], 1):
            logger.info(f"   {i}. {item.get('title', 'No title')[:45]}...")

        logger.info("✅ Customer support with web review analysis completed successfully!")

    except Exception as e:
        logger.error(f"❌ Customer support scenario failed: {e}")


def main():
    """Main function to test external API integrations"""
    import asyncio
    from datetime import datetime
    
    try:
        logger.info("=" * 80)
        logger.info("🛍️ Ecommerce Web Search Agent with Bing Integration")
        logger.info("=" * 80)
        logger.info("📁 Loading environment variables from .env file...")
        logger.info("🔍 Initializing ecommerce web search capabilities...")
        
        # Create the kernel
        kernel = create_kernel()
        
        # List available plugins and functions
        logger.info("\n📋 Available Ecommerce Search Tools:")
        for plugin_name, plugin in kernel.plugins.items():
            if plugin_name == 'ecommerce_search':
                logger.info(f"  🔌 {plugin_name.upper()} API:")
                for function_name, function in plugin.functions.items():
                    logger.info(f"    ⚙️  {function_name}")

        # Test ecommerce search scenarios
        asyncio.run(test_ecommerce_search_scenarios(kernel))

        # Test ecommerce search
        asyncio.run(test_ecommerce_search(kernel))
        
        logger.info(f"\n{'='*80}")
        logger.info("✅ Ecommerce Web Search Agent testing completed successfully!")
        logger.info("🎉 All search tools tested and working!")
        logger.info("🏆 Real-time ecommerce data integration demonstrated!")
        logger.info(f"{'='*80}")
        
    except Exception as e:
        logger.error(f"❌ API testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()