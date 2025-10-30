from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import os
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
            print("✅ Using Cosmos DB connection key")
            _container = _client.get_database_client(os.environ["COSMOS_DB"]).get_container_client(os.environ["COSMOS_CONTAINER"])
        except Exception as e:
            print(f"❌ Cosmos DB connection failed: {e}")
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
        print(f"❌ Failed to create embedding kernel: {e}")
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
        print(f"❌ Embedding generation failed: {e}")
        # Fallback to mock embeddings
        return [[0.1] * 1536 for _ in texts]  # Mock embedding vector

async def retrieve(query: str, k: int = 5):
    """Retrieve relevant documents using text search (fallback from vector similarity)"""
    try:
        client, container = get_cosmos_client()
        if client is None or container is None:
            raise Exception("Cosmos DB not available")
            
        # For now, use text-based search instead of vector similarity
        # This is a fallback until vector search is properly configured
        sql = "SELECT TOP @k c.id, c.text FROM c WHERE CONTAINS(c.text, @query, true)"
        params = [{"name": "@k", "value": k}, {"name": "@query", "value": query}]
        results = list(container.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
        
        # If no results from text search, get some random documents
        if not results:
            sql = "SELECT TOP @k c.id, c.text FROM c"
            params = [{"name": "@k", "value": k}]
            results = list(container.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
            
        return results
    except Exception as e:
        print(f"❌ RAG retrieval failed: {e}")
        # Fallback to mock ecommerce data
        return [
            {"id": "product-001", "text": "Wireless Bluetooth Headphones: Premium noise-canceling headphones with 30-hour battery life. Price: $199.99. Category: Electronics. In stock: 45 units."},
            {"id": "shipping-001", "text": "Free shipping on orders over $50. Standard shipping: 3-5 business days. Express shipping: 1-2 business days for $9.99."}
        ]
