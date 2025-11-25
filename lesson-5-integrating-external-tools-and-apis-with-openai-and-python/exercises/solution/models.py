# models.py - Pydantic models for structured outputs
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class OrderStatus(str, Enum):
    """Enum for order status values"""
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    NOT_FOUND = "not_found"
    ERROR = "error"

class ProductAvailability(str, Enum):
    """Enum for product availability"""
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class OrderResponse(BaseModel):
    """Response model for order status queries"""
    order_id: str = Field(description="The order identifier")
    status: OrderStatus = Field(description="Current status of the order")
    tracking_number: Optional[str] = Field(None, description="Tracking number if available")
    estimated_delivery: Optional[str] = Field(None, description="Estimated delivery date")
    items: List[str] = Field(description="List of items in the order")
    message: Optional[str] = Field(None, description="Additional message or error details")

class ProductResponse(BaseModel):
    """Response model for product information queries"""
    product_id: str = Field(description="The product identifier")
    name: str = Field(description="Product name")
    price: float = Field(description="Product price")
    category: str = Field(description="Product category")
    description: str = Field(description="Product description")
    availability: ProductAvailability = Field(description="Product availability status")
    stock_quantity: int = Field(description="Current stock quantity")
    rating: float = Field(description="Product rating (0-5)")
    reviews_count: int = Field(description="Number of reviews")
    message: Optional[str] = Field(None, description="Additional message or error details")

class CustomerServiceResponse(BaseModel):
    """Main response model for customer service queries"""
    query_type: str = Field(description="Type of query (order_status, product_info, general)")
    human_readable_response: str = Field(description="Human-readable response for the customer")
    structured_data: Optional[dict] = Field(default=None, description="Structured data if applicable")
    tools_used: List[str] = Field(default_factory=list, description="List of tools that were used to answer the query")
    confidence_score: float = Field(default=0.8, description="Confidence score (0-1) for the response")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up actions")
