# Sports Analyst Agent State Management with State Machine Demo

This demo implements comprehensive agent state management with a finite state machine for sports analysis. It demonstrates how to track agent context and progress across interactions, manage state transitions, and maintain conversation flow for sports fans.

## What This Demo Covers

- **State Machine Design**: Implementing a finite state machine with clear phases for sports analysis
- **State Transitions with History**: Managing transitions with history tracking and trigger recording
- **Context Tracking**: Maintaining conversation context and sports requirements
- **Progress Monitoring**: Tracking data completeness, tool execution, and phase durations
- **Transition History**: Complete audit trail of state changes with timestamps and triggers
- **Issue Resolution**: Handling problems and edge cases systematically
- **State Snapshots**: Real-time debugging and monitoring of agent state
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

### 2. Comprehensive State Management
- **Session Tracking**: Unique session IDs with creation and update timestamps
- **Sports Requirements Management**: Dynamic requirement gathering for teams, leagues, and players
- **Tool Execution Tracking**: Record of sports tools called and their results
- **Issue Resolution**: Systematic problem identification and resolution
- **Data Completeness**: Automatic calculation of sports data completeness percentage
- **Phase Transition History**: Complete audit trail of all state changes with triggers
- **Phase Duration Tracking**: Calculate time spent in each phase
- **State Snapshots**: Real-time state inspection for debugging and monitoring
- **Transition Triggers**: Every transition has explicit, descriptive triggers:
  - `query_type_identified` - Identified user's query type (game_scores, player_stats, team_analysis)
  - `requirements_complete` - All required fields gathered or user satisfied
  - `tools_planned` - Tool execution plan created
  - `tools_executed` - Sports data tools completed
  - `issues_detected` - Problems found requiring resolution
  - `analysis_complete` - Analysis validated with no issues
  - `issues_resolved` - All problems successfully handled
  - `output_complete` / `output_generated` - Final structured output generated
  - `llm_suggested_{phase}` - LLM suggested specific phase transition
  - `invalid_phase_suggestion` - LLM suggestion invalid, using fallback
  - `error_fallback` - Exception occurred, using recovery path

### 3. State-Aware Processing
- **Sports Context-Aware Prompts**: LLM prompts that include current state information for sports analysis
- **Automatic State Transitions**: Smart progression through state machine phases with explicit, descriptive triggers
- **Manual State Transitions**: All phase transitions use `transition_to()` for proper history tracking (never direct phase assignment)
- **LLM-Suggested Transitions**: LLM phase suggestions recorded with `llm_suggested_{phase}` trigger
- **Error Handling**: Graceful handling of state transition errors with recovery and explicit triggers
- **Progress Monitoring**: Real-time tracking of sports analysis progress and issues
- **Transition Timeline**: Human-readable summary of all state changes with descriptive triggers and timestamps

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
- **State Transitions**: Clear progression through each phase with triggers
- **Sports Context Tracking**: Team/league/player requirements, tools called, and data completeness
- **Issue Management**: Problem identification and resolution
- **Structured Sports Outputs**: Pydantic-validated sports analysis responses
- **Progress Monitoring**: Real-time state summaries with completion status
- **Transition History**: Complete timeline of state changes with timestamps
- **Phase Duration Metrics**: Time spent in each phase of the workflow

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
- **Proper Transition Tracking**: Always use `transition_to()` or `advance()` - never direct phase assignment
- **Explicit Triggers**: Every state transition has a descriptive trigger for debugging (no generic "auto_advance")
- **Error Handling**: Robust error handling at each state transition with explicit error triggers
- **Progress Monitoring**: Real-time visibility into agent progress and issues
- **Extensibility**: Easy to add new states and transitions
- **Complete Audit Trail**: Full history of state transitions with descriptive triggers for debugging and analysis
- **In-Session State Management**: Stateful processing within a session without persistent storage
- **Summary Logging**: Concise output with essential workflow information and transition history

## Code Structure

```
├── main.py              # Main demo with sports analyst state machine implementation
├── state.py             # Agent state management and state machine
├── models.py            # Pydantic model definitions for sports data
├── tools/               # Semantic Kernel tools
│   ├── sports_scores.py    # Sports scores tool for game data
│   └── player_stats.py     # Player statistics tool
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
- **AgentState**: Core state management class with comprehensive tracking
  - `phase_history`: List of all state transitions with timestamps and triggers
  - `advance(trigger="auto_advance")`: Progress to next phase with optional trigger recording
  - `transition_to(phase, trigger="manual_transition")`: Explicit transition to specific phase with optional trigger
  - `get_transition_summary()`: Human-readable timeline of state changes
  - `get_phase_duration(phase)`: Calculate time spent in each phase
  - `snapshot()`: Complete state snapshot for debugging
- **Phase Enum**: Defines all possible agent states (8 phases)
- **State Transitions**: Automatic and manual state progression with trigger tracking
- **Context Tracking**: Requirements, tools, issues, progress, and transition history
- **Error Handling**: Graceful handling of state transition failures with recovery

## Advanced State Features

### Phase Transition History
Every state transition is recorded with:
- **From Phase**: The starting phase
- **To Phase**: The destination phase
- **Timestamp**: When the transition occurred
- **Trigger**: What caused the transition (e.g., `auto_advance`, `issues_detected`, `output_generated`)
- **Transition Type**: Whether it was automatic or explicit

### State Debugging Tools
- **`state.snapshot()`**: Get complete state for inspection
- **`state.print_snapshot()`**: Print formatted state summary
- **`state.get_transition_summary()`**: Get human-readable transition timeline
- **`state.get_phase_duration(phase)`**: Calculate time spent in specific phase

### Logging Output
The demo uses **summary logging** approach:
- **Tool execution summaries** instead of individual tool call logs
- **Final state summary** with key metrics
- **Transition history timeline** at the end of each scenario
- **Workflow completion status** and session duration
- **Error messages** when issues occur

## Troubleshooting

- **State Transition Errors**: Check that the LLM is returning valid JSON with proper phase suggestions
- **Tool Execution Failures**: Verify that tools are properly registered and accessible
- **Context Loss**: Ensure state is being properly maintained across interactions
- **Phase Stuck**: Check data completeness thresholds and issue resolution logic. Use `state.get_transition_summary()` to see transition history
- **Debugging State Issues**: Use `state.snapshot()` or `state.print_snapshot()` to inspect current state
- **Environment Issues**: Same as Lesson 1 - check your Azure OpenAI configuration