# Sports Analyst Agent with Bing Search Integration

This demo showcases a sports analyst agent that uses **Azure AI Agents with Bing grounding** to perform real-time sports news and search queries. It demonstrates how to connect Azure's Foundry Bing Search with the **Semantic Kernel framework**, returning live, structured results on basketball and other sports.

## 🎯 What This Demo Covers

- **Live Bing Search Integration** using Azure AI Foundry
- **Semantic Kernel Tool Plugin** wrapping a sports-specific search function
- **Real-Time Sports Analysis** via grounded search (no mocks)
- **Structured JSON Responses** parsed and validated from the assistant
- **Memory-Optional Architecture** focused on query/response quality

---

## 🔌 Bing Search Plugin: `SearchTools`

- Performs live web searches for basketball scores, player highlights, and news
- Uses Azure AI Agents and Bing Search grounding
- Returns structured search results:
  ```json
  {
    "title": "LeBron dominates in 30-point performance",
    "url": "https://espn.com/...",
    "snippet": "LeBron James put up 30 points in a big win over the Warriors..."
  }
  ```
- Configured as a Semantic Kernel plugin via `tools/search.py`

---

## ✅ Prerequisites

- Python 3.8 or higher
- Azure OpenAI Service with a valid Bing Search grounding agent
- Azure identity authentication (via `DefaultAzureCredential`)
- A properly configured `.env` file (see below)

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
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

---

## 🚀 How to Run

```bash
python main.py
```

This will:
- Initialize the Semantic Kernel and register the `sports_search` plugin
- Perform a live query for `"latest NBA highlights"` using Bing Search
- Log and display the top 3 search results

---

## 🧪 Sample Output

```
🌐 Testing Bing Sports Web Search
1. LeBron drops 30 as Lakers top Warriors
   URL: https://espn.com/lakers-vs-warriors-highlights
   Snippet: LeBron James scored 30 in a win against Golden State...

2. Curry's clutch three not enough
   URL: https://nba.com/curry-clutch-three
   Snippet: Stephen Curry hit a late 3-pointer but the Lakers held on...

3. NBA Power Rankings after Tuesday’s games
   URL: https://sportsnews.com/nba-power-rankings
   Snippet: The Lakers surge to 2nd in the Western Conference...
```

---

## 🧠 Code Overview

```
demo/
├── main.py              # Focused sports agent demo using Bing search
├── tools/
│   └── search.py        # Semantic Kernel tool wrapping Bing-grounded AI Agent
├── models.py            # (optional) Pydantic models for structured parsing
├── requirements.txt     # Project dependencies
└── .env                 # Environment variables (not checked into source control)
```

---

## 📚 Key Concepts

### Bing Search Integration

- **Live Search Results**: No mocks or hardcoded responses
- **Semantic Kernel Tool**: Wrapped with `@kernel_function` and callable by plugin name
- **JSON Parsing**: Assistant must return structured JSON (not freeform text)
- **Temporary Threads**: Each search creates and cleans up an agent thread

### Azure AI Agent Design

- **Threaded Agent Interaction**: Thread → Message → Run → Message List
- **Grounding via Bing**: The `connection_id` routes messages through Bing search grounding
- **Secure Identity**: Uses Azure CLI or environment identity via `DefaultAzureCredential`

---

## ✅ Use Cases

- Basketball news aggregation
- Real-time player performance insights
- Live search result summarization
- Context injection into larger sports agents
- Cross-league sports information retrieval (NBA, NFL, WNBA, NCAA)

---

## 🔧 Troubleshooting

| Problem | Solution |
|--------|----------|
| `Missing configuration` | Ensure all `.env` variables are set correctly |
| `No JSON returned by Agent` | Check that Bing grounding is properly connected to your Agent |
| Search returns generic text | Review Agent prompt instructions and grounding connection |
| Search not triggering | Ensure `search.py` method is properly wrapped with `@kernel_function` |

Enable detailed debugging:
```python
logging.basicConfig(level=logging.DEBUG)
```

---

## 🧱 Future Enhancements

- Inject search results into larger agent workflows
- Add summarization or scoring on top of search output
- Chain queries with memory-enabled agents
- Use sports entity detection for automatic query refinement
- Support sports-specific embeddings or semantic reranking

---

## 🎉 Summary

This demo is a minimal and modular example of how to:

- Ground an Azure AI Agent with **Bing Search**
- Wrap it into a **Semantic Kernel plugin**
- Perform **live, structured sports queries**
- Use it as the foundation for a full-featured **sports analyst AI agent**

```bash
🏀 Powered by Azure AI Agents + Semantic Kernel + Bing Grounding
```
