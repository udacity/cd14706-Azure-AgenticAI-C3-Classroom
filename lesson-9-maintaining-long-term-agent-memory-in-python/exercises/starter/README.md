# Exercise

Implement an AssistantAgent that uses long-term memory to provide contextual, personalized responses.

### **Prerequisites**

* Comfortable with async Python and class design
* Familiarity with Semantic Kernel's ChatCompletionService
* Lessons 1–8 completed (especially Lesson 8's agentic RAG patterns)

### **Instructions**

This exercise focuses on implementing the core logic of the `AssistantAgent`'s `chat` method in `main.py` and the database interaction in `long_term_memory/core.py`.

#### **Part 1: Implement Core Memory Operations (`long_term_memory/core.py`)**

1.  **In `add_memory()`:**
    *   Implement the logic to add the `item` to Cosmos DB.
    *   **Hint:** Use `self._container.upsert_item(item.to_dict())`.

2.  **In `get_memory()`:**
    *   Implement the logic to retrieve a memory item from Cosmos DB.
    *   **Hint:** Use `self._container.read_item(item=memory_id, partition_key=session_id)`.

#### **Part 2: Implement the Agent's Chat Logic (`main.py`)**

Your task is to complete the four `TODO`s within the `AssistantAgent`'s `chat` method. The setup and helper functions have been pre-implemented for you.

1.  **TODO 1: Retrieve Relevant Memories**
    *   Call `self.memory.search_memories()` to find memories relevant to the user's query.

2.  **TODO 2: Get the Agent's Response**
    *   Call `chat_service.get_chat_message_contents()` to get the contextual answer from the LLM. Remember to extract the `content` from the response.

3.  **TODO 3: Store the User's Query**
    *   Call `self.memory.add_memory()` to save the user's query to long-term memory.

4.  **TODO 4: Store the Agent's Response**
    *   Call `self.memory.add_memory()` to save the agent's response to long-term memory.

#### **Part 3: Test Your Implementation**
*   Once the `chat` method is complete, uncomment the "Assistant Agent with Memory" section in the `run_demo()` function to test your agent.

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
