# Exercise

Integrate Cosmos DB RAG utilities, upsert sample snippets, retrieve with text-based search, and combine with ecommerce tool plugins in test routines.

### **Prerequisites**

* Azure Cosmos DB configured; `.env` file set up with credentials

* Ecommerce data populated in Cosmos DB (see Setup Instructions below)

* Ability to call helper functions from `rag/ingest.py` and `rag/retriever.py`

* Lessons 1–6 completed

### **Setup Instructions**

You have two options for storing ecommerce data:

#### **Option 1: Shared Container (Recommended for Free Tier)**
Use the existing `sports_docs` container with different partition keys. This avoids RU/s limits.

```bash
# Navigate to lesson-7 root directory
cd /path/to/lesson-7-building-database-agents-in-python

# Run the ecommerce data setup script
python3 setup_ecomm_data.py
```

This will:
- Add 14 ecommerce documents to your existing `sports_docs` container
- Use a `pk` field set to `"ecommerce"` for filtering (sports data uses `pk="sports"`)
- No additional RU/s consumption
- **Note:** The container's partition key is `/id` (defined in `.env`), and each document's `id` is the actual partition key value

#### **Option 2: Separate Container**
Create a dedicated `ecomm_docs` container. Most student accounts should support this if within RU/s limits.

**Typical Account Limits:**
- Free Tier: 1000 RU/s free
- Total Limit: Usually 2000 RU/s
- Minimum per container: 400 RU/s

To check your available capacity:
```bash
az cosmosdb sql container list --account-name <your-account> --resource-group <your-rg> --database-name sports_agent_db
az cosmosdb sql container throughput show --account-name <your-account> --resource-group <your-rg> --database-name sports_agent_db --name sports_docs
```

To create a separate container:
1. Update your `.env`:
   ```env
   COSMOS_ECOMM_CONTAINER=ecomm_docs
   ```
2. Modify `setup_ecomm_data.py` to create the new container with `throughput=400`
3. Keep `COSMOS_PARTITION_KEY=/id` (same partition key path for consistency)

**Note:** If you encounter RU/s limit errors, use Option 1 (shared container).

### **Instructions**

1. Import the RAG helpers in `main.py`:
   - `from rag.ingest import upsert_snippet, embed_texts`
   - `from rag.retriever import retrieve`

2. Create an async function `test_cosmos_db_operations()` that:
   - Upserts several test product texts using `upsert_snippet(product_id, text, pk="ecommerce")`.
   - For a small list of queries, calls `await retrieve(query, k=3)` and logs each result's `id` and first ~100 characters of `text`.
   - **Note:** The `pk` parameter is just a field for filtering (e.g., `WHERE c.pk = 'ecommerce'`), not the partition key. The actual partition key is the document's `id` field (as defined by `COSMOS_PARTITION_KEY=/id` in `.env`).

3. In `create_kernel()`, keep the standard Semantic Kernel setup with Azure OpenAI services and register the ecommerce tools as Semantic Kernel plugins (`inventory`, `shipping`, `pricing`, `recommendations`, `reviews`).

4. In `main()`, call `asyncio.run(test_cosmos_db_operations())` before the external API tests to validate the database path first.

5. Ensure logs clearly separate sections for Cosmos DB, external APIs, and scenarios.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`}
