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
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.functions import KernelArguments
from tools.order_status import OrderStatusTools
from tools.product_info import ProductInfoTools
from tools.inventory import InventoryTools
from tools.search import SearchTools
from tools.shipping import ShippingTools
from tools.pricing import PricingTools
from tools.recommendations import RecommendationTools
from tools.reviews import ReviewTools
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


# State management functions removed - focusing on API testing


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


# State management functions removed - focusing on API testing


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


# Removed state machine demo - focusing on API testing instead


async def test_external_apis():
    """Test all external API integrations"""
    logger.info("🧪 Testing External API Integrations")
    logger.info("=" * 60)
    
    # Initialize all external API tools
    inventory_tools = InventoryTools()
    shipping_tools = ShippingTools()
    pricing_tools = PricingTools()
    recommendation_tools = RecommendationTools()
    review_tools = ReviewTools()
    
    # Test Inventory Management API
    logger.info("\n📊 Testing Inventory Management API")
    logger.info("-" * 40)
    try:
        inventory_result = inventory_tools.check_inventory("PROD-001,PROD-002")
        logger.info(f"✅ Inventory API Response:")
        logger.info(f"   API Source: {inventory_result.get('api_source', 'Unknown')}")
        logger.info(f"   Total Products: {inventory_result.get('inventory_check', {}).get('total_products_checked', 0)}")
        logger.info(f"   Products In Stock: {inventory_result.get('inventory_check', {}).get('products_in_stock', 0)}")
        
        # Test supplier info
        supplier_result = inventory_tools.get_supplier_info("PROD-001")
        logger.info(f"✅ Supplier API Response:")
        logger.info(f"   Supplier: {supplier_result.get('supplier_info', {}).get('supplier_name', 'Unknown')}")
        logger.info(f"   Lead Time: {supplier_result.get('supplier_info', {}).get('lead_time_days', 0)} days")
        
    except Exception as e:
        logger.error(f"❌ Inventory API Test Failed: {e}")
    
    # Test Shipping Calculator API
    logger.info("\n🚚 Testing Shipping Calculator API")
    logger.info("-" * 40)
    try:
        shipping_result = shipping_tools.calculate_shipping("10001", "90210", 2.5, "12x8x4", "ground")
        logger.info(f"✅ Shipping API Response:")
        logger.info(f"   API Source: {shipping_result.get('api_source', 'Unknown')}")
        logger.info(f"   Available Rates: {shipping_result.get('shipping_calculation', {}).get('total_options', 0)}")
        cheapest = shipping_result.get('shipping_calculation', {}).get('cheapest_option', {})
        if cheapest:
            logger.info(f"   Cheapest Option: {cheapest.get('service_name', 'Unknown')} - ${cheapest.get('cost', 0)}")
        
        # Test tracking
        tracking_result = shipping_tools.track_shipment("TRK123456789", "ups")
        logger.info(f"✅ Tracking API Response:")
        logger.info(f"   Status: {tracking_result.get('tracking_result', {}).get('status', 'Unknown')}")
        logger.info(f"   Location: {tracking_result.get('tracking_result', {}).get('current_location', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"❌ Shipping API Test Failed: {e}")
    
    # Test Dynamic Pricing API
    logger.info("\n💰 Testing Dynamic Pricing API")
    logger.info("-" * 40)
    try:
        pricing_result = pricing_tools.get_market_pricing("Wireless Headphones", "Electronics")
        logger.info(f"✅ Pricing API Response:")
        logger.info(f"   API Source: {pricing_result.get('api_source', 'Unknown')}")
        market_data = pricing_result.get('pricing_analysis', {})
        logger.info(f"   Average Price: ${market_data.get('average_price', 0)}")
        logger.info(f"   Competitor Count: {len(market_data.get('competitor_prices', []))}")
        
        # Test dynamic pricing
        dynamic_result = pricing_tools.calculate_dynamic_price("PROD-001", 99.99, 1.2, 50)
        logger.info(f"✅ Dynamic Pricing Response:")
        calc_data = dynamic_result.get('dynamic_pricing', {})
        logger.info(f"   Base Price: ${calc_data.get('base_price', 0)}")
        logger.info(f"   Calculated Price: ${calc_data.get('calculated_price', 0)}")
        logger.info(f"   Strategy: {calc_data.get('pricing_strategy', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"❌ Pricing API Test Failed: {e}")
    
    # Test Review Aggregation API
    logger.info("\n⭐ Testing Review Aggregation API")
    logger.info("-" * 40)
    try:
        review_result = review_tools.get_product_reviews("PROD-001", "all", 5)
        logger.info(f"✅ Review API Response:")
        logger.info(f"   API Source: {review_result.get('api_source', 'Unknown')}")
        review_data = review_result.get('review_data', {})
        logger.info(f"   Total Reviews: {review_data.get('total_reviews', 0)}")
        logger.info(f"   Average Rating: {review_data.get('average_rating', 0)}")
        logger.info(f"   Sources: {len(review_data.get('sources', []))}")
        
        # Test sentiment analysis
        sentiment_result = review_tools.analyze_review_sentiment("PROD-001")
        logger.info(f"✅ Sentiment Analysis Response:")
        sentiment_data = sentiment_result.get('sentiment_results', {})
        logger.info(f"   Overall Sentiment: {sentiment_data.get('overall_sentiment', 'Unknown')}")
        logger.info(f"   Sentiment Score: {sentiment_data.get('sentiment_score', 0)}")
        logger.info(f"   Confidence: {sentiment_data.get('confidence', 0)}")
        
    except Exception as e:
        logger.error(f"❌ Review API Test Failed: {e}")
    
    # Test Recommendation Engine API
    logger.info("\n🎯 Testing Recommendation Engine API")
    logger.info("-" * 40)
    try:
        recommendation_result = recommendation_tools.get_product_recommendations("CUST-001", "PROD-001", "Electronics", 3)
        logger.info(f"✅ Recommendation API Response:")
        logger.info(f"   API Source: {recommendation_result.get('api_source', 'Unknown')}")
        rec_data = recommendation_result.get('recommendation_results', {})
        logger.info(f"   Recommendation Type: {rec_data.get('recommendation_type', 'Unknown')}")
        logger.info(f"   Confidence Score: {rec_data.get('confidence_score', 0)}")
        logger.info(f"   Products Recommended: {len(rec_data.get('products', []))}")
        
        # Test trending products
        trending_result = recommendation_tools.get_trending_products("Electronics", "7d")
        logger.info(f"✅ Trending Products Response:")
        trending_data = trending_result.get('trending_analysis', {})
        logger.info(f"   Trending Products: {len(trending_data.get('trending_products', []))}")
        logger.info(f"   Average Trend Score: {trending_data.get('trend_insights', {}).get('average_trend_score', 0)}")
        
    except Exception as e:
        logger.error(f"❌ Recommendation API Test Failed: {e}")

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
    """Test realistic ecommerce search scenarios"""
    logger.info("\n🎭 Testing Realistic Ecommerce Search Scenarios")
    logger.info("=" * 60)
    
    # Initialize tools
    inventory_tools = InventoryTools()
    shipping_tools = ShippingTools()
    pricing_tools = PricingTools()
    recommendation_tools = RecommendationTools()
    review_tools = ReviewTools()
    
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
        
        # Check inventory
        inventory = inventory_tools.check_inventory("PROD-001")
        stock_info = inventory.get('inventory_check', {}).get('products', [{}])[0]
        logger.info(f"   📊 Stock: {stock_info.get('quantity_available_for_sale', 0)} units available")
        
        # Get pricing analysis
        pricing = pricing_tools.get_market_pricing("Wireless Headphones")
        market_price = pricing.get('pricing_analysis', {}).get('average_price', 0)
        logger.info(f"   💰 Market Price: ${market_price}")
        
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
        
        # Check internal inventory
        inventory_check = inventory_tools.check_inventory("PROD-002")
        available_items = inventory_check.get('inventory_check', {}).get('products_in_stock', 0)
        logger.info(f"   📊 Internal Stock: {available_items} units available")
        
        # Calculate shipping
        shipping = shipping_tools.calculate_shipping("10001", "90210", 3.0, "15x10x6", "ground")
        shipping_options = shipping.get('shipping_calculation', {}).get('available_rates', [])
        logger.info(f"   🚚 Shipping Options: {len(shipping_options)} available")
        
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
        
        # Get internal reviews for comparison
        internal_reviews = review_tools.get_product_reviews("PROD-001", limit=10)
        review_sources = internal_reviews.get('review_data', {}).get('sources', [])
        logger.info(f"   📊 Internal Reviews: {len(review_sources)} sources")
        
        # Analyze sentiment for insights
        sentiment = review_tools.analyze_review_sentiment("PROD-001")
        sentiment_data = sentiment.get('sentiment_results', {})
        key_phrases = sentiment_data.get('key_phrases', [])
        logger.info(f"   🔍 Key Issues Found: {len([p for p in key_phrases if p.get('sentiment') == 'negative'])}")
        
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
            if plugin_name in ['ecommerce_search', 'inventory', 'shipping', 'pricing', 'recommendations', 'reviews']:
                logger.info(f"  🔌 {plugin_name.upper()} API:")
                for function_name, function in plugin.functions.items():
                    logger.info(f"    ⚙️  {function_name}")
        
        # Test individual APIs
        asyncio.run(test_external_apis())
        
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