# Exercise

Integrate a web search plugin, invoke its functions via Semantic Kernel, unwrap `FunctionResult.value`, and combine with internal tools in realistic scenarios.

### **Prerequisites**

* Ability to register and invoke SK plugins and functions

* Basic JSON parsing with Python (`json.loads`)

* Lessons 1–5 completed

### **Instructions**

1. In `create_kernel()`, register the search plugin with `kernel.add_plugin(SearchTools(), "ecommerce_search")`.

2. Implement `test_ecommerce_search(kernel)`:
   - Invoke `product_web_search` with a `KernelArguments(query=..., max_results=...)`.
   - Unwrap `FunctionResult.value`; if it’s a string, parse with `json.loads`.
   - Log `title`, `url`, `snippet` for each item (limit to a few results).

3. Extend `test_ecommerce_search(kernel)` to also invoke `price_comparison_search` and `product_review_search`, following the same unwrapping and logging pattern.

4. Implement `test_ecommerce_search_scenarios(kernel)` with at least:
   - Product research: run a product web search, log a couple of result titles, then check internal inventory and pricing.
   - Price comparison: run price comparison search, log count and a few items, then check internal shipping and inventory.
   - Review analysis: run review search, log a few sources, then compare with internal review aggregation and sentiment.

5. In `main()`, list available search and internal plugins; then run `test_external_apis()` (if present), `test_ecommerce_search_scenarios(kernel)`, and `test_ecommerce_search(kernel)` using `asyncio.run(...)`.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`
