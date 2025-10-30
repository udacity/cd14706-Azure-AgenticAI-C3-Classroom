# Exercise Solution

[VIDEO_PLACEHOLDER: Short-Term Memory for Conversational Context]

### **Solution Walkthrough**

We add a `ShortTermMemory` to persist recent conversation and tool calls, then incorporate that context into the next prompt to improve continuity.

```python
# Add and use conversation context
memory.add_conversation("user", query)
context = memory.get_context_window(max_tokens=1000)

prompt = f"""
{create_customer_service_prompt()}

Previous conversation context:
{context}

Current customer query: {query}
"""
customer_service_function = kernel.add_function(
    function_name="customer_service",
    plugin_name="customer_service",
    prompt=prompt,
)
```

Tool usage is captured in memory to build an e‑commerce context (orders, products) that the agent can reference later.

```python
# Persist tool outcomes (excerpt)
if tool == "order_status":
    memory.add_tool_call("order_status", {"order_id": order_id}, {
        "order_id": order_id,
        "status": "shipped",
        "tracking_number": "TRK789",
        "estimated_delivery": "2024-01-20",
    })
```

We close the loop by appending the assistant’s final response back into memory, keeping the session coherent.

```python
memory.add_conversation("assistant", validated_response.human_readable_response)
```

```
🧠 Memory State: Items, Tokens, Usage%
🛒 Ecommerce Context: Order IDs, Product IDs, Recent queries, Tool calls
```

[IMAGE_PLACEHOLDER: Screengrab of logs showing memory stats and ecommerce context]

### **Key Takeaway**

> The solution introduces short‑term memory and feeds it into prompts to maintain context and improve responses across turns.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
