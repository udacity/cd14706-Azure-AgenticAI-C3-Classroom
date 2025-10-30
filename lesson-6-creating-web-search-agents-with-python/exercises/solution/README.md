# Exercise Solution

[VIDEO_PLACEHOLDER: Ecommerce Web Search Agent with Bing]

### **Solution Walkthrough**

We register a search plugin and add targeted tests that call specific search functions and unwrap results from `FunctionResult.value`.

```python
# Register search tools
kernel.add_plugin(SearchTools(), "ecommerce_search")

# Invoke product web search (excerpt)
search_func = kernel.plugins["ecommerce_search"].functions["product_web_search"]
args = KernelArguments(query="wireless headphones best 2024", max_results=3)
result = await kernel.invoke(search_func, args)
items = json.loads(result.value) if isinstance(result.value, str) else result.value
```

We extend this to price comparison and review searches, then log title/URL/snippet for quick verification.

```python
# Price comparison (excerpt)
price_func = kernel.plugins["ecommerce_search"].functions["price_comparison_search"]
price_args = KernelArguments(product_name="Sony WH-1000XM5", max_results=3)
price_result = await kernel.invoke(price_func, price_args)
```

Finally, we combine search with internal tools (inventory, shipping, pricing, reviews, recommendations) in realistic scenarios to show how web and internal data complement each other.

```python
# Scenario: Product research with web search (excerpt)
search_args = KernelArguments(query=f"{product_name} specifications features", max_results=3)
search_result = await kernel.invoke(search_func, search_args)
search_data = json.loads(search_result.value) if isinstance(search_result.value, str) else search_result.value
inventory = inventory_tools.check_inventory("PROD-001")
pricing = pricing_tools.get_market_pricing("Wireless Headphones")
```

```
✅ Ecommerce Web Search Agent testing completed successfully!
```

[IMAGE_PLACEHOLDER: Screengrab of logs showing product search, price comparison, and review results]

### **Key Takeaway**

> The solution integrates Bing‑backed search as a plugin and demonstrates practical ecommerce flows by combining web results with internal APIs.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
