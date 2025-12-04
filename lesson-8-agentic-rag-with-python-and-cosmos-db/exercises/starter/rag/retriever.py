from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.cosmos.exceptions import CosmosHttpResponseError
import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Reduce verbosity of Azure SDK logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.connectors.ai.open_ai.services.open_ai_handler").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Lazy initialization of Cosmos client
_client = None
_container = None

# Lazy initialization of embedding kernel (reuse to avoid asyncio cleanup issues)
_embedding_kernel = None

def get_cosmos_client():
    """Get or create Cosmos DB client and container"""
    global _client, _container
    if _client is None:
        try:
            _client = CosmosClient(os.environ["COSMOS_ENDPOINT"], os.environ["COSMOS_KEY"])
            logger.info("✅ Using Cosmos DB connection key")
            _container = _client.get_database_client(os.environ["COSMOS_DB"]).get_container_client(os.environ["COSMOS_CONTAINER"])
        except Exception as e:
            logger.error(f"❌ Cosmos DB connection failed: {e}")
            _client = None
            _container = None
    return _client, _container

def get_embedding_kernel():
    """Get or create Semantic Kernel instance for embeddings (reused to avoid cleanup issues)"""
    global _embedding_kernel
    if _embedding_kernel is None:
        try:
            # TODO: Create a Semantic Kernel instance for embeddings
            # Hint: Use _embedding_kernel.add_service() with AzureTextEmbedding
            _embedding_kernel = Kernel()

            logger.info("✅ Embedding kernel created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create embedding kernel: {e}")
            return None
    return _embedding_kernel

async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using Semantic Kernel"""
    try:
        kernel = get_embedding_kernel()
        if kernel is None:
            raise Exception("Failed to create embedding kernel")
        
        embedding_service = kernel.get_service(type=AzureTextEmbedding)
        embeddings = []
        for text in texts:
            result = await embedding_service.generate_embeddings(text)
            # Convert to list of floats - handle different return types
            if hasattr(result, 'tolist'):
                embedding_list = result.tolist()
            elif isinstance(result, list):
                embedding_list = result
            else:
                embedding_list = list(result)
            
            # Flatten nested lists if needed and ensure all values are floats
            # Handle case where embedding_list might be nested (list of lists)
            if embedding_list and isinstance(embedding_list[0], (list, tuple)):
                # If first element is a list/tuple, flatten it - use the first nested list
                embedding_list = embedding_list[0]
            
            # Ensure all values are floats - recursively handle any remaining nested structures
            def flatten_to_floats(value):
                if isinstance(value, (list, tuple)):
                    # If it's a list, take the first element or flatten further
                    if value and isinstance(value[0], (list, tuple)):
                        return flatten_to_floats(value[0])
                    return float(value[0]) if value else 0.0
                return float(value)
            
            embedding_list = [flatten_to_floats(x) for x in embedding_list]
            embeddings.append(embedding_list)
        logger.info(f"✅ Generated {len(embeddings)} embeddings (dimension: {len(embeddings[0]) if embeddings else 0})")
        return embeddings
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        raise Exception(f"Failed to generate embeddings: {e}")

async def _execute_query_with_retry(container, sql: str, params: list, enable_cross_partition: bool, max_retries: int = 3):
    """Execute Cosmos DB query with retry logic for 400 errors (query plan issues)

    Cosmos DB CONTAINS queries sometimes fail with HTTP 400 on first attempt
    because the query plan needs to be fetched. This function retries with
    exponential backoff to handle this gracefully.
    """
    for attempt in range(max_retries):
        try:
            return list(container.query_items(query=sql, parameters=params, enable_cross_partition_query=enable_cross_partition))
        except CosmosHttpResponseError as e:
            # Check if it's a 400 error (query plan issue) and not the last attempt
            if e.status_code == 400 and attempt < max_retries - 1:
                # Exponential backoff: 0.1s, 0.2s, 0.4s
                wait_time = 0.1 * (2 ** attempt)
                await asyncio.sleep(wait_time)
                continue
            # Re-raise if not a 400 error or if it's the last attempt
            raise
        except Exception as e:
            error_str = str(e).lower()
            # Fallback: check error message for 400 errors (in case exception type differs)
            if ("400" in error_str or "bad request" in error_str) and attempt < max_retries - 1:
                # Exponential backoff: 0.1s, 0.2s, 0.4s
                wait_time = 0.1 * (2 ** attempt)
                await asyncio.sleep(wait_time)
                continue
            # Re-raise if not a 400 error or if it's the last attempt
            raise
    return []

async def retrieve_with_vector_search(query: str, k: int = 5, partition_key: str = None) -> List[Dict[str, Any]]:
    """Retrieve documents using vector similarity search"""
    try:
        client, container = get_cosmos_client()
        if client is None or container is None:
            raise Exception("Cosmos DB not available")

        # Generate embedding for the query
        query_embedding = await embed_texts([query])
        query_vector = query_embedding[0]

        # Validate embedding format
        if not query_vector or not isinstance(query_vector, list):
            raise ValueError(f"Invalid embedding format: {type(query_vector)}")

        if len(query_vector) == 0:
            raise ValueError("Empty embedding vector")

        # Ensure all values are floats
        query_vector = [float(x) for x in query_vector]

        logger.debug(f"Query vector dimension: {len(query_vector)}, first few values: {query_vector[:3]}")

        # TODO: Use vector similarity search
        sql = """"""
        params = [
            {"name": "@k", "value": k},
            {"name": "@queryVector", "value": query_vector}
        ]

        logger.debug(f"Executing vector search with {len(query_vector)}-dimensional vector")
        results = list(container.query_items(query=sql, parameters=params, enable_cross_partition_query=True))

        logger.info(f"✅ Vector search returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"❌ Vector search failed: {e}")
        import traceback
        logger.debug(f"Vector search traceback: {traceback.format_exc()}")
        return []

async def retrieve_with_text_search(query: str, k: int = 5, partition_key: str = None) -> List[Dict[str, Any]]:
    """Retrieve documents using text-based search as fallback

    Note: CONTAINS() in Cosmos DB has limitations:
    - Word-based matching only (not phrase matching)
    - Case-sensitive by default
    - Works best with simple keyword queries (e.g., "headphones", "keyboard")
    - May return 0 results for complex sentence queries
    - Requires proper indexing for optimal performance

    In hybrid search, vector search compensates for these limitations.
    """
    try:
        client, container = get_cosmos_client()
        if client is None or container is None:
            raise Exception("Cosmos DB not available")

        # Build query with optional partition key filter
        if partition_key:
            sql = "SELECT TOP @k c.id, c.text, c.pk FROM c WHERE CONTAINS(c.text, @query, true) AND c.pk = @pk"
            params = [{"name": "@k", "value": k}, {"name": "@query", "value": query}, {"name": "@pk", "value": partition_key}]
        else:
            sql = "SELECT TOP @k c.id, c.text, c.pk FROM c WHERE CONTAINS(c.text, @query, true)"
            params = [{"name": "@k", "value": k}, {"name": "@query", "value": query}]

        results = await _execute_query_with_retry(container, sql, params, enable_cross_partition=True)

        logger.info(f"✅ Text search returned {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"❌ Text search failed: {e}")
        return []

def rerank_results(results_list: List[List[Dict[str, Any]]], k: int = 5) -> List[Dict[str, Any]]:
    """Rerank results from multiple search methods using Reciprocal Rank Fusion (RRF)"""
    if not results_list:
        return []

    ranked_results = {}
    for results in results_list:
        for i, result in enumerate(results):
            doc_id = result.get("id")
            if doc_id not in ranked_results:
                ranked_results[doc_id] = {"doc": result, "score": 0}
            ranked_results[doc_id]["score"] += 1 / (i + 60)  # RRF formula

    sorted_results = sorted(ranked_results.values(), key=lambda x: x["score"], reverse=True)
    
    final_results = [item["doc"] for item in sorted_results[:k]]
    return final_results

async def retrieve_with_hybrid_search(query: str, k: int = 5, partition_key: str = None) -> List[Dict[str, Any]]:
    """Retrieve documents using hybrid search (vector + text) and rerank with RRF"""
    try:
        # Perform vector and text searches in parallel
        vector_results_task = retrieve_with_vector_search(query, k, partition_key)
        text_results_task = retrieve_with_text_search(query, k, partition_key)
        
        vector_results, text_results = await asyncio.gather(vector_results_task, text_results_task)

        # Rerank results
        reranked_results = rerank_results([vector_results, text_results], k)
        
        logger.info(f"✅ Hybrid search reranked {len(reranked_results)} results")
        return reranked_results

    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        return []

async def retrieve(query: str, k: int = 5, search_type: str = "hybrid", partition_key: str = None) -> List[Dict[str, Any]]:
    """
    Retrieve relevant documents using the specified search method

    Args:
        query: The search query
        k: Number of documents to retrieve
        search_type: Type of search ("vector", "text", "hybrid")
        partition_key: Optional partition key to filter results (prevents cross-partition contamination)

    Returns:
        List of retrieved documents with metadata
    """
    logger.info(f"🔍 Retrieving documents for query: '{query}' (k={k}, type={search_type})")

    try:
        if search_type == "vector":
            results = await retrieve_with_vector_search(query, k, partition_key)
        elif search_type == "text":
            results = await retrieve_with_text_search(query, k, partition_key)
        else:  # hybrid
            results = await retrieve_with_hybrid_search(query, k, partition_key)

        # Add metadata to results
        for i, result in enumerate(results):
            result["retrieval_rank"] = i + 1
            result["search_type"] = search_type

        logger.info(f"✅ Retrieved {len(results)} documents")
        return results

    except Exception as e:
        logger.error(f"❌ Document retrieval failed: {e}")
        return []


