# Lesson 9: Maintaining Long-Term Agent Memory in Python

## Module Overview

**Module Title:** Maintaining Long-Term Agent Memory in Python  
**Module Type:** Implementation  
**Subskill:** Long-term Memory Management for AI Agents with Python, OpenAI, and Cosmos DB  
**Primary Learning Objective:** Develop methods for updating and managing an agent's memory using Python with Cosmos DB to maintain context over extended sessions; demonstrating how to prune or reorder memory for better performance.

## Learning Objectives

By the end of this lesson, you will be able to:

1. **Develop methods for updating and managing agent memory** using Python with Cosmos DB
2. **Demonstrate how to prune or reorder memory for better performance** using advanced algorithms
3. **Maintain context over extended sessions** with intelligent memory management
4. **Implement performance optimization strategies** for long-term memory systems
5. **Use AI-powered memory scoring** for intelligent retention decisions
6. **Apply different pruning and reordering strategies** based on memory characteristics

## Key Concepts

### 1. Long-Term Memory Management
- **Memory Persistence**: Storing agent memories across extended sessions using Cosmos DB
- **Memory Types**: Conversation, tool calls, system events, and knowledge memories
- **Memory Metadata**: Importance scores, access patterns, and contextual information

### 2. Memory Pruning Strategies
- **Importance-based Pruning**: Remove memories with low importance scores
- **Age-based Pruning**: Archive old memories based on creation date
- **Access Frequency Pruning**: Remove rarely accessed memories
- **Hybrid Pruning**: Combine multiple strategies for optimal results
- **AI-Optimized Pruning**: Use OpenAI to intelligently score memories for retention

### 3. Memory Reordering for Performance
- **Priority-based Reordering**: Sort memories by computed priority scores
- **Recency-based Reordering**: Prioritize recently accessed memories
- **Access Frequency Reordering**: Order by how often memories are accessed
- **AI-Powered Reordering**: Use AI to calculate optimal memory priorities

### 4. Performance Optimization
- **Memory Efficiency**: Maximize the value of retained memories
- **Storage Utilization**: Optimize database storage usage
- **Retrieval Performance**: Improve memory search and access speed
- **Context Preservation**: Maintain relevant context across sessions

## Implementation Features

### Enhanced MemoryItem Class
```python
@dataclass
class MemoryItem:
    # Core fields
    id: str
    session_id: str
    content: str
    memory_type: str
    importance_score: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    tags: List[str]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
    # Performance optimization fields
    priority_score: float = 0.0
    relevance_score: float = 0.0
    memory_size: int = 0
    access_frequency: float = 0.0
    decay_factor: float = 1.0
    is_archived: bool = False
    retention_priority: int = 0
```

### AI-Powered Memory Management
- **OpenAI Integration**: Uses Semantic Kernel for intelligent memory scoring
- **Intelligent Pruning**: AI determines which memories to retain or archive
- **Smart Reordering**: AI calculates optimal memory priorities
- **Context-Aware Scoring**: Considers memory relevance and importance

### Advanced Pruning Strategies
1. **AI-Optimized Pruning**: Uses OpenAI to score memories for retention
2. **Heuristic Fallback**: Rule-based scoring when AI is unavailable
3. **Multi-factor Analysis**: Considers importance, recency, access patterns
4. **Archival System**: Archives instead of deleting for learning purposes

### Performance Optimization Methods
- **Comprehensive Optimization**: Combines pruning, reordering, and archiving
- **Performance Metrics**: Tracks memory efficiency and storage utilization
- **Automated Management**: Configurable auto-pruning and reordering
- **Real-time Monitoring**: Continuous performance assessment

## Usage Examples

### Basic Memory Management
```python
# Create long-term memory system
ltm = LongTermMemory(
    max_memories=1000,
    importance_threshold=0.3,
    enable_ai_scoring=True
)

# Add memories with context
await ltm.add_memory(
    session_id="user_session_001",
    content="User planning trip to Japan",
    memory_type="conversation",
    importance_score=0.8,
    tags=["travel", "japan"],
    context="User is planning a major trip"
)
```

### AI-Powered Optimization
```python
# Run comprehensive memory optimization
optimization_results = await ltm.optimize_memory_performance()

print(f"Pruned memories: {optimization_results['pruned_memories']}")
print(f"Reordered memories: {optimization_results['reordered_memories']}")
print(f"Archived memories: {optimization_results['archived_memories']}")
```

### Memory Search and Retrieval
```python
# Search by content
travel_memories = ltm.search_memories(session_id, query="japan")

# Search by importance
important_memories = ltm.search_memories(session_id, min_importance=0.7)

# Search by memory type
tool_memories = ltm.search_memories(session_id, memory_type="tool_call")
```

## Pruning Strategies

### 1. Importance-based Pruning
- Removes memories with importance scores below threshold
- Preserves high-value memories
- Simple and effective for basic use cases

### 2. Age-based Pruning
- Archives memories older than specified days
- Prevents memory bloat from old data
- Good for time-sensitive applications

### 3. Access Frequency Pruning
- Removes rarely accessed memories
- Keeps frequently used information
- Optimizes for active memory usage

### 4. Hybrid Pruning
- Combines multiple strategies
- More sophisticated decision making
- Better overall performance

### 5. AI-Optimized Pruning
- Uses OpenAI to score memories intelligently
- Considers multiple factors simultaneously
- Most advanced and effective approach

## Reordering Strategies

### 1. Importance-based Reordering
- Sorts by importance score (descending)
- Prioritizes high-value memories
- Simple and intuitive

### 2. Recency-based Reordering
- Sorts by last accessed time (descending)
- Prioritizes recently used memories
- Good for active sessions

### 3. Access Frequency Reordering
- Sorts by access count (descending)
- Prioritizes frequently used memories
- Optimizes for repeated access patterns

### 4. AI-Powered Reordering
- Uses AI to calculate optimal priorities
- Considers multiple factors
- Most sophisticated approach

## Performance Metrics

### Memory Efficiency
- Ratio of active memories to total memories
- Higher values indicate better efficiency
- Target: > 0.8 (80% efficiency)

### Storage Utilization
- Ratio of active memories to maximum capacity
- Lower values indicate more room for growth
- Target: < 0.9 (90% utilization)

### Optimization Score
- Combined metric of efficiency and utilization
- Higher values indicate better overall performance
- Target: > 0.7 (70% optimization score)

## Environment Setup

### Required Environment Variables
```bash
# Cosmos DB Configuration
COSMOS_ENDPOINT=your_cosmos_endpoint
COSMOS_KEY=your_cosmos_key
COSMOS_DB=your_database_name
COSMOS_CONTAINER=your_container_name

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment
AZURE_OPENAI_EMBED_DEPLOYMENT=your_embedding_deployment
```

### Installation
```bash
pip install -r requirements.txt
```

### Running the Demo
```bash
python long_term_memory.py
```

## Learning Outcomes

After completing this lesson, you will understand:

1. **Memory Management Fundamentals**: How to store, retrieve, and manage agent memories
2. **Performance Optimization**: Techniques for improving memory system performance
3. **AI Integration**: How to use OpenAI for intelligent memory management
4. **Pruning Strategies**: Different approaches to memory cleanup and optimization
5. **Reordering Techniques**: Methods for organizing memories for better retrieval
6. **Real-world Applications**: How to apply these concepts in production systems

## Best Practices

1. **Regular Optimization**: Run memory optimization regularly to maintain performance
2. **Monitor Metrics**: Track performance metrics to identify issues early
3. **Use AI Scoring**: Leverage AI-powered scoring for better memory management
4. **Archive vs Delete**: Archive old memories instead of deleting for learning
5. **Context Preservation**: Maintain relevant context across sessions
6. **Performance Tuning**: Adjust thresholds and strategies based on usage patterns

## Troubleshooting

### Common Issues
1. **Memory Not Pruning**: Check if auto-pruning is enabled and thresholds are appropriate
2. **Poor Performance**: Run comprehensive optimization and check metrics
3. **AI Scoring Fails**: Verify OpenAI configuration and fallback to heuristic methods
4. **Storage Issues**: Monitor storage utilization and adjust max_memories limit

### Debug Tips
1. Enable detailed logging to track memory operations
2. Check performance metrics regularly
3. Monitor memory statistics for trends
4. Test different pruning and reordering strategies

## Next Steps

1. **Experiment with Strategies**: Try different pruning and reordering approaches
2. **Monitor Performance**: Track metrics over time to optimize settings
3. **Extend Functionality**: Add custom scoring algorithms or memory types
4. **Production Deployment**: Apply these techniques to real-world applications

This lesson provides a comprehensive foundation for maintaining long-term agent memory with advanced performance optimization techniques using Python, OpenAI, and Cosmos DB.