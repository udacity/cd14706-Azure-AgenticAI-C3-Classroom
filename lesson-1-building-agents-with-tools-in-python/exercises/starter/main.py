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
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
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
        # TODO CREATE KERNEL
        
        # Add Azure services
        logger.info("🤖 Adding Azure Chat Completion service...")
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
        # TODO RETURN KERNEL
        
    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise


def main():
    """Main function to demonstrate the kernel setup"""
    try:
        logger.info("=" * 60)
        logger.info("🎯 Starting Semantic Kernel Demo")
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
        
        logger.info("=" * 60)
        logger.info("✅ Demo completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()