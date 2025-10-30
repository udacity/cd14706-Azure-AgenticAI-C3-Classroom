# Sports Analyst Agent with External APIs Demo

This demo showcases a sports analyst agent that integrates external APIs with memory management capabilities. The agent can provide comprehensive sports analysis by combining real-time data from multiple external sources with conversation memory.

## What This Demo Covers

- **External API Integration**: Connecting to multiple sports-related external APIs
- **Memory Management**: Short-term memory for sports conversations and context
- **Sports News API**: Latest sports news and breaking updates
- **Team Standings API**: Current team rankings and playoff pictures
- **Sports Analytics API**: Advanced statistics and performance metrics
- **Sports Scores API**: Game results and live scores
- **Player Stats API**: Individual player statistics and performance
- **Real-time Data**: Live data from external sports services
- **Error Handling**: Robust error handling for API failures

## External APIs Integrated

### 1. Sports News API
- **Purpose**: Latest sports news and breaking updates
- **Features**: 
  - Get latest news by league and team
  - Breaking news alerts
  - News search functionality
  - Sentiment analysis of news articles
- **Mock Endpoints**: `api.sportsnews.com`

### 2. Team Standings API
- **Purpose**: Team rankings and playoff information
- **Features**:
  - Current team standings by conference
  - Playoff picture analysis
  - Team power rankings
  - Historical standings data
- **Mock Endpoints**: `api.sportsstandings.com`

### 3. Sports Analytics API
- **Purpose**: Advanced statistics and performance analysis
- **Features**:
  - Team analytics and metrics
  - Player performance analytics
  - Game-by-game analysis
  - Trend analysis and predictions
- **Mock Endpoints**: `api.sportsanalytics.com`

### 4. Sports Scores API
- **Purpose**: Game results and live scores
- **Features**:
  - Recent game scores by league
  - Team-specific score filtering
  - Live game updates
  - Historical game data
- **Mock Implementation**: Local mock data

### 5. Player Stats API
- **Purpose**: Individual player statistics
- **Features**:
  - Player statistics by league
  - Season-long performance data
  - Recent form analysis
  - Injury status tracking
- **Mock Implementation**: Local mock data

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
Create a `.env` file in the demo directory with the following variables:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_name
AZURE_OPENAI_EMBED_DEPLOYMENT=your_embedding_deployment_name
AZURE_OPENAI_KEY=your_azure_openai_key
```

### 3. Run the Demo
```bash
python main.py
```

## Expected Output

The demo will run comprehensive scenarios showcasing external API integration:

### 1. External API Testing
**Tests each external API independently:**
- Sports News API testing
- Team Standings API testing  
- Sports Analytics API testing
- Sports Scores API testing
- Player Stats API testing

**Each test shows:**
- API response structure and data
- Error handling capabilities
- Response time and reliability
- Data validation and processing

### 2. Integration Scenarios
**Realistic sports analysis scenarios:**

**Scenario 1: Game Scores Query with External APIs**
- Check recent game scores
- Get latest team news
- Show current standings
- Provide comprehensive analysis

**Scenario 2: Player Stats with External APIs**
- Get player statistics
- Retrieve player news
- Analyze performance trends
- Compare with other players

**Scenario 3: Comprehensive Sports Analysis**
- Complete team analysis
- News, standings, and analytics
- Memory-based follow-up questions
- Real-time data integration

## Code Structure

```
demo/
├── main.py                    # Main demo application
├── memory.py                  # Short-term memory implementation
├── models.py                  # Pydantic models for structured outputs
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── tools/                     # External API tools
    ├── sports_news.py         # Sports news API integration
    ├── team_standings.py      # Team standings API integration
    ├── sports_analytics.py    # Sports analytics API integration
    ├── sports_scores.py       # Sports scores tool
    └── player_stats.py        # Player statistics tool
```

## Key Learning Points

### External API Integration
- **API Design Patterns**: How to structure external API calls
- **Error Handling**: Robust error handling for API failures
- **Data Validation**: Validating external API responses
- **Rate Limiting**: Managing API rate limits and quotas
- **Caching**: Implementing caching for external data

### Memory Management
- **Context Windows**: Managing conversation context
- **Entity Tracking**: Tracking sports entities (teams, players, leagues)
- **Tool Call History**: Recording and retrieving tool usage
- **Memory Search**: Searching through conversation history
- **Eviction Strategies**: Managing memory limits

### Sports Domain Knowledge
- **Data Models**: Structured data models for sports information
- **API Integration**: Connecting to multiple sports data sources
- **Real-time Updates**: Handling live sports data
- **Analytics**: Advanced sports statistics and metrics

## Demo Scenarios

### Scenario 1: Game Scores with External APIs
```
User: "I want to check the Lakers game scores"
Agent: [Calls sports_scores API] "The Lakers won 120-115 against the Warriors..."
User: "What about the Warriors game?"
Agent: [Uses memory context] "As I mentioned, the Warriors lost 120-115..."
User: "Can you get the latest news about these teams?"
Agent: [Calls sports_news API] "Here's the latest news about both teams..."
User: "Show me the current standings for both teams"
Agent: [Calls team_standings API] "The Lakers are 1st in the West, Warriors are 2nd..."
```

### Scenario 2: Player Stats with External APIs
```
User: "I want to know about LeBron James' stats"
Agent: [Calls player_stats API] "LeBron is averaging 25.2 points, 7.8 rebounds..."
User: "How about Stephen Curry?"
Agent: [Calls player_stats API] "Stephen Curry is averaging 28.1 points, 4.4 rebounds..."
User: "Can you get recent news about these players?"
Agent: [Calls sports_news API] "Here's the latest news about both players..."
User: "What's the analytics on their performance?"
Agent: [Calls sports_analytics API] "The analytics show LeBron has a 28.4 PER..."
```

## Error Handling

The demo includes comprehensive error handling for:
- **API Failures**: Graceful handling of external API errors
- **Network Issues**: Timeout and connection error handling
- **Data Validation**: Pydantic model validation errors
- **Memory Limits**: Memory eviction and overflow handling
- **Rate Limiting**: API rate limit management

## Performance Considerations

- **Async Operations**: Non-blocking API calls
- **Caching**: Intelligent caching of external data
- **Memory Management**: Efficient memory usage patterns
- **Error Recovery**: Automatic retry mechanisms
- **Response Time**: Optimized API response handling

## Future Enhancements

- **Real API Integration**: Replace mock APIs with real sports APIs
- **WebSocket Support**: Real-time updates via WebSocket connections
- **Machine Learning**: Predictive analytics and insights
- **Multi-language Support**: Support for multiple languages
- **Advanced Caching**: Redis-based caching for better performance

## Troubleshooting

### Common Issues

1. **Environment Variables**: Ensure all required environment variables are set
2. **API Keys**: Verify Azure OpenAI API keys are valid
3. **Network Connectivity**: Check internet connection for external API calls
4. **Memory Issues**: Monitor memory usage for large conversations
5. **Rate Limits**: Be aware of API rate limits and quotas

### Debug Mode

Enable debug logging by setting the log level to DEBUG in the main.py file:

```python
logging.basicConfig(level=logging.DEBUG)
```

This will provide detailed information about API calls, memory operations, and error handling.
