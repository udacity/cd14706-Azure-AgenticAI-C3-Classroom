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
        self.session_id = session_id
        self.memory = LongTermMemory(
            max_memories=1000,
            importance_threshold=0.3,
            enable_ai_scoring=True
        )
        self.kernel = get_openai_kernel()
        if self.kernel is None:
            logger.warning("Kernel could not be initialized. AI-related functionalities will be disabled.")

    async def chat(self, query: str) -> str:
        if not self.kernel:
            return "Error: The AI kernel is not available. Please check your configuration."

        # 1. Retrieve relevant memories
        # TODO: Retrieve relevant memories using self.memory.search_memories()
        # Hint: Use self.session_id, the user's query, a min_importance of 0.0, and a limit of 5.
        retrieved_memories = []

        # 2. Build memory context for the prompt
        memory_context = "\n\nRelevant past conversations:\n"
        if retrieved_memories:
            for mem in retrieved_memories:
                memory_context += f"- {mem.content} (importance: {mem.importance_score:.2f})\n"
            logger.info(f"Found {len(retrieved_memories)} relevant memories.")
        else:
            memory_context += "- No relevant memories found.\n"
            logger.info("No relevant memories found.")

        # 3. Create the prompt and get the LLM response
        prompt = f"""You are a helpful assistant with access to past conversation history and tool results.
Use the information from past conversations to provide a comprehensive and contextual answer.

{memory_context}

Current user query: {query}
Answer:"""
        
        chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
        chat_history = ChatHistory(system_message=prompt)

        settings = OpenAIChatPromptExecutionSettings(temperature=0.7, max_tokens=1000)
        
        # TODO: Get the agent's response using chat_service.get_chat_message_contents()
        # Hint: Pass in the chat_history, settings, and kernel.
        response = "" # Placeholder

        # 4. Store the new conversation in memory
        tags = self._extract_tags(query)
        # TODO: Add the user's query to the long-term memory
        # Hint: Use self.memory.add_memory with the session_id, query, "conversation" type, importance of 0.7, and the extracted tags.
        
        # TODO: Add the agent's response to the long-term memory
        # Hint: Use self.memory.add_memory with the session_id, response, "conversation" type, importance of 0.6, and tags.

        return response

    def _extract_tags(self, text: str) -> list:
        text_lower = text.lower()
        keywords = ["order", "product", "customer", "ord-", "prod-",
                    "shipping", "tracking", "inventory", "stock",
                    "price", "review", "rating", "delivery", "item", "purchase"]
        found_tags = [kw for kw in keywords if kw in text_lower]
        return found_tags if found_tags else ["customer"]


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
