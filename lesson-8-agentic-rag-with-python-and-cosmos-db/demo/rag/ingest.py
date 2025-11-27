import os
import logging
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
from rag.retriever import embed_texts, get_cosmos_client

async def delete_all_items(partition_key: str):
    """Delete all items with the specified partition key to prevent contamination between runs"""
    try:
        _ , container = get_cosmos_client()
        if not container:
            raise Exception("Cosmos DB container not available")
        
        query = "SELECT c.id, c.pk FROM c WHERE c.pk = @pk"
        params = [{"name": "@pk", "value": partition_key}]
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        
        deleted_count = 0
        for item in items:
            container.delete_item(item=item["id"], partition_key=item["pk"])
            deleted_count += 1
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} items with partition key '{partition_key}'")
        return deleted_count
    except Exception as e:
        print(f"Failed to cleanup items: {e}")
        return 0

async def upsert_snippet(doc_id, text, pk="sports"):
    """Upsert a document with its embedding into Cosmos DB"""
    try:
        _ , container = get_cosmos_client()
        if not container:
            raise Exception("Cosmos DB container not available")

        embeddings = await embed_texts([text])
        vec = embeddings[0]
        keywords = text.split(':')[0] if ':' in text else text[:100]
        container.upsert_item({
            "id": doc_id,
            "pk": pk,
            "text": text,
            "keywords": keywords,
            "embedding": vec
        })
        print(f"{doc_id} upserted with Semantic Kernel embeddings.")
    except Exception as e:
        print(f"Failed to upsert {doc_id}: {e}")

async def upsert_all_sports_data():
    """Upsert all sports data."""
    test_sports_data = [
        ("sports-lakers-001", "Los Angeles Lakers: NBA team, current record 15-10. Key players: LeBron James, Anthony Davis. Recent performance: Won 3 of last 5 games. Next game: vs Warriors."),
        ("sports-lebron-001", "LeBron James: Lakers forward, 39 years old. Season stats: 25.2 PPG, 7.8 RPG, 6.8 APG. Recent form: Excellent. Injury status: Healthy."),
        ("sports-warriors-001", "Golden State Warriors: NBA team, current record 12-13. Key players: Stephen Curry, Klay Thompson. Recent performance: Lost 4 of last 5 games."),
        ("sports-nba-news-001", "NBA Trade Rumors: Lakers looking for shooting help, Warriors considering roster changes. Recent trades: None significant. Free agency: Several role players available."),
        ("sports-standings-001", "NBA Western Conference Standings: Lakers 15-10 (5th place), Warriors 12-13 (9th place). Top teams: Timberwolves 18-7, Thunder 17-8."),
        ("sports-anthony-davis-001", "Anthony Davis: Lakers center, 31 years old. Season stats: 24.8 PPG, 12.1 RPG, 2.4 BPG. Recent form: Strong. Injury status: Healthy."),
        ("sports-curry-001", "Stephen Curry: Warriors guard, 35 years old. Season stats: 28.5 PPG, 4.8 RPG, 5.2 APG. Recent form: Good. Injury status: Healthy."),
        ("sports-nba-schedule-001", "Upcoming NBA games: Lakers vs Warriors (Dec 25), Celtics vs Heat (Dec 26), Nuggets vs Suns (Dec 27). All games at 8:00 PM ET.")
    ]
    
    for data_id, data_text in test_sports_data:
        await upsert_snippet(data_id, data_text, pk="sports")
    
    print("All test sports data upserted successfully!")
