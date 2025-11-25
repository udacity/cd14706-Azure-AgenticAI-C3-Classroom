# Sports Analyst with Pydantic Validation Demo

This demo demonstrates how to build a sports analyst agent using Semantic Kernel with automatic tool invocation and Pydantic validation for structured outputs. It shows how to combine real tool execution with validated, structured data for sports queries.

## What This Demo Covers

- **Semantic Kernel with Automatic Function Calling**: Using `FunctionChoiceBehavior.Auto()` to automatically invoke sports tools
- **Pydantic Model Definition**: Creating structured data models for sports analysis
- **Tool Integration**: Registering and invoking sports tools (`get_sports_scores`, `get_player_stats`)
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

### 2. Sports Analysis Tools (with `@kernel_function` decorator)
- **Sports Scores Tool** (`get_sports_scores`): Get recent game scores across multiple leagues
- **Player Stats Tool** (`get_player_stats`): Look up detailed player statistics and performance data
- **Multi-League Support**: NBA, NFL, MLB, NHL, Premier League
- **Automatic Invocation**: Tools are automatically called by Semantic Kernel when needed

### 3. Automatic Function Calling
```python
# Configure execution settings with automatic function calling
execution_settings = kernel.get_prompt_execution_settings_from_service_id(
    service_id=chat_service.service_id
)
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

# Get chat completion with automatic tool invocation
result = await chat_service.get_chat_message_contents(
    chat_history=chat_history,
    settings=execution_settings,
    kernel=kernel
)
```

### 4. Validation Pipeline
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

## How It Works

### Step 1: Register Tools as Plugins
```python
kernel.add_plugin(SportsScoresTools(), "sports_scores")
kernel.add_plugin(PlayerStatsTools(), "player_stats")
```
Tools decorated with `@kernel_function` are automatically discoverable.

### Step 2: Create Chat History
```python
chat_history = ChatHistory()
chat_history.add_system_message(create_sports_analysis_prompt())
chat_history.add_user_message(query)
```

### Step 3: Enable Automatic Function Calling
```python
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
```
This allows Semantic Kernel to automatically invoke tools when the LLM needs data.

### Step 4: Invoke and Get Structured Response
The LLM will:
1. Determine which tools to call (e.g., `get_sports_scores`, `get_player_stats`)
2. Semantic Kernel automatically executes those tools
3. LLM receives the real data and generates a structured JSON response
4. Response is validated against Pydantic models

## Key Learning Points

### Automatic Function Calling
Using `FunctionChoiceBehavior.Auto()` enables Semantic Kernel to automatically invoke registered tools when the LLM determines it needs data to answer a query. This ensures:
- Real data is retrieved from tools
- LLM receives actual sports scores and player statistics
- Accurate, validated responses based on tool outputs

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
- **Automatic function calling** with `FunctionChoiceBehavior.Auto()`
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
