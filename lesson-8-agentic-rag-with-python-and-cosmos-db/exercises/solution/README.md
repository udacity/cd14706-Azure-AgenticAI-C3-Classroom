# Exercise Solution

[VIDEO_PLACEHOLDER: Agentic RAG with Cosmos DB]

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

Quality is judged via an LLM function that returns a JSON payload we parse and trust only if it’s valid JSON; otherwise we fall back safely.

```python
assessment_function = self.kernel.add_function(
    function_name="assess_retrieval_quality",
    plugin_name="rag_assessment",
    prompt=assessment_prompt,
)
assessment_text = str(await self.kernel.invoke(assessment_function))
json_str = assessment_text[assessment_text.find('{'):assessment_text.rfind('}')+1]
assessment = json.loads(json_str) if json_str else {"confidence": 0.5, ...}
```

We then synthesize an answer from the retrieved snippets, citing context where relevant.

```python
context = "\n\n".join(
    f"Document {i+1} (ID: {d.get('id','unknown')}):\n{d.get('text','')}" for i, d in enumerate(retrieved_docs)
)
answer_function = self.kernel.add_function(
    function_name="generate_answer",
    plugin_name="rag_answer",
    prompt=answer_prompt,
)
answer = str(await self.kernel.invoke(answer_function)).strip()
```

```
🔄 Retrieval attempts and confidence are logged for each query
```

[IMAGE_PLACEHOLDER: Screengrab of logs showing retrieval attempts, confidence, and sources]

### **Key Takeaway**

> The solution adds an agentic RAG loop that assesses retrieval quality, refines queries as needed, and then generates grounded answers.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
