from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.cosmos.exceptions import CosmosHttpResponseError
import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

load_dotenv()

# Lazy initialization of Cosmos client
_client = None
_container = None

def get_cosmos_client():
    global _client, _container
    if _client is None:
        try:
            _client = CosmosClient(os.environ["COSMOS_ENDPOINT"], os.environ["COSMOS_KEY"])
            print("Using Cosmos DB connection key")
            _container = _client.get_database_client(os.environ["COSMOS_DB"]).get_container_client(os.environ["COSMOS_CONTAINER"])
        except Exception as e:
            print(f"Cosmos DB connection failed: {e}")
            _client = None
            _container = None
    return _client, _container

# Initialize Semantic Kernel for embeddings
def create_embedding_kernel():
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
    except Exception as e:
        print(f"Failed to create embedding kernel: {e}")
        # Return None to trigger fallback
        return None
    return kernel

async def embed_texts(texts):
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
        return embeddings
    except Exception as e:
        print(f"Embedding generation failed: {e}")
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

async def retrieve(query: str, k: int = 5, partition_key: str = None):
    """Retrieve relevant documents using text search (fallback from vector similarity)
    
    Args:
        query: Search query text
        k: Number of results to return
        partition_key: Optional partition key to filter results (prevents cross-partition contamination)
    """
    try:
        client, container = get_cosmos_client()
        if client is None or container is None:
            raise Exception("Cosmos DB not available")
        
        # Build query with optional partition key filter
        # Split query into terms and search for any term match (OR logic)
        query_terms = query.lower().split()

        if partition_key:
            # Filter by partition key to prevent contamination from other runs
            # Search for any term in the query using OR logic
            if len(query_terms) == 1:
                sql = "SELECT TOP @k c.id, c.text FROM c WHERE CONTAINS(LOWER(c.text), @term0) AND c.pk = @pk"
                params = [{"name": "@k", "value": k}, {"name": "@term0", "value": query_terms[0]}, {"name": "@pk", "value": partition_key}]
            else:
                # Build OR conditions for multiple terms
                conditions = " OR ".join([f"CONTAINS(LOWER(c.text), @term{i})" for i in range(len(query_terms))])
                sql = f"SELECT TOP @k c.id, c.text FROM c WHERE ({conditions}) AND c.pk = @pk"
                params = [{"name": "@k", "value": k}] + [{"name": f"@term{i}", "value": term} for i, term in enumerate(query_terms)] + [{"name": "@pk", "value": partition_key}]
            enable_cross_partition = True
        else:
            # Legacy behavior: search across all partitions
            if len(query_terms) == 1:
                sql = "SELECT TOP @k c.id, c.text FROM c WHERE CONTAINS(LOWER(c.text), @term0)"
                params = [{"name": "@k", "value": k}, {"name": "@term0", "value": query_terms[0]}]
            else:
                conditions = " OR ".join([f"CONTAINS(LOWER(c.text), @term{i})" for i in range(len(query_terms))])
                sql = f"SELECT TOP @k c.id, c.text FROM c WHERE {conditions}"
                params = [{"name": "@k", "value": k}] + [{"name": f"@term{i}", "value": term} for i, term in enumerate(query_terms)]
            enable_cross_partition = True

        results = await _execute_query_with_retry(container, sql, params, enable_cross_partition)

        # If no results from text search, return empty list (don't hallucinate with random documents)
        return results
    except Exception as e:
        print(f"RAG retrieval failed: {e}")
        return []
