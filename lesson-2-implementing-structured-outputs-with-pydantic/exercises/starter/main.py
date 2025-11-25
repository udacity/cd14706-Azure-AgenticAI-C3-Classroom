# lesson-2-implementing-structured-outputs-with-pydantic/exercises/solution/main.py - Structured Outputs with Pydantic
"""
Structured Outputs with Pydantic

This demo demonstrates:
- Semantic Kernel setup with tools
- Pydantic model validation
- Structured JSON output generation
- Customer service agent with validated responses
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
from tools.order_status import OrderStatusTools
from tools.product_info import ProductInfoTools
from models import CustomerServiceResponse, OrderResponse, ProductResponse, OrderStatus, ProductAvailability

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


async def process_customer_query(kernel: Kernel, query: str) -> CustomerServiceResponse:
    """Process a customer query using Semantic Kernel and return validated response"""
    try:
        logger.info(f"🤖 Processing customer query: {query}")

        # Create chat history
        chat_history = ChatHistory()
        chat_history.add_system_message(create_customer_service_prompt())
        chat_history.add_user_message(query)

        # Get the chat completion service
        chat_service = kernel.get_service(type=ChatCompletionClientBase)

        # Configure execution settings with automatic function calling
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


async def run_demo_scenarios(kernel: Kernel):
    """Run demo scenarios showcasing structured outputs with Pydantic validation"""
    demo_queries = [
        "What's the status of my order ORD-001?",
        "Can you tell me about product PROD-002?",
        "I need help with my order ORD-999 that doesn't exist",
        "What products do you have available?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"🎭 Demo Scenario {i}: {query}")
        logger.info(f"{'='*60}")
        
        try:
            # Process the query
            response = await process_customer_query(kernel, query)
            
            # Display results
            logger.info(f"📝 Human-readable response:")
            logger.info(f"   {response.human_readable_response}")
            
            logger.info(f"🔧 Tools used: {', '.join(response.tools_used)}")
            logger.info(f"📊 Confidence score: {response.confidence_score}")
            logger.info(f"💡 Follow-up suggestions: {', '.join(response.follow_up_suggestions)}")
            
            if response.structured_data:
                logger.info(f"📋 Structured data:")
                logger.info(f"   {json.dumps(response.structured_data, indent=2)}")
            
            logger.info(f"✅ Scenario {i} completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Scenario {i} failed: {e}")


def main():
    """Main function to demonstrate structured outputs with Pydantic validation"""
    import asyncio
    
    try:
        logger.info("=" * 60)
        logger.info("🎯 Starting Structured Outputs with Pydantic Demo")
        logger.info("=" * 60)
        logger.info("📁 Loading environment variables from .env file...")
        
        # Create the kernel
        kernel = create_kernel()
        
        # List available plugins and functions
        logger.info("📋 Available plugins and functions:")
        for plugin_name, plugin in kernel.plugins.items():
            logger.info(f"  🔌 Plugin: {plugin_name}")
            for function_name, function in plugin.functions.items():
                logger.info(f"    ⚙️  Function: {function_name}")
        
        # Run demo scenarios
        logger.info(f"\n{'='*60}")
        logger.info("🎭 Running Demo Scenarios")
        logger.info(f"{'='*60}")
        
        asyncio.run(run_demo_scenarios(kernel))
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ Demo completed successfully!")
        logger.info("🎉 All Pydantic validations passed!")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()