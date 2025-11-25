# Exercise Solution

[VIDEO_PLACEHOLDER: Short-Term Memory for Conversational Context]

### **Solution Walkthrough**

We add a `ShortTermMemory` to persist recent conversation and tool calls, then incorporate that context into the next prompt to improve continuity.

```python
# Add and use conversation context
memory.add_conversation("user", query)
context = memory.get_context_window(max_tokens=1000)

# Create chat history with memory context
chat_history = ChatHistory()
chat_history.add_system_message(f"{create_customer_service_prompt()}\n\nPrevious conversation context:\n{context}")
chat_history.add_user_message(f"Current customer query: {query}")

# Enable automatic tool calling
chat_service = kernel.get_service(type=ChatCompletionClientBase)
execution_settings = kernel.get_prompt_execution_settings_from_service_id(
    service_id=chat_service.service_id
)
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
```

The LLM automatically invokes tools when needed using `FunctionChoiceBehavior.Auto()`. Tool results are captured in memory to build an e‑commerce context (orders, products) that the agent can reference later.

```python
# Extract and store actual tool calls from chat history
for message in result:
    if hasattr(message, 'items'):
        for item in message.items:
            if hasattr(item, 'function_name') and item.function_name:
                tool_name = item.function_name
                tool_args = getattr(item, 'arguments', {})
                tool_result = getattr(item, 'result', None)
                if tool_result:
                    memory.add_tool_call(tool_name, tool_args, tool_result)
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
