# Exercise Solution

[VIDEO_PLACEHOLDER: Integrating External APIs with Semantic Kernel]

### **Solution Walkthrough**

We expand the kernel by registering multiple external API plugins so the agent can pull real‑time data across inventory, shipping, pricing, recommendations, and reviews.

```python
# Register external API tools
kernel.add_plugin(InventoryTools(), "inventory")
kernel.add_plugin(ShippingTools(), "shipping")
kernel.add_plugin(PricingTools(), "pricing")
kernel.add_plugin(RecommendationTools(), "recommendations")
kernel.add_plugin(ReviewTools(), "reviews")
```

The solution adds explicit test routines to exercise each API and log key fields. These are narrow, inspectable checks rather than end‑to‑end flows.

```python
# Example: Shipping rate calculation (excerpt)
shipping_result = shipping_tools.calculate_shipping("10001", "90210", 2.5, "12x8x4", "ground")
cheapest = shipping_result.get('shipping_calculation', {}).get('cheapest_option', {})
if cheapest:
    logger.info(f"Cheapest: {cheapest.get('service_name')} - ${cheapest.get('cost')}")
```

We also include realistic integration scenarios (product research, order processing, customer support) that combine multiple APIs and summarize outcomes.

```python
# Scenario: Product research (excerpt)
inventory = inventory_tools.check_inventory(product_id)
pricing = pricing_tools.get_market_pricing("Wireless Headphones")
reviews = review_tools.get_product_reviews(product_id, limit=3)
recommendations = recommendation_tools.get_product_recommendations(product_id=product_id, limit=2)
```

```
✅ External API Integration Testing completed successfully!
```

[IMAGE_PLACEHOLDER: Screengrab of logs showing inventory/pricing/reviews summaries]

### **Key Takeaway**

> The solution registers multiple external API plugins and adds focused tests plus scenarios to validate real‑time data flows end‑to‑end.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
