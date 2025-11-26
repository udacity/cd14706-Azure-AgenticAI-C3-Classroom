import os
import logging
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

load_dotenv()

# Reduce verbosity of Azure SDK logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.connectors.ai.open_ai.services.open_ai_handler").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

client = CosmosClient(os.environ["COSMOS_ENDPOINT"], os.environ["COSMOS_KEY"])
print("Using Cosmos DB connection key for ecommerce data ingestion")
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

async def embed_texts(texts):
    """Generate embeddings using Semantic Kernel"""
    kernel = create_embedding_kernel()
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
    return embeddings

async def upsert_snippet(doc_id, text, pk="ecommerce"):
    """Upsert a document with its embedding into Cosmos DB"""
    try:
        embeddings = await embed_texts([text])
        vec = embeddings[0]
        container.upsert_item({
            "id": doc_id,
            "pk": pk,
            "text": text,
            "embedding": vec
        })
        print(f"{doc_id} upserted with Semantic Kernel embeddings.")
    except Exception as e:
        print(f"Failed to upsert {doc_id}: {e}")

if __name__ == "__main__":
    import asyncio
    test_products = [
        ("product-001", "Wireless Bluetooth Headphones: Premium noise-canceling headphones with 30-hour battery life. Price: $199.99. Category: Electronics. In stock: 45 units."),
        ("product-002", "Smart Fitness Watch: Water-resistant fitness tracker with heart rate monitoring and GPS. Price: $149.99. Category: Wearables. In stock: 23 units."),
        ("product-003", "Organic Coffee Beans: Single-origin Ethiopian coffee beans, medium roast. Price: $24.99. Category: Food & Beverage. In stock: 67 units."),
        ("product-004", "Laptop Stand: Adjustable aluminum laptop stand for ergonomic workspace. Price: $39.99. Category: Office Supplies. In stock: 12 units."),
        ("product-005", "Yoga Mat: Non-slip premium yoga mat with carrying strap. Price: $49.99. Category: Sports & Fitness. In stock: 34 units."),
        ("shipping-001", "Free shipping on orders over $50. Standard shipping: 3-5 business days. Express shipping: 1-2 business days for $9.99."),
        ("return-001", "30-day return policy for all items. Items must be in original condition with tags. Free return shipping provided."),
        ("warranty-001", "1-year manufacturer warranty on electronics. Extended warranty available for purchase. Contact support for warranty claims.")
    ]
    async def main():
        for product_id, product_text in test_products:
            await upsert_snippet(product_id, product_text, pk="ecommerce")
        print("All ecommerce snippets upserted with Semantic Kernel embeddings.")
    asyncio.run(main())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
