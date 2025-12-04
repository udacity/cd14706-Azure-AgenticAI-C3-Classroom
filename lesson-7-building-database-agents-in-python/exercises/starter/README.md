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

Your task is to complete the helper functions in the `rag` directory and update the `process_customer_query` function in `main.py`.

#### **Part 1: Implement Data Ingestion (`rag/ingest.py`)**

1.  **In `delete_all_items()`:**
    *   Implement the logic to query and delete all items for a given partition key. This prevents data contamination between test runs.
    *   **Hint:** Use the query `"SELECT c.id FROM c WHERE c.pk = @pk"` and loop through the results, calling `container.delete_item()` for each.

2.  **In `upsert_snippet()`:**
    *   Implement the logic to generate embeddings for the text and upsert the document into Cosmos DB.
    *   **Hint:** Call `embed_texts()` to get the embeddings, create a dictionary for the document, and use `container.upsert_item()`.

#### **Part 2: Implement Data Retrieval (`rag/retriever.py`)**

1.  **In `_execute_query_with_retry()`:**
    *   Implement a retry loop with exponential backoff to handle potential query plan issues in Cosmos DB.
    *   **Hint:** Use a `for` loop with `max_retries` and `asyncio.sleep()` for the backoff.

2.  **In `retrieve()`:**
    *   Build the SQL query for a text-based search using `CONTAINS`.
    *   Execute the query using the `_execute_query_with_retry` function you just implemented.
    *   Return the query results (if no results found, return empty list to prevent hallucination).
    *   **Hint:** Remember to add a filter for the `partition_key` if it's provided.

#### **Part 3: Update Agent Logic (`main.py`)**

1.  **In `process_customer_query()`:**
    *   Replace the temporary `kernel.add_function` and `kernel.invoke` calls with a direct implementation using `ChatCompletionService`.
    *   **Hint:** Get the `ChatCompletionService` from the kernel, create a `ChatHistory`, add the system prompt and user query, configure `OpenAIChatPromptExecutionSettings` with `FunctionChoiceBehavior.Auto()`, and then call `chat_service.get_chat_message_contents()`.
