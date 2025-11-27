# Exercise Solution - Advanced Agentic RAG with E-commerce Data

[VIDEO_PLACEHOLDER: Agentic RAG with Cosmos DB]

## **What This Solution Demonstrates**

This solution implements a production-ready agentic RAG system with several key architectural patterns:

1.  **Optimized Vector Search:** Uses Cosmos DB's `ORDER BY VectorDistance` for efficient server-side sorting of vector search results. This leverages the database's native capabilities rather than sorting in application code.

2.  **Advanced Hybrid Retrieval:** Combines vector search (semantic understanding) and text search (keyword precision) using **Reciprocal Rank Fusion (RRF)**. Both searches run in parallel via `asyncio.gather()`, and results are merged intelligently to surface the most relevant documents.

3.  **Keywords Field Pattern:** Demonstrates extracting searchable keywords from verbose text during ingestion. The `keywords` field (extracted from text before the first colon) enables efficient `CONTAINS()` queries without searching through entire product descriptions.

4.  **Confidence Calibration with Structured Prompts:** Shows how to guide LLM assessments with explicit scoring rubrics (0.8-1.0 for highly relevant, 0.6-0.79 for relevant with gaps, etc.). Uses 500-character snippets to provide sufficient context while managing token usage.

5.  **Separation of Concerns:** Follows clean architecture principles by separating data ingestion (`rag/ingest.py`) from orchestration logic (`main.py`), making the codebase maintainable and testable.

---

### **Solution Walkthrough**

The core of the solution remains an autonomous RAG agent that evaluates retrieval quality and can refine its query. However, the retrieval step is now much more powerful.

```python
# The agent's retrieval call now uses the advanced hybrid search by default
retrieved_docs = await retrieve(query, k=5, partition_key="ecommerce")
```

The hybrid search function in `rag/retriever.py` runs both vector and text searches concurrently and intelligently re-ranks the results.

```python
# Hybrid search runs both retrieval methods in parallel
vector_results_task = retrieve_with_vector_search(query, k, partition_key)
text_results_task = retrieve_with_text_search(query, k, partition_key)
vector_results, text_results = await asyncio.gather(vector_results_task, text_results_task)

# Reciprocal Rank Fusion (RRF) combines the results
reranked_results = rerank_results([vector_results, text_results], k)
```

The data ingestion has been centralized in `rag/ingest.py`, and `main.py` now simply calls the function to populate the database, making the code cleaner.

```python
# In main.py, we now import and call the data ingestion function
from rag.ingest import delete_all_items, upsert_all_ecommerce_data

# Clean up old data
await delete_all_items("ecommerce")

# Upsert all ecommerce data from the ingest module
await upsert_all_ecommerce_data()
```

The agent's assessment loop and final answer generation remain the same, but they now benefit from the higher-quality, re-ranked documents provided by the improved retrieval strategy.

```
🔄 Retrieval attempts and confidence are logged, now powered by a superior hybrid search.
```

[IMAGE_PLACEHOLDER: Screengrab of logs showing retrieval attempts, confidence, and sources]

### **Key Takeaway**

> This solution showcases an advanced, production-ready RAG agent. It uses an efficient hybrid retrieval strategy with re-ranking and follows best practices for code structure by separating data ingestion logic from the main application flow.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]