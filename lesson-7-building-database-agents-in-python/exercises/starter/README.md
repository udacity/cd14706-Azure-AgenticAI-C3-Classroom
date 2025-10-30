# Exercise

Integrate Cosmos DB RAG utilities, upsert sample snippets, retrieve with vector search, and combine with ecommerce tool plugins in test routines.

### **Prerequisites**

* Azure Cosmos DB and vector search enabled; `.env` configured

* Ability to call helper functions from `rag/ingest.py` and `rag/retriever.py`

* Lessons 1–6 completed

### **Instructions**

1. Import the RAG helpers in `main.py`:
   - `from rag.ingest import upsert_snippet, embed_texts`
   - `from rag.retriever import retrieve`

2. Create an async function `test_cosmos_db_operations()` that:
   - Upserts several test product texts using `upsert_snippet(product_id, text, pk=...)`.
   - For a small list of queries, calls `await retrieve(query, k=3)` and logs each result’s `id` and first ~100 characters of `text`.

3. In `create_kernel()`, keep the standard Azure OpenAI setup and register the ecommerce tools (`inventory`, `shipping`, `pricing`, `recommendations`, `reviews`).

4. In `main()`, call `asyncio.run(test_cosmos_db_operations())` before the external API tests to validate the database path first.

5. Ensure logs clearly separate sections for Cosmos DB, external APIs, and scenarios.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`}
