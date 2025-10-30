# models.py - Pydantic models for Sports Analyst Agentic RAG implementation
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RAGQuery(BaseModel):
    """Model for RAG query input"""
    query: str = Field(description="The user's sports query")
    max_retrieval_attempts: Optional[int] = Field(3, description="Maximum number of retrieval attempts")
    confidence_threshold: Optional[float] = Field(0.7, description="Confidence threshold for retrieval quality")

class RAGResponse(BaseModel):
    """Response model for Agentic RAG queries"""
    query: str = Field(description="The original sports query")
    answer: str = Field(description="Generated sports analysis based on retrieved documents")
    sources: List[Dict[str, Any]] = Field(description="List of retrieved source documents")
    confidence_score: float = Field(description="Confidence score for the retrieval quality (0-1)")
    retrieval_attempts: int = Field(description="Number of retrieval attempts made")
    needs_recheck: bool = Field(description="Whether the agent determined re-checking was needed")
    reasoning: str = Field(description="Reasoning for the retrieval quality assessment")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the retrieval process")

class DocumentSource(BaseModel):
    """Model for document sources in RAG responses"""
    id: str = Field(description="Document identifier")
    text: str = Field(description="Document text content")
    score: Optional[float] = Field(None, description="Relevance score for the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional document metadata")

class RetrievalQualityAssessment(BaseModel):
    """Model for retrieval quality assessment"""
    confidence: float = Field(description="Confidence score for retrieval quality (0-1)")
    reasoning: str = Field(description="Reasoning for the assessment")
    issues: List[str] = Field(description="List of identified issues with the retrieval")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions for improving retrieval")

class QueryRefinement(BaseModel):
    """Model for query refinement suggestions"""
    original_query: str = Field(description="The original sports query")
    refined_query: str = Field(description="The refined sports query")
    refinement_reason: str = Field(description="Reason for the refinement")
    confidence_improvement: Optional[float] = Field(None, description="Expected confidence improvement")

# Sports-specific models
class SportType(str, Enum):
    """Enum for different sports types"""
    NFL = "nfl"
    NBA = "nba"
    SOCCER = "soccer"
    TENNIS = "tennis"
    BASEBALL = "baseball"
    HOCKEY = "hockey"
    GOLF = "golf"
    OTHER = "other"

class AnalysisType(str, Enum):
    """Enum for different types of sports analysis"""
    STATISTICS = "statistics"
    PERFORMANCE = "performance"
    TRENDS = "trends"
    STANDINGS = "standings"
    PREDICTIONS = "predictions"
    COMPARISON = "comparison"
    INJURY = "injury"
    TRADE = "trade"

class SportsAnalysisResponse(BaseModel):
    """Enhanced response model for sports analysis queries"""
    query: str = Field(description="The original sports query")
    analysis: str = Field(description="Comprehensive sports analysis")
    sport_type: Optional[SportType] = Field(None, description="Type of sport analyzed")
    analysis_type: Optional[AnalysisType] = Field(None, description="Type of analysis performed")
    sources: List[Dict[str, Any]] = Field(description="List of retrieved source documents")
    confidence_score: float = Field(description="Confidence score for the analysis (0-1)")
    key_statistics: Optional[Dict[str, Any]] = Field(None, description="Key statistics extracted")
    trends: Optional[List[str]] = Field(None, description="Identified trends")
    predictions: Optional[List[str]] = Field(None, description="Predictions or insights")
    retrieval_attempts: int = Field(description="Number of retrieval attempts made")
    needs_recheck: bool = Field(description="Whether re-checking was needed")
    reasoning: str = Field(description="Reasoning for the analysis quality")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class PlayerPerformance(BaseModel):
    """Model for player performance data"""
    player_name: str = Field(description="Name of the player")
    team: str = Field(description="Team name")
    position: str = Field(description="Player position")
    statistics: Dict[str, Any] = Field(description="Player statistics")
    performance_rating: Optional[float] = Field(None, description="Overall performance rating")
    trends: Optional[List[str]] = Field(None, description="Performance trends")

class TeamPerformance(BaseModel):
    """Model for team performance data"""
    team_name: str = Field(description="Name of the team")
    league: str = Field(description="League name")
    record: str = Field(description="Team record (wins-losses)")
    statistics: Dict[str, Any] = Field(description="Team statistics")
    strengths: Optional[List[str]] = Field(None, description="Team strengths")
    weaknesses: Optional[List[str]] = Field(None, description="Team weaknesses")
    recent_form: Optional[str] = Field(None, description="Recent form description")

# Legacy models for backward compatibility
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
    structured_data: Optional[dict] = Field(None, description="Structured data if applicable")
    tools_used: List[str] = Field(description="List of tools that were used to answer the query")
    confidence_score: float = Field(description="Confidence score (0-1) for the response")
    follow_up_suggestions: List[str] = Field(description="Suggested follow-up actions")
