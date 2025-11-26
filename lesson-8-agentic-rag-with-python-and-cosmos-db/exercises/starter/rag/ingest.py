import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

load_dotenv()

# Initialize Cosmos client for ecommerce data
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
    # TODO: Create a Semantic Kernel instance for embeddings
    # Hint: Use kernel.add_service() with AzureTextEmbedding from environment variables
    kernel = Kernel()

    return kernel

async def embed_texts(texts):
    """Generate embeddings using Semantic Kernel"""
    kernel = create_embedding_kernel()
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

async def delete_all_items(partition_key: str):
    """Delete all items with the specified partition key to prevent contamination between runs"""
    try:
        # Query all items with the specified partition key
        query = "SELECT c.id FROM c WHERE c.pk = @pk"
        params = [{"name": "@pk", "value": partition_key}]
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        
        # Delete each item
        deleted_count = 0
        for item in items:
            try:
                # Use item["id"] as partition_key since COSMOS_PARTITION_KEY=/id
                container.delete_item(item=item["id"], partition_key=item["id"])
                deleted_count += 1
            except Exception as e:
                error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
                print(f"Warning: Failed to delete item {item['id']}: {error_msg}")
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} items with partition key '{partition_key}'")
        return deleted_count
    except Exception as e:
        print(f"Failed to cleanup items: {e}")
        return 0

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
    # Ecommerce product information snippets
    async def main():
        await upsert_snippet("product-001", "Wireless Bluetooth Headphones: Premium noise-canceling headphones with 30-hour battery life. Price: $199.99. Category: Electronics. In stock: 45 units.")
        await upsert_snippet("product-002", "Smart Fitness Watch: Water-resistant fitness tracker with heart rate monitoring and GPS. Price: $149.99. Category: Wearables. In stock: 23 units.")
        await upsert_snippet("product-003", "Organic Coffee Beans: Single-origin Ethiopian coffee beans, medium roast. Price: $24.99. Category: Food & Beverage. In stock: 67 units.")
        await upsert_snippet("product-004", "Laptop Stand: Adjustable aluminum laptop stand for ergonomic workspace. Price: $39.99. Category: Office Supplies. In stock: 12 units.")
        await upsert_snippet("product-005", "Yoga Mat: Non-slip premium yoga mat with carrying strap. Price: $49.99. Category: Sports & Fitness. In stock: 34 units.")
        await upsert_snippet("shipping-001", "Free shipping on orders over $50. Standard shipping: 3-5 business days. Express shipping: 1-2 business days for $9.99.")
        await upsert_snippet("return-001", "30-day return policy for all items. Items must be in original condition with tags. Free return shipping provided.")
        await upsert_snippet("warranty-001", "1-year manufacturer warranty on electronics. Extended warranty available for purchase. Contact support for warranty claims.")
        print("All ecommerce snippets upserted with Semantic Kernel embeddings.")
    asyncio.run(main())
