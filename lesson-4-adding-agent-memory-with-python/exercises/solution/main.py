# lesson-4-adding-agent-memory-with-python/exercises/solution/main.py - Agent Memory Management
"""
Agent Memory Management with Short-Term Memory

This demo demonstrates:
- Semantic Kernel setup with tools
- Short-term memory implementation for customer service
- Memory persistence and context management
- Customer service agent with memory capabilities
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
from tools.order_status import OrderStatusTools
from tools.product_info import ProductInfoTools
from models import CustomerServiceResponse, OrderResponse, ProductResponse, OrderStatus, ProductAvailability
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
        kernel.add_plugin(OrderStatusTools(), "order_status")
        logger.info("✅ OrderStatusTools plugin added successfully")
        
        kernel.add_plugin(ProductInfoTools(), "product_info")
        logger.info("✅ ProductInfoTools plugin added successfully")
        
        logger.info("🎉 Semantic Kernel setup completed successfully!")
        return kernel
        
    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise


def create_customer_service_prompt() -> str:
    """Create a prompt that requests structured JSON output"""
    return """
You are a helpful customer service agent. You have access to tools to check order status and product information.

When a customer asks about their order or a product, use the appropriate tools and then provide a response in the following JSON format. ALL FIELDS ARE REQUIRED:

{
    "query_type": "order_status" or "product_info" or "general",
    "human_readable_response": "A helpful, friendly response to the customer",
    "structured_data": {
        // Include relevant data based on query type - ALL FIELDS REQUIRED
    },
    "tools_used": ["list", "of", "tools", "used"],
    "confidence_score": 0.95,
    "follow_up_suggestions": ["suggestion1", "suggestion2"]
}

For order status queries, the structured_data should match this format (ALL FIELDS REQUIRED):
{
    "order_id": "ORD-12345",
    "status": "processing",
    "tracking_number": "TRK789",
    "estimated_delivery": "2024-01-20",
    "items": ["Item 1", "Item 2"],
    "message": "Order is being processed"
}

For product info queries, the structured_data should match this format (ALL FIELDS REQUIRED):
{
    "product_id": "PROD-67890",
    "name": "Sample Product",
    "price": 29.99,
    "category": "Electronics",
    "description": "A great product",
    "availability": "in_stock",
    "stock_quantity": 50,
    "rating": 4.5,
    "reviews_count": 100,
    "message": "Product is available"
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
        customer_response = CustomerServiceResponse(**response_data)
        
        # If there's structured data, validate it against the appropriate model
        if customer_response.structured_data:
            if query_type == "order_status":
                # Add fallback values for order data
                order_data = customer_response.structured_data
                if order_data.get("order_id") is None:
                    order_data["order_id"] = "ORD-UNKNOWN"
                if order_data.get("status") is None:
                    order_data["status"] = "not_found"
                if order_data.get("items") is None:
                    order_data["items"] = []
                elif isinstance(order_data.get("items"), list):
                    # Ensure items are strings, not dicts
                    order_data["items"] = [str(item.get("name", item)) if isinstance(item, dict) else
                                            str(item) for item in order_data["items"]]

                order_response = OrderResponse(**order_data)
                logger.info(f"✅ Order data validated: {order_response.order_id} - {order_response.status}")
                
            elif query_type == "product_info":
                # Add fallback values for product data
                product_data = customer_response.structured_data
                # Map tool field names to model field names
                if "in_stock" in product_data:
                    product_data["availability"] = "in_stock" if product_data["in_stock"] else "out_of_stock"
                if "reviews" in product_data:
                    product_data["reviews_count"] = product_data["reviews"]
                # Map invalid availability values to valid enum values
                if product_data.get("availability") == "not_available":
                    product_data["availability"] = "out_of_stock"
                elif product_data.get("availability") not in ["in_stock", "out_of_stock", "discontinued", None]:
                    # Map common invalid values to valid enum values
                    availability_mapping = {
                        "not found": "out_of_stock",
                        "unavailable": "out_of_stock",
                        "available": "in_stock",
                        "yes": "in_stock",
                        "no": "out_of_stock"
                    }
                    product_data["availability"] = availability_mapping.get(
                        str(product_data["availability"]).lower(),
                        "out_of_stock"
                    )
                # Add fallbacks
                if product_data.get("product_id") is None:
                    product_data["product_id"] = "PROD-UNKNOWN"
                if product_data.get("name") is None:
                    product_data["name"] = "Unknown Product"
                if product_data.get("price") is None:
                    product_data["price"] = 0.0
                if product_data.get("category") is None:
                    product_data["category"] = "Unknown"
                if product_data.get("description") is None:
                    product_data["description"] = "No description available"
                if product_data.get("availability") is None:
                    product_data["availability"] = "out_of_stock"
                if product_data.get("stock_quantity") is None:
                    product_data["stock_quantity"] = 0
                if product_data.get("rating") is None:
                    product_data["rating"] = 0.0
                if product_data.get("reviews_count") is None:
                    product_data["reviews_count"] = 0

                product_response = ProductResponse(**product_data)
                logger.info(f"✅ Product data validated: {product_response.product_id} - {product_response.name}")
        
        logger.info("🎉 All Pydantic validation passed!")
        return customer_response
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        raise ValueError(f"Invalid JSON in response: {e}")
    except Exception as e:
        logger.error(f"❌ Pydantic validation failed: {e}")
        raise ValueError(f"Validation error: {e}")


async def process_customer_query_with_memory(kernel: Kernel, query: str, memory: ShortTermMemory) -> CustomerServiceResponse:
    """Process a customer query using Semantic Kernel with memory context"""
    try:
        logger.info(f"🤖 Processing customer query with memory: {query}")
        
        # Add user query to memory
        memory.add_conversation("user", query)
        
        # Get conversation context for the prompt
        context = memory.get_context_window(max_tokens=1000)
        
        # Create chat history with memory context
        chat_history = ChatHistory()
        chat_history.add_system_message(f"{create_customer_service_prompt()}\n\nPrevious conversation context:\n{context}")
        chat_history.add_user_message(f"Current customer query: {query}")

        # Get chat completion service and enable automatic tool calling
        chat_service = kernel.get_service(type=ChatCompletionClientBase)
        execution_settings = kernel.get_prompt_execution_settings_from_service_id(
            service_id=chat_service.service_id
        )
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Execute with automatic tool calling
        result = await chat_service.get_chat_message_contents(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel
        )
        response_text = str(result[0].content) if result else ""
        
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

        # Track tool usage in memory
        if validated_response.tools_used and validated_response.structured_data:
            for tool_name in validated_response.tools_used:
                # Extract relevant input based on query
                tool_input = {}
                if tool_name == "order_status" and validated_response.structured_data.get('order_id'):
                    tool_input = {"order_id": validated_response.structured_data['order_id']}
                elif tool_name == "product_info" and validated_response.structured_data.get('product_id'):
                    tool_input = {"product_id": validated_response.structured_data['product_id']}

                # Add tool call to memory
                memory.add_tool_call(tool_name, tool_input, validated_response.structured_data, success=True)
                logger.info(f"📞 Tracked tool call in memory: {tool_name}")

        # Add assistant response to memory
        memory.add_conversation("assistant", validated_response.human_readable_response)

        return validated_response
        
    except Exception as e:
        logger.error(f"❌ Failed to process customer query: {e}")
        # Add error to memory
        memory.add_conversation("assistant", f"I apologize, but I encountered an error: {e}")
        # Return a fallback response
        return CustomerServiceResponse(
            query_type="general",
            human_readable_response=f"I apologize, but I encountered an error processing your request: {e}",
            structured_data=None,
            tools_used=[],
            confidence_score=0.0,
            follow_up_suggestions=["Please try rephrasing your question", "Contact support if the issue persists"]
        )


async def run_memory_demo(kernel: Kernel):
    """Run demo scenarios showcasing memory functionality"""
    demo_scenarios = [
        {
            "name": "Order Status Query with Memory",
            "inputs": [
                "I need to check my order status",
                "My order number is ORD-001",
                "Can you tell me more about the items in that order?"
            ]
        },
        {
            "name": "Product Information with Memory",
            "inputs": [
                "I want to know about a product",
                "The product ID is PROD-001",
                "Is that product still in stock?"
            ]
        },
        {
            "name": "Mixed Query with Memory Context",
            "inputs": [
                "I have a question about order ORD-002",
                "I also want to know about product PROD-002",
                "Can you tell me about both the order and product?"
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
            response = await process_customer_query_with_memory(kernel, user_input, memory)

            # Display tools used
            if response.tools_used:
                logger.info(f"🔧 Tools Called:")
                for tool in response.tools_used:
                    logger.info(f"   - {tool}")

            # Display response
            logger.info(f"📝 Agent Response:")
            logger.info(f"   {response.human_readable_response}")
            
            # Show memory state
            memory_summary = memory.get_memory_summary()
            logger.info(f"🧠 Memory State:")
            logger.info(f"   Items: {memory_summary['total_items']}")
            logger.info(f"   Tokens: {memory_summary['total_tokens']}")
            logger.info(f"   Usage: {memory_summary['memory_usage_percent']:.1f}%")
            
            # Show ecommerce context
            customer_context = memory.get_customer_context()
            logger.info(f"🛒 Ecommerce Context:")
            logger.info(f"   Order IDs: {customer_context['order_ids']}")
            logger.info(f"   Product IDs: {customer_context['product_ids']}")
            logger.info(f"   Recent queries: {len(customer_context['recent_queries'])}")
            logger.info(f"   Tool calls: {len(customer_context['tool_calls'])}")
        
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
        search_results = memory.search_memory("order")
        logger.info(f"   Found {len(search_results)} items containing 'order'")
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
        logger.info("  - Short-term memory for customer conversations")
        logger.info("  - Context window management")
        logger.info("  - Ecommerce entity tracking (orders, products)")
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