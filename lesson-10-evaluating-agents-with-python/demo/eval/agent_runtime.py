# agent_runtime.py
from typing import Any, Dict, List
from pydantic import BaseModel

import asyncio
import logging

logger = logging.getLogger(__name__)


class SportsAnalystResponse(BaseModel):
    query_type: str
    human_readable_response: str
    structured_data: Dict[str, Any]
    tools_used: List[str]
    confidence_score: float
    follow_up_suggestions: List[str] = []


class MockAgent:
    async def process_query(self, query: str, query_type: str) -> SportsAnalystResponse:
        tools_used: List[str] = []
        structured: Dict[str, Any] = {}

        if query_type == "player_stats":
            tools_used.append("player_stats_tool")
            structured = {
                "player_name": "LeBron James",
                "points_per_game": 25.2,
                "rebounds_per_game": 7.8,
                "assists_per_game": 8.1,
                "field_goal_percentage": 52.3,
                "team": "Los Angeles Lakers"
            }
        elif query_type == "team_performance":
            tools_used.append("team_performance_tool")
            structured = {
                "team_name": "Los Angeles Lakers",
                "wins": 42,
                "losses": 30,
                "win_percentage": 58.3,
                "conference_rank": 4,
                "recent_form": "W-L-W-W-L"
            }
        elif query_type == "game_analysis":
            tools_used.append("game_analysis_tool")
            structured = {
                "game_id": "LAL_GSW_2024_01_15",
                "home_team": "Los Angeles Lakers",
                "away_team": "Golden State Warriors",
                "final_score": "LAL 118 - GSW 112",
                "key_players": ["LeBron James", "Stephen Curry"],
                "analysis_summary": "Lakers won with strong defense in the 4th quarter"
            }
        else:
            tools_used.append("general_sports_tool")
            structured = {"query_type": "general", "sports_news_provided": True}

        return SportsAnalystResponse(
            query_type=query_type,
            human_readable_response=f"I've analyzed your {query_type} request: {query}",
            structured_data=structured,
            tools_used=tools_used,
            confidence_score=0.85,
            follow_up_suggestions=["Would you like more detailed analysis or different statistics?"],
        )


def run_request(query: str, query_type: str) -> SportsAnalystResponse:
    """
    Synchronous entrypoint used by judge.py.
    Runs the mock sports analyst agent and returns a pydantic model instance.
    """
    agent = MockAgent()
    try:
        return asyncio.run(agent.process_query(query, query_type))
    except RuntimeError:
        # If we're already in an event loop (e.g., Jupyter), fall back to a nested loop approach.
        # For most CLI runs this won't trigger.
        import nest_asyncio  # optional; install if you hit this path
        nest_asyncio.apply()
        return asyncio.get_event_loop().run_until_complete(agent.process_query(query, query_type))
