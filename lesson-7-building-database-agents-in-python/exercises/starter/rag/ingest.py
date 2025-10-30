import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

load_dotenv()

# Initialize Cosmos client for ecommerce data
client = CosmosClient(os.environ["COSMOS_ENDPOINT"], os.environ["COSMOS_KEY"])
print("✅ Using Cosmos DB connection key for ecommerce data ingestion")
db = client.create_database_if_not_exists(id=os.environ["COSMOS_DB"])
container = db.create_container_if_not_exists(
    id=os.environ["COSMOS_CONTAINER"],
    partition_key=PartitionKey(path=os.environ["COSMOS_PARTITION_KEY"]),
    indexing_policy={"vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}]}
)

# Initialize Semantic Kernel for embeddings
def create_embedding_kernel():
    kernel = Kernel()
    kernel.add_service(
        AzureTextEmbedding(
            deployment_name=os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"],
            endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_KEY"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"]
        )
    )
    return kernel

def embed_texts(texts):
    """Generate embeddings using Semantic Kernel"""
    kernel = create_embedding_kernel()
    embedding_service = kernel.get_service(type=AzureTextEmbedding)
    embeddings = []
    for text in texts:
        result = embedding_service.generate_embeddings(text)
        # Convert ndarray to list for JSON serialization
        if hasattr(result, 'tolist'):
            embeddings.append(result.tolist())
        else:
            embeddings.append(list(result))
    return embeddings

def upsert_snippet(doc_id, text, pk="ecommerce"):
    """Upsert a document with its embedding into Cosmos DB"""
    try:
        # TODO: Upsert the snippet into Cosmos DB
        print(f"✅ {doc_id} upserted with Semantic Kernel embeddings.")
    except Exception as e:
        print(f"❌ Failed to upsert {doc_id}: {e}")

if __name__ == "__main__":
    # Ecommerce product information snippets
    upsert_snippet("product-001", "Wireless Bluetooth Headphones: Premium noise-canceling headphones with 30-hour battery life. Price: $199.99. Category: Electronics. In stock: 45 units.")
    upsert_snippet("product-002", "Smart Fitness Watch: Water-resistant fitness tracker with heart rate monitoring and GPS. Price: $149.99. Category: Wearables. In stock: 23 units.")
    upsert_snippet("product-003", "Organic Coffee Beans: Single-origin Ethiopian coffee beans, medium roast. Price: $24.99. Category: Food & Beverage. In stock: 67 units.")
    upsert_snippet("product-004", "Laptop Stand: Adjustable aluminum laptop stand for ergonomic workspace. Price: $39.99. Category: Office Supplies. In stock: 12 units.")
    upsert_snippet("product-005", "Yoga Mat: Non-slip premium yoga mat with carrying strap. Price: $49.99. Category: Sports & Fitness. In stock: 34 units.")
    upsert_snippet("shipping-001", "Free shipping on orders over $50. Standard shipping: 3-5 business days. Express shipping: 1-2 business days for $9.99.")
    upsert_snippet("return-001", "30-day return policy for all items. Items must be in original condition with tags. Free return shipping provided.")
    upsert_snippet("warranty-001", "1-year manufacturer warranty on electronics. Extended warranty available for purchase. Contact support for warranty claims.")
    print("✅ All ecommerce snippets upserted with Semantic Kernel embeddings.")
