# lesson-1-building-agents-with-tools-in-python/exercises/solution/main.py - Setting up the Kernel with tools
"""
Setting up the Kernel with tools

This demo demonstrates:
- Semantic Kernel setup
- Tools setup
"""

import os
import sys
import logging
from dotenv import load_dotenv
from semantic_kernel import Kernel
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory
from tools.order_status import OrderStatusTools
from tools.product_info import ProductInfoTools

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress verbose logs from specific modules
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('semantic_kernel').setLevel(logging.WARNING)


def create_kernel():
    """Create and configure Semantic Kernel with Azure services and tools"""
    try:
        logger.info("🚀 Starting Semantic Kernel setup...")

        # Get Azure configuration
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
        DEPLOYMENT_CHAT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        DEPLOYMENT_EMBED = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]

        # Create kernel
        logger.info("🔧 Creating Semantic Kernel instance...")
        # TODO CREATE KERNEL

        # Add Azure services
        logger.info("💬 Adding Azure Chat Completion service...")
        # TODO ADD AZURE CHAT COMPLETION SERVICE

        logger.info("✅ Azure Chat Completion service added successfully")

        logger.info("🧠 Adding Azure Text Embedding service...")
        # TODO ADD AZURE TEXT EMBEDDING SERVICE

        logger.info("✅ Azure Text Embedding service added successfully")

        # Add tools as SK plugins
        logger.info("🛠️ Adding custom tools as Semantic Kernel plugins...")
        # TODO ADD ORDER STATUS TOOLS
        logger.info("✅ OrderStatusTools plugin added successfully")
        # TODO ADD PRODUCT INFO TOOLS
        logger.info("✅ ProductInfoTools plugin added successfully")

        logger.info("🎉 Semantic Kernel setup completed successfully!")
        return kernel

    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise




async def chat_with_agent(kernel: Kernel, user_query: str) -> str:


    """Run a single chat turn with the agent."""


    try:


        chat_service = kernel.get_service(type=ChatCompletionClientBase)


        chat_history = ChatHistory()




        system_message = """You are a helpful e-commerce customer service agent.


You have access to tools that can help you check order status and product information.

Use these tools when a customer asks a relevant question."""




        chat_history.add_system_message(system_message)


        chat_history.add_user_message(user_query)




        # Enable automatic function calling


        execution_settings = OpenAIChatPromptExecutionSettings(


            function_choice_behavior=FunctionChoiceBehavior.Auto()


        )




        logger.info(f"💬 User Query: \"{user_query}\"")

        response = await chat_service.get_chat_message_contents(

            chat_history=chat_history,

            settings=execution_settings,

            kernel=kernel

        )



        agent_response = response[0].content

        logger.info(f"🤖 Agent Response: \"{agent_response}\"")

        return agent_response


    except Exception as e:

        logger.error(f"❌ Error in chat_with_agent: {e}")

        return f"An error occurred: {e}"


async def main():
    """Main function to demonstrate the kernel setup and agent functionality"""
    try:
        logger.info("=" * 60)
        logger.info("🎯 Starting Semantic Kernel Demo")
        logger.info("=" * 60)
        logger.info("📁 Loading environment variables from .env file...")

        # Create the kernel
        kernel = create_kernel()
        
        # List available plugins and functions (original output)
        logger.info("📋 Available plugins and functions:")
        for plugin_name, plugin in kernel.plugins.items():
            logger.info(f"  🔌 Plugin: {plugin_name}")
            for function_name, function in plugin.functions.items():
                logger.info(f"    ⚙️  Function: {function_name}")
        
        # Run a single agent query
        await chat_with_agent(kernel, "What is the status of order ORD-001?")

        logger.info("=" * 60)
        logger.info("✅ Demo completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)




if __name__ == "__main__":


    asyncio.run(main())