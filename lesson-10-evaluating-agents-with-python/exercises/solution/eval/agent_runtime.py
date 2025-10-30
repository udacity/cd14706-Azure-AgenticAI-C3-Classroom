# agent_runtime.py
from typing import Any, Dict, List
from pydantic import BaseModel

import asyncio
import logging

logger = logging.getLogger(__name__)


class CustomerServiceResponse(BaseModel):
    query_type: str
    human_readable_response: str
    structured_data: Dict[str, Any]
    tools_used: List[str]
    confidence_score: float
    follow_up_suggestions: List[str] = []


class MockAgent:
    async def process_query(self, query: str, query_type: str) -> CustomerServiceResponse:
        tools_used: List[str] = []
        structured: Dict[str, Any] = {}

        if query_type == "order_status":
            tools_used.append("order_lookup_tool")
            structured = {
                "order_id": "ORD-001",
                "status": "shipped",
                "tracking_number": "TRK123456789",
                "estimated_delivery": "2025-10-01",
            }
        elif query_type == "product_info":
            tools_used.append("product_info_tool")
            structured = {
                "product_id": "PROD-001",
                "name": "Wireless Bluetooth Headphones",
                "price": 99.99,
                "in_stock": True,
            }
        elif query_type == "recommendations":
            tools_used.append("recommendation_tool")
            structured = {
                "recommendations": [
                    {"product_id": "PROD-101", "name": "Gaming Headset", "price": 129.99},
                    {"product_id": "PROD-102", "name": "Mechanical Keyboard", "price": 89.99},
                ]
            }
        else:
            tools_used.append("general_support_tool")
            structured = {"query_type": "general", "assistance_provided": True}

        return CustomerServiceResponse(
            query_type=query_type,
            human_readable_response=f"I've processed your {query_type} request: {query}",
            structured_data=structured,
            tools_used=tools_used,
            confidence_score=0.85,
            follow_up_suggestions=["Is there anything else I can help you with?"],
        )


def run_request(query: str, query_type: str) -> CustomerServiceResponse:
    """
    Synchronous entrypoint used by judge.py.
    Runs the mock agent and returns a pydantic model instance.
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
