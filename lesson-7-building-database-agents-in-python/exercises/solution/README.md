# Exercise Solution

[VIDEO_PLACEHOLDER: Cosmos DB + Agentic Database Workflows]

### **Solution Walkthrough**

We add Cosmos‑backed RAG utilities using Semantic Kernel's embedding service and demonstrate both upserting and text-based retrieval, then tie this into the agent's tool ecosystem.

**Important Note:** The `pk` field is used for filtering data (e.g., `pk="ecommerce"` vs `pk="sports"`), but it's NOT the partition key. The actual partition key is `/id` (defined in `.env`), meaning each document's `id` field is the partition key value. This solution can work with either a shared container or a separate `ecomm_docs` container.

```python
# Upsert test snippets (excerpt)
for product_id, text in test_products:
    upsert_snippet(product_id, text, pk="ecommerce")
```

We then retrieve with text-based search (CONTAINS) and log concise snippets to validate indexing and search functionality. The `pk` field helps us filter ecommerce data from sports data in the same container.

```python
# Retrieve with text-based search (excerpt)
# Note: We filter by pk field, not partition key
results = await retrieve(query, k=3)
for i, r in enumerate(results, 1):
    logger.info(f"{i}. {r.get('id')}: {r.get('text', '')[:100]}...")
```

The kernel is extended with ecommerce tool plugins so data from Cosmos DB can be complemented by live APIs in scenarios.

```python
kernel.add_plugin(InventoryTools(), "inventory")
kernel.add_plugin(ShippingTools(), "shipping")
kernel.add_plugin(PricingTools(), "pricing")
kernel.add_plugin(RecommendationTools(), "recommendations")
kernel.add_plugin(ReviewTools(), "reviews")
```

```
✅ Ecommerce Database Agent Testing completed successfully!
```

[IMAGE_PLACEHOLDER: Screengrab of logs for upserts and text search results]

### **Key Takeaway**

> The solution integrates Cosmos DB text-based search with tool plugins, enabling retrieval‑augmented interactions across ecommerce data. Vector search will be introduced in Lesson 8.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
