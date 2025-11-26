# Sports Analyst Database Agent with Cosmos DB Integration

This demo showcases a sports analyst agent that uses **Azure Cosmos DB with text-based search** to perform sports data retrieval and analysis. It demonstrates how to connect Cosmos DB with the **Semantic Kernel framework**, returning structured results on basketball and other sports through RAG (Retrieval-Augmented Generation). Note: Vector search will be introduced in Lesson 8.

## 🎯 What This Demo Covers

- **Cosmos DB Text-Based Search Integration** using Azure's database capabilities
- **RAG (Retrieval-Augmented Generation)** for sports data retrieval
- **Semantic Kernel Tool Plugins** wrapping sports-specific database functions
- **Sports Data Analysis** via text search and structured data
- **Database Operations** including upserting and reading sports information with embeddings
- **Memory-Optional Architecture** focused on query/response quality

---

## 🔌 Cosmos DB Integration: `RAG System`

- Performs text-based searches for basketball scores, player stats, and team information
- Uses Azure Cosmos DB with embeddings (for future vector search) and CONTAINS text search
- Returns structured sports data from the database:
  ```json
  {
    "id": "lakers-001",
    "text": "Los Angeles Lakers: NBA team, current record 15-10. Key players: LeBron James, Anthony Davis...",
    "embedding": [0.1, 0.2, ...]
  }
  ```
- Configured as a Semantic Kernel plugin via `rag/retriever.py`

---

## ✅ Prerequisites

- Python 3.8 or higher
- Azure OpenAI Service with text embedding capabilities
- Azure Cosmos DB account
- A properly configured `.env` file (see below)

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env` File

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-aoai-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_KEY=your_azure_openai_key_here

# Azure Cosmos DB Configuration for Sports Data
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_KEY=your_cosmos_db_key_here
COSMOS_DB=your_database_name
COSMOS_CONTAINER=your_container_name
COSMOS_PARTITION_KEY=/pk
```

### 3. Run the Demo

```bash
python main.py
```

This will:
- **Test Cosmos DB operations** (upserting and reading sports data)
- **Demonstrate RAG capabilities** with text-based search for sports content
- **Show sports analyst functionality** with basketball and NBA information retrieval

### 4. Test Data Ingestion

To populate the database with sample sports data:

```bash
python rag/ingest.py
```

This will upsert sample sports information with vector embeddings.

---

## 🧪 What Gets Tested

### Cosmos DB Operations
- **Data Upserting**: Sports data with embeddings for future vector search (teams, players, games)
- **Data Retrieval**: Text-based search using CONTAINS for sports content
- **Query Processing**: Text search with fallback strategies

### Sports Analyst Agent Features
- **Game Scores**: Live and historical game results and statistics
- **Player Statistics**: Detailed player performance data and analysis
- **Team Analysis**: Team standings, rosters, and performance metrics
- **League Information**: Standings, schedules, and league-wide statistics
- **Sports News**: Trade rumors, injury reports, and breaking news

---

## 🔧 Technical Architecture

### RAG Implementation
1. **Data Ingestion**: Sports information is upserted with embeddings generated using Semantic Kernel's AzureTextEmbedding service (for future vector search in L8)
2. **Query Processing**: User queries are processed through the RAG retriever
3. **Text Search**: Sports content is found using CONTAINS text search
4. **Fallback Strategy**: If no matches found, random documents are returned
5. **Response Generation**: Retrieved data is used to generate sports analysis responses

### Database Schema
- **Container**: Stores sports documents with embeddings
- **Partition Key**: `/pk` for efficient querying
- **Vector Index**: `quantizedFlat` configured (will be used in L8)
- **Fields**: `id`, `pk`, `text`, `embedding`

---

## 🚀 Key Features

- **Text-Based Search**: Uses CONTAINS queries for sports content retrieval (vector search in L8)
- **Embedding Generation**: Uses Semantic Kernel's AzureTextEmbedding service to prepare data for future vector search
- **RAG Integration**: Combines retrieval with generation for intelligent responses
- **Sports Focus**: Specialized for basketball, NBA, and sports analysis
- **Structured Data**: Pydantic models for type-safe responses
- **Error Handling**: Graceful fallbacks and comprehensive logging
- **Scalable**: Built on Azure Cosmos DB for enterprise-scale applications

---

## 📊 Sample Output

```
🏀 Sports Analyst Database Agent with Cosmos DB Demo
================================================================================

🗄️ Testing Cosmos DB Operations for Sports Data
============================================================
📝 Testing sports data upserting...
   ✅ Upserted: demo-lakers-001
   ✅ Upserted: demo-lebron-001
   ✅ Upserted: demo-warriors-001
   ✅ Upserted: demo-nba-news-001
✅ All demo sports data upserted successfully!

📖 Testing sports data retrieval...
   🔍 Query: 'Lakers'
   📊 Found 3 results:
      1. demo-lakers-001: Los Angeles Lakers: NBA team, current record 15-10...
      2. demo-lebron-001: LeBron James: Lakers forward, 39 years old...
      3. demo-warriors-001: Golden State Warriors: NBA team, current record 12-13...

---

## 🔍 Troubleshooting

### Common Issues

1. **Cosmos DB Connection**: Ensure your Cosmos DB account is properly configured
2. **Environment Variables**: Verify all required environment variables are set
3. **Dependencies**: Make sure all packages are installed correctly
4. **Cross-Partition Queries**: CONTAINS queries require enable_cross_partition_query=True

### Debug Mode

Enable debug logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Related Resources

- [Azure Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [Semantic Kernel Documentation](https://github.com/microsoft/semantic-kernel)
- [Azure OpenAI Embeddings](https://docs.microsoft.com/en-us/azure/ai-services/openai/concepts/embeddings)
- [RAG Pattern Best Practices](https://docs.microsoft.com/en-us/azure/ai-services/openai/concepts/rag)
- [Cosmos DB Query Reference](https://docs.microsoft.com/en-us/azure/cosmos-db/sql-query-getting-started)