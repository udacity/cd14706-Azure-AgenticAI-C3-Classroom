# Agent Memory Management Demo

This demo extends the previous lessons by implementing comprehensive agent memory management with short-term memory capabilities. It demonstrates how to maintain conversation context, track sports entities, and manage memory efficiently across interactions.

## What This Demo Covers

- **Short-Term Memory**: Implementing memory for sports analysis conversations
- **Context Management**: Maintaining conversation history and context windows
- **Entity Tracking**: Tracking sports teams, players, and leagues mentioned
- **Memory Search**: Searching through conversation history for relevant information
- **Memory Eviction**: Managing memory limits and eviction strategies
- **Pydantic Validation**: Structured outputs with validated responses

## Key Features

### 1. Memory Management
- **Conversation History**: Track user and assistant messages with timestamps
- **Context Windows**: Generate context windows for LLM prompts
- **Memory Search**: Search through conversation history for specific topics
- **Memory Eviction**: Automatic eviction when memory limits are exceeded
- **Token Management**: Track token usage and manage memory efficiently

### 2. Sports Entity Tracking
- **Team Tracking**: Track mentioned teams across conversations
- **Player Tracking**: Track mentioned players and their context
- **League Tracking**: Track mentioned leagues and sports
- **Tool Call History**: Record and track tool calls and their results
- **Context Extraction**: Extract sports-specific context from conversations

### 3. Memory-Aware Processing
- **Context-Rich Prompts**: Include conversation history in LLM prompts
- **Memory Persistence**: Maintain memory across multiple interactions
- **Smart Eviction**: Intelligent memory eviction based on usage and importance
- **Search Capabilities**: Find relevant information from conversation history

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
python demo.py
```

## Expected Output

The demo will run through three comprehensive scenarios that showcase memory management:

### 1. Game Scores Query with Memory
**Multi-step conversation:**
- "I want to check the Lakers game scores"
- "What about the Warriors game?"
- "Can you tell me more about those games?"

**Memory features demonstrated:**
- Conversation history tracking
- Team context extraction
- Tool call memory
- Context window generation

### 2. Player Stats with Memory
**Multi-step conversation:**
- "I want to know about LeBron James' stats"
- "How about Stephen Curry?"
- "Can you compare their performances?"

**Memory features demonstrated:**
- Player context tracking
- Cross-reference capabilities
- Memory search functionality
- Context persistence

### 3. Mixed Sports Query with Memory Context
**Multi-step conversation:**
- "I have a question about the Lakers"
- "I also want to know about LeBron James"
- "Can you give me a complete analysis of the Lakers and LeBron?"

**Memory features demonstrated:**
- Multi-entity tracking
- Complex context management
- Memory search and retrieval
- Comprehensive analysis

For each scenario, you'll see:
- **Memory State**: Current memory usage and statistics
- **Sports Context**: Tracked teams, players, and leagues
- **Tool Calls**: History of tools used and their results
- **Context Windows**: Generated context for LLM prompts
- **Memory Search**: Search results from conversation history

## Key Learning Points

### Memory Management Benefits
- **Context Preservation**: Maintains conversation context across interactions
- **Entity Tracking**: Tracks sports entities mentioned in conversations
- **Efficient Storage**: Manages memory usage with smart eviction strategies
- **Search Capabilities**: Enables finding relevant information from history

### Sports Analysis Benefits
- **Team Context**: Maintains context about teams across conversations
- **Player Context**: Tracks player information and performance data
- **League Context**: Manages league-specific information and rules
- **Tool Integration**: Seamlessly integrates with sports analysis tools

### Agent Design Patterns
- **Memory-Aware Prompts**: Context-rich prompts that include conversation history
- **Entity Extraction**: Automatic extraction of sports entities from conversations
- **Smart Eviction**: Intelligent memory management based on usage patterns
- **Search Integration**: Built-in search capabilities for conversation history

### Best Practices Demonstrated
- **Memory Limits**: Setting appropriate limits for memory usage
- **Token Management**: Efficient token counting and management
- **Context Windows**: Generating optimal context windows for LLM prompts
- **Entity Tracking**: Systematic tracking of domain-specific entities

## Code Structure

```
├── demo.py              # Main demo script
├── main.py              # Core memory management implementation
├── memory.py            # Short-term memory implementation
├── state.py             # Agent state management
├── synthesis.py         # Response synthesis
├── models.py            # Pydantic model definitions
├── tools/               # Semantic Kernel tools
│   ├── sports_scores.py
│   └── player_stats.py
└── requirements.txt     # Dependencies
```

## Memory Architecture

### Memory Components
- **ShortTermMemory**: Core memory management class
- **Conversation Items**: Individual conversation entries with metadata
- **Context Windows**: Generated context for LLM prompts
- **Entity Tracking**: Sports-specific entity extraction and tracking
- **Search Functionality**: Memory search and retrieval capabilities

### Memory Management
- **Token Counting**: Automatic token estimation and tracking
- **Eviction Strategy**: FIFO eviction when limits are exceeded
- **Memory Export/Import**: Persistence capabilities for memory
- **Search Indexing**: Efficient search through conversation history

## Troubleshooting

- **Memory Limits**: Adjust max_items and max_tokens parameters if needed
- **Context Windows**: Check token limits and context window generation
- **Entity Tracking**: Verify entity extraction logic and patterns
- **Tool Integration**: Ensure tools are properly registered and accessible
- **Environment Issues**: Check your Azure OpenAI configuration