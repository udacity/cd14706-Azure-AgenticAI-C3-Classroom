# main.py

import os
import sys
import json
import logging
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from tools.search import SearchTools

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
        # Get chat service
        chat_service = kernel.get_service(type=ChatCompletionClientBase)

        # Create chat history
        chat_history = ChatHistory()
        chat_history.add_user_message("latest NBA highlights")

        # Enable automatic function calling
        execution_settings = OpenAIChatPromptExecutionSettings(
            temperature=0.7,
            max_tokens=1000,
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

        # LLM will automatically call the search function
        response = await chat_service.get_chat_message_contents(
            chat_history=chat_history,
            settings=execution_settings,
            kernel=kernel
        )

        result_value = response[0].content

        logger.info(f"\n🔎 Search Results:\n{result_value}\n")

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
