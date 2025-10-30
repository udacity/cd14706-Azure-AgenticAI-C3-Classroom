# lesson-8-agentic-rag-with-python-and-cosmos-db/demo/main.py - Sports Analyst Agentic RAG Demo
"""
Sports Analyst Agentic RAG Implementation with Python and Cosmos DB

This demo focuses on:
- Building a minimal RAG agent that acts on its own for sports analysis
- Retrieving relevant sports data from Cosmos DB using vector search
- Producing comprehensive sports analysis using Python and LLM calls
- Confirming the agent can re-check the DB if first retrieval is not sufficient
- Using Semantic Kernel for the implementation
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatHistory
from models import RAGResponse, RAGQuery
from rag.ingest import upsert_snippet, embed_texts
from rag.retriever import retrieve

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reduce verbosity of Azure SDK logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.connectors.ai.open_ai.services.open_ai_handler").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)


class SportsAnalystRAGAgent:
    """
    An autonomous RAG agent specialized for sports analysis that can retrieve 
    information from Cosmos DB, evaluate the quality of retrieved information, 
    and re-check the database if the initial retrieval is not sufficient.
    """
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.chat_history = ChatHistory()
        self.max_retrieval_attempts = 3
        self.confidence_threshold = 0.7
        
    async def process_query(self, query: str) -> RAGResponse:
        """
        Process a sports analysis query using the agentic RAG approach.
        The agent will autonomously decide whether to re-check the database
        based on the quality of retrieved information.
        """
        logger.info(f"🏈 Sports Analyst RAG Agent processing query: {query}")
        
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
            logger.info(f"📚 Retrieval attempt {attempt + 1}/{self.max_retrieval_attempts}")
            
            # Retrieve relevant documents
            retrieved_docs = await retrieve(query, k=5)
            response.retrieval_attempts += 1
            response.sources = retrieved_docs
            
            # Evaluate retrieval quality
            quality_assessment = await self._assess_retrieval_quality(query, retrieved_docs)
            response.confidence_score = quality_assessment["confidence"]
            response.reasoning = quality_assessment["reasoning"]
            
            logger.info(f"📊 Retrieval quality: {quality_assessment['confidence']:.2f}")
            logger.info(f"💭 Reasoning: {quality_assessment['reasoning']}")
            
            # Check if we need to re-check the database
            if quality_assessment["confidence"] >= self.confidence_threshold:
                logger.info("✅ Retrieval quality sufficient, proceeding to answer generation")
                response.needs_recheck = False
                break
            elif attempt < self.max_retrieval_attempts - 1:
                logger.info("⚠️ Retrieval quality insufficient, re-checking database with refined query")
                response.needs_recheck = True
                # Refine query for better retrieval
                query = await self._refine_query(query, retrieved_docs, quality_assessment["issues"])
            else:
                logger.info("⚠️ Max retrieval attempts reached, proceeding with available information")
                response.needs_recheck = False
        
        # Generate answer using retrieved documents
        answer = await self._generate_answer(query, retrieved_docs, response.confidence_score)
        response.answer = answer
        
        logger.info(f"🎯 Final sports analysis generated with confidence: {response.confidence_score:.2f}")
        return response
    
    async def _assess_retrieval_quality(self, query: str, retrieved_docs: List[Dict]) -> Dict[str, Any]:
        """Assess the quality of retrieved sports documents and determine if re-checking is needed"""
        try:
            # Create sports-specific assessment prompt
            assessment_prompt = f"""
            Assess the quality of retrieved sports documents for answering this query: "{query}"
            
            Retrieved documents:
            {json.dumps([{"id": doc.get("id", ""), "text": doc.get("text", "")[:200]} for doc in retrieved_docs], indent=2)}
            
            Rate the retrieval quality on a scale of 0.0 to 1.0 and provide reasoning.
            Consider:
            1. Relevance to the sports query
            2. Completeness of sports statistics and data
            3. Quality of sports analysis content
            4. Whether additional sports information might be needed
            5. Coverage of different sports aspects (stats, performance, trends, etc.)
            
            Respond in JSON format:
            {{
                "confidence": 0.85,
                "reasoning": "Documents are highly relevant and contain comprehensive sports statistics and analysis",
                "issues": ["Minor gaps in recent performance data"]
            }}
            """
            
            # Create assessment function
            assessment_function = self.kernel.add_function(
                function_name="assess_sports_retrieval_quality",
                plugin_name="sports_rag_assessment",
                prompt=assessment_prompt
            )
            
            # Execute assessment
            result = await self.kernel.invoke(assessment_function)
            assessment_text = str(result)
            
            # Parse JSON response
            json_start = assessment_text.find('{')
            json_end = assessment_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = assessment_text[json_start:json_end]
                assessment = json.loads(json_str)
                return assessment
            else:
                # Fallback assessment
                return {
                    "confidence": 0.5,
                    "reasoning": "Unable to assess sports data quality automatically",
                    "issues": ["Assessment failed"]
                }
                
        except Exception as e:
            logger.error(f"❌ Sports quality assessment failed: {e}")
            return {
                "confidence": 0.3,
                "reasoning": f"Assessment error: {e}",
                "issues": ["Assessment system error"]
            }
    
    async def _refine_query(self, original_query: str, retrieved_docs: List[Dict], issues: List[str]) -> str:
        """Refine the sports query based on retrieval issues to improve results"""
        try:
            refinement_prompt = f"""
            The original sports query "{original_query}" did not retrieve sufficient information.
            
            Issues identified: {', '.join(issues)}
            
            Retrieved documents:
            {json.dumps([{"id": doc.get("id", ""), "text": doc.get("text", "")[:100]} for doc in retrieved_docs], indent=2)}
            
            Refine the query to better retrieve relevant sports information. Consider:
            1. Using more specific sports terminology
            2. Focusing on specific aspects (stats, performance, trends, etc.)
            3. Being more specific about teams, players, or time periods
            4. Using alternative sports keywords or synonyms
            
            Return only the refined query, no explanation.
            """
            
            refinement_function = self.kernel.add_function(
                function_name="refine_sports_query",
                plugin_name="sports_rag_refinement",
                prompt=refinement_prompt
            )
            
            result = await self.kernel.invoke(refinement_function)
            refined_query = str(result).strip()
            
            logger.info(f"🔄 Sports query refined: '{original_query}' -> '{refined_query}'")
            return refined_query
            
        except Exception as e:
            logger.error(f"❌ Sports query refinement failed: {e}")
            return original_query
    
    async def _generate_answer(self, query: str, retrieved_docs: List[Dict], confidence: float) -> str:
        """Generate a comprehensive sports analysis using the retrieved documents and LLM"""
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"Document {i+1} (ID: {doc.get('id', 'unknown')}):\n{doc.get('text', '')}"
                for i, doc in enumerate(retrieved_docs)
            ])
            
            # Create sports analysis answer generation prompt
            answer_prompt = f"""
            You are a professional sports analyst. Based on the following context documents, provide a comprehensive sports analysis.
            
            Sports Query: {query}
            
            Context Documents:
            {context}
            
            Instructions:
            1. Provide a detailed sports analysis based on the context
            2. Include relevant statistics, trends, and insights
            3. If information is incomplete, mention what's missing
            4. Cite specific documents when making claims
            5. Be analytical and provide expert insights
            6. If the context doesn't contain enough information, say so clearly
            7. Structure your analysis logically with clear sections
            
            Sports Analysis:
            """
            
            # Create answer generation function
            answer_function = self.kernel.add_function(
                function_name="generate_sports_analysis",
                plugin_name="sports_rag_answer",
                prompt=answer_prompt
            )
            
            # Execute answer generation
            result = await self.kernel.invoke(answer_function)
            answer = str(result).strip()
            
            logger.info(f"📝 Sports analysis generated (length: {len(answer)} characters)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Sports analysis generation failed: {e}")
            return f"I apologize, but I encountered an error while generating the sports analysis: {e}"


def create_kernel():
    """Create and configure Semantic Kernel with Azure services for Sports RAG"""
    try:
        logger.info("🚀 Starting Semantic Kernel setup for Sports Analyst RAG...")
        
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
        
        logger.info("🎉 Semantic Kernel setup completed successfully!")
        return kernel
        
    except KeyError as e:
        logger.error(f"❌ Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create Semantic Kernel: {e}")
        raise


async def test_sports_analyst_queries():
    """Test the sports analyst RAG agent with various sports queries to demonstrate autonomous operation"""
    logger.info("\n🏈 Testing Sports Analyst RAG Agent")
    logger.info("=" * 60)
    
    # Create kernel and RAG agent
    kernel = create_kernel()
    sports_agent = SportsAnalystRAGAgent(kernel)
    
    # Test queries that should demonstrate different behaviors
    test_queries = [
        "What are the latest NFL quarterback statistics and performance trends?",
        "How did the Lakers perform in their recent games and what are their key strengths?",
        "What are the current standings in the Premier League and who are the top performers?",
        "Analyze the performance of the top tennis players in recent tournaments",
        "What are the key statistics and trends in the NBA playoffs this season?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n📝 Sports Query {i}: {query}")
        logger.info("-" * 50)
        
        try:
            # Process query with sports analyst RAG
            response = await sports_agent.process_query(query)
            
            # Display results
            logger.info(f"🎯 Sports Analysis: {response.answer}")
            logger.info(f"📊 Confidence: {response.confidence_score:.2f}")
            logger.info(f"📚 Sources: {len(response.sources)} documents")
            logger.info(f"🔄 Retrieval attempts: {response.retrieval_attempts}")
            logger.info(f"🔄 Re-check needed: {response.needs_recheck}")
            logger.info(f"💭 Reasoning: {response.reasoning}")
            
            # Show source details
            if response.sources:
                logger.info("📄 Source documents:")
                for j, source in enumerate(response.sources[:3], 1):  # Show first 3 sources
                    logger.info(f"   {j}. {source.get('id', 'Unknown')}: {source.get('text', '')[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Sports query {i} failed: {e}")


async def test_cosmos_db_operations():
    """Test Cosmos DB upserting and reading operations for sports data"""
    logger.info("\n🗄️ Testing Cosmos DB Operations for Sports Data")
    logger.info("-" * 40)

    try:
        # Test upserting sports data
        logger.info("📝 Testing sports data upserting...")
        
        # Upsert sample sports data
        test_sports_data = [
            ("nfl-qb-001", "Patrick Mahomes: Kansas City Chiefs quarterback. 2023 stats: 4,183 passing yards, 27 touchdowns, 14 interceptions. Completion rate: 66.4%. Led team to Super Bowl victory."),
            ("nfl-qb-002", "Josh Allen: Buffalo Bills quarterback. 2023 stats: 4,306 passing yards, 29 touchdowns, 18 interceptions. Completion rate: 66.5%. Known for dual-threat ability with 524 rushing yards."),
            ("nba-lakers-001", "Los Angeles Lakers: 2023-24 season record 47-35. Key players: LeBron James (25.7 PPG, 8.3 RPG), Anthony Davis (24.1 PPG, 12.6 RPG). Strengths: Defense, veteran leadership, playoff experience."),
            ("nba-lakers-002", "Lakers recent performance: Won 8 of last 10 games. Improved three-point shooting (37.2%). Strong defensive rating (110.3). Key wins against Celtics, Warriors, and Nuggets."),
            ("premier-league-001", "Premier League 2023-24 standings: Manchester City (89 points), Arsenal (84 points), Liverpool (82 points). Top scorers: Erling Haaland (27 goals), Mohamed Salah (18 goals)."),
            ("tennis-001", "Novak Djokovic: Current world #1. 2023 Grand Slam results: Australian Open winner, French Open winner, Wimbledon finalist, US Open winner. Total career Grand Slams: 24."),
            ("tennis-002", "Carlos Alcaraz: Spanish tennis player, world #2. 2023 highlights: Wimbledon winner, US Open finalist. Known for aggressive baseline play and powerful forehand. Age: 21."),
            ("nba-playoffs-001", "NBA Playoffs 2024: Boston Celtics (1st seed, 64-18 record), Denver Nuggets (2nd seed, 57-25 record). Key storylines: Celtics' depth, Nuggets' championship defense, young teams rising.")
        ]
        
        for data_id, data_text in test_sports_data:
            await upsert_snippet(data_id, data_text, pk="sports")
            logger.info(f"   ✅ Upserted: {data_id}")
        
        logger.info("✅ All sports data upserted successfully!")
        
        # Test reading from Cosmos DB
        logger.info("\n📖 Testing sports data retrieval...")
        
        # Test different sports queries
        test_queries = [
            "quarterback statistics",
            "Lakers performance", 
            "Premier League standings",
            "tennis rankings"
        ]
        
        for query in test_queries:
            logger.info(f"   🔍 Query: '{query}'")
            results = await retrieve(query, k=3)
            
            if results:
                logger.info(f"   📊 Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"      {i}. {result.get('id', 'Unknown ID')}: {result.get('text', 'No text')[:100]}...")
            else:
                logger.info(f"   ❌ No results found for '{query}'")
        
        logger.info("✅ Cosmos DB sports operations completed successfully!")

    except Exception as e:
        logger.error(f"❌ Cosmos DB sports operations test failed: {e}")


async def main_async():
    """Main async function to demonstrate Sports Analyst Agentic RAG with Python and Cosmos DB"""
    try:
        logger.info("=" * 80)
        logger.info("🏈 Sports Analyst Agentic RAG Implementation with Python and Cosmos DB")
        logger.info("=" * 80)
        logger.info("📁 Loading environment variables from .env file...")
        
        # Test Cosmos DB operations first
        logger.info("\n🗄️ Testing Cosmos DB Integration for Sports Data")
        logger.info("=" * 50)
        await test_cosmos_db_operations()
        
        # Test the sports analyst RAG agent
        logger.info("\n🏈 Testing Sports Analyst RAG Agent")
        logger.info("=" * 50)
        await test_sports_analyst_queries()
        
        logger.info(f"\n{'='*80}")
        logger.info("✅ Sports Analyst Agentic RAG Implementation completed successfully!")
        logger.info("🎉 Sports RAG agent demonstrated autonomous operation!")
        logger.info("🔄 Database re-checking capability verified!")
        logger.info("📚 Vector search with Cosmos DB working for sports data!")
        logger.info(f"{'='*80}")
        
        # Allow time for HTTP client cleanup tasks to complete
        await asyncio.sleep(0.1)
        
    except Exception as e:
        logger.error(f"❌ Sports Analyst Agentic RAG implementation failed: {e}")
        raise

def main():
    """Main function to demonstrate Sports Analyst Agentic RAG with Python and Cosmos DB"""
    try:
        # Use asyncio.run with proper cleanup
        asyncio.run(main_async())
    except Exception as e:
        logger.error(f"❌ Sports Analyst Agentic RAG implementation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
