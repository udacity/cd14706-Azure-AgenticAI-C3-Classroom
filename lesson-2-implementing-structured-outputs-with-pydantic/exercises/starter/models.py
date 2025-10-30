# models.py - Pydantic models for structured outputs
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class OrderStatus(str, Enum):
    """Enum for order status values"""
    # TODO ADD ORDER STATUS VALUES

class ProductAvailability(str, Enum):
    """Enum for product availability"""
    # TODO ADD PRODUCT AVAILABILITY VALUES

class OrderResponse(BaseModel):
    """Response model for order status queries"""
    # TODO ADD ORDER RESPONSE FIELDS

class ProductResponse(BaseModel):
    """Response model for product information queries"""
    # TODO ADD PRODUCT RESPONSE FIELDS

class CustomerServiceResponse(BaseModel):
    """Main response model for customer service queries"""
    query_type: str = Field(description="Type of query (order_status, product_info, general)")
    human_readable_response: str = Field(description="Human-readable response for the customer")
    structured_data: Optional[dict] = Field(None, description="Structured data if applicable")
    tools_used: List[str] = Field(description="List of tools that were used to answer the query")
    confidence_score: float = Field(description="Confidence score (0-1) for the response")
    follow_up_suggestions: List[str] = Field(description="Suggested follow-up actions")
