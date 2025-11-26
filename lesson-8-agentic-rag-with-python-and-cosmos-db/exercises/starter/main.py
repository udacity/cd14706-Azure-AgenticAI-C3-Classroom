
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
        logger.info(f" Agentic RAG Agent processing query: {query}")
        
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
            
            logger.info(f"Retrieval quality: {quality_assessment['confidence']:.2f}")
            logger.info(f"Reasoning: {quality_assessment['reasoning']}")
            
            # Check if we need to re-check the database
            if quality_assessment["confidence"] >= self.confidence_threshold:
                logger.info("Retrieval quality sufficient, proceeding to answer generation")
                response.needs_recheck = False
                break
            elif attempt < self.max_retrieval_attempts - 1:
                logger.info("Retrieval quality insufficient, re-checking database with refined query")
                response.needs_recheck = True
                # Refine query for better retrieval
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
            
            # Use ChatCompletionService directly (recommended approach)
            chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
            chat_history = ChatHistory()
            chat_history.add_user_message(assessment_prompt)

            settings = OpenAIChatPromptExecutionSettings(
                temperature=0.1,
                max_tokens=500
            )
            
            response = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=settings,
                kernel=self.kernel
            )
            assessment_text = response[0].content.strip()
            
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
            logger.error(f"Quality assessment failed: {e}")
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
            
            # Use ChatCompletionService directly (recommended approach)
            chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
            chat_history = ChatHistory()
            chat_history.add_user_message(refinement_prompt)

            settings = OpenAIChatPromptExecutionSettings(
                temperature=0.3,
                max_tokens=200
            )
            
            response = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=settings,
                kernel=self.kernel
            )
            refined_query = response[0].content.strip()
            
            logger.info(f"🔄 Query refined: '{original_query}' -> '{refined_query}'")
            return refined_query
            
        except Exception as e:
            logger.error(f"Query refinement failed: {e}")
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
            
            # Use ChatCompletionService directly (recommended approach)
            chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
            chat_history = ChatHistory()
            chat_history.add_user_message(answer_prompt)

            settings = OpenAIChatPromptExecutionSettings(
                temperature=0.7,
                max_tokens=1000
            )
            
            response = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=settings,
                kernel=self.kernel
            )
            answer = response[0].content.strip()
            
            logger.info(f"📝 Answer generated (length: {len(answer)} characters)")
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return f"I apologize, but I encountered an error while generating an answer: {e}"


def create_kernel():
    """Create and configure Semantic Kernel with Azure services for RAG"""
    try:
        logger.info("Starting Semantic Kernel setup for Agentic RAG...")
        
        # Get Azure configuration
        logger.info("Retrieving Azure OpenAI configuration from environment variables...")
        AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
        AZURE_OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]
        DEPLOYMENT_CHAT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
        DEPLOYMENT_EMBED = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
        
        logger.info(f" Configuration loaded - Endpoint: {AZURE_OPENAI_ENDPOINT}")
        logger.info(f" Chat deployment: {DEPLOYMENT_CHAT}, Embedding deployment: {DEPLOYMENT_EMBED}")
        
        # Create kernel
        logger.info(" Creating Semantic Kernel instance...")
        kernel = Kernel()
        
        # Add Azure services
        logger.info(" Adding Azure Chat Completion service...")
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=DEPLOYMENT_CHAT,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info(" Azure Chat Completion service added successfully")
        
        logger.info(" Adding Azure Text Embedding service...")
        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=DEPLOYMENT_EMBED,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
        )
        logger.info(" Azure Text Embedding service added successfully")
        
        logger.info(" Semantic Kernel setup completed successfully!")
        return kernel
        
    except KeyError as e:
        logger.error(f" Missing required environment variable: {e}")
        raise
    except Exception as e:
        logger.error(f" Failed to create Semantic Kernel: {e}")
        raise


async def test_agentic_rag_queries():
    """Test the agentic RAG agent with various queries to demonstrate autonomous operation"""
    logger.info("\n Testing Agentic RAG Agent")
    logger.info("=" * 60)
    
    # Create kernel and RAG agent
    kernel = create_kernel()
    rag_agent = AgenticRAGAgent(kernel)
    
    # Mix of queries: policies that work well + one product query showing agentic retry
    test_queries = [
        "Tell me about shipping policies and return policies",
        "How do I return a product?",
        "What shipping options are available?",
        "Show me wireless headphones and their prices",  # Product query - will trigger agentic retry
        "Can I get extended warranty on electronics?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n📝 Test Query {i}: {query}")
        logger.info("-" * 50)
        
        try:
            # Process query with agentic RAG
            response = await rag_agent.process_query(query)
            
            # Display results
            logger.info(f" Answer: {response.answer}")
            logger.info(f" Confidence: {response.confidence_score:.2f}")
            logger.info(f"📚 Sources: {len(response.sources)} documents")
            logger.info(f"🔄 Retrieval attempts: {response.retrieval_attempts}")
            logger.info(f"🔄 Re-check needed: {response.needs_recheck}")
            logger.info(f" Reasoning: {response.reasoning}")
            
            # Show source details
            if response.sources:
                logger.info("📄 Source documents:")
                for j, source in enumerate(response.sources[:3], 1):  # Show first 3 sources
                    logger.info(f"   {j}. {source.get('id', 'Unknown')}: {source.get('text', '')[:100]}...")
            
        except Exception as e:
            logger.error(f" Query {i} failed: {e}")


async def test_cosmos_db_operations():
    """Test Cosmos DB upserting and reading operations for RAG"""
    logger.info("\n Testing Cosmos DB Operations for RAG")
    logger.info("-" * 40)

    try:
        # Clean up any stale data from previous runs
        logger.info("🧹 Cleaning up stale data from previous runs...")
        from rag.ingest import delete_all_items
        deleted_count = await delete_all_items("ecommerce")
        if deleted_count > 0:
            logger.info(f"    Removed {deleted_count} stale items")
        else:
            logger.info("    No stale items found")
        
        # Test upserting ecommerce data
        logger.info("\n📝 Testing data upserting...")
        
        # Upsert sample ecommerce products
        test_products = [
            ("product-001", "PRODUCT: Wireless Bluetooth Headphones - Premium over-ear headphones perfect for music lovers and travelers. Active noise-canceling technology blocks ambient sound. 30-hour battery life for extended listening sessions. Price: $199.99. Category: Electronics/Audio. In stock: 45 units. Brand: AudioTech. Bluetooth 5.0 connectivity, quick charge feature gets you 5 hours in 10 minutes. Comfortable memory foam ear cushions."),
            ("product-002", "PRODUCT: Smart Fitness Watch - Advanced wearable fitness tracker for athletes and health enthusiasts. Continuous heart rate monitoring with GPS tracking for outdoor activities. Price: $149.99. Category: Wearables/Fitness. In stock: 23 units. Brand: FitTrack. Sleep tracking, 7-day battery life, 50-meter water resistance for swimming. Compatible with iOS and Android smartphones."),
            ("product-003", "PRODUCT: Organic Coffee Beans - Premium single-origin Ethiopian coffee from high-altitude farms. Medium roast brings out fruity and floral notes with bright acidity. Price: $24.99. Category: Food & Beverage/Coffee. In stock: 67 units. Brand: Artisan Roast. 12oz whole bean bag, fair trade certified, roasted fresh weekly. Perfect for pour-over, French press, or espresso."),
            ("product-004", "PRODUCT: Laptop Stand - Adjustable aluminum stand for MacBook, Dell, HP and other laptops. Creates ergonomic workspace setup to reduce neck strain. Price: $39.99. Category: Office Supplies/Desk Accessories. In stock: 12 units. Brand: ErgoDesk. Height adjustable, foldable portable design, fits 13-17 inch laptops. Non-slip silicone pads protect your device."),
            ("product-005", "PRODUCT: Yoga Mat - Professional-grade non-slip yoga mat for home workouts and studio practice. Premium cushioning provides joint protection during poses. Price: $49.99. Category: Sports & Fitness/Yoga Equipment. In stock: 34 units. Brand: ZenFlow. 72x24 inches, 6mm thickness, TPE eco-friendly material. Includes carrying strap and alignment guides."),
            ("product-006", "PRODUCT: Gaming Keyboard - Mechanical gaming keyboard designed for competitive esports and PC gamers. Cherry MX Red switches provide fast linear response. RGB backlit keys with customizable lighting effects. Price: $129.99. Category: Electronics/Gaming Peripherals. In stock: 28 units. Brand: GameTech Pro. Programmable macro keys, detachable wrist rest, USB passthrough port, anti-ghosting technology. Compatible with Windows and Mac."),
            ("product-007", "PRODUCT: Wireless Mouse - High-precision wireless gaming mouse for FPS and MOBA games. 16000 DPI optical sensor with adjustable sensitivity on the fly. Price: $79.99. Category: Electronics/Gaming Peripherals. In stock: 52 units. Brand: GameTech Pro. Rechargeable lithium battery lasts 70 hours, 6 programmable buttons, RGB lighting effects, ergonomic right-hand design. Works with PC and laptop computers."),
            ("product-008", "PRODUCT: Office Chair - Premium ergonomic mesh office chair designed for all-day comfort and productivity. Lumbar support system adjusts to your spine curvature. Price: $249.99. Category: Office Supplies/Office Furniture. In stock: 15 units. Brand: ErgoDesk. Adjustable seat height and armrests, 360-degree swivel, supports up to 300lbs. 5-year manufacturer warranty. Suitable for home office and corporate workspace."),
            ("product-009", "PRODUCT: Running Shoes - Lightweight performance running shoes for marathon training and daily runs. Cushioned EVA midsole absorbs impact for joint protection. Price: $89.99. Category: Sports & Fitness/Athletic Footwear. In stock: 41 units. Brand: RunFast. Available in sizes 6-12 for men and women. Breathable mesh upper, shock absorption, reflective details for night running. Ideal for road running and treadmill workouts."),
            ("product-010", "PRODUCT: Wireless Earbuds - True wireless Bluetooth earbuds with active noise cancellation for immersive audio. Compact design fits comfortably in ears during workouts and commutes. Price: $119.99. Category: Electronics/Audio. In stock: 38 units. Brand: AudioTech. 8-hour battery per charge plus 24 hours with charging case, touch controls, IPX5 sweat and water resistance. Perfect for music, podcasts, and calls."),
            ("shipping-info", "SHIPPING INFORMATION: Free standard shipping available on all orders over $50. Standard delivery takes 3-5 business days via USPS or UPS. Express shipping option delivers in 1-2 business days for additional $9.99 fee. International shipping available to Canada and Mexico. Same-day delivery available in select metropolitan cities for $19.99 premium fee."),
            ("return-policy", "RETURN POLICY: We offer a generous 30-day return policy on all products purchased from our store. Items must be returned in original condition with all tags attached and original packaging. Free return shipping labels provided for your convenience. Refunds processed within 5-7 business days after we receive your return. Exchanges available for different sizes or colors of the same product."),
            ("warranty-info", "WARRANTY INFORMATION: All electronics come with standard 1-year manufacturer warranty covering defects in materials and workmanship. Extended warranty plans available for purchase at checkout. Contact our customer support team to file warranty claims. Warranty does not cover accidental damage or normal wear and tear. Optional accidental damage protection plans available for high-value electronics and appliances.")
        ]
        
        for product_id, product_text in test_products:
            await upsert_snippet(product_id, product_text, pk="ecommerce")
            logger.info(f"    Upserted: {product_id}")
        
        logger.info(" All test products upserted successfully!")
        
        # Test reading from Cosmos DB
        logger.info("\n📖 Testing data retrieval...")
        
        # Test different queries - simple keywords like demo
        test_queries = [
            "gaming keyboard",
            "wireless mouse",
            "office chair",
            "headphones"
        ]

        for query in test_queries:
            logger.info(f"    Query: '{query}'")
            results = await retrieve(query, k=3)

            if results:
                logger.info(f"    Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"      {i}. {result.get('id', 'Unknown ID')}: {result.get('text', 'No text')[:100]}...")
            else:
                logger.info(f"    No results found for '{query}'")
        
        logger.info(" Cosmos DB operations completed successfully!")

    except Exception as e:
        logger.error(f" Cosmos DB operations test failed: {e}")


async def main_async():
    """Main async function to run all tests in a single event loop"""
    try:
        logger.info("=" * 80)
        logger.info("Agentic RAG Implementation with Python and Cosmos DB")
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