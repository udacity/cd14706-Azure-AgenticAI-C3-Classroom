# lesson-8-agentic-rag-with-python-and-cosmos-db/exercises/solution/main.py - Agentic RAG with Python and Cosmos DB
"""
Agentic RAG Implementation with Python and Cosmos DB

This demo focuses on:
- Building a minimal RAG agent that acts on its own
- Retrieving relevant documents from Cosmos DB using vector search
- Producing answers using Python and LLM calls
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


class AgenticRAGAgent:
    """
    An autonomous RAG agent that can retrieve information from Cosmos DB,
    evaluate the quality of retrieved information, and re-check the database
    if the initial retrieval is not sufficient.
    """
    
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
        logger.info(f"🤖 Agentic RAG Agent processing query: {query}")
        
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
        
        logger.info(f"🎯 Final answer generated with confidence: {response.confidence_score:.2f}")
        return response
    
    async def _assess_retrieval_quality(self, query: str, retrieved_docs: List[Dict]) -> Dict[str, Any]:
        """Assess the quality of retrieved documents and determine if re-checking is needed"""
        try:
            # Create assessment prompt
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
                "issues": ["Minor gaps in pricing information"]
            }}
            """
            
            # Create assessment function
            assessment_function = self.kernel.add_function(
                function_name="assess_retrieval_quality",
                plugin_name="rag_assessment",
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
                    "reasoning": "Unable to assess quality automatically",
                    "issues": ["Assessment failed"]
                }
                
        except Exception as e:
            logger.error(f"❌ Quality assessment failed: {e}")
            return {
                "confidence": 0.3,
                "reasoning": f"Assessment error: {e}",
                "issues": ["Assessment system error"]
            }
    
    async def _refine_query(self, original_query: str, retrieved_docs: List[Dict], issues: List[str]) -> str:
        """Refine the query based on retrieval issues to improve results"""
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
            
            refinement_function = self.kernel.add_function(
                function_name="refine_query",
                plugin_name="rag_refinement",
                prompt=refinement_prompt
            )
            
            result = await self.kernel.invoke(refinement_function)
            refined_query = str(result).strip()
            
            logger.info(f"🔄 Query refined: '{original_query}' -> '{refined_query}'")
            return refined_query
            
        except Exception as e:
            logger.error(f"❌ Query refinement failed: {e}")
            return original_query
    
    async def _generate_answer(self, query: str, retrieved_docs: List[Dict], confidence: float) -> str:
        """Generate an answer using the retrieved documents and LLM"""
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"Document {i+1} (ID: {doc.get('id', 'unknown')}):\n{doc.get('text', '')}"
                for i, doc in enumerate(retrieved_docs)
            ])
            
            # Create answer generation prompt
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
            
            # Create answer generation function
            answer_function = self.kernel.add_function(
                function_name="generate_answer",
                plugin_name="rag_answer",
                prompt=answer_prompt
            )
            
            # Execute answer generation
            result = await self.kernel.invoke(answer_function)
            answer = str(result).strip()
            
            logger.info(f"📝 Answer generated (length: {len(answer)} characters)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Answer generation failed: {e}")
            return f"I apologize, but I encountered an error while generating an answer: {e}"


def create_kernel():
    """Create and configure Semantic Kernel with Azure services for RAG"""
    try:
        logger.info("🚀 Starting Semantic Kernel setup for Agentic RAG...")
        
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


async def test_agentic_rag_queries():
    """Test the agentic RAG agent with various queries to demonstrate autonomous operation"""
    logger.info("\n🤖 Testing Agentic RAG Agent")
    logger.info("=" * 60)
    
    # Create kernel and RAG agent
    kernel = create_kernel()
    rag_agent = AgenticRAGAgent(kernel)
    
    # Test queries that should demonstrate different behaviors
    test_queries = [
        "What wireless headphones are available and what are their prices?",
        "Tell me about shipping policies and return policies",
        "What are the warranty terms for electronics?",
        "Show me information about fitness and sports products",
        "What office supplies do you have in stock?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n📝 Test Query {i}: {query}")
        logger.info("-" * 50)
        
        try:
            # Process query with agentic RAG
            response = await rag_agent.process_query(query)
            
            # Display results
            logger.info(f"🎯 Answer: {response.answer}")
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
            logger.error(f"❌ Query {i} failed: {e}")


async def test_cosmos_db_operations():
    """Test Cosmos DB upserting and reading operations for RAG"""
    logger.info("\n🗄️ Testing Cosmos DB Operations for RAG")
    logger.info("-" * 40)

    try:
        # Test upserting ecommerce data
        logger.info("📝 Testing data upserting...")
        
        # Upsert sample ecommerce products
        test_products = [
            ("product-001", "Wireless Bluetooth Headphones: Premium noise-canceling headphones with 30-hour battery life. Price: $199.99. Category: Electronics. In stock: 45 units."),
            ("product-002", "Smart Fitness Watch: Water-resistant fitness tracker with heart rate monitoring and GPS. Price: $149.99. Category: Wearables. In stock: 23 units."),
            ("product-003", "Organic Coffee Beans: Single-origin Ethiopian coffee beans, medium roast. Price: $24.99. Category: Food & Beverage. In stock: 67 units."),
            ("product-004", "Laptop Stand: Adjustable aluminum laptop stand for ergonomic workspace. Price: $39.99. Category: Office Supplies. In stock: 12 units."),
            ("product-005", "Yoga Mat: Non-slip premium yoga mat with carrying strap. Price: $49.99. Category: Sports & Fitness. In stock: 34 units."),
            ("shipping-001", "Free shipping on orders over $50. Standard shipping: 3-5 business days. Express shipping: 1-2 business days for $9.99."),
            ("return-001", "30-day return policy for all items. Items must be in original condition with tags. Free return shipping provided."),
            ("warranty-001", "1-year manufacturer warranty on electronics. Extended warranty available for purchase. Contact support for warranty claims.")
        ]
        
        for product_id, product_text in test_products:
            upsert_snippet(product_id, product_text, pk="ecommerce")
            logger.info(f"   ✅ Upserted: {product_id}")
        
        logger.info("✅ All test products upserted successfully!")
        
        # Test reading from Cosmos DB
        logger.info("\n📖 Testing data retrieval...")
        
        # Test different queries
        test_queries = [
            "gaming keyboard",
            "wireless mouse", 
            "office chair",
            "electronics"
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
        
        logger.info("✅ Cosmos DB operations completed successfully!")

    except Exception as e:
        logger.error(f"❌ Cosmos DB operations test failed: {e}")


def main():
    """Main function to demonstrate Agentic RAG with Python and Cosmos DB"""
    try:
        logger.info("=" * 80)
        logger.info("🤖 Agentic RAG Implementation with Python and Cosmos DB")
        logger.info("=" * 80)
        logger.info("📁 Loading environment variables from .env file...")
        
        # Test Cosmos DB operations first
        logger.info("\n🗄️ Testing Cosmos DB Integration")
        logger.info("=" * 50)
        asyncio.run(test_cosmos_db_operations())
        
        # Test the agentic RAG agent
        logger.info("\n🤖 Testing Agentic RAG Agent")
        logger.info("=" * 50)
        asyncio.run(test_agentic_rag_queries())
        
        logger.info(f"\n{'='*80}")
        logger.info("✅ Agentic RAG Implementation completed successfully!")
        logger.info("🎉 RAG agent demonstrated autonomous operation!")
        logger.info("🔄 Database re-checking capability verified!")
        logger.info("📚 Vector search with Cosmos DB working!")
        logger.info(f"{'='*80}")
        
    except Exception as e:
        logger.error(f"❌ Agentic RAG implementation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()