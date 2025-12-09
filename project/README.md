# Building Agents with Microsoft Azure

A comprehensive travel concierge agent built with Microsoft Semantic Kernel, Azure OpenAI, and Cosmos DB for vector RAG.

## 🎯 Project Overview

This project demonstrates how to build intelligent agents using Microsoft's AI stack:

- **Semantic Kernel**: Tool orchestration and state management
- **Azure OpenAI**: GPT-4o-mini for chat and text-embedding-3-small for embeddings
- **Cosmos DB**: Vector RAG for long-term memory and knowledge retrieval
- **Memory Systems**: Short-term and long-term memory for context management
- **External APIs**: Weather, currency, search, and card recommendation services

## 🏗️ Architecture

The agent follows a state machine pattern with the following phases:

```
Init → ClarifyRequirements → PlanTools → ExecuteTools → Synthesize → Done
```

### Key Features
- **Multi-tool Integration**: Weather, FX, search, card recommendations
- **Vector RAG**: Semantic search over curated knowledge base
- **Memory Systems**: Short-term and long-term memory for context management
- **State Management**: Robust state machine with error handling
- **Evaluation Harness**: Comprehensive testing and validation
- **Azure Integration**: Full Azure OpenAI and Cosmos DB integration

## 🚀 Quick Start

### ⚡ Super Quick Start (5 minutes)
```bash
# 1. Clone and setup
git clone <repository-url>
cd project/solution
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# 3. Test the system
python app/scripts/system_check.py

# 4. Start chatting!
python chat.py
```

### Prerequisites
1. **Azure Resources**:
   - Azure OpenAI service with GPT-4o-mini and text-embedding-3-small deployments
   - Cosmos DB account with vector search enabled
   - Azure Key Vault (optional, for secrets management)

2. **Environment Setup**:
```bash
# Clone the repository
git clone <repository-url>
cd project/solution

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your Azure credentials
```

### Environment Variables
Create a `.env` file in `project/solution/`:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-aoai.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small

# Cosmos DB
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your_cosmos_key_here
COSMOS_DB=ragdb
COSMOS_CONTAINER=snippets
COSMOS_PARTITION_KEY=/pk

# Optional: Bing Search
BING_KEY=your_bing_key_here
```

### Running the Agent

#### Basic Usage
```python
from app.main import run_request

# Plan a trip
plan = run_request(
    destination="Paris",
    travel_dates="2026-06-01 to 2026-06-08",
    card="BankGold"
)
print(plan)
```

#### Command Line
```bash
# Run the agent
python -m app.main

# Run evaluation
python -m app.eval.judge

# Check system health
python app/scripts/aoai_check.py
python app/scripts/cosmos_check.py
```

### 💬 Chat Interface

The easiest way to interact with the agent is through the **CLI chat interface**:

```bash
# Start chatting with the agent
python chat.py

# Or run the chat interface directly
python app/chat.py
```

#### Chat Features
- **Natural Conversation**: Just tell the agent about your travel plans
- **Interactive Commands**: 
  - `help` - Show available commands
  - `status` - Show session status
  - `clear` - Clear conversation history
  - `quit` - Exit the chat
- **Formatted Output**: Beautiful display of travel plans, weather, restaurants, and card recommendations
- **Error Handling**: Graceful error messages and recovery

#### Example Chat Session
```
🌍 TRAVEL CREDIT CARD CONCIERGE AGENT
============================================================
I can help you plan your travel and recommend credit cards!

Just tell me:
• Where you want to go
• When you're traveling  
• What credit card you have (or want recommendations)

Type 'help' for more options, 'quit' to exit
============================================================

💬 You: I want to go to Paris in March with my Chase Sapphire card

🤖 Agent: Thinking...

🎯 TRAVEL PLAN GENERATED!
========================================
📍 Destination: Paris
📅 Dates: March 2026

🌤️  Weather: 12°C, Partly Cloudy
💡 Recommendation: Pack layers and an umbrella

🍽️  Restaurants (3 found):
   1. Le Comptoir du Relais (⭐4.5, $$$)
   2. L'As du Fallafel (⭐4.2, $)
   3. Le Procope (⭐4.0, $$)

💳 Card Recommendation: Chase Sapphire Preferred
   💰 Benefit: 2x points on travel and dining
   💱 FX Fee: No foreign transaction fees

📋 Next Steps:
   1. Book flights 2-3 months in advance
   2. Reserve restaurants for dinner
   3. Check visa requirements
   4. Purchase travel insurance

📚 Sources: 5 references
```

#### When to Use the Chat Interface
- **After completing the setup** (environment variables configured)
- **During development** to test the agent's responses
- **For demonstrations** to show the agent's capabilities
- **For learning** to understand how the agent processes requests

### 🎯 Demo Script
Try the interactive demo to see all features:

```bash
# Run the demo script
python demo.py
```

This will show you:
- Programmatic API usage
- Chat interface features
- Development workflow
- Example interactions

## 🧪 Testing

The project uses a **hybrid testing strategy** combining pytest unit tests with system health checks:

### 🎯 Testing Strategy

#### **Pytest Unit Tests** - Code Logic & Validation
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Component interaction testing  
- **Model Tests**: Pydantic schema validation
- **State Machine Tests**: Agent state transition validation
- **Memory Tests**: Short-term and long-term memory functionality

#### **Health Check Scripts** - External Services & System Health
- **Azure OpenAI**: Service connectivity and deployment validation
- **Cosmos DB**: Database connection and vector search testing
- **Tool Integration**: External API connectivity and response validation
- **Memory Systems**: Short-term and long-term memory demonstrations
- **System Health**: End-to-end system functionality

### 🚀 Running Tests

#### **Comprehensive Test Suite**
```bash
# Run all tests (pytest + health checks)
python run_tests.py

# Run only pytest unit tests
python run_tests.py --unit

# Run only system health checks
python run_tests.py --health

# Run individual health checks
python run_tests.py --individual

# Quick tests (skip slow ones)
python run_tests.py --quick

# Verbose output
python run_tests.py --verbose
```

#### **Individual Test Categories**
```bash
# Pytest unit tests
python -m pytest tests/ -v

# Specific test files
python -m pytest tests/test_state.py -v
python -m pytest tests/test_models.py -v
python -m pytest tests/test_tools.py -v
python -m pytest tests/test_integration.py -v

# Health check scripts
python app/scripts/aoai_check.py --verbose
python app/scripts/cosmos_check.py --verbose
python app/scripts/tool_check.py --verbose
python app/scripts/state_check.py
python app/scripts/memory_demo.py
python app/scripts/long_term_memory_demo.py
```

### 📊 Test Coverage

#### **Unit Tests (50+ tests)**
- ✅ **State Management**: Phase transitions and data handling
- ✅ **Model Validation**: Pydantic schemas with valid/invalid data
- ✅ **Tool Functions**: Individual tool testing with mocks
- ✅ **Memory Systems**: Short-term and long-term memory functionality
- ✅ **Integration**: End-to-end workflow validation

#### **Health Checks**
- ✅ **Azure OpenAI**: Chat and embedding service connectivity
- ✅ **Cosmos DB**: Database connection and vector search
- ✅ **External APIs**: Weather, FX, search, and card services
- ✅ **Memory Systems**: Short-term and long-term memory demonstrations
- ✅ **State Machine**: Complete state transition validation

### 🎯 Evaluation Harness
```bash
# Run comprehensive evaluation
python -m app.eval.judge
```

**Test Cases**:
1. **Paris Trip**: European destination with EUR currency
2. **Tokyo Trip**: Asian destination with JPY currency  
3. **Barcelona Trip**: Mediterranean destination with EUR currency

**Metrics Evaluated**:
- ✅ Valid JSON output structure
- ✅ Citation presence and quality
- ✅ Card recommendation accuracy
- ✅ Weather data completeness
- ✅ Currency conversion accuracy
- ✅ RAG knowledge integration

## 📁 Project Structure

```
project/solution/
├── app/                    # Main application
│   ├── main.py            # Entry point with Semantic Kernel
│   ├── models.py          # Pydantic schemas
│   ├── knowledge_base.py  # Card knowledge base data
│   ├── state.py           # Agent state machine
│   ├── agent.py           # Azure OpenAI client functions
│   ├── memory.py          # Short-term memory system
│   ├── long_term_memory/  # Long-term memory with Cosmos DB
│   ├── tools/             # Tool implementations
│   │   ├── weather.py     # Open-Meteo weather API
│   │   ├── fx.py          # Frankfurter currency API
│   │   ├── search.py      # Bing search API
│   │   └── card.py        # Card recommendation engine
│   ├── rag/               # Vector RAG system
│   │   ├── ingest.py      # Data ingestion
│   │   └── retriever.py   # Vector search
│   ├── eval/              # Evaluation harness
│   │   └── judge.py       # Test runner and metrics
│   ├── scripts/           # Health check scripts
│   │   ├── aoai_check.py  # Azure OpenAI health check
│   │   ├── cosmos_check.py # Cosmos DB health check
│   │   ├── tool_check.py  # Tool integration test
│   │   ├── state_check.py # State machine test
│   │   ├── memory_demo.py # Short-term memory demo
│   │   ├── long_term_memory_demo.py # Long-term memory demo
│   │   └── health_check.py # Comprehensive health check
│   ├── utils/             # Utility modules
│   │   ├── config.py      # Configuration validation
│   │   └── logger.py      # Centralized logging
│   └── checks/            # Health check modules
│       ├── aoai.py        # Azure OpenAI utilities
│       └── tools.py       # Tool testing utilities
├── tests/                 # Pytest test suite
│   ├── test_state.py      # State machine unit tests
│   ├── test_models.py     # Model validation tests
│   ├── test_tools.py      # Tool function tests
│   ├── test_memory.py     # Short-term memory tests
│   ├── test_long_term_memory_simple.py # Long-term memory tests
│   ├── test_memory_integration.py # Memory integration tests
│   └── test_integration.py # Integration tests
├── examples/              # Usage examples
│   ├── basic_usage.py     # Basic usage example
│   ├── advanced_usage.py  # Advanced usage example
│   ├── memory_learning_example.py # Memory learning example
│   └── long_term_memory_integration.py # Long-term memory integration
├── docs/                  # Documentation
│   └── API.md            # API reference
├── run_tests.py          # Unified test runner
├── pytest.ini           # Pytest configuration
├── requirements.txt      # Python dependencies
├── env.example          # Environment variable template
└── README.md            # This file
```

## 🛠️ Development

### Adding New Tools

1. **Create the tool class**:
```python
# app/tools/my_tool.py
from semantic_kernel.functions import kernel_function

class MyTool:
    @kernel_function(name="my_function", description="Does something useful")
    def my_function(self, param1: str, param2: int):
        # Implementation
        return {"result": "success"}

# Backward compatibility
def my_function(param1: str, param2: int):
    return MyTool().my_function(param1, param2)
```

2. **Register in main.py**:
```python
from app.tools.my_tool import MyTool
kernel.add_plugin(MyTool(), "MyTool")
```

3. **Use in agent**:
```python
my_tool = kernel.get_plugin("MyTool")
result = my_tool["my_function"].invoke(kernel, param1="value", param2=42)
```

### State Management

The agent uses a robust state machine:

```python
from app.state import AgentState, Phase

state = AgentState()
state.advance()  # Move to next phase
print(f"Current phase: {state.phase}")
```

### Memory Systems

The system includes both short-term and long-term memory for context management:

#### **Short-Term Memory**
```python
from app.memory import ShortTermMemory

# Create memory instance
memory = ShortTermMemory(max_items=20, max_tokens=2000)

# Add conversation items
memory.add_conversation("user", "I want to go to Paris")
memory.add_conversation("assistant", "Paris is a great destination!")
memory.add_tool_call("weather", {"location": "Paris"}, {"temp": 22})

# Search and retrieve context
results = memory.search_memory("Paris")
context = memory.get_context_window()
```

#### **Long-Term Memory**
```python
from app.long_term_memory import LongTermMemory

# Create long-term memory
ltm = LongTermMemory(max_memories=1000, importance_threshold=0.3)

# Add important memories
ltm.add_memory(
    session_id="user_001",
    content="User prefers luxury hotels",
    memory_type="conversation",
    importance_score=0.8,
    tags=["preference", "hotel"]
)

# Search and manage memories
memories = ltm.search_memories("user_001", query="hotel")
ltm.prune_memories(strategy='hybrid')
```

### RAG Integration

The system includes vector RAG for knowledge retrieval:

```python
from app.rag.retriever import retrieve

# Search for relevant information
results = retrieve("BankGold rewards", k=5)
print(f"Found {len(results)} relevant snippets")
```

## 🐛 Troubleshooting

### Common Issues

1. **Cosmos DB Connection Error**:
   - Verify `COSMOS_ENDPOINT` and `COSMOS_KEY` in `.env`
   - Check RBAC permissions or use connection key
   - Ensure vector indexing is enabled on the container

2. **Azure OpenAI Errors**:
   - Verify endpoint and deployment names match your Azure setup
   - Check API key permissions and quotas
   - Ensure deployments are active and accessible

3. **Tool Execution Errors**:
   - Check external API availability and rate limits
   - Verify API keys (Bing, etc.) are valid
   - Review tool function signatures and parameters

4. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and module structure
   - Verify `.env` file is in the correct location

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export PYTHONPATH=.
export DEBUG=1
python -m app.main
```

## 📊 Performance

- **Response Time**: ~2-5 seconds per request
- **Token Usage**: ~500-1000 tokens per synthesis
- **Memory**: Efficient with lazy loading and caching
- **Scalability**: Stateless design, ready for containerization
- **Reliability**: Comprehensive error handling and fallbacks

## 🔒 Security

- **Authentication**: Azure DefaultAzureCredential
- **Secrets Management**: Environment variables (use Key Vault in production)
- **Data Privacy**: No PII stored, only travel planning data
- **API Security**: All external APIs use HTTPS
- **RBAC**: Proper Azure role-based access control

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run the agent
python -m app.main
```

### Container Deployment
```bash
# Build the container
docker build -f infra/Dockerfile -t travel-agent .

# Run the container
docker run -p 8000:8000 --env-file .env travel-agent
```

### Azure Container Apps
The project includes a Dockerfile for easy deployment to Azure Container Apps or other container platforms.

## 📈 Monitoring

The system includes comprehensive monitoring:

- **Health Checks**: Automated system health verification
- **Evaluation Metrics**: Continuous quality assessment
- **Error Tracking**: Detailed error logging and reporting
- **Performance Monitoring**: Response time and token usage tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the evaluation harness: `python -m app.eval.judge`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.md](../LICENSE.md) file for details.

## 📞 Support

For issues and questions:

1. **Check the troubleshooting section** above
2. **Run health checks** to identify issues
3. **Review evaluation results** for quality metrics
4. **Check Azure service status** in the Azure portal
5. **Review logs** for detailed error information

## 🎓 Learning Objectives

This project demonstrates:

- **Agent Architecture**: State machines and tool orchestration
- **Memory Systems**: Short-term and long-term memory for context management
- **Azure Integration**: OpenAI and Cosmos DB best practices
- **Vector RAG**: Semantic search and knowledge retrieval
- **Memory Management**: Pruning, reordering, and performance optimization
- **Evaluation**: Comprehensive testing and quality assurance
- **Production Readiness**: Error handling, monitoring, and deployment

## 🔗 Additional Resources

- [Microsoft Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [Azure Cosmos DB](https://azure.microsoft.com/en-us/products/cosmos-db)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Azure Container Apps](https://azure.microsoft.com/en-us/products/container-apps)