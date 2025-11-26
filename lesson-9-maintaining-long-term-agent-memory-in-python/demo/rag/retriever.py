from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Lazy initialization of Cosmos client
_client = None
_container = None

def get_cosmos_client():
    """Get or create Cosmos DB client and container"""
    global _client, _container
    if _client is None:
        try:
            _client = CosmosClient(os.environ["COSMOS_ENDPOINT"], os.environ["COSMOS_KEY"])
            logger.info("Using Cosmos DB connection key")
            _container = _client.get_database_client(os.environ["COSMOS_DB"]).get_container_client(os.environ["COSMOS_CONTAINER"])
        except Exception as e:
            logger.error(f"Cosmos DB connection failed: {e}")
            _client = None
            _container = None
    return _client, _container

def create_embedding_kernel():
    """Create Semantic Kernel instance for embeddings"""
    kernel = Kernel()
    try:
        kernel.add_service(
            AzureTextEmbedding(
                deployment_name=os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"],
                endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_key=os.environ["AZURE_OPENAI_KEY"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"]
            )
        )
        logger.info("Embedding kernel created successfully")
    except Exception as e:
        logger.error(f"Failed to create embedding kernel: {e}")
        return None
    return kernel

async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using Semantic Kernel"""
    try:
        kernel = create_embedding_kernel()
        if kernel is None:
            raise Exception("Failed to create embedding kernel")
        
        embedding_service = kernel.get_service(type=AzureTextEmbedding)
        embeddings = []
        for text in texts:
            result = await embedding_service.generate_embeddings(text)
            # Convert ndarray to list for JSON serialization
            if hasattr(result, 'tolist'):
                embeddings.append(result.tolist())
            else:
                embeddings.append(list(result))
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise Exception(f"Failed to generate embeddings: {e}")

async def retrieve_with_vector_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve documents using vector similarity search"""
    try:
        client, container = get_cosmos_client()
        if client is None or container is None:
            raise Exception("Cosmos DB not available")
        
        # Generate embedding for the query
        query_embedding = await embed_texts([query])
        query_vector = query_embedding[0]
        
        # Use vector similarity search
        sql = """
        SELECT TOP @k c.id, c.text, c.pk, 
               VectorDistance(c.embedding, @queryVector, false) as distance
        FROM c 
        ORDER BY VectorDistance(c.embedding, @queryVector, false)
        """
        params = [
            {"name": "@k", "value": k},
            {"name": "@queryVector", "value": query_vector}
        ]
        
        results = list(container.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
        logger.info(f"Vector search returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []

async def retrieve_with_text_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve documents using text-based search as fallback"""
    try:
        client, container = get_cosmos_client()
        if client is None or container is None:
            raise Exception("Cosmos DB not available")
        
        # Use text-based search
        sql = "SELECT TOP @k c.id, c.text, c.pk FROM c WHERE CONTAINS(c.text, @query, true)"
        params = [{"name": "@k", "value": k}, {"name": "@query", "value": query}]
        results = list(container.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
        
        # If no results from text search, get some random documents
        if not results:
            logger.warning("No text search results, falling back to random documents")
            sql = "SELECT TOP @k c.id, c.text, c.pk FROM c"
            params = [{"name": "@k", "value": k}]
            results = list(container.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
        
        logger.info(f"Text search returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Text search failed: {e}")
        return []

async def retrieve_with_hybrid_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve documents using hybrid search (vector + text)"""
    try:
        # Try vector search first
        vector_results = await retrieve_with_vector_search(query, k)
        
        if vector_results:
            logger.info("Using vector search results")
            return vector_results
        
        # Fallback to text search
        logger.info("Vector search failed, falling back to text search")
        text_results = await retrieve_with_text_search(query, k)
        
        if text_results:
            logger.info("Using text search results")
            return text_results
        
        logger.warning("All search methods failed - returning empty results")
        return []
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        return []

async def retrieve(query: str, k: int = 5, search_type: str = "hybrid") -> List[Dict[str, Any]]:
    """
    Retrieve relevant documents using the specified search method
    
    Args:
        query: The search query
        k: Number of documents to retrieve
        search_type: Type of search ("vector", "text", "hybrid")
    
    Returns:
        List of retrieved documents with metadata
    """
    logger.info(f"Retrieving documents for query: '{query}' (k={k}, type={search_type})")
    
    try:
        if search_type == "vector":
            results = await retrieve_with_vector_search(query, k)
        elif search_type == "text":
            results = await retrieve_with_text_search(query, k)
        else:  # hybrid
            results = await retrieve_with_hybrid_search(query, k)
        
        # Add metadata to results
        for i, result in enumerate(results):
            result["retrieval_rank"] = i + 1
            result["search_type"] = search_type
        
        logger.info(f"Retrieved {len(results)} documents")
        return results
        
    except Exception as e:
        logger.error(f"Document retrieval failed: {e}")
        return []

async def assess_retrieval_quality(query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Assess the quality of retrieved documents
    
    Args:
        query: The original query
        retrieved_docs: List of retrieved documents
    
    Returns:
        Quality assessment with confidence score and reasoning
    """
    try:
        if not retrieved_docs:
            return {
                "confidence": 0.0,
                "reasoning": "No documents retrieved",
                "issues": ["No documents found"],
                "suggestions": ["Try a different query", "Check database connectivity"]
            }
        
        # Simple quality assessment based on document count and content
        doc_count = len(retrieved_docs)
        query_words = set(query.lower().split())
        
        # Check relevance by counting query word matches
        total_matches = 0
        for doc in retrieved_docs:
            doc_text = doc.get("text", "").lower()
            matches = sum(1 for word in query_words if word in doc_text)
            total_matches += matches
        
        avg_matches = total_matches / doc_count if doc_count > 0 else 0
        relevance_score = min(avg_matches / len(query_words), 1.0) if query_words else 0.0
        
        # Calculate confidence based on document count and relevance
        count_score = min(doc_count / 3, 1.0)  # Prefer 3+ documents
        confidence = (relevance_score * 0.7 + count_score * 0.3)
        
        # Determine issues and suggestions
        issues = []
        suggestions = []
        
        if confidence < 0.5:
            issues.append("Low relevance to query")
            suggestions.append("Try more specific keywords")
        
        if doc_count < 2:
            issues.append("Insufficient document count")
            suggestions.append("Try broader search terms")
        
        if avg_matches < 1:
            issues.append("No keyword matches found")
            suggestions.append("Check spelling and try synonyms")
        
        reasoning = f"Retrieved {doc_count} documents with {avg_matches:.1f} average keyword matches per document"
        
        return {
            "confidence": confidence,
            "reasoning": reasoning,
            "issues": issues,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        return {
            "confidence": 0.3,
            "reasoning": f"Assessment error: {e}",
            "issues": ["Assessment system error"],
            "suggestions": ["Try again later"]
        }
