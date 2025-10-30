# Exercise Solution

[VIDEO_PLACEHOLDER: Validated Structured Outputs with Pydantic]

### **Solution Walkthrough**

We add a prompt that instructs the model to return strict JSON and then validate the LLM output with Pydantic. This ensures downstream code can rely on a typed shape.

```python
# Create prompt to require strict JSON with schemas
prompt = f"""{create_customer_service_prompt()}\n\nCustomer query: {query}"""
customer_service_function = kernel.add_function(
    function_name="customer_service",
    plugin_name="customer_service",
    prompt=prompt,
)
result = await kernel.invoke(customer_service_function)
response_text = str(result)
```

We then parse the JSON substring and validate it against Pydantic models. Only the response structure and typed `structured_data` are checked; invalid JSON raises a clear error.

```python
# Parse and validate
json_start = response_text.find('{')
json_end = response_text.rfind('}') + 1
json_str = response_text[json_start:json_end]
response_data = json.loads(json_str)

customer_response = CustomerServiceResponse(**response_data)
if customer_response.structured_data:
    if query_type == "order_status":
        OrderResponse(**customer_response.structured_data)
    elif query_type == "product_info":
        ProductResponse(**customer_response.structured_data)
```

After invoking a few demo queries, we log the validated results for quick inspection.

```
🎉 All Pydantic validation passed!
```

[IMAGE_PLACEHOLDER: Screengrab of console showing human-readable response and JSON block]

### **Key Takeaway**

> The solution constrains LLM outputs to a schema and guarantees correctness with Pydantic validation.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
