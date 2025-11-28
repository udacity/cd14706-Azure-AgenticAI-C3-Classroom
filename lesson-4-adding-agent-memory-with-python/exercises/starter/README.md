# Exercise

Add short-term memory to capture recent conversation and tool calls, and use that memory to provide context to subsequent prompts.

### **Prerequisites**

* Ability to modify prompts and add functions in Semantic Kernel

* Understanding of basic data structures for in-memory storage

* Lessons 1–3 completed (kernel, validation, state patterns)

### **Instructions**

**NOTE:** The main.py file already has automatic tool invocation (from Lesson 2) and memory integration fully implemented. Your task is to complete the `ShortTermMemory` class in `memory.py` only.

#### Complete the `ShortTermMemory` class in `memory.py`:

1. **In the `add_conversation()` method:**
   - Complete the `item` dictionary with: `role`, `content`, `timestamp`, `tokens`, and `metadata` fields.
   - Use `datetime.now().isoformat()` for timestamp.
   - Use `self._estimate_tokens(content)` for token count.
   - Ensure metadata uses the provided parameter or defaults to an empty dict.
   - After creating the `item`, append it to `self.memory_items`.

2. **In the `add_tool_call()` method:**
   - Complete the `metadata` dictionary with: `type`, `tool_name`, `input`, `output`, and `success` fields.
   - Set `type` to `'tool_call'`.
   - Use the function parameters for the other fields.

#### What's Already Implemented:

- ✅ Kernel setup with Azure OpenAI (from Lesson 1)
- ✅ Automatic tool invocation with `FunctionChoiceBehavior.Auto()` (from Lesson 2)
- ✅ Pydantic validation (from Lesson 2)
- ✅ Memory integration into main agent flow
- ✅ All helper methods in `ShortTermMemory`: `get_context_window()`, `get_memory_summary()`, `get_customer_context()`, etc.

#### Testing Your Implementation:

Run `python main.py` to test your memory implementation. The agent will:
- Process customer queries with automatic tool calling
- Store conversations and tool calls in your `ShortTermMemory`
- Display memory statistics, ecommerce context, and conversation history

#### Success Criteria:

When you run the exercise, you should see:
```
🧠 Memory State:
   Items: 4
   Tokens: 156
   Usage: 40.0%
🛒 Ecommerce Context:
   Order IDs: ['ORD-001']
   Product IDs: ['PROD-001']
   Tool calls: 2
```

This confirms that:
- Conversations are being stored in memory
- Tool calls are being tracked
- Memory statistics are calculated correctly
- Context is being extracted from conversations

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`