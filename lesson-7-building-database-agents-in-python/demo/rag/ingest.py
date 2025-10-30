import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

load_dotenv()

# Initialize Cosmos client for sports data
client = CosmosClient(os.environ["COSMOS_ENDPOINT"], os.environ["COSMOS_KEY"])
print("✅ Using Cosmos DB connection key for sports data ingestion")
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
        # Convert ndarray to list for JSON serialization
        if hasattr(result, 'tolist'):
            embeddings.append(result.tolist())
        else:
            embeddings.append(list(result))
    return embeddings

async def upsert_snippet(doc_id, text, pk="sports"):
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
        print(f"✅ {doc_id} upserted with Semantic Kernel embeddings.")
    except Exception as e:
        print(f"❌ Failed to upsert {doc_id}: {e}")

async def main():
    """Main function to upsert sports data"""
    # Sports information snippets
    await upsert_snippet("lakers-001", "Los Angeles Lakers: NBA team based in Los Angeles. Current record: 15-10. Key players: LeBron James, Anthony Davis, Austin Reaves. Recent performance: Won 3 of last 5 games. Next game: vs Golden State Warriors.")
    await upsert_snippet("lebron-001", "LeBron James: Lakers forward, 39 years old. Season stats: 25.2 PPG, 7.8 RPG, 6.8 APG. Recent form: Excellent, averaging 28 points in last 5 games. Injury status: Healthy. Contract: 2 years remaining.")
    await upsert_snippet("warriors-001", "Golden State Warriors: NBA team based in San Francisco. Current record: 12-13. Key players: Stephen Curry, Klay Thompson, Draymond Green. Recent performance: Lost 4 of last 5 games. Next game: vs Los Angeles Lakers.")
    await upsert_snippet("curry-001", "Stephen Curry: Warriors guard, 35 years old. Season stats: 28.1 PPG, 4.4 RPG, 4.9 APG. Recent form: Struggling with shooting, 22% from 3-point range. Injury status: Healthy. Contract: 3 years remaining.")
    await upsert_snippet("nba-standings-001", "NBA Western Conference Standings: 1. Minnesota Timberwolves (18-5), 2. Oklahoma City Thunder (16-8), 3. Denver Nuggets (16-10), 4. Sacramento Kings (14-10), 5. Los Angeles Lakers (15-10). Playoff race heating up.")
    await upsert_snippet("nba-news-001", "NBA Trade Rumors: Lakers looking for shooting help, Warriors considering roster changes. Recent trades: None significant. Free agency: Several role players available. Draft: 2024 class showing promise.")
    await upsert_snippet("nba-schedule-001", "NBA Schedule: Lakers vs Warriors tonight at 8:00 PM PST. Key matchups this week: Celtics vs Heat, Nuggets vs Suns. Playoff implications: High stakes for both teams.")
    await upsert_snippet("nba-stats-001", "NBA League Leaders: Scoring - Luka Doncic (32.4 PPG), Rebounds - Rudy Gobert (12.8 RPG), Assists - Tyrese Haliburton (12.1 APG). Team stats: Celtics best offense, Timberwolves best defense.")
    print("✅ All sports snippets upserted with Semantic Kernel embeddings.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
