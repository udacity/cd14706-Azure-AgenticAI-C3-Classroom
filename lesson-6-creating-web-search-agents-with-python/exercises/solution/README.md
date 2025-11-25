# Exercise Solution: Ecommerce Web Search Agent with Bing

[VIDEO_PLACEHOLDER: Ecommerce Web Search Agent with Bing]

## 🎯 Solution Overview

This solution demonstrates a complete implementation of an ecommerce search agent that integrates Bing Search grounding with Azure AI Agents. All three search functions are fully implemented with production-ready error handling and JSON response formatting.

## ✅ What's Implemented

### 1. Product Web Search (`product_web_search`)
**Purpose:** General product information and ecommerce data search

**Implementation highlights:**
- Uses Azure AI Project client with Bing grounding connection
- Strong JSON formatting prompt to ensure parseable responses
- Returns structured results with title, URL, and snippet
- Thread cleanup after each search

```python
def product_web_search(self, query: str, max_results: int = 5):
    client = AIProjectClient(endpoint=self.project_endpoint, credential=self.cred)
    thread = client.agents.threads.create()

    client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"""Search for product information and ecommerce data: {query}

CRITICAL: You MUST return your response as a valid JSON array ONLY. Do not include any explanation, text, or commentary.
Return ONLY a JSON array in this exact format:
[
  {{"title": "result title", "url": "https://example.com", "snippet": "description"}},
  {{"title": "result title 2", "url": "https://example2.com", "snippet": "description 2"}}
]

Return the JSON array and nothing else."""
    )

    client.agents.runs.create_and_process(thread_id=thread.id, agent_id=self.agent_id)
    # ... extract and parse JSON results ...
```

### 2. Price Comparison Search (`price_comparison_search`)
**Purpose:** Search for price comparison data across multiple retailers

**Key implementation details:**
- **Lines 99-112:** Complete `messages.create()` call with all required parameters
- Custom prompt asking for price comparison across different retailers and marketplaces
- Adjusted JSON format example to show retailer/price information
- Strong JSON formatting instructions prevent prose responses

**Solution to TODO at line 99-103:**
```python
client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"""Search for price comparison for {product_name} across different retailers and marketplaces

CRITICAL: You MUST return your response as a valid JSON array ONLY. Do not include any explanation, text, or commentary.
Return ONLY a JSON array in this exact format:
[
  {{"title": "retailer name - price", "url": "https://example.com", "snippet": "price and availability details"}},
  {{"title": "retailer name 2 - price", "url": "https://example2.com", "snippet": "price and availability details"}}
]

Return the JSON array and nothing else."""
)
```

### 3. Product Review Search (`product_review_search`)
**Purpose:** Search for product reviews, ratings, and customer feedback

**Key implementation details:**
- **Lines 165-178:** Complete `messages.create()` call with all required parameters
- **Critical fix:** Uses natural wording to avoid Bing content policy refusals
- Instead of "Search for reviews and ratings" (which can trigger refusal)
- Uses "Find web articles and pages about [product] reviews and ratings"
- This natural phrasing is treated as a standard web search query

**Solution to TODO at line 156-160:**
```python
client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"""Find web articles and pages about "{product_name} reviews" and "{product_name} ratings". Search for expert reviews, user opinions, and product feedback available online.

CRITICAL: You MUST return your response as a valid JSON array ONLY. Do not include any explanation, text, or commentary.
Return ONLY a JSON array in this exact format:
[
  {{"title": "review source - rating", "url": "https://example.com", "snippet": "review summary and rating"}},
  {{"title": "review source 2 - rating", "url": "https://example2.com", "snippet": "review summary and rating"}}
]

Return the JSON array and nothing else."""
)
```

## 🔧 Critical Fixes Applied

### Fix #1: Stronger JSON Prompt Formatting
**Problem:** Bing was returning prose text instead of JSON arrays
**Solution:** Added "CRITICAL: You MUST return your response as a valid JSON array ONLY" with explicit format examples

**Before:**
```python
content=f"Search for price comparison for {product_name}"
```

**After:**
```python
content=f"""Search for price comparison for {product_name} across different retailers and marketplaces

CRITICAL: You MUST return your response as a valid JSON array ONLY. Do not include any explanation, text, or commentary.
Return ONLY a JSON array in this exact format:
[
  {{"title": "retailer name - price", "url": "https://example.com", "snippet": "price and availability details"}},
  ...
]

Return the JSON array and nothing else."""
```

### Fix #2: Natural Wording for Review Searches
**Problem:** "Search for reviews and ratings" triggered Bing content policy refusal: "I'm sorry, but I cannot assist with that request."
**Solution:** Reworded to sound like a natural web search query

**Before:**
```python
content=f"Search for reviews and ratings for {product_name} from review sites, forums, and ecommerce platforms"
```

**After:**
```python
content=f"""Find web articles and pages about "{product_name} reviews" and "{product_name} ratings". Search for expert reviews, user opinions, and product feedback available online.
```

This phrasing avoids triggering content policies while achieving the same search goal.

### Fix #3: Package Version Compatibility
**Problem:** `azure-ai-projects==2.0.0b2` changed API structure, causing `'AgentsOperations' object has no attribute 'threads'`
**Solution:** Pinned to compatible versions in `requirements.txt`:

```
azure-ai-projects==1.0.0
azure-ai-agents==1.2.0b3
azure-identity
```

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file with your Azure credentials:

```env
# Azure OpenAI Config
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=your-chat-deployment
AZURE_OPENAI_EMBED_DEPLOYMENT=your-embedding-deployment
AZURE_OPENAI_KEY=your-api-key

# Azure AI Project for Bing Grounding
PROJECT_ENDPOINT=https://your-project.openai.azure.com/
AGENT_ID=your-agent-id
BING_CONNECTION_ID=your-bing-grounding-connection-id
```

### 3. Run the Solution

```bash
python main.py
```

**Expected output:**
```
🔎 Testing: Product Web Search
✅ Returned 3 results
   1. Best Wireless Headphones 2024 - Top Picks
   2. Wireless Headphone Buying Guide | Tech Reviews
   3. Premium Wireless Headphones Comparison

💰 Testing: Price Comparison Search
✅ Returned 3 results
   1. Amazon - $349.99 (In Stock)
   2. Best Buy - $359.99 (Available for pickup)
   3. B&H Photo - $349.00 (Free shipping)

⭐ Testing: Product Review Search
✅ Returned 3 results
   1. iPhone 15 Pro Review - 4.5/5 Stars | TechRadar
   2. iPhone 15 Pro: Expert Review and Rating | CNET
   3. User Reviews: iPhone 15 Pro (4.7/5) | Consumer Reports

✅ Ecommerce Web Search Agent testing completed successfully!
```

### 4. Run Simple Test (Optional)

For focused testing of just the search functions:

```bash
python test_search_simple.py
```

## 🧪 Testing All Scenarios

The `main.py` file includes comprehensive tests for:

1. **Product Web Search Test** - General product queries
2. **Price Comparison Test** - Retailer price data
3. **Product Review Test** - Review aggregation
4. **Combined Scenario Tests** - Integration with internal tools:
   - Product research (web search + inventory + pricing)
   - Comparison shopping (price search + recommendations)
   - Customer intelligence (reviews + internal review data)

## 📚 Key Concepts Demonstrated

### 1. Bing Search Grounding
- Azure AI Agents can ground responses with live Bing Search results
- Configured via `BING_CONNECTION_ID` in the agent setup
- Provides real-time, accurate web data

### 2. Prompt Engineering for Structured Output
- Strong formatting instructions ensure JSON responses
- Explicit format examples show the expected structure
- "CRITICAL" prefix emphasizes the importance

### 3. Content Policy Awareness
- Some query phrasings may trigger safety filters
- Reword to sound like natural web searches
- Avoid command-like language; prefer question/search phrasing

### 4. Thread Management
- Create temporary threads for each search
- Always cleanup with `client.agents.threads.delete(thread_id=thread.id)`
- Prevents thread accumulation and resource leaks

### 5. Error Handling
- Check configuration before making requests
- Catch and return friendly error messages
- Log raw responses for debugging (`print(raw_json[:300])`)

## 🔧 Troubleshooting

| Problem | Solution |
|--------|----------|
| `Missing configuration` | Verify all `.env` variables are set |
| `No JSON returned by Agent` | Check Bing grounding connection in Azure AI Project |
| JSON parsing error | Ensure strong formatting prompt is included |
| Bing refuses request | Use natural search query wording ("Find articles about...") |
| `'AgentsOperations' object has no attribute 'threads'` | Use `azure-ai-projects==1.0.0` not 2.0.0b2 |
| Package conflicts | Install exact versions from `requirements.txt` |

## 💡 Best Practices

1. **Always include JSON formatting instructions** - Don't rely on the agent to guess the format
2. **Provide format examples** - Show exactly what structure you expect
3. **Use natural query wording** - Especially for potentially sensitive topics like reviews
4. **Clean up threads** - Delete after use to prevent resource accumulation
5. **Log raw responses during development** - Helps debug JSON parsing issues
6. **Pin package versions** - Azure AI SDKs are evolving; exact versions prevent breakage

## 🎉 Summary

This solution demonstrates:
- ✅ Complete implementation of all three search functions
- ✅ Production-ready error handling
- ✅ Strong JSON formatting prompts
- ✅ Natural query wording to avoid content policy issues
- ✅ Proper thread lifecycle management
- ✅ Integration with Semantic Kernel plugins
- ✅ Real-world ecommerce scenarios

The key learnings are:
1. **Prompt engineering matters** - Strong formatting instructions are essential for reliable JSON responses
2. **Wording matters** - Natural search phrasing avoids content policy triggers
3. **Version pinning matters** - Azure AI SDKs require specific version combinations

---

**Next Steps:**
- Integrate these search functions into larger agent workflows
- Add result caching for frequently searched items
- Implement semantic reranking of search results
- Combine with internal tools for comprehensive product intelligence
