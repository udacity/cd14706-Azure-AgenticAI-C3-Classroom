import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments, FunctionResult
from models import RAGResponse, RAGQuery
from rag.ingest import upsert_snippet, embed_texts
from rag.retriever import retrieve

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.connectors.ai.open_ai.services.open_ai_handler").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.ERROR)  # Suppress asyncio cleanup warnings


class ToolLoggingFilter:
    async def on_function_invocation(self, kernel: Kernel, function: Any, arguments: KernelArguments) -> None:
        logger.info(f"Agent selected tool: {function.name}")
        logger.debug(f"Tool arguments: {dict(arguments)}")
    
    async def on_function_result(self, kernel: Kernel, function: Any, arguments: KernelArguments, result: FunctionResult) -> None:
        logger.info(f"Tool {function.name} completed successfully")


class AgenticRAGAgent:
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.chat_history = ChatHistory()
        self.max_retrieval_attempts = 3
        self.confidence_threshold = 0.7
        
    async def process_query(self, query: str) -> RAGResponse:
        """
        Process a query using the agentic RAG approach.
        The agent will autonomously decide whether to re-check the database
        based on the quality of retrieved information.
        """
        logger.info(f"Agentic RAG Agent processing query: {query}")
        
        # Initialize response
        response = RAGResponse(
            query=query,
            answer="",
            sources=[],
            confidence_score=0.0,
            retrieval_attempts=0,
            needs_recheck=False,
            reasoning=""
        )
        
        # Attempt retrieval with potential re-checking
        for attempt in range(self.max_retrieval_attempts):
            logger.info(f"Retrieval attempt {attempt + 1}/{self.max_retrieval_attempts}")
            
            retrieved_docs = await retrieve(query, k=5)
            response.retrieval_attempts += 1
            response.sources = retrieved_docs
            
            quality_assessment = await self._assess_retrieval_quality(query, retrieved_docs)
            response.confidence_score = quality_assessment["confidence"]
            response.reasoning = quality_assessment["reasoning"]
            
            logger.info(f"Retrieval quality: {quality_assessment['confidence']:.2f}")
            logger.info(f"Reasoning: {quality_assessment['reasoning']}")
            
            if quality_assessment["confidence"] >= self.confidence_threshold:
                logger.info("Retrieval quality sufficient, proceeding to answer generation")
                response.needs_recheck = False
                break
            elif attempt < self.max_retrieval_attempts - 1:
                logger.info("Retrieval quality insufficient, re-checking database with refined query")
                response.needs_recheck = True
                query = await self._refine_query(query, retrieved_docs, quality_assessment["issues"])
            else:
                logger.info("Max retrieval attempts reached, proceeding with available information")
                response.needs_recheck = False
        
        # Generate answer using retrieved documents
        answer = await self._generate_answer(query, retrieved_docs, response.confidence_score)
        response.answer = answer
        
        logger.info(f"Final answer generated with confidence: {response.confidence_score:.2f}")
        return response
    
    async def _assess_retrieval_quality(self, query: str, retrieved_docs: List[Dict]) -> Dict[str, Any]:
        try:
            assessment_prompt = f"""
            Assess the quality of retrieved documents for answering this query: "{query}"
            
            Retrieved documents:
            {json.dumps([{"id": doc.get("id", ""), "text": doc.get("text", "")[:200]} for doc in retrieved_docs], indent=2)}
            
            Rate the retrieval quality on a scale of 0.0 to 1.0 and provide reasoning.
            Consider:
            1. Relevance to the query
            2. Completeness of information
            3. Quality of content
            4. Whether additional information might be needed
            
            Respond in JSON format:
            {{
                "confidence": 0.85,
                "reasoning": "Documents are highly relevant and contain comprehensive information",
                "issues": ["Minor gaps in player statistics"]
            }}
            """
            
            # Use ChatCompletionService directly (recommended approach)
            chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
            chat_history = ChatHistory()
            chat_history.add_user_message(assessment_prompt)
            
            settings = OpenAIChatPromptExecutionSettings(
                temperature=0.1,
                max_tokens=500
            )
            
            logger.info("Assessing retrieval quality with LLM")
            
            response = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=settings,
                kernel=self.kernel
            )
            assessment_text = response[0].content.strip()
            
            json_start = assessment_text.find('{')
            json_end = assessment_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = assessment_text[json_start:json_end]
                assessment = json.loads(json_str)
                return assessment
            else:
                return {
                    "confidence": 0.5,
                    "reasoning": "Unable to assess quality automatically",
                    "issues": ["Assessment failed"]
                }
                
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {
                "confidence": 0.3,
                "reasoning": f"Assessment error: {e}",
                "issues": ["Assessment system error"]
            }
    
    async def _refine_query(self, original_query: str, retrieved_docs: List[Dict], issues: List[str]) -> str:
        try:
            refinement_prompt = f"""
            The original query "{original_query}" did not retrieve sufficient information.
            
            Issues identified: {', '.join(issues)}
            
            Retrieved documents:
            {json.dumps([{"id": doc.get("id", ""), "text": doc.get("text", "")[:100]} for doc in retrieved_docs], indent=2)}
            
            Refine the query to better retrieve relevant information. Consider:
            1. Using different keywords
            2. Being more specific or general
            3. Focusing on different aspects
            
            Return only the refined query, no explanation.
            """
            
            # Use ChatCompletionService directly (recommended approach)
            chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
            chat_history = ChatHistory()
            chat_history.add_user_message(refinement_prompt)
            
            settings = OpenAIChatPromptExecutionSettings(
                temperature=0.3,
                max_tokens=200
            )
            
            logger.info("Refining query with LLM")
            
            response = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=settings,
                kernel=self.kernel
            )
            refined_query = response[0].content.strip()
            
            logger.info(f"Query refined: '{original_query}' -> '{refined_query}'")
            return refined_query
            
        except Exception as e:
            logger.error(f"Query refinement failed: {e}")
            return original_query
    
    async def _generate_answer(self, query: str, retrieved_docs: List[Dict], confidence: float) -> str:
        try:
            context = "\n\n".join([
                f"Document {i+1} (ID: {doc.get('id', 'unknown')}):\n{doc.get('text', '')}"
                for i, doc in enumerate(retrieved_docs)
            ])
            
            answer_prompt = f"""
            Based on the following context documents, answer the user's question.
            
            Question: {query}
            
            Context Documents:
            {context}
            
            Instructions:
            1. Provide a comprehensive answer based on the context
            2. If information is incomplete, mention what's missing
            3. Cite specific documents when possible
            4. Be helpful and accurate
            5. If the context doesn't contain enough information, say so clearly
            
            Answer:
            """
            
            # Use ChatCompletionService directly (recommended approach)
            chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
            chat_history = ChatHistory()
            chat_history.add_user_message(answer_prompt)
            
            settings = OpenAIChatPromptExecutionSettings(
                temperature=0.7,
                max_tokens=1000
            )
            
            logger.info("Generating answer with LLM")
            
            response = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=settings,
                kernel=self.kernel
            )
            answer = response[0].content.strip()
            
            logger.info(f"Answer generated (length: {len(answer)} characters)")
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return f"I apologize, but I encountered an error while generating an answer: {e}"


def create_kernel():
    try:
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
        DEPLOYMENT_CHAT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        DEPLOYMENT_EMBED = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
        
        kernel = Kernel()
        
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=DEPLOYMENT_CHAT,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        
        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=DEPLOYMENT_EMBED,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        
        kernel.function_invocation_filters.append(ToolLoggingFilter())
        
        return kernel
        
    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to create Semantic Kernel: {e}")
        raise


async def test_agentic_rag_queries():
    logger.info("\nTesting Agentic RAG Agent")
    logger.info("=" * 60)
    
    kernel = create_kernel()
    rag_agent = AgenticRAGAgent(kernel)
    
    test_queries = [
        "What are the Lakers' recent game results and current record?",
        "Tell me about LeBron James' season statistics and performance",
        "What are the latest NBA trade rumors and news?",
        "Show me information about the Warriors team and their key players",
        "What are the current NBA standings and team records?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\nTest Query {i}: {query}")
        logger.info("-" * 50)
        
        try:
            response = await rag_agent.process_query(query)
            
            logger.info(f"Answer: {response.answer}")
            logger.info(f"Confidence: {response.confidence_score:.2f}")
            logger.info(f"Sources: {len(response.sources)} documents")
            logger.info(f"Retrieval attempts: {response.retrieval_attempts}")
            logger.info(f"Re-check needed: {response.needs_recheck}")
            logger.info(f"Reasoning: {response.reasoning}")
            
            if response.sources:
                logger.info("Source documents:")
                for j, source in enumerate(response.sources[:3], 1):
                    logger.info(f"   {j}. {source.get('id', 'Unknown')}: {source.get('text', '')[:100]}...")
            
        except Exception as e:
            logger.error(f"Query {i} failed: {e}")


async def test_cosmos_db_operations():
    logger.info("\nTesting Cosmos DB Operations for RAG")
    logger.info("-" * 40)

    try:
        logger.info("Testing data upserting...")
        
        test_sports_data = [
            ("sports-lakers-001", "Los Angeles Lakers: NBA team, current record 15-10. Key players: LeBron James, Anthony Davis. Recent performance: Won 3 of last 5 games. Next game: vs Warriors."),
            ("sports-lebron-001", "LeBron James: Lakers forward, 39 years old. Season stats: 25.2 PPG, 7.8 RPG, 6.8 APG. Recent form: Excellent. Injury status: Healthy."),
            ("sports-warriors-001", "Golden State Warriors: NBA team, current record 12-13. Key players: Stephen Curry, Klay Thompson. Recent performance: Lost 4 of last 5 games."),
            ("sports-nba-news-001", "NBA Trade Rumors: Lakers looking for shooting help, Warriors considering roster changes. Recent trades: None significant. Free agency: Several role players available."),
            ("sports-standings-001", "NBA Western Conference Standings: Lakers 15-10 (5th place), Warriors 12-13 (9th place). Top teams: Timberwolves 18-7, Thunder 17-8."),
            ("sports-anthony-davis-001", "Anthony Davis: Lakers center, 31 years old. Season stats: 24.8 PPG, 12.1 RPG, 2.4 BPG. Recent form: Strong. Injury status: Healthy."),
            ("sports-curry-001", "Stephen Curry: Warriors guard, 35 years old. Season stats: 28.5 PPG, 4.8 RPG, 5.2 APG. Recent form: Good. Injury status: Healthy."),
            ("sports-nba-schedule-001", "Upcoming NBA games: Lakers vs Warriors (Dec 25), Celtics vs Heat (Dec 26), Nuggets vs Suns (Dec 27). All games at 8:00 PM ET.")
        ]
        
        for data_id, data_text in test_sports_data:
            await upsert_snippet(data_id, data_text, pk="sports")
            logger.info(f"   Upserted: {data_id}")
        
        logger.info("All test sports data upserted successfully!")
        
        logger.info("\nTesting data retrieval...")
        
        test_queries = [
            "Lakers",
            "LeBron James",
            "Warriors",
            "NBA standings"
        ]
        
        for query in test_queries:
            logger.info(f"   Query: '{query}'")
            results = await retrieve(query, k=3)
            
            if results:
                logger.info(f"   Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"      {i}. {result.get('id', 'Unknown ID')}: {result.get('text', 'No text')[:100]}...")
            else:
                logger.info(f"   No results found for '{query}'")
        
        logger.info("Cosmos DB operations completed successfully!")

    except Exception as e:
        logger.error(f"Cosmos DB operations test failed: {e}")


async def main_async():
    """Main async function to run all tests in a single event loop"""
    try:
        logger.info("=" * 80)
        logger.info("Sports Analyst Agentic RAG Implementation with Python and Cosmos DB")
        logger.info("=" * 80)
        
        logger.info("\nTesting Cosmos DB Integration")
        logger.info("=" * 50)
        await test_cosmos_db_operations()
        
        logger.info("\nTesting Agentic RAG Agent")
        logger.info("=" * 50)
        await test_agentic_rag_queries()
        
        logger.info(f"\n{'='*80}")
        logger.info("Agentic RAG Implementation completed successfully!")
        logger.info(f"{'='*80}")
        
    except Exception as e:
        logger.error(f"Agentic RAG implementation failed: {e}")
        sys.exit(1)

def main():
    """Main entry point - runs async code in a single event loop"""
    try:
        # Suppress asyncio cleanup warnings (harmless but noisy)
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")
        
        # Run all async code in a single event loop to avoid cleanup issues
        asyncio.run(main_async())
        
    except Exception as e:
        logger.error(f"Agentic RAG implementation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
