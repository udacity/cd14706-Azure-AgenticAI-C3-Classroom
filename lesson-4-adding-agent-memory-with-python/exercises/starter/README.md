# Exercise

Add short‑term memory to capture recent conversation and tool calls, and use that memory to provide context to subsequent prompts.

### **Prerequisites**

* Ability to modify prompts and add functions in Semantic Kernel

* Understanding of basic data structures for in‑memory storage

* Lessons 1–3 completed (kernel, validation, state patterns)

### **Instructions**

1. Create or import `ShortTermMemory` that can store conversation turns and tool calls, and expose helpers like `add_conversation`, `add_tool_call`, `get_context_window`, `get_memory_summary`, and `get_customer_context`.

2. In `process_customer_query_with_memory(...)`, call `memory.add_conversation("user", query)` before invoking the model.

3. Retrieve prior context with `context = memory.get_context_window(max_tokens=1000)` and embed it into the customer service prompt as a dedicated "Previous conversation context" section.

4. Create a SK function from that prompt and invoke it to get `response_text`; validate as in Lesson 2 to produce `validated_response`.

5. Append the assistant’s natural‑language response to memory using `memory.add_conversation("assistant", validated_response.human_readable_response)`.

6. If the response indicates specific tool usage, record representative tool calls and their results with `memory.add_tool_call(tool_name, args_dict, result_dict)`.

7. In `run_memory_demo(...)`, for each input turn, log the agent response, current memory summary (`total_items`, `total_tokens`, `memory_usage_percent`), ecommerce context (`order_ids`, `product_ids`, `recent_queries`, `tool_calls`), and at the end print a short context window and a search result sample.

8. Keep the kernel and Pydantic validation from prior lessons; only augment the flow with memory collection and context injection.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`