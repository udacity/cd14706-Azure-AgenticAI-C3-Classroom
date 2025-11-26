import asyncio
import logging
from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from long_term_memory.core import LongTermMemory
from long_term_memory.ai import get_openai_kernel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def seed_sample_memories(ltm: LongTermMemory):
    s1, s2, s3 = "customer_session_001", "customer_session_002", "customer_session_003"

    # Customer session 1 - Order status queries with ACTUAL order details
    await ltm.add_memory(s1, "Order ORD-12345: Status is SHIPPED. Tracking number: TRK789. Shipped on 2025-11-20. Expected delivery: 2025-11-27.",
                         "tool_call", 0.9, ["order", "order-status", "ORD-12345", "shipped"])
    await ltm.add_memory(s1, "Order ORD-12345 contains: (1) Wireless Headphones ($79.99), (2) Phone Case ($19.99). Total: $99.98",
                         "tool_call", 0.8, ["order", "products", "items", "ORD-12345"])
    await ltm.add_memory(s1, "Shipping address for ORD-12345: 123 Main St, San Francisco, CA 94102",
                         "tool_call", 0.7, ["order", "shipping", "address"])
    await ltm.add_memory(s1, "User asked: When will my order ORD-12345 arrive?",
                         "conversation", 0.6, ["order", "delivery", "question"])

    # Customer session 2 - Product information with ACTUAL product details
    await ltm.add_memory(s2, "Product PROD-67890: Wireless Noise-Cancelling Headphones. Price: $99.99. Stock: 24 units available. Color options: Black, Silver, Blue.",
                         "tool_call", 0.8, ["product", "product-info", "PROD-67890", "headphones"])
    await ltm.add_memory(s2, "PROD-67890 Reviews: 4.5/5 stars (128 reviews). Top review: 'Amazing sound quality and battery life!' Features: 30hr battery, Bluetooth 5.0, ANC",
                         "tool_call", 0.7, ["product", "reviews", "ratings", "PROD-67890"])
    await ltm.add_memory(s2, "User asked: Tell me about the wireless headphones PROD-67890",
                         "conversation", 0.6, ["product", "question"])

    # Customer session 3 - Mixed queries
    await ltm.add_memory(s3, "User asked about recent order and product availability",
                         "conversation", 0.8, ["order", "product", "availability"])
    await ltm.add_memory(s3, "Checked inventory for PROD-001: 50 units available",
                         "conversation", 0.4, ["product", "inventory", "PROD-001"])
    await ltm.add_memory(s3, "User requested shipping options for order ORD-12345",
                         "tool_call", 0.6, ["order", "shipping", "ORD-12345"])

    # Extra low-importance to trigger pruning
    for i in range(12):
        await ltm.add_memory(f"customer_session_{i+4}",
                             f"Low-signal customer memory {i}",
                             "conversation", 0.15 + 0.02 * i, ["customer", "test"])


class AssistantAgent:
    def __init__(self, session_id: str = "assistant_session_default"):
        # TODO: Step 1 - Initialize the AssistantAgent
        # Store session_id as self.session_id
        # Create LongTermMemory instance with:
        #   max_memories=1000
        #   importance_threshold=0.3
        #   enable_ai_scoring=True
        # Get OpenAI kernel using get_openai_kernel()
        # Log warning if kernel is None
        pass

    async def chat(self, query: str) -> str:
        # TODO: Step 2 - Implement the chat method
        # 1. Check if kernel is available (return error message if not)
        # 2. Retrieve relevant memories using self.memory.search_memories()
        #    - Use self.session_id, query, min_importance=0.0, limit=5
        # 3. Build memory_context string from retrieved memories
        #    - Format: "\n\nRelevant past conversations:\n- {content} (importance: {score:.2f})\n"
        #    - Log number of memories found (or "No relevant memories found")
        # 4. Create prompt with:
        #    - System role: "You are a helpful assistant with access to past conversation history and tool results."
        #    - Memory context
        #    - User query
        #    - Instructions to use information from past conversations
        # 5. Get LLM response:
        #    - chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
        #    - Create ChatHistory and add prompt as user message
        #    - Use OpenAIChatPromptExecutionSettings(temperature=0.7, max_tokens=1000)
        #    - Call get_chat_message_contents()
        # 6. Store conversation in memory:
        #    - User query: memory_type="conversation", importance=0.7
        #    - Agent response: memory_type="conversation", importance=0.6
        #    - Use self._extract_tags() for tags
        # 7. Return the response
        pass

    def _extract_tags(self, text: str) -> list:
        # TODO: Step 3 - Implement tag extraction
        # Convert text to lowercase
        # Check for keywords: ["order", "product", "customer", "ORD-", "PROD-",
        #                       "shipping", "tracking", "inventory", "stock",
        #                       "price", "review", "rating", "delivery", "item", "purchase"]
        # Return list of found keywords, or ["customer"] if none found
        pass


async def run_demo():
    logger.info("=" * 80)
    logger.info("Long-Term Agent Memory - Demo")
    logger.info("=" * 80)

    ltm = LongTermMemory(
        max_memories=15,
        importance_threshold=0.3,
        enable_ai_scoring=True,
    )

    await seed_sample_memories(ltm)

    logger.info("\nSearch within customer session")
    customer = ltm.search_memories("customer_session_001", query="order", limit=5)
    logger.info(f"Found {len(customer)} 'order' memories")

    if customer:
        first = customer[0]
        ltm.update_memory_importance(first.id, first.session_id, 0.95)
        logger.info(f"Raised importance of {first.id} to 0.95")

    logger.info("\nGlobal memory stats")
    stats = ltm.get_memory_statistics()
    logger.info(f"Stats: {stats}")

    logger.info("\nPrune by importance")
    logger.info(f"Pruned: {ltm.prune_memories(strategy='importance')}")
    logger.info("\nHybrid prune")
    logger.info(f"Pruned: {ltm.prune_memories(strategy='hybrid')}")

    logger.info("\nReorder customer session by importance")
    logger.info(f"Reordered: {ltm.reorder_memories('customer_session_001', 'importance')}")

    logger.info("\nOptimize (AI + heuristics)")
    results = await ltm.optimize_memory_performance()
    logger.info(f"Optimization results: {results}")

    # Part 2: AssistantAgent Conversation Demo
    # TODO: Step 4 - After implementing AssistantAgent, uncomment this section to test it
    """
    logger.info("\n" + "=" * 80)
    logger.info("Assistant Agent with Memory - Conversation Demo")
    logger.info("=" * 80)

    # Use customer_session_001 to access the seeded order/product memories
    agent = AssistantAgent(session_id="customer_session_001")

    queries = [
        "What's the status of my order ORD-12345?",
        "Tell me about product PROD-67890",
        "Do you have any information about my recent orders?"
    ]

    for i, query in enumerate(queries, 1):
        logger.info(f"\n--- User Query {i}: {query} ---")
        response = await agent.chat(query)
        logger.info(f"Agent: {response[:200]}..." if len(response) > 200 else f"Agent: {response}")

        session_stats = agent.memory.get_memory_statistics(agent.session_id)
        logger.info(f"Session memories: {session_stats.get('total_memories', 0)}")
    """

    logger.info("\nDemo complete")


def main():
    try:
        asyncio.run(run_demo())
    except Exception as e:
        logger.error(f"Demo failed: {e}")


if __name__ == "__main__":
    main()
