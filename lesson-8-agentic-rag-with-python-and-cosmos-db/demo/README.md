# Sports Analyst Agentic RAG Demo

This demo demonstrates how to build a **minimal RAG agent that acts on its own** for sports analysis using **Azure Cosmos DB with vector search** and the **Semantic Kernel** framework in Python. The agent can autonomously retrieve relevant sports data, evaluate retrieval quality, and re-check the database if the first retrieval is not sufficient.

## 🔍 What This Demo Demonstrates

- **Agentic RAG Implementation** - A self-acting sports analyst agent that makes autonomous decisions
- **Cosmos DB Integration** with vector embeddings and similarity search for sports data
- **Autonomous Re-checking** - Agent can re-check the database if retrieval quality is insufficient
- **Vector Search with Fallback** - Hybrid search approach with text fallback for sports queries
- **Quality Assessment** - Agent evaluates retrieval quality and makes re-checking decisions
- **Sports Analysis Synthesis** - Generates comprehensive sports analysis using retrieved documents

> This demonstrates the core learning objective: building a minimal RAG agent that acts on its own, retrieving relevant sports documents from Cosmos DB and producing comprehensive sports analysis using Python and LLM calls, with the ability to re-check the DB if the first retrieval is not sufficient.

---

## 🏈 Sports Analyst RAG Agent: Overview

### ✅ Description

The Sports Analyst RAG agent demonstrates autonomous operation by:

- **Autonomous Decision Making** - Agent decides when to re-check the database for sports data
- **Quality Assessment** - Evaluates retrieval quality using confidence scoring for sports queries
- **Query Refinement** - Automatically refines sports queries for better retrieval
- **Multi-attempt Retrieval** - Can make multiple retrieval attempts with different strategies
- **Intelligent Fallback** - Falls back from vector search to text search to mock sports data

### 🧠 Under the Hood

- Uses `azure-cosmos` SDK for database operations
- Generates embeddings with Semantic Kernel's `AzureTextEmbedding` service
- Implements hybrid search (vector + text) with intelligent fallback
- Uses Semantic Kernel's AzureChatCompletion for LLM-based quality assessment and query refinement
- Autonomous re-checking based on confidence thresholds
- Specialized for sports analysis with domain-specific prompts

---

## 🔁 How the Sports Analyst RAG Works

1. **Query Reception**: Agent receives a sports analysis query
2. **Initial Retrieval**: Retrieves sports documents using hybrid search approach
3. **Quality Assessment**: Agent evaluates retrieval quality using LLM-based assessment
4. **Autonomous Decision**: If quality is insufficient, agent decides to re-check
5. **Query Refinement**: Agent refines the sports query based on identified issues
6. **Re-retrieval**: Agent retrieves sports documents again with refined query
7. **Answer Synthesis**: Agent generates comprehensive sports analysis using retrieved documents
8. **Response Delivery**: Agent provides analysis with confidence score and reasoning

---

## ✅ Setup Requirements

### Prerequisites

- **Azure Cosmos DB** account with:
  - **Vector search enabled** with `quantizedFlat` indexing
  - **Database and container** configured for vector search
- **Azure OpenAI Service** with:
  - **Text embedding model** deployed (e.g., text-embedding-3-small)
  - **Chat completion model** deployed (e.g., gpt-4o-mini)
- Python 3.13+
- `.env` file with required Azure keys

### .env Example

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-aoai-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_KEY=your_azure_openai_key_here

# Azure Cosmos DB Configuration
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_KEY=your_cosmos_db_key_here
COSMOS_DB=your_database_name
COSMOS_CONTAINER=your_container_name
COSMOS_PARTITION_KEY=/pk
```

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the `.env` example above and fill in your actual Azure service details.

### 3. Run the Demo

```bash
python main.py
```

This will:
- **Test Cosmos DB operations** (upserting and reading sports data)
- **Test the Sports Analyst RAG agent** with various sports queries
- **Demonstrate autonomous operation** with re-checking capability
- **Show sports analysis generation** with confidence scoring

### 4. Test Data Ingestion

To populate the database with sample sports data:

```bash
python rag/ingest.py
```

This will upsert sample sports information with vector embeddings.

---

## 🧪 What Gets Tested

### Sports Analyst RAG Agent Capabilities
- **Autonomous Operation**: Agent makes independent decisions about re-checking
- **Quality Assessment**: LLM-based evaluation of sports data retrieval quality
- **Query Refinement**: Automatic sports query improvement based on retrieval issues
- **Multi-attempt Retrieval**: Multiple retrieval attempts with different strategies
- **Confidence Scoring**: Comprehensive confidence assessment and reasoning

### Cosmos DB Integration
- **Vector Search**: Semantic similarity search using embeddings for sports data
- **Text Search Fallback**: Text-based search when vector search fails
- **Hybrid Search**: Intelligent combination of vector and text search
- **Data Ingestion**: Upserting sports documents with vector embeddings

### Sports Analysis Generation
- **Context Synthesis**: Combining information from multiple retrieved sports documents
- **Source Citation**: Proper attribution of sports information sources
- **Confidence Reporting**: Transparent reporting of analysis confidence
- **Error Handling**: Graceful handling of retrieval and synthesis errors

---

## 🏈 Sports Data Coverage

The demo includes comprehensive sports data covering:

- **NFL**: Quarterback statistics, team performance, season standings
- **NBA**: Player stats, team records, playoff analysis
- **Soccer**: Premier League standings, player performance, World Cup data
- **Tennis**: Player rankings, Grand Slam results, performance trends
- **General Sports**: Statistics, trends, and analysis across multiple sports

---

## 🎯 Key Features

### Autonomous Decision Making
- Agent evaluates retrieval quality and decides whether to re-check
- Uses confidence thresholds to determine when additional retrieval is needed
- Automatically refines queries based on identified issues

### Sports-Specific Analysis
- Specialized prompts for sports analysis
- Focus on statistics, performance trends, and strategic insights
- Domain-specific quality assessment for sports data

### Robust Error Handling
- Graceful fallback from vector search to text search to mock data
- Comprehensive error handling and logging
- User-friendly error messages and suggestions

---

## 📊 Example Queries

The demo tests various sports analysis queries:

- "What are the latest NFL quarterback statistics and performance trends?"
- "How did the Lakers perform in their recent games and what are their key strengths?"
- "What are the current standings in the Premier League and who are the top performers?"
- "Analyze the performance of the top tennis players in recent tournaments"
- "What are the key statistics and trends in the NBA playoffs this season?"

---

## 🔧 Technical Architecture

- **Semantic Kernel**: LLM orchestration, function calling, and service management (AzureChatCompletion and AzureTextEmbedding)
- **Azure Cosmos DB**: Vector database with hybrid search capabilities
- **Azure OpenAI**: Embedding generation via Semantic Kernel's AzureTextEmbedding and text completion via AzureChatCompletion
- **Pydantic**: Data validation and structured outputs
- **Async/Await**: Asynchronous processing for better performance

---

## 📈 Performance Features

- **Lazy Loading**: Cosmos DB client initialization only when needed
- **Caching**: Efficient caching of embeddings and search results
- **Parallel Processing**: Async operations for better throughput
- **Error Recovery**: Robust fallback mechanisms for reliability

---

## 🎉 Success Indicators

When the demo runs successfully, you should see:

- ✅ Cosmos DB operations completed successfully
- ✅ Sports data upserted with vector embeddings
- ✅ Sports Analyst RAG agent demonstrated autonomous operation
- ✅ Database re-checking capability verified
- ✅ Vector search with Cosmos DB working for sports data
- ✅ Comprehensive sports analysis generated with confidence scoring

This demo showcases the power of Agentic RAG for sports analysis, demonstrating how an AI agent can autonomously retrieve, evaluate, and synthesize sports information to provide expert-level analysis.
