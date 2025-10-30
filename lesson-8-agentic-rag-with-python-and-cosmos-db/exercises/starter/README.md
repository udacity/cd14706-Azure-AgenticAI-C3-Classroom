# Exercise

Build an agentic RAG loop that assesses retrieval quality, optionally refines the query, and then generates an answer from Cosmos DB results.

### **Prerequisites**

* Cosmos DB vector search and embeddings configured (see lesson 7)

* Ability to create SK functions and parse/validate JSON

* Lessons 1–7 completed

### **Instructions**

1. Create an `AgenticRAGAgent` class with:
   - `process_query(query)`: main loop with a bounded number of retrieval attempts.
   - `_assess_retrieval_quality(...)`: SK function that returns JSON with `confidence`, `reasoning`, and `issues`.
   - `_refine_query(...)`: SK function that returns a refined query string based on issues and retrieved docs.
   - `_generate_answer(...)`: SK function that synthesizes an answer from retrieved context blocks.

2. In `process_query(query)`, implement the loop:
   - Call `await retrieve(query, k=5)` and store `sources` and `retrieval_attempts`.
   - Call `_assess_retrieval_quality(...)` and set `confidence_score`, `reasoning`.
   - If `confidence` ≥ threshold, break; otherwise, when attempts remain, call `_refine_query(...)` to update `query` and retry.

3. After the loop, call `_generate_answer(...)` with the final `query`, `retrieved_docs`, and `confidence`, and store `answer`.

4. Create `test_agentic_rag_queries()` that instantiates the agent and runs several queries; log the final `answer`, `confidence`, `sources` count, `retrieval_attempts`, `needs_recheck`, and `reasoning`.

5. In `main()`, run `test_cosmos_db_operations()` (from lesson 7) first, then `test_agentic_rag_queries()`.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`
