# lesson-1-building-agents-with-tools-in-python/demo/main.py - Sports Analyst Bot
"""
Sports Analyst Bot with Semantic Kernel

This demo demonstrates:
- Semantic Kernel setup with sports analysis tools
- Sports scores and player statistics tools
- AI-powered sports analysis and insights
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
from tools.sports_scores import SportsScoresTools
from tools.player_stats import PlayerStatsTools

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
logging.getLogger('tools').setLevel(logging.WARNING)


def create_kernel():
    """Create and configure Semantic Kernel with Azure services and sports tools"""
    try:
        logger.info("🚀 Starting Semantic Kernel setup for Sports Analyst Bot...")
        
        # Get Azure configuration
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"] # 2024-10-21
        DEPLOYMENT_CHAT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        DEPLOYMENT_EMBED = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
        
        # Create kernel
        logger.info("🔧 Creating Semantic Kernel instance and adding services/tools...")
        kernel = Kernel()
        
        # Add Azure services
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=DEPLOYMENT_CHAT,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info("✅ Azure Chat Completion service added successfully")
        
        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=DEPLOYMENT_EMBED,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info("✅ Azure Text Embedding service added successfully")
        
        # Add sports tools as SK plugins
        logger.info("🏀 Adding sports analysis tools as Semantic Kernel plugins...")
        kernel.add_plugin(SportsScoresTools(), "sports_scores")
        logger.info("✅ SportsScoresTools plugin added successfully")
        kernel.add_plugin(PlayerStatsTools(), "player_stats")
        logger.info("✅ PlayerStatsTools plugin added successfully")
        
        logger.info("🎉 Sports Analyst Bot setup completed successfully!")
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





        system_message = """You are an expert sports analyst with access to real-time sports data. You can:


1. Get recent sports scores for various leagues (NBA, NFL, MLB, NHL, Premier League, etc.)


2. Look up detailed player statistics and performance data


Use the available tools when you need current sports information."""





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


    """Main function to demonstrate the Sports Analyst Bot"""


    try:
        logger.info("=" * 60)
        logger.info("🏀 Starting Sports Analyst Bot Demo")
        logger.info("=" * 60)
        logger.info("📁 Loading environment variables from .env file...")





        # Create the kernel


        kernel = create_kernel()





        # List available plugins and functions


        logger.info("📋 Available sports analysis tools:")


        for plugin_name, plugin in kernel.plugins.items():


            logger.info(f"  🔌 Plugin: {plugin_name}")


            for function_name, function in plugin.functions.items():


                logger.info(f"    ⚙️  Function: {function_name}")


        


                logger.info("-" * 60)





        # Run conversational agent demo


        await chat_with_agent(kernel, "Show me NBA scores.")

        logger.info("=" * 60)
        logger.info("✅ Sports Analyst Bot Demo completed successfully!")
        logger.info("=" * 60)





    except Exception as e:


        logger.error(f"❌ Demo failed: {e}")


        import traceback


        traceback.print_exc()


        sys.exit(1)








if __name__ == "__main__":


    asyncio.run(main())

