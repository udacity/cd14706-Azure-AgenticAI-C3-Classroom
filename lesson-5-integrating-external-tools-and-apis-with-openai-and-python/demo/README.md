# Sports Analyst Agent with External APIs Demo

This demo showcases a sports analyst agent that integrates external APIs using Azure OpenAI and Semantic Kernel.

## What This Demo Covers

- **Azure OpenAI Integration**: Using Azure OpenAI with Semantic Kernel
- **External API Integration**: Real sports APIs (NewsAPI.org, Ball Don't Lie API)
- **Memory Management**: Short-term memory for conversation context
- **Automatic Tool Calling**: FunctionChoiceBehavior for tool selection
- **Structured Output**: Pydantic models for validated responses
- **Error Handling**: Robust error handling with fallbacks

## Tools

### 1. Sports News API (External - NewsAPI.org)
- Latest sports news by league and team
- Real-time article aggregation
- Requires API key

### 2. Player Stats API (External - Ball Don't Lie API)
- NBA player statistics
- Fallback to mock data if unavailable
- No API key required

### 3. Sports Scores Tool (Mock)
- Game scores demonstration
- Local mock data

### 4. Team Standings Tool (Mock)
- Team rankings demonstration
- Local mock data

### 5. Sports Analytics Tool (Mock)
- Advanced statistics demonstration
- Local mock data

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI Service account
- Required environment variables (see Setup section)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the demo directory:

```env
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=your_deployment
AZURE_OPENAI_EMBED_DEPLOYMENT=your_embedding
AZURE_OPENAI_KEY=your_key
NEWSAPI_KEY=your_newsapi_key
BALLDONTLIE_API_KEY=your_balldontlie_key
```

### 3. Run the Demo
```bash
python main.py
```

## Expected Output

### 1. API Testing
- Sports News API test
- Player Stats API test

### 2. Demo Scenarios
**Scenario 1: Game Scores Query**
- Game scores lookup
- Team news retrieval
- Standings display
- Multi-turn conversation

**Scenario 2: Player Stats**
- Player statistics
- Player news
- Performance analytics
- Context-aware responses

**Scenario 3: Comprehensive Analysis**
- Team analysis
- News, standings, analytics
- Memory-based follow-ups

## Code Structure

```
demo/
├── main.py                    # Main demo
├── memory.py                  # Short-term memory
├── models.py                  # Pydantic models
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
└── tools/
    ├── sports_news.py         # NewsAPI.org integration
    ├── player_stats.py        # Ball Don't Lie API
    ├── sports_scores.py       # Mock scores
    ├── team_standings.py      # Mock standings
    └── sports_analytics.py    # Mock analytics
```

## Key Learning Points

- External API integration with Semantic Kernel
- Automatic tool calling with FunctionChoiceBehavior
- Memory management for context
- Pydantic models for validation
- Error handling and fallbacks
- Structured JSON output

## Usage Examples

### Game Scores Query
```
User: "I want to check the Lakers game scores"
Agent: [Uses sports_scores tool]
User: "Can you get the latest news about these teams?"
Agent: [Calls NewsAPI.org]
```

### Player Stats Query
```
User: "I want to know about LeBron James' stats"
Agent: [Calls Ball Don't Lie API]
User: "Can you get recent news about these players?"
Agent: [Calls NewsAPI.org]
```

## Error Handling

- API failures with fallbacks
- Network timeout handling
- Pydantic validation errors
- Memory management

## Troubleshooting

1. Set all environment variables in `.env`
2. Verify Azure OpenAI API keys
3. Check internet connection for external APIs
4. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
