# Exercise Solution - Agentic RAG with E-commerce Data

[VIDEO_PLACEHOLDER: Agentic RAG with Cosmos DB]

## **Data Setup**

This exercise uses e-commerce data. You have two options:

**Option 1: Shared Container (Simpler)**
- Use your existing `sports_docs` container from previous lessons
- Ecommerce data will be stored with `pk="ecommerce"` for organization
- No `.env` changes needed

**Option 2: Separate Container (Recommended for Isolation)**
- Create a dedicated container for ecommerce data
- Update `.env`: `COSMOS_CONTAINER=ecommerce-container`
- Better isolation and cleaner testing

Most students can use **Option 1** (shared container).

---

### **Solution Walkthrough**

We implement an autonomous RAG agent that evaluates retrieval quality and refines the query before answering. The loop attempts retrieval up to a threshold.

```python
# Retrieval loop with quality assessment (excerpt)
for attempt in range(self.max_retrieval_attempts):
    retrieved_docs = await retrieve(query, k=5)
    qa = await self._assess_retrieval_quality(query, retrieved_docs)
    if qa["confidence"] >= self.confidence_threshold:
        break
    query = await self._refine_query(query, retrieved_docs, qa["issues"])
```

Quality is judged via an LLM call that returns a JSON payload we parse and trust only if it's valid JSON; otherwise we fall back safely.

```python
# Use ChatCompletionService directly
chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
chat_history = ChatHistory()
chat_history.add_user_message(assessment_prompt)

settings = OpenAIChatPromptExecutionSettings(temperature=0.1, max_tokens=500)
response = await chat_service.get_chat_message_contents(
    chat_history=chat_history,
    settings=settings,
    kernel=self.kernel
)
assessment_text = response[0].content.strip()

# Parse JSON response
json_start = assessment_text.find('{')
json_end = assessment_text.rfind('}') + 1
if json_start != -1 and json_end > json_start:
    json_str = assessment_text[json_start:json_end]
    assessment = json.loads(json_str)
else:
    assessment = {"confidence": 0.5, "reasoning": "Unable to assess", "issues": []}
```

We then synthesize an answer from the retrieved snippets, citing context where relevant.

```python
# Prepare context from retrieved documents
context = "\n\n".join([
    f"Document {i+1} (ID: {doc.get('id', 'unknown')}):\n{doc.get('text', '')}"
    for i, doc in enumerate(retrieved_docs)
])

# Generate answer using ChatCompletionService
chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
chat_history = ChatHistory()
chat_history.add_user_message(answer_prompt)

settings = OpenAIChatPromptExecutionSettings(temperature=0.7, max_tokens=1000)
response = await chat_service.get_chat_message_contents(
    chat_history=chat_history,
    settings=settings,
    kernel=self.kernel
)
answer = response[0].content.strip()
```

```
🔄 Retrieval attempts and confidence are logged for each query
```

[IMAGE_PLACEHOLDER: Screengrab of logs showing retrieval attempts, confidence, and sources]

### **Key Takeaway**

> The solution adds an agentic RAG loop that assesses retrieval quality, refines queries as needed, and then generates grounded answers.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
