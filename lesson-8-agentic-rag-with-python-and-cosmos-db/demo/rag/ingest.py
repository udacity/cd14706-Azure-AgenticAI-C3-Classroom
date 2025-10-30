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
    """Upsert a sports document with its embedding into Cosmos DB"""
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
    # Sports data snippets for ingestion
    await upsert_snippet("nfl-qb-001", "Patrick Mahomes: Kansas City Chiefs quarterback. 2023 stats: 4,183 passing yards, 27 touchdowns, 14 interceptions. Completion rate: 66.4%. Led team to Super Bowl victory.")
    await upsert_snippet("nfl-qb-002", "Josh Allen: Buffalo Bills quarterback. 2023 stats: 4,306 passing yards, 29 touchdowns, 18 interceptions. Completion rate: 66.5%. Known for dual-threat ability with 524 rushing yards.")
    await upsert_snippet("nfl-qb-003", "Lamar Jackson: Baltimore Ravens quarterback. 2023 stats: 3,678 passing yards, 24 touchdowns, 7 interceptions. Completion rate: 67.2%. Rushing: 821 yards, 5 touchdowns. MVP candidate.")
    await upsert_snippet("nba-lakers-001", "Los Angeles Lakers: 2023-24 season record 47-35. Key players: LeBron James (25.7 PPG, 8.3 RPG), Anthony Davis (24.1 PPG, 12.6 RPG). Strengths: Defense, veteran leadership, playoff experience.")
    await upsert_snippet("nba-lakers-002", "Lakers recent performance: Won 8 of last 10 games. Improved three-point shooting (37.2%). Strong defensive rating (110.3). Key wins against Celtics, Warriors, and Nuggets.")
    await upsert_snippet("nba-celtics-001", "Boston Celtics: 2023-24 season record 64-18. Key players: Jayson Tatum (26.9 PPG, 8.1 RPG), Jaylen Brown (23.0 PPG, 5.5 RPG). Strengths: Depth, three-point shooting, defense.")
    await upsert_snippet("premier-league-001", "Premier League 2023-24 standings: Manchester City (89 points), Arsenal (84 points), Liverpool (82 points). Top scorers: Erling Haaland (27 goals), Mohamed Salah (18 goals).")
    await upsert_snippet("premier-league-002", "Manchester City: Defending champions. Key players: Erling Haaland, Kevin De Bruyne, Rodri. Strengths: Possession play, attacking depth, Pep Guardiola tactics.")
    await upsert_snippet("tennis-001", "Novak Djokovic: Current world #1. 2023 Grand Slam results: Australian Open winner, French Open winner, Wimbledon finalist, US Open winner. Total career Grand Slams: 24.")
    await upsert_snippet("tennis-002", "Carlos Alcaraz: Spanish tennis player, world #2. 2023 highlights: Wimbledon winner, US Open finalist. Known for aggressive baseline play and powerful forehand. Age: 21.")
    await upsert_snippet("tennis-003", "Iga Swiatek: Polish tennis player, world #1 in women's tennis. 2023 highlights: French Open winner, WTA Finals winner. Known for powerful groundstrokes and mental toughness.")
    await upsert_snippet("nba-playoffs-001", "NBA Playoffs 2024: Boston Celtics (1st seed, 64-18 record), Denver Nuggets (2nd seed, 57-25 record). Key storylines: Celtics' depth, Nuggets' championship defense, young teams rising.")
    await upsert_snippet("nba-playoffs-002", "Denver Nuggets: Defending NBA champions. Key players: Nikola Jokic (26.4 PPG, 12.4 RPG, 9.0 APG), Jamal Murray (21.2 PPG). Strengths: Jokic's playmaking, team chemistry, playoff experience.")
    await upsert_snippet("nfl-teams-001", "NFL 2023 season: Kansas City Chiefs (11-6), Buffalo Bills (11-6), Baltimore Ravens (13-4). Key storylines: Chiefs' dynasty, Bills' playoff struggles, Ravens' MVP season.")
    await upsert_snippet("nfl-teams-002", "Kansas City Chiefs: Defending Super Bowl champions. Key players: Patrick Mahomes, Travis Kelce, Chris Jones. Strengths: Mahomes' improvisation, Andy Reid's coaching, playoff experience.")
    await upsert_snippet("soccer-world-001", "World Cup 2026: Hosted by USA, Canada, and Mexico. Qualification: 48 teams. Key storylines: Messi's final World Cup, young talent emergence, host nation expectations.")
    await upsert_snippet("soccer-world-002", "Lionel Messi: Argentine forward, 8 Ballon d'Or winner. 2023 highlights: World Cup winner, Inter Miami transfer. Known for dribbling, passing, and finishing ability.")
    await upsert_snippet("basketball-stats-001", "NBA 2023-24 season statistics: League average points per game: 115.6. Three-point percentage: 36.1%. Free throw percentage: 78.9%. Pace: 101.2 possessions per game.")
    await upsert_snippet("basketball-stats-002", "NBA scoring leaders 2023-24: Luka Doncic (33.9 PPG), Joel Embiid (34.7 PPG), Giannis Antetokounmpo (30.4 PPG). Rebounding: Domantas Sabonis (13.7 RPG), Nikola Jokic (12.4 RPG).")
    await upsert_snippet("football-stats-001", "NFL 2023 season statistics: League average passing yards per game: 225.8. Rushing yards per game: 118.9. Total touchdowns: 1,371. Field goal percentage: 85.2%.")
    await upsert_snippet("football-stats-002", "NFL passing leaders 2023: Tua Tagovailoa (4,624 yards), Dak Prescott (4,516 yards), Jared Goff (4,575 yards). Rushing: Josh Jacobs (1,653 yards), Derrick Henry (1,167 yards).")
    print("✅ All sports snippets upserted with Semantic Kernel embeddings.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
