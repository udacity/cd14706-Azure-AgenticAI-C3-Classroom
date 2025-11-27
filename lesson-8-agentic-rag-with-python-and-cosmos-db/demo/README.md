# Sports Analyst Agentic RAG Demo

This demo demonstrates an **advanced, autonomous RAG agent** for sports analysis. It uses **Azure Cosmos DB** with hybrid search and the **Semantic Kernel** framework in Python. The agent autonomously retrieves sports data, evaluates the quality of that retrieval, and refines its queries to provide accurate, data-driven analysis.

## 🔍 Key Patterns Demonstrated

- **Server-Side Vector Search:** Uses Cosmos DB's `ORDER BY VectorDistance` to leverage database-native vector indexing and sorting, reducing application-layer processing.
- **Hybrid Retrieval Architecture:** Combines vector search (for semantic similarity) and text search (for keyword matching) in parallel, then merges results using **Reciprocal Rank Fusion (RRF)** to maximize relevance.
- **Keywords Extraction Pattern:** Extracts compact, searchable keywords from verbose text during ingestion, enabling efficient `CONTAINS()` queries without full-text scanning.
- **Clean Architecture:** Separates data ingestion concerns (`rag/ingest.py`) from application logic (`main.py`), following single-responsibility principles.

---

## 🏈 Sports Analyst RAG Agent: Overview

### ✅ Description

The Sports Analyst RAG agent demonstrates autonomous operation by:

- **Autonomous Decision Making** - Decides when to re-check the database for better sports data based on a confidence score.
- **Quality Assessment** - Evaluates the relevance and completeness of retrieved documents.
- **Query Refinement** - Automatically refines sports queries if the initial results are poor.
- **Multi-attempt Retrieval** - Makes multiple attempts to find the best information.

### 🧠 Under the Hood

- **`azure-cosmos` SDK**: Powers all database operations.
- **Hybrid Search**: Intelligently combines `VectorDistance` (for semantic meaning) and `CONTAINS` (for keyword precision).
- **Reciprocal Rank Fusion (RRF)**: Merges search results into a single, highly relevant list.
- **Semantic Kernel**: Orchestrates calls to Azure OpenAI for embedding generation, quality assessment, and final answer synthesis.

---

## 🔁 How the Sports Analyst RAG Works

1.  **Query Reception**: The agent receives a sports-related query (e.g., "Tell me about LeBron James' season stats").
2.  **Hybrid Retrieval**: The agent performs both a vector search and a text search in parallel against the Cosmos DB. The results are merged and re-ranked using RRF.
3.  **Quality Assessment**: The agent uses an LLM to assess the quality of the retrieved documents. It asks, "Is this information good enough to answer the user's question?"
4.  **Autonomous Decision**: If the quality score is below a confidence threshold (0.7), the agent decides to refine its query.
5.  **Query Refinement**: The agent uses an LLM to generate a better, more specific query.
6.  **Re-retrieval**: The agent executes the new query. This loop can happen up to 3 times.
7.  **Answer Synthesis**: The agent generates a comprehensive, human-readable answer using the best-retrieved documents as its context.

---

## ✅ Setup Requirements

### Prerequisites

- **Azure Cosmos DB** account with vector search enabled.
- **Azure OpenAI Service** with deployed models for chat (`gpt-4o-mini`) and text embedding (`text-embedding-3-small`).
- Python 3.10+
- A `.env` file with your Azure service credentials.

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

Create a `.env` file and populate it with your Azure credentials as shown in the example above.

### 3. Run the Demo

```bash
python main.py
```

This script will:
- **Clean and Ingest Data**: Automatically clear old sports data and upsert a fresh sample set from `rag/ingest.py`.
- **Test Local Retrieval**: Run a few simple queries to confirm the connection.
- **Test the Agent**: Execute a series of complex sports queries to demonstrate the full agentic RAG workflow.

---

## 📊 Example Queries

The demo tests various sports analysis queries that showcase the agent's ability to handle different types of questions:

- "What are the Lakers' recent game results and current record?"
- "Tell me about LeBron James' season statistics and performance"
- "What are the latest NBA trade rumors and news?"
- "Show me information about the Warriors team and their key players"
- "What are the current NBA standings and team records?"

---

## 🎉 Success Indicators

When the demo runs successfully, you should see:

- ✅ Cosmos DB operations completing successfully.
- ✅ Sports data being cleaned and upserted.
- ✅ The Agentic RAG agent processing each query, including performing multiple retrieval attempts for difficult questions.
- ✅ A final, well-reasoned answer for each query, generated from the retrieved context.
- ✅ The script completing with an exit code of 0.