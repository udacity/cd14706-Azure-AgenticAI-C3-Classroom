# Exercise: Ecommerce Web Search Agent with Bing

[VIDEO_PLACEHOLDER: Ecommerce Web Search Agent with Bing]

## 🎯 Exercise Objective

In this exercise, you'll complete an ecommerce search agent by implementing two missing search functions. You'll learn how to:

- Integrate Bing Search grounding with Azure AI Agents
- Format search queries and prompts for reliable JSON responses
- Handle different types of product searches (price comparison and reviews)
- Combine web search with Semantic Kernel plugins

## 📋 What You'll Build

You'll complete a `SearchTools` class with three search functions:

1. **product_web_search** - Already implemented as a reference example
2. **price_comparison_search** - TODO: You need to implement this
3. **product_review_search** - TODO: You need to implement this

## ✅ Prerequisites

- Python 3.8 or higher
- Azure OpenAI Service deployment
- Azure AI Project with Bing Search grounding agent configured
- Azure identity authentication (via `DefaultAzureCredential`)

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important:** This exercise requires specific package versions:
```
azure-ai-projects==1.0.0
azure-ai-agents==1.2.0b3
azure-identity
```

### 2. Create `.env` File

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

## 📝 Exercise Instructions

### Step 1: Review the Working Example

Open `tools/search.py` and examine the `product_web_search` function. This is a complete, working implementation that shows the pattern you'll follow.

Key elements to notice:
```python
# 1. Create AI Project client and thread
client = AIProjectClient(endpoint=self.project_endpoint, credential=self.cred)
thread = client.agents.threads.create()

# 2. Create message with search query and JSON formatting instructions
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

# 3. Process the agent run
client.agents.runs.create_and_process(thread_id=thread.id, agent_id=self.agent_id)

# 4. Extract results and parse JSON
messages = list(client.agents.messages.list(thread_id=thread.id))
# ... extract raw_json from assistant messages ...
results = json.loads(raw_json)
```

### Step 2: Implement Price Comparison Search

In `tools/search.py`, find the `price_comparison_search` function. You'll see a TODO comment:

```python
client.agents.messages.create(
    # TODO: Fill in the missing parameters to search for price comparison for {product_name} across different retailers and marketplaces
    # Hint: You need thread_id, role, and content parameters
    # The content should ask Bing to search for price comparison data and return results as JSON
)
```

**Your task:** Fill in the `messages.create()` call following the pattern from `product_web_search`.

**Hints:**
- Use `thread_id=thread.id` and `role="user"`
- In the content, ask Bing to search for price comparison for the product across retailers
- Include the CRITICAL JSON formatting instructions (copy from the working example)
- Adjust the JSON format example to show retailer/price information

### Step 3: Implement Product Review Search

In `tools/search.py`, find the `product_review_search` function. You'll see another TODO:

```python
client.agents.messages.create(
    # TODO: Fill in the missing parameters to search for reviews and ratings for {product_name} from review sites, forums, and ecommerce platforms
    # Hint: You need thread_id, role, and content parameters
    # The content should ask Bing to search for product reviews and return results as JSON
)
```

**Your task:** Fill in the `messages.create()` call for review searches.

**Important tip:** Word your search query naturally, like "Find web articles and pages about [product] reviews and ratings". This helps avoid content policy issues with the Bing grounding service.

### Step 4: Test Your Implementation

Run the main test file:

```bash
python main.py
```

You should see output for all three search functions, indicating that your implemented search functions are correctly integrated and returning results.


## 🧪 Testing Your Implementation

Run the exercise:
```bash
python main.py
```

You should see output showing:
- Product Web Search results
- Price Comparison Search results
- Product Review Search results
- Confirmation that the Ecommerce Web Search Agent testing completed successfully!

You can also run the simple test:

```bash
python test_search_simple.py
```


## 🔧 Troubleshooting

| Problem | Solution |
|--------|----------|
| `Missing configuration` | Verify all `.env` variables are set |
| `No JSON returned by Agent` | Check Bing grounding connection in Azure AI Project |
| JSON parsing error | Ensure your prompt includes the CRITICAL JSON formatting instructions |
| Bing refuses request | Reword your search query to sound more natural (e.g., "Find articles about...") |
| `'AgentsOperations' object has no attribute 'threads'` | Verify `azure-ai-projects==1.0.0` is installed |

## 💡 Key Concepts

1. **Bing Grounding** - Azure AI Agents can use Bing Search as a grounding source for real-time web data
2. **Prompt Engineering for JSON** - Strong formatting instructions ensure consistent, parseable responses
3. **Natural Query Wording** - Some queries may trigger content policies; reword them to sound like natural web searches
4. **Thread Cleanup** - Always delete threads after use with `client.agents.threads.delete(thread_id=thread.id)`

## 📚 Reference

Compare your implementation with the solution in `exercises/solution/tools/search.py` to see:
- Complete implementations of all three functions
- Stronger JSON prompt formatting
- Natural wording for review searches
- Error handling patterns

---

Once you complete this exercise, you'll understand how to integrate live web search into your AI agents using Azure's Bing grounding capability!
