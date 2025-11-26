# Exercise

Implement an AssistantAgent that uses long-term memory to provide contextual, personalized responses.

### **Prerequisites**

* Comfortable with async Python and class design
* Familiarity with Semantic Kernel's ChatCompletionService
* Lessons 1–8 completed (especially Lesson 8's agentic RAG patterns)

### **Instructions**

This exercise has two parts:

#### **Part 1: Memory Infrastructure (Already Implemented)**

The memory infrastructure operations are already complete:
- Seeding sample memories
- Searching and filtering memories
- Updating memory importance
- Pruning strategies (importance-based and hybrid)
- Memory reordering
- AI-powered optimization

Run the code to see Part 1 working.

#### **Part 2: Implement AssistantAgent (Your Task)**

**Step 1: Implement `__init__` method**
- Store the session_id
- Create a LongTermMemory instance (max_memories=1000, importance_threshold=0.3, enable_ai_scoring=True)
- Get the OpenAI kernel using `get_openai_kernel()`
- Log a warning if kernel is None

**Step 2: Implement `chat` method**

The chat method should:
1. Check if kernel is available (return error message if not)
2. Retrieve relevant memories using `self.memory.search_memories()`
   - Use session_id, query, min_importance=0.0, limit=5
3. Build a memory context string from retrieved memories
   - Format: `"\n\nRelevant past conversations:\n- {content} (importance: {score:.2f})\n"`
4. Create a prompt that includes:
   - System role ("You are a helpful assistant...")
   - Memory context
   - User query
   - Instructions to reference past conversations
5. Get LLM response using ChatCompletionService:
   - `chat_service = self.kernel.get_service(type=ChatCompletionClientBase)`
   - Create ChatHistory and add prompt
   - Use OpenAIChatPromptExecutionSettings (temperature=0.7, max_tokens=1000)
   - Call `get_chat_message_contents()`
6. Store the conversation as memories:
   - User query: memory_type="conversation", importance=0.7
   - Agent response: memory_type="conversation", importance=0.6
   - Use `self._extract_tags()` for tags
7. Return the response

**Step 3: Implement `_extract_tags` method**
- Convert text to lowercase
- Check for keywords: "order", "product", "customer", "ORD-", "PROD-", "shipping", "tracking", "inventory", "stock", "price", "review", "rating", "delivery", "item", "purchase"
- Return found keywords, or ["customer"] if none found

**Step 4: Test Your Implementation**
- Uncomment the Part 2 demo code in `run_demo()`
- Run the code and verify:
  - Query 1: No memories found → generic response
  - Query 2: Memories starting to accumulate
  - Query 3: Agent references past conversations
  - Session memories grow: 2 → 4 → 6

### **Expected Behavior**

When complete, you should see:
```
Assistant Agent with Memory - Conversation Demo
--- User Query 1: What's the status of my order ORD-12345? ---
No relevant memories found
Agent: [Response without memory context]
Session memories: 2

--- User Query 2: Tell me about product PROD-67890 ---
Found X relevant memories
Agent: [Response with memory context]
Session memories: 4

--- User Query 3: Do you have any information about my recent orders? ---
Found Y relevant memories
Agent: [Response referencing past conversations]
Session memories: 6
```

### **Hints**

- Look at Lesson 8's agentic RAG for ChatCompletionService usage patterns
- Memory retrieval is similar to vector search in previous lessons
- The memory infrastructure (Part 1) shows how to use `LongTermMemory` methods
- Check the solution README for code examples if you get stuck

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`
