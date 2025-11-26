# lesson-9-maintaining-long-term-agent-memory-in-python/exercises/solution/main.py
"""
Maintaining Long-Term Agent Memory in Python with Cosmos DB

This demo focuses on:
- Adding and retrieving long-term agent memories
- Searching and filtering memories
- Demonstrating pruning and reordering strategies
- Showing memory statistics
- Running full optimization with AI-powered pruning and reordering
"""

import asyncio
import logging
from long_term_memory.core import LongTermMemory  # 👈 updated import

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

import logging

# Reduce Azure SDK noise
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def seed_sample_memories(ltm: LongTermMemory):
    """Seed the memory system with sample data across multiple sessions."""
    s1, s2, s3 = "travel_session_001", "work_session_002", "personal_session_003"

    # Travel session
    await ltm.add_memory(s1, "User planning trip to Japan for cherry blossom season",
                         "conversation", 0.9, ["travel", "japan", "cherry-blossoms"])
    await ltm.add_memory(s1, "Booked flights to Tokyo for March 15-25",
                         "tool_call", 0.8, ["booking", "flights", "tokyo"])
    await ltm.add_memory(s1, "Reserved hotel in Shibuya district",
                         "tool_call", 0.7, ["booking", "hotel", "shibuya"])
    await ltm.add_memory(s1, "Asked about best cherry blossom viewing spots",
                         "conversation", 0.6, ["travel", "japan", "sightseeing"])

    # Work session
    await ltm.add_memory(s2, "Working on quarterly report presentation",
                         "conversation", 0.7, ["work", "presentation", "quarterly"])
    await ltm.add_memory(s2, "Scheduled team sync next Tuesday",
                         "system_event", 0.5, ["work", "meeting", "team"])
    await ltm.add_memory(s2, "Completed data analysis for Q3 metrics",
                         "tool_call", 0.6, ["work", "analysis", "metrics"])

    # Personal session
    await ltm.add_memory(s3, "User's birthday is next month",
                         "conversation", 0.8, ["personal", "birthday"])
    await ltm.add_memory(s3, "Favorite restaurant closed down",
                         "conversation", 0.3, ["personal", "restaurant"])
    await ltm.add_memory(s3, "Learning Spanish language",
                         "knowledge", 0.6, ["personal", "learning", "spanish"])

    # Extra low-importance to trigger pruning
    for i in range(12):
        await ltm.add_memory(f"test_session_{i+4}",
                             f"Low-signal test memory {i}",
                             "conversation", 0.15 + 0.02 * i, ["test"])


async def run_demo():
    logger.info("=" * 80)
    logger.info("🧠 Long-Term Agent Memory — Demo")
    logger.info("=" * 80)

    ltm = LongTermMemory(
        max_memories=15,
        importance_threshold=0.3,
        enable_ai_scoring=True,
    )

    # Seed data
    await seed_sample_memories(ltm)

    # Search
    logger.info("\n🔍 Search within travel session")
    travel = ltm.search_memories("travel_session_001", query="japan", limit=5)
    logger.info(f"Found {len(travel)} 'japan' memories")

    # Update importance
    if travel:
        first = travel[0]
        ltm.update_memory_importance(first.id, first.session_id, 0.95)
        logger.info(f"Raised importance of {first.id} to 0.95")

    # Stats
    logger.info("\n📊 Global memory stats")
    stats = ltm.get_memory_statistics()
    logger.info(f"Stats: {stats}")

    # Pruning
    logger.info("\n✂️ Prune by importance")
    logger.info(f"Pruned: {ltm.prune_memories(strategy='importance')}")
    logger.info("\n✂️ Hybrid prune")
    logger.info(f"Pruned: {ltm.prune_memories(strategy='hybrid')}")

    # Reordering
    logger.info("\n🔄 Reorder travel session by importance")
    logger.info(f"Reordered: {ltm.reorder_memories('travel_session_001', 'importance')}")

    # Optimization
    logger.info("\n🚀 Optimize (AI + heuristics)")
    results = await ltm.optimize_memory_performance()
    logger.info(f"Optimization results: {results}")

    logger.info("\n✅ Demo complete")


def main():
    try:
        asyncio.run(run_demo())
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
