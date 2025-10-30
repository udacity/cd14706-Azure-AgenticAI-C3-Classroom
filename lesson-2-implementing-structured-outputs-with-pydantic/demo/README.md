# Sports Analyst with Pydantic Validation Demo

This demo extends the basic Semantic Kernel setup by adding Pydantic validation for structured sports analysis outputs. It demonstrates how to create a sports analyst agent that returns both human-readable responses and validated, structured data for sports queries.

## What This Demo Covers

- **Pydantic Model Definition**: Creating structured data models for sports analysis
- **Structured JSON Output**: Prompting the LLM to return JSON matching Pydantic schemas
- **Data Validation**: Automatically validating LLM responses against Pydantic models
- **Sports Analysis Agent**: A complete agent that handles game scores, player stats, and team analysis
- **Error Handling**: Graceful handling of validation errors and malformed responses

## Key Features

### 1. Pydantic Models for Sports
- `GameResult`: Validates game scores and match data
- `PlayerPerformance`: Validates player statistics and performance data  
- `TeamAnalysis`: Validates team standings and analysis data
- `SportsAnalysisResponse`: Main response wrapper with sports-specific metadata
- **Enums**: `GameStatus`, `LeagueType`, `PlayerPosition` for type safety

### 2. Sports Analysis Tools
- **Sports Scores Tool**: Get recent game scores across multiple leagues
- **Player Stats Tool**: Look up detailed player statistics and performance data
- **Multi-League Support**: NBA, NFL, MLB, NHL, Premier League

### 3. Validation Pipeline
- JSON parsing from LLM responses
- Pydantic model validation for sports data
- Type checking and data integrity
- Error handling with fallback responses

## Prerequisites

1. **Azure OpenAI Resource**: Same as Lesson 1
2. **Python Environment**: Python 3.8 or higher
3. **Dependencies**: Install with `pip install -r requirements.txt`

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in this directory:
```bash
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

The demo will run through several sports analysis scenarios:

1. **Game Scores Query**: "What were the recent NBA scores?"
2. **Player Stats Query**: "Tell me about LeBron James' performance this season"
3. **Team Analysis Query**: "How did the Kansas City Chiefs do in their last game?"
4. **Comparison Query**: "Compare Stephen Curry and Luka Doncic's stats"
5. **Season Outlook Query**: "What's the outlook for the Lakers this season?"

For each scenario, you'll see:
- Human-readable sports analysis
- Structured data validated against Pydantic models
- Tools used and confidence scores
- Analysis insights and predictions
- Follow-up suggestions

## Key Learning Points

### Pydantic Model Benefits for Sports Data
- **Type Safety**: Automatic type checking for sports statistics
- **Validation**: Built-in data validation with clear error messages
- **Enums**: Type-safe league, position, and status values
- **Documentation**: Self-documenting models with field descriptions

### Structured Output Benefits for Sports Analysis
- **Consistency**: Guaranteed response format for sports data
- **Integration**: Easy to integrate with sports databases and APIs
- **Error Handling**: Clear validation errors when data is malformed
- **Analysis**: Structured data enables advanced analytics

### Best Practices Demonstrated
- Clear prompt engineering for sports JSON output
- Robust error handling and fallbacks
- Separation of concerns (prompts, validation, display)
- Comprehensive logging for debugging
- Sports-specific metadata and insights

## Sports Data Models

### GameResult Model
- Game identification and basic info
- Team names and scores
- Game status and timing
- Venue and attendance data

### PlayerPerformance Model
- Player identification and physical stats
- League-specific performance statistics
- Contract and salary information
- Recent form and injury status

### TeamAnalysis Model
- Team standings and records
- Conference and division rankings
- Home/away performance splits
- Current streaks and trends

## Code Structure

```
demo/
├── main.py              # Main demo with Pydantic validation pipeline
├── models.py            # Pydantic model definitions for sports
├── tools/               # Sports analysis tools
│   ├── sports_scores.py # Game scores tool
│   └── player_stats.py  # Player statistics tool
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Sample Sports Data

The demo includes comprehensive mock data for:

### NBA Players
- LeBron James (Los Angeles Lakers) - Small Forward
- Stephen Curry (Golden State Warriors) - Point Guard  
- Luka Doncic (Dallas Mavericks) - Point Guard

### NFL Players
- Patrick Mahomes (Kansas City Chiefs) - Quarterback
- Josh Allen (Buffalo Bills) - Quarterback

### Recent Games
- NBA: Lakers vs Celtics, Warriors vs Heat, Bulls vs Knicks, Mavericks vs Suns
- NFL: Chiefs vs Bills, 49ers vs Cowboys, Buccaneers vs Eagles
- MLB: Yankees vs Red Sox, Dodgers vs Giants
- NHL: Maple Leafs vs Canadiens, Bruins vs Rangers
- Premier League: Manchester United vs Liverpool, Arsenal vs Chelsea

## Troubleshooting

- **Validation Errors**: Check that your prompts are requesting the exact JSON format
- **JSON Parsing Errors**: Ensure the LLM is returning valid JSON
- **Type Errors**: Verify that your Pydantic models match the expected data structure
- **Environment Issues**: Same as Lesson 1 - check your Azure OpenAI configuration

## Extending the Demo

### Adding More Sports
1. Add new league enums to `LeagueType`
2. Create league-specific position enums
3. Add mock data for new leagues
4. Update tool descriptions

### Advanced Analytics
1. Add prediction models
2. Include historical trend analysis
3. Implement player comparison algorithms
4. Add team performance metrics

### Real API Integration
1. Replace mock data with real sports APIs
2. Add authentication handling
3. Implement rate limiting and caching
4. Add real-time data updates

This Sports Analyst demo demonstrates how Pydantic validation can enhance sports analysis applications by providing structured, validated data that's perfect for building advanced sports analytics platforms.
