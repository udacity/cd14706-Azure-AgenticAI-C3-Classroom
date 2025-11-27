# Exercise

Build an Agentic RAG system that autonomously evaluates retrieval quality and refines queries.

## **Data Setup**

This exercise uses e-commerce data (policies and products). You have two options:

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

## **Learning Objectives**

By completing this exercise, you will:

1. **Implement agentic retrieval** - Build a RAG agent that makes autonomous decisions
2. **Quality assessment** - Use LLM to evaluate retrieval quality with confidence scoring
3. **Query refinement** - Automatically improve queries based on retrieval issues
4. **Multi-attempt retrieval** - Implement retry logic with refined queries
5. **Answer synthesis** - Generate grounded answers citing retrieved documents

---

## **Prerequisites**

* Completed Lessons 1-7
* Familiarity with async Python
* Understanding of RAG concepts from Lesson 7
* Azure Cosmos DB with vector search enabled
* Azure OpenAI deployed models (chat + embedding)

---

## **Instructions**

### **Part 1: Data Ingestion**

Run the ingestion script to populate your Cosmos DB:

```bash
python rag/ingest.py
```

This creates:
- Policy documents (shipping-info, return-policy, warranty-info)
- Product catalog (wireless headphones, gaming laptop, smart watch, etc.)

### **Part 2: Implement AgenticRAG Class**

The `AgenticRAG` class in `main.py` has TODO markers for you to implement:

#### **TODO 1: Implement `_assess_retrieval_quality` method**

**Goal**: Use LLM to evaluate if retrieved documents answer the query well.

**Steps**:
1. Create an assessment prompt asking the LLM to evaluate retrieval quality
2. Use ChatCompletionService to get LLM assessment
3. Parse JSON response with fields: `confidence` (0.0-1.0), `reasoning`, `issues`
4. Handle JSON parsing errors gracefully with fallback

**Hint**: Look at the solution README for the ChatCompletionService pattern.

#### **TODO 2: Implement `_refine_query` method**

**Goal**: Use LLM to improve the query based on retrieval issues.

**Steps**:
1. Create a refinement prompt with original query, retrieved docs, and issues
2. Use ChatCompletionService to get refined query
3. Extract refined query from LLM response
4. Fall back to original query if refinement fails

**Hint**: The refined query should be more specific or use different keywords.

#### **TODO 3: Implement the agentic retrieval loop in `answer` method**

**Goal**: Retrieve documents with quality assessment and retry logic.

**Steps**:
1. Loop up to `max_retrieval_attempts` (default 3)
2. Retrieve documents using `retrieve()` function
3. Assess retrieval quality using `_assess_retrieval_quality()`
4. If confidence >= threshold, break the loop
5. Otherwise, refine query and try again
6. After loop, use best retrieved docs for answer synthesis

**Hint**: Track confidence scores to use the best retrieval attempt.

#### **TODO 4: Implement answer synthesis**

**Goal**: Generate answer using retrieved documents as context.

**Steps**:
1. Build context string from retrieved documents (with document IDs)
2. Create answer prompt with context and user query
3. Use ChatCompletionService to generate answer
4. Return formatted response with answer, confidence, and reasoning

---

## **Testing Your Implementation**

Run the exercise code:

```bash
python main.py
```

### **Expected Behavior**

The demo will test 5 queries with different retrieval characteristics:

**High-confidence queries (1-2 attempts)**:
```
Query: "Tell me about shipping policies and return policies"
✅ Confidence: 0.90 (1 attempt)
Answer: [Well-grounded answer citing policy documents]
```

**Medium-confidence queries (2-3 attempts)**:
```
Query: "Show me wireless headphones and their prices"
⚠️ Confidence: 0.40 (3 attempts - demonstrates retry logic)
Answer: [Answer based on best retrieval attempt]
```

**What to look for**:
- Query refinement happening when confidence is low
- Multiple retrieval attempts for difficult queries
- Confidence scores reflecting retrieval quality
- Answers citing specific document IDs

---

## **Key Concepts**

### **Agentic Behavior**

The agent makes autonomous decisions:
- **When to retry**: Based on confidence threshold (0.7)
- **How to refine**: Uses LLM to analyze issues and improve query
- **When to stop**: After max attempts or sufficient confidence

### **Quality Assessment**

LLM evaluates retrieval using:
- **Relevance**: Do documents address the query?
- **Completeness**: Is enough information present?
- **Specificity**: Are documents specific enough?

Returns structured assessment:
```json
{
  "confidence": 0.85,
  "reasoning": "Documents directly address shipping and return policies",
  "issues": []
}
```

### **Query Refinement**

When retrieval quality is poor, LLM refines the query:
- Original: "Show me headphones"
- Refined: "Show me wireless headphones with price and specifications"

---

## **Common Challenges**

1. **JSON Parsing Errors**: LLM might return malformed JSON
   - **Solution**: Implement robust parsing with fallback values

2. **Infinite Loops**: Query refinement doesn't improve results
   - **Solution**: Use `max_retrieval_attempts` limit

3. **Poor Vector Search**: Product queries return policy docs
   - **Solution**: This is expected! Demonstrates why agentic retry is valuable

4. **Empty Retrievals**: No documents found
   - **Solution**: Check that ingest.py ran successfully

---

## **Hints**

- Reference the solution README for ChatCompletionService code patterns
- Use `temperature=0.1` for quality assessment (more deterministic)
- Use `temperature=0.7` for answer synthesis (more creative)
- Log confidence scores to debug retrieval quality
- Start with policy queries (they work better than product queries)

---

## **Success Criteria**

Your implementation is complete when:

✅ Quality assessment returns confidence scores
✅ Query refinement generates improved queries
✅ Retrieval loop attempts multiple times for low-confidence results
✅ Answer synthesis cites retrieved documents
✅ Demo runs without errors for all 5 test queries

---

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`
