# Sports Analyst Agent State Management with State Machine Demo

This demo extends the previous lessons by implementing comprehensive agent state management with a finite state machine for sports analysis. It demonstrates how to track agent context and progress across interactions, manage state transitions, and maintain conversation flow for sports fans.

## What This Demo Covers

- **State Machine Design**: Implementing a finite state machine with clear phases for sports analysis
- **State Transitions**: Managing transitions between different agent states
- **Context Tracking**: Maintaining conversation context and sports requirements
- **Progress Monitoring**: Tracking data completeness and tool execution
- **Issue Resolution**: Handling problems and edge cases systematically
- **Pydantic Validation**: Structured outputs with validated sports data

## Key Features

### 1. State Machine Phases
- **Init**: Create session/state; capture initial sports analysis goal
- **ClarifyRequirements**: Ask targeted questions until required fields are present (team, league, player)
- **PlanTools**: Decide which sports tools to call and with what args
- **ExecuteTools**: Call sports scores/player stats tools and collect results
- **AnalyzeResults**: Process tool outputs and validate data completeness
- **ResolveIssues**: Handle any problems or edge cases
- **ProduceStructuredOutput**: Emit Pydantic-validated JSON and natural language sports analysis
- **Done**: Process complete

### 2. State Management
- **Session Tracking**: Unique session IDs and timestamps
- **Sports Requirements Management**: Dynamic requirement gathering for teams, leagues, and players
- **Tool Execution Tracking**: Record of sports tools called and their results
- **Issue Resolution**: Systematic problem identification and resolution
- **Data Completeness**: Automatic calculation of sports data completeness percentage

### 3. State-Aware Processing
- **Sports Context-Aware Prompts**: LLM prompts that include current state information for sports analysis
- **Automatic State Transitions**: Smart progression through state machine phases
- **Error Handling**: Graceful handling of state transition errors
- **Progress Monitoring**: Real-time tracking of sports analysis progress and issues

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

The demo will run through three comprehensive scenarios that showcase the state machine:

### 1. Game Scores Query
**Multi-step conversation:**
- "I want to check recent game scores"
- "I'm interested in the Lakers in the NBA"
- "That's all I need to know"

**State progression:** Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ProduceStructuredOutput → Done

### 2. Player Stats Query
**Multi-step conversation:**
- "I want to know about a player's performance"
- "Tell me about LeBron James in the NBA"
- "Thanks for the information"

**State progression:** Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ProduceStructuredOutput → Done

### 3. Complex Multi-Step Query
**Multi-step conversation:**
- "I need help analyzing my favorite team"
- "The Warriors are struggling this season"
- "Can you also tell me about Stephen Curry's stats?"
- "That helps, thank you"

**State progression:** Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ResolveIssues → ProduceStructuredOutput → Done

For each scenario, you'll see:
- **State Transitions**: Clear progression through each phase
- **Sports Context Tracking**: Team/league/player requirements, tools called, and data completeness
- **Issue Management**: Problem identification and resolution
- **Structured Sports Outputs**: Pydantic-validated sports analysis responses
- **Progress Monitoring**: Real-time state summaries

## Key Learning Points

### State Machine Benefits
- **Predictable Flow**: Clear progression through defined phases
- **Context Preservation**: Maintains conversation context across interactions
- **Error Recovery**: Systematic handling of issues and edge cases
- **Progress Tracking**: Real-time monitoring of agent progress and data completeness

### State Management Benefits
- **Session Continuity**: Maintains state across multiple user interactions
- **Requirement Tracking**: Dynamic gathering and validation of user requirements
- **Tool Orchestration**: Systematic execution of tools based on current state
- **Issue Resolution**: Structured approach to problem identification and resolution

### Agent Design Patterns
- **State-Aware Prompts**: Context-rich prompts that include current state information
- **Automatic Transitions**: Smart progression through state machine phases
- **Graceful Degradation**: Fallback handling when state transitions fail
- **Comprehensive Logging**: Detailed tracking of state changes and decisions

### Best Practices Demonstrated
- **Separation of Concerns**: Clear separation between state management, tool execution, and response generation
- **Error Handling**: Robust error handling at each state transition
- **Progress Monitoring**: Real-time visibility into agent progress and issues
- **Extensibility**: Easy to add new states and transitions

## Code Structure

```
├── main.py              # Main demo with sports analyst state machine implementation
├── state.py             # Agent state management and state machine
├── models.py            # Pydantic model definitions for sports data
├── tools/               # Semantic Kernel tools for sports analysis
│   ├── sports_scores.py
│   └── player_stats.py
└── requirements.txt     # Dependencies
```

## State Machine Architecture

### State Transitions
```
Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults
                                                           ↓
Done ← ProduceStructuredOutput ← ResolveIssues ←──────────┘
```

### Key Components
- **AgentState**: Core state management class with phase tracking
- **Phase Enum**: Defines all possible agent states
- **State Transitions**: Automatic and manual state progression
- **Context Tracking**: Requirements, tools, issues, and progress
- **Error Handling**: Graceful handling of state transition failures

## Troubleshooting

- **State Transition Errors**: Check that the LLM is returning valid JSON with proper phase suggestions
- **Tool Execution Failures**: Verify that tools are properly registered and accessible
- **Context Loss**: Ensure state is being properly maintained across interactions
- **Phase Stuck**: Check data completeness thresholds and issue resolution logic
- **Environment Issues**: Same as Lesson 1 - check your Azure OpenAI configuration