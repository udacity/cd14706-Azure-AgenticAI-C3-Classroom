# lesson-9-maintaining-long-term-agent-memory-in-python/exercises/solution/main.py
"""
Maintaining Long-Term Agent Memory in Python with Cosmos DB - Sports Analyst Agent

This demo focuses on:
- Adding and retrieving long-term sports analyst agent memories
- Searching and filtering sports-related memories
- Demonstrating pruning and reordering strategies
- Showing memory statistics
- Running full optimization with AI-powered pruning and reordering
"""

import asyncio
import logging
from long_term_memory.core import LongTermMemory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Reduce Azure SDK noise
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def seed_sample_memories(ltm: LongTermMemory):
    # Three sessions, varied types/importance to exercise pruning/reordering
    s1, s2, s3 = "nba_session_001", "nfl_session_002", "mlb_session_003"

    await ltm.add_memory(s1, "Lakers won the championship last season", "conversation", 0.9, ["basketball","nba","championship","lakers"])
    await ltm.add_memory(s1, "LeBron James scored 40 points in Game 7", "tool_call", 0.8, ["basketball","nba","lebron","scoring"])
    await ltm.add_memory(s1, "Anthony Davis had 15 rebounds", "tool_call", 0.7, ["basketball","nba","davis","rebounds"])
    await ltm.add_memory(s1, "Asked about best playoff strategies", "conversation", 0.6, ["basketball","nba","playoffs","strategy"])

    await ltm.add_memory(s2, "Chiefs won Super Bowl LVIII", "conversation", 0.7, ["football","nfl","superbowl","chiefs"])
    await ltm.add_memory(s2, "Patrick Mahomes threw 3 touchdowns", "system_event", 0.5, ["football","nfl","mahomes","touchdowns"])
    await ltm.add_memory(s2, "Completed season statistics analysis", "tool_call", 0.6, ["football","nfl","analysis","statistics"])

    await ltm.add_memory(s3, "Yankees won the World Series", "conversation", 0.8, ["baseball","mlb","worldseries","yankees"])
    await ltm.add_memory(s3, "Aaron Judge hit 62 home runs", "conversation", 0.3, ["baseball","mlb","judge","homers"])
    await ltm.add_memory(s3, "Learning advanced baseball analytics", "knowledge", 0.6, ["baseball","mlb","analytics","learning"])

    # Add extra low-importance memories to trigger pruning
    for i in range(12):
        await ltm.add_memory(f"test_session_{i+4}", f"Low-signal test memory {i}", "conversation", 0.15 + 0.02*i, ["test"])


async def run_demo():
    logger.info("=" * 80)
    logger.info("🏈 Long-Term Sports Analyst Agent Memory — Demo")
    logger.info("=" * 80)

    # Keep it small so pruning/reordering definitely kick in
    ltm = LongTermMemory(
        max_memories=15,
        importance_threshold=0.3,
        enable_ai_scoring=True
    )

    # Seed
    await seed_sample_memories(ltm)

    # Search (single-partition queries)
    logger.info("\n🔍 Search within NBA session")
    nba = ltm.search_memories("nba_session_001", query="lakers", min_importance=0.0, limit=5)
    logger.info(f"Found {len(nba)} 'lakers' memories")

    # Update importance of first result to test updates
    if nba:
        first = nba[0]
        ltm.update_memory_importance(first.id, first.session_id, 0.95)
        logger.info(f"Raised importance of {first.id} to 0.95")

    # Show stats (cross-partition)
    logger.info("\n📊 Global memory stats")
    stats = ltm.get_memory_statistics()
    logger.info(f"Stats: {stats}")

    # Explicit pruning demos
    logger.info("\n✂️ Prune by importance")
    pruned_imp = ltm.prune_memories(strategy="importance")
    logger.info(f"Pruned by importance: {pruned_imp}")

    logger.info("\n✂️ Hybrid prune (client-side sort; no composite index required)")
    pruned_hybrid = ltm.prune_memories(strategy="hybrid")
    logger.info(f"Pruned by hybrid: {pruned_hybrid}")

    # Reordering demos
    logger.info("\n🔄 Reorder NBA session by importance")
    reordered = ltm.reorder_memories("nba_session_001", strategy="importance")
    logger.info(f"Reordered: {reordered}")

    # Full optimization (AI pruning -> reorder -> archive -> metrics)
    logger.info("\n🚀 Optimize (AI + heuristics)")
    results = await ltm.optimize_memory_performance()
    logger.info(f"Optimization results: {results}")

    logger.info("\n🏆 Sports Analyst Agent Demo complete")


def main():
    try:
        asyncio.run(run_demo())
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
