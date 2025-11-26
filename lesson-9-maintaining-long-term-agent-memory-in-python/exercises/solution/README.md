# Exercise Solution

[VIDEO_PLACEHOLDER: Long‑Term Memory with Pruning and Reordering]

This solution demonstrates two key components: memory infrastructure operations and an AssistantAgent that leverages long-term memory for contextual conversations.

---

## **Part 1: Memory Infrastructure Operations**

We instantiate `LongTermMemory` with limits and scoring, then seed multi‑session memories to showcase search, stats, pruning, and reordering (as shown in video).

```python
# Initialize and seed
ltm = LongTermMemory(max_memories=15, importance_threshold=0.3, enable_ai_scoring=True)
await seed_sample_memories(ltm)
```

We run targeted operations: search and importance updates, statistics, multiple pruning strategies, and reordering per session.

```python
# Search & update
customer = ltm.search_memories("customer_session_001", query="order", limit=5)
if customer:
    ltm.update_memory_importance(customer[0].id, customer[0].session_id, 0.95)

# Prune & reorder
ltm.prune_memories(strategy='importance')
ltm.prune_memories(strategy='hybrid')
ltm.reorder_memories('customer_session_001', 'importance')
```

Finally, we run full optimization which uses AI‑assisted scoring plus heuristics.

```
🚀 Optimize (AI + heuristics)
Optimization results: {'pruned': 0, 'reordered': 15, 'archived': 0, ...}
```

---

## **Part 2: AssistantAgent with Memory**

The `AssistantAgent` class demonstrates how an agent uses long-term memory to provide contextual responses.

### **Initialization**

```python
class AssistantAgent:
    def __init__(self, session_id: str = "assistant_session_default"):
        self.session_id = session_id
        self.memory = LongTermMemory(
            max_memories=1000,
            importance_threshold=0.3,
            enable_ai_scoring=True
        )
        self.kernel = get_openai_kernel()
```

### **Memory-Enhanced Chat**

The `chat` method retrieves relevant memories before responding:

```python
async def chat(self, query: str) -> str:
    # Step 1: Retrieve relevant memories
    memories = self.memory.search_memories(
        self.session_id,
        query=query,
        min_importance=0.0,
        limit=5
    )

    # Step 2: Build memory context
    memory_context = ""
    if memories:
        memory_context = "\n\nRelevant past conversations:\n"
        for mem in memories:
            memory_context += f"- {mem.content} (importance: {mem.importance_score:.2f})\n"
```

### **LLM Invocation with Context**

```python
    # Step 3: Create prompt with memory
    prompt = f"""You are a helpful assistant...
{memory_context}
User query: {query}
"""

    # Step 4: Get LLM response using ChatCompletionService
    chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
    chat_history = ChatHistory()
    chat_history.add_user_message(prompt)

    settings = OpenAIChatPromptExecutionSettings(
        temperature=0.7,
        max_tokens=1000
    )

    response_obj = await chat_service.get_chat_message_contents(
        chat_history=chat_history,
        settings=settings,
        kernel=self.kernel
    )
    response = response_obj[0].content.strip()
```

### **Storing Conversations**

```python
    # Step 5: Store conversation as memories
    await self.memory.add_memory(
        self.session_id,
        f"User asked: {query}",
        "conversation",
        importance_score=0.7,
        tags=self._extract_tags(query)
    )

    await self.memory.add_memory(
        self.session_id,
        f"Agent responded: {response}",
        "conversation",
        importance_score=0.6,
        tags=self._extract_tags(response)
    )

    return response
```

### **Tag Extraction**

```python
def _extract_tags(self, text: str) -> list:
    text_lower = text.lower()
    tags = []

    keywords = ["order", "product", "customer", "ORD-", "PROD-",
                "shipping", "tracking", "inventory", "stock", "price",
                "review", "rating", "delivery", "item", "purchase"]
    for keyword in keywords:
        if keyword in text_lower:
            tags.append(keyword)

    return tags if tags else ["customer"]
```

---

## **Conversation Demo Output**

```
Assistant Agent with Memory - Conversation Demo
================================================================================

--- User Query 1: What's the status of my order ORD-12345? ---
Retrieving relevant memories for query: What's the status of my order ORD-12345?
Found 2 relevant memories
Invoking LLM with memory context...
Agent: Your order ORD-12345 has been shipped. The tracking number for your shipment is TRK789.
       It was shipped on November 20, 2025, and the expected delivery date is November 27, 2025.
Session memories: 5

--- User Query 2: Tell me about product PROD-67890 ---
Retrieving relevant memories for query: Tell me about product PROD-67890
Found 1 relevant memories
Agent: I'm sorry, but I don't have any specific information about product PROD-67890 in the
       past conversations from this session.
Session memories: 7

--- User Query 3: Do you have any information about my recent orders? ---
Retrieving relevant memories for query: Do you have any information about my recent orders?
Found 3 relevant memories
Agent: Yes, I have information about one of your recent orders. Your order with the ID ORD-12345
       has been shipped. The tracking number for your shipment is TRK789, and it was shipped on
       November 20, 2025. The expected delivery date is November 27, 2025.
Session memories: 9
```

[IMAGE_PLACEHOLDER: Screengrab showing memory retrieval, LLM invocation, and session memory growth]

---

## **Key Takeaways**

1. **Memory Infrastructure**: Search, prune, reorder, and optimize memories efficiently
2. **Contextual Agent**: Retrieve relevant memories before responding to provide personalized answers
3. **Memory Storage**: Store conversations for future reference, enabling continuity across sessions
4. **Tag Organization**: Extract keywords to organize and retrieve memories effectively

> The solution demonstrates complete long-term memory management with an agent that uses memory to provide context-aware, personalized responses.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
