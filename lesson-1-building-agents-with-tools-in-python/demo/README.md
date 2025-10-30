# Sports Analyst Bot Demo

This demo showcases a Sports Analyst Bot built with Semantic Kernel and Azure OpenAI. It demonstrates how to create an AI agent that can analyze sports data, provide insights, and answer questions about games, players, and statistics.

## What This Demo Covers

- **Semantic Kernel Setup**: Basic kernel configuration with Azure OpenAI
- **Custom Sports Tools**: Two specialized tools for sports analysis
- **Sports Scores Tool**: Get recent game scores across multiple leagues
- **Player Stats Tool**: Look up detailed player statistics and performance data
- **AI-Powered Analysis**: Leverage LLM capabilities for sports insights

## Sports Analysis Tools

### 1. Sports Scores Tool (`sports_scores.py`)
- **Function**: `get_sports_scores(league, team, days_back)`
- **Supported Leagues**: NBA, NFL, MLB, NHL, Premier League
- **Features**:
  - Get recent game scores
  - Filter by specific team
  - Multiple leagues support
  - Game status and timing information

### 2. Player Stats Tool (`player_stats.py`)
- **Function**: `get_player_stats(player_name, league, season)`
- **Supported Leagues**: NBA, NFL, MLB, NHL
- **Features**:
  - Detailed player statistics
  - Performance metrics
  - Recent form analysis
  - Injury status information

## Prerequisites

1. **Azure OpenAI Resource**: You need an Azure OpenAI resource with:
   - A chat completion deployment (e.g., gpt-4o-mini)
   - An embedding deployment (e.g., text-embedding-3-small)

2. **Python Environment**: Python 3.8 or higher

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in this directory:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-aoai-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_KEY=your_azure_openai_key_here
```

### 3. Run the Demo

```bash
python main.py
```

## Expected Output

The demo will show:

1. **Kernel Setup**: Azure services configuration and tool registration
2. **Available Tools**: List of sports analysis functions
3. **Demo Scenarios**:
   - NBA scores retrieval
   - Player statistics lookup (LeBron James)
   - NFL team-specific scores (Kansas City Chiefs)
   - Player search (Patrick Mahomes)

## Sample Data

The demo includes mock data for:

### NBA Players
- LeBron James (Los Angeles Lakers)
- Stephen Curry (Golden State Warriors)
- Luka Doncic (Dallas Mavericks)

### NFL Players
- Patrick Mahomes (Kansas City Chiefs)
- Josh Allen (Buffalo Bills)

### Recent Games
- NBA: Lakers vs Celtics, Warriors vs Heat, Bulls vs Knicks
- NFL: Chiefs vs Bills, 49ers vs Cowboys
- MLB: Yankees vs Red Sox
- NHL: Maple Leafs vs Canadiens
- Premier League: Manchester United vs Liverpool

## Key Features Demonstrated

### 1. Tool Integration
- Seamless integration with Semantic Kernel
- Function decorators for easy tool creation
- Error handling and logging

### 2. Data Structure
- Well-organized mock data
- Realistic sports statistics
- Multiple league support

### 3. Analysis Capabilities
- Recent performance trends
- Statistical insights
- Context-aware responses

## Extending the Demo

### Adding More Leagues
1. Add league data to the mock_scores dictionary
2. Include corresponding player data
3. Update the tool descriptions

### Real API Integration
1. Replace mock data with real sports API calls
2. Add authentication handling
3. Implement rate limiting and caching

### Advanced Analysis
1. Add prediction algorithms
2. Include historical data analysis
3. Implement trend analysis

## Code Structure

```
demo/
├── main.py              # Main demo script
├── tools/               # Sports analysis tools
│   ├── sports_scores.py # Game scores tool
│   └── player_stats.py  # Player statistics tool
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Troubleshooting

- **Missing environment variables**: Ensure all required Azure OpenAI variables are set
- **Import errors**: Check that you're in the correct directory and dependencies are installed
- **Tool errors**: Verify the tools directory structure and file permissions
- **API errors**: Confirm your Azure OpenAI resource is properly configured

## Next Steps

This demo provides a foundation for building more sophisticated sports analysis applications:

1. **Real-time Data**: Integrate with live sports APIs
2. **Advanced Analytics**: Add machine learning models for predictions
3. **User Interface**: Build a web or mobile app
4. **Notifications**: Add alerts for favorite teams/players
5. **Social Features**: Enable sharing and discussion of analysis

The Sports Analyst Bot demonstrates how AI can enhance sports analysis by providing instant access to data and intelligent insights that would be difficult to gather manually.
