# Exercise

Register multiple external API tool plugins and add focused test routines and scenarios to validate real‑time integrations.

### **Prerequisites**

* Ability to register plugins in Semantic Kernel

* Comfort reading and logging nested dict responses

* Lessons 1–3 completed; Lesson 4 optional

### **Instructions**

1. In `create_kernel()`, register the external tools by adding:
   - `kernel.add_plugin(InventoryTools(), "inventory")`
   - `kernel.add_plugin(ShippingTools(), "shipping")`
   - `kernel.add_plugin(PricingTools(), "pricing")`
   - `kernel.add_plugin(RecommendationTools(), "recommendations")`
   - `kernel.add_plugin(ReviewTools(), "reviews")`

2. Create `test_external_apis()` that calls each tool with sample inputs and logs key fields from the returned dicts (e.g., totals, cheapest shipping option, avg price, review counts, sentiment summary).

3. Create `test_api_integration_scenarios()` and implement three scenarios:
   - Product Research: inventory check → market pricing → reviews → recommendations (log concise summaries).
   - Order Processing: multi‑item inventory check → shipping options → delivery estimate.
   - Customer Support: reviews and sentiment for issues → competitor comparison.

4. In `main()`, after listing available plugins, invoke both `test_external_apis()` and `test_api_integration_scenarios()` with `asyncio.run(...)`.

5. Keep structured validation from prior lessons if present; this exercise focuses on tool registration and integration tests rather than state management.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`