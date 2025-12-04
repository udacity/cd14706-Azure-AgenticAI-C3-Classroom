import asyncio
import logging
from typing import Optional, Any
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments, FunctionResult
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
    s1, s2, s3 = "lakers_session_001", "warriors_session_002", "nba_analysis_session_003"

    # Lakers session with ACTUAL game data
    await ltm.add_memory(s1, "Lakers last 5 games: Won vs Suns (118-114), Lost vs Nuggets (102-109), Won vs Clippers (125-120), Won vs Pelicans (112-108), Lost vs Warriors (115-120). Record: 3-2",
                         "tool_call", 0.9, ["lakers", "games", "scores", "recent"])
    await ltm.add_memory(s1, "Lakers current standings: 20-15 record (57.1% win rate), 5th place in Western Conference, 4.5 games behind 1st place",
                         "tool_call", 0.8, ["lakers", "standings", "conference", "record", "current", "season"])
    await ltm.add_memory(s1, "LeBron James stats (last 5 games avg): 26.4 PPG, 7.2 RPG, 8.6 APG, 51.2% FG. Playing 36.2 min/game. Age 39 season performance remains strong.",
                         "tool_call", 0.8, ["lakers", "lebron-james", "lebron", "james", "player-stats", "performance", "stats", "season"])
    await ltm.add_memory(s1, "User asked: How have the Lakers been performing in recent games?",
                         "conversation", 0.6, ["lakers", "question", "performance"])

    await ltm.add_memory(s2, "User inquired about Warriors team performance",
                         "conversation", 0.7, ["warriors", "team-analysis"])
    await ltm.add_memory(s2, "Retrieved Warriors record: 12-13, lost 4 of last 5 games",
                         "system_event", 0.5, ["warriors", "record", "games"])
    await ltm.add_memory(s2, "Analyzed Warriors offensive rating and defensive metrics",
                         "tool_call", 0.6, ["warriors", "analytics", "metrics"])

    await ltm.add_memory(s3, "User asked about NBA trade rumors and latest news",
                         "conversation", 0.8, ["nba", "trade-rumors", "news"])
    await ltm.add_memory(s3, "Retrieved latest NBA news about Lakers and Warriors",
                         "conversation", 0.3, ["nba", "news", "lakers", "warriors"])
    await ltm.add_memory(s3, "User interested in player statistics and season performance",
                         "knowledge", 0.6, ["nba", "player-stats", "season"])

    for i in range(12):
        await ltm.add_memory(f"test_session_{i+4}",
                             f"Low-signal test memory {i}",
                             "conversation", 0.15 + 0.02 * i, ["test"])


class SportsAnalystAgent:
    def __init__(self, session_id: str = "sports_analyst_session_default"):
        self.session_id = session_id
        self.memory = LongTermMemory(
            max_memories=1000,
            importance_threshold=0.3,
            enable_ai_scoring=True
        )
        self.kernel: Optional[Kernel] = get_openai_kernel()
        
        if self.kernel is None:
            logger.warning("OpenAI kernel not available - agent will work without LLM")
    
    async def chat(self, query: str) -> str:
        if self.kernel is None:
            return "I'm sorry, but I need Azure OpenAI configuration to respond. Please check your environment variables."
        
        logger.info(f"Retrieving relevant memories for query: {query}")
        memories = self.memory.search_memories(
            self.session_id,
            query=query,
            min_importance=0.0,
            limit=10
        )
        
        memory_context = ""
        if memories:
            memory_context = "\n\nRelevant past conversations:\n"
            for mem in memories:
                memory_context += f"- {mem.content} (importance: {mem.importance_score:.2f})\n"
            logger.info(f"Found {len(memories)} relevant memories")
        else:
            logger.info("No relevant memories found")
        
        prompt = f"""You are an expert sports analyst. Answer the user's question using ONLY the specific facts, statistics, and details from the 'Relevant past conversations' below.

CRITICAL INSTRUCTIONS:
- When statistics are available (scores, percentages, player stats, records), cite them explicitly and precisely
- Tool results and system events contain factual data - share these specific details directly with the user
- Do NOT generalize or use vague language when specific numbers and data exist in the context
- Distinguish between different metrics (e.g., "last 5 games record" vs "season record")
- If you lack specific information to fully answer the question, acknowledge what's missing

Relevant past conversations:
{memory_context}

User Question: {query}

Answer (use specific facts, numbers, and statistics from the context):"""
        
        # Use ChatCompletionService directly (recommended approach)
        chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
        chat_history = ChatHistory()
        chat_history.add_user_message(prompt)
        
        from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
        settings = OpenAIChatPromptExecutionSettings(
            temperature=0.7,
            max_tokens=1000
        )
        
        logger.info("Invoking LLM with memory context...")
        response_obj = await chat_service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=self.kernel
        )
        response = response_obj[0].content.strip()
        
        logger.info(f"Agent response generated ({len(response)} chars)")
        
        await self.memory.add_memory(
            self.session_id,
            f"User asked: {query}",
            "conversation",
            importance_score=0.7,
            tags=self._extract_tags(query)
        )
        
        await self.memory.add_memory(
            self.session_id,
            f"Agent responded: {response}",
            "conversation",
            importance_score=0.6,
            tags=self._extract_tags(response)
        )
        
        logger.info("Conversation stored in long-term memory")
        
        return response
    
    def _extract_tags(self, text: str) -> list:
        text_lower = text.lower()
        tags = []
        
        keywords = ["lakers", "warriors", "nba", "nfl", "mlb", "nhl", "lebron", "curry", "james", "scores", "stats", "standings", "game", "team", "player", "news", "analytics"]
        for keyword in keywords:
            if keyword in text_lower:
                tags.append(keyword)
        
        return tags if tags else ["sports"]


async def run_demo():
    logger.info("=" * 80)
    logger.info("Long-Term Agent Memory - Sports Analyst Demo")
    logger.info("=" * 80)

    ltm = LongTermMemory(
        max_memories=15,
        importance_threshold=0.3,
        enable_ai_scoring=True
    )

    await seed_sample_memories(ltm)

    logger.info("\nSearch within Lakers session")
    lakers = ltm.search_memories("lakers_session_001", query="lakers", limit=5)
    logger.info(f"Found {len(lakers)} 'lakers' memories")

    if lakers:
        first = lakers[0]
        ltm.update_memory_importance(first.id, first.session_id, 0.95)
        logger.info(f"Raised importance of {first.id} to 0.95")

    logger.info("\nGlobal memory stats")
    stats = ltm.get_memory_statistics()
    logger.info(f"Stats: {stats}")

    logger.info("\nPrune by importance")
    logger.info(f"Pruned: {ltm.prune_memories(strategy='importance')}")
    logger.info("\nHybrid prune")
    logger.info(f"Pruned: {ltm.prune_memories(strategy='hybrid')}")

    logger.info("\nReorder Lakers session by importance")
    logger.info(f"Reordered: {ltm.reorder_memories('lakers_session_001', 'importance')}")

    logger.info("\nOptimize (AI + heuristics)")
    results = await ltm.optimize_memory_performance()
    logger.info(f"Optimization results: {results}")

    logger.info("\n" + "=" * 80)
    logger.info("Sports Analyst Agent with Memory - Conversation Demo")
    logger.info("=" * 80)

    # Use lakers_session_001 to access the seeded Lakers/sports memories
    agent = SportsAnalystAgent(session_id="lakers_session_001")
    
    queries = [
        "Tell me about the Lakers recent games",
        "What are the Lakers current record and standings?",
        "How has LeBron James been performing this season?"
    ]
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n--- User Query {i}: {query} ---")
        response = await agent.chat(query)
        logger.info(f"Agent: {response[:200]}..." if len(response) > 200 else f"Agent: {response}")
        
        session_stats = agent.memory.get_memory_statistics(agent.session_id)
        logger.info(f"Session memories: {session_stats.get('total_memories', 0)}")
    
    logger.info("\nDemo complete")


def main():
    try:
        asyncio.run(run_demo())
    except Exception as e:
        logger.error(f"Demo failed: {e}")


if __name__ == "__main__":
    main()
