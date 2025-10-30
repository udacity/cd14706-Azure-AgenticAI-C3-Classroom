# Exercise Solution

[VIDEO_PLACEHOLDER: Cosmos DB + Agentic Database Workflows]

### **Solution Walkthrough**

We add Cosmos‑backed RAG utilities and demonstrate both upserting and vector retrieval, then tie this into the agent’s tool ecosystem.

```python
# Upsert test snippets (excerpt)
for product_id, text in test_products:
    upsert_snippet(product_id, text, pk="test")
```

We then retrieve with vector search and log concise snippets to validate indexing and similarity semantics.

```python
# Retrieve with vector search (excerpt)
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

[IMAGE_PLACEHOLDER: Screengrab of logs for upserts and vector search results]

### **Key Takeaway**

> The solution integrates Cosmos DB vector search with tool plugins, enabling retrieval‑augmented interactions across ecommerce data.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
