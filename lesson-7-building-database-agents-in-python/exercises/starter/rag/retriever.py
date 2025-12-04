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
    # TODO: Implement retry logic with exponential backoff
    # Hint: Loop max_retries times, catch CosmosHttpResponseError for 400 errors
    # Use await asyncio.sleep(0.1 * (2 ** attempt)) for exponential backoff
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
        
        # TODO: Build SQL query with CONTAINS for text search
        # Hint: If partition_key provided, add "AND c.pk = @pk" to filter by partition
        # Use enable_cross_partition = True (CONTAINS requires it)
        # Set sql, params, enable_cross_partition variables

        # TODO: Execute query using _execute_query_with_retry
        # Hint: results = await _execute_query_with_retry(container, sql, params, enable_cross_partition)

        # TODO: If no results from text search, return empty list (don't hallucinate with random documents)
        # Hint: Simply return the results from the query above

        results = []
    except Exception as e:
        print(f"RAG retrieval failed: {e}")
        return []
