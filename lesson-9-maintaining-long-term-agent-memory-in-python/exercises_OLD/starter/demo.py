#!/usr/bin/env python3
"""
Demo script for Lesson 9: Maintaining Long-Term Agent Memory in Python

This script demonstrates the key learning objectives:
- Develop methods for updating and managing agent memory using Python with Cosmos DB
- Demonstrate how to prune or reorder memory for better performance
- Maintain context over extended sessions with intelligent memory management
"""

import asyncio
import logging
from long_term_memory import LongTermMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_memory_pruning_and_reordering():
    """
    Demonstrate memory pruning and reordering for better performance.
    This showcases the core learning objectives of the lesson.
    """
    print("🧠 Lesson 9: Maintaining Long-Term Agent Memory in Python")
    print("=" * 70)
    print("🎯 Learning Objectives:")
    print("   • Develop methods for updating and managing agent memory using Python with Cosmos DB")
    print("   • Demonstrate how to prune or reorder memory for better performance")
    print("   • Maintain context over extended sessions with intelligent memory management")
    print("=" * 70)
    
    # Create memory system with small limit to trigger pruning
    ltm = LongTermMemory(
        max_memories=5,  # Small limit to demonstrate pruning
        importance_threshold=0.4,
        enable_ai_scoring=True
    )
    
    print(f"✅ Created memory system with {ltm.max_memories} memory limit")
    print()
    
    # Add memories with varying importance to demonstrate pruning
    print("📝 Adding memories with varying importance levels...")
    
    memories_data = [
        ("session_001", "User's birthday is next month", "conversation", 0.9, ["personal", "birthday"]),
        ("session_001", "Weather is sunny today", "conversation", 0.2, ["weather", "daily"]),
        ("session_001", "Important project deadline approaching", "conversation", 0.8, ["work", "deadline"]),
        ("session_001", "Random thought about coffee", "conversation", 0.1, ["personal", "coffee"]),
        ("session_001", "User completed major milestone", "system_event", 0.9, ["work", "milestone"]),
        ("session_001", "Casual conversation about weekend", "conversation", 0.3, ["personal", "weekend"]),
        ("session_001", "Critical system error occurred", "system_event", 0.95, ["system", "error"]),
    ]
    
    for session_id, content, memory_type, importance, tags in memories_data:
        await ltm.add_memory(
            session_id=session_id,
            content=content,
            memory_type=memory_type,
            importance_score=importance,
            tags=tags
        )
        print(f"   ✓ Added: {content[:30]}... (importance: {importance})")
    
    print(f"\n📊 Memory Statistics Before Optimization:")
    stats_before = ltm.get_memory_statistics()
    print(f"   • Total memories: {stats_before['total_memories']}")
    print(f"   • Average importance: {stats_before['average_importance']:.2f}")
    
    # Demonstrate different pruning strategies
    print(f"\n✂️ Demonstrating Memory Pruning Strategies:")
    print("-" * 50)
    
    pruning_strategies = ['importance', 'age', 'access_frequency', 'hybrid', 'ai_optimized']
    for strategy in pruning_strategies:
        if strategy in ltm.pruning_strategies:
            print(f"   • {strategy.replace('_', ' ').title()} pruning: Available")
    
    # Run AI-powered optimization (this will trigger pruning)
    print(f"\n🚀 Running AI-Powered Memory Optimization:")
    print("-" * 45)
    print("This demonstrates pruning and reordering for better performance...")
    
    optimization_results = await ltm.optimize_memory_performance()
    
    print(f"\n✅ Optimization Results:")
    print(f"   • Pruned memories: {optimization_results['pruned_memories']}")
    print(f"   • Reordered memories: {optimization_results['reordered_memories']}")
    print(f"   • Archived memories: {optimization_results['archived_memories']}")
    print(f"   • Optimization time: {optimization_results['optimization_time']:.2f}s")
    
    # Show performance improvements
    perf = optimization_results.get('performance_improvements', {})
    if 'error' not in perf:
        print(f"\n📈 Performance Improvements:")
        print(f"   • Memory efficiency: {perf.get('memory_efficiency', 0):.2%}")
        print(f"   • Storage utilization: {perf.get('storage_utilization', 0):.2%}")
        print(f"   • Optimization score: {perf.get('optimization_score', 0):.2f}")
    
    # Demonstrate reordering strategies
    print(f"\n🔄 Demonstrating Memory Reordering Strategies:")
    print("-" * 50)
    
    reorder_strategies = ['importance', 'recency', 'access_frequency']
    for strategy in reorder_strategies:
        reordered = ltm.reorder_memories("session_001", strategy=strategy)
        print(f"   • {strategy.title()} reordering: {reordered} memories reordered")
    
    # Final statistics
    print(f"\n📊 Memory Statistics After Optimization:")
    stats_after = ltm.get_memory_statistics()
    print(f"   • Total memories: {stats_after['total_memories']}")
    print(f"   • Average importance: {stats_after['average_importance']:.2f}")
    print(f"   • Memory efficiency improved through optimization")
    
    # Demonstrate memory search
    print(f"\n🔍 Memory Search Capabilities:")
    print("-" * 35)
    
    # Search by importance
    important_memories = ltm.search_memories("session_001", min_importance=0.7)
    print(f"   • High-importance memories: {len(important_memories)}")
    
    # Search by memory type
    system_memories = ltm.search_memories("session_001", memory_type="system_event")
    print(f"   • System event memories: {len(system_memories)}")
    
    # Search by content
    work_memories = ltm.search_memories("session_001", query="work")
    print(f"   • Work-related memories: {len(work_memories)}")
    
    print(f"\n🎉 Lesson 9 Demonstration Complete!")
    print("=" * 70)
    print("✅ Key Learning Objectives Achieved:")
    print("   ✓ Developed methods for updating and managing agent memory using Python with Cosmos DB")
    print("   ✓ Demonstrated how to prune or reorder memory for better performance")
    print("   ✓ Maintained context over extended sessions with intelligent memory management")
    print("   ✓ Implemented performance optimization strategies for long-term memory systems")
    print("=" * 70)

async def main():
    """Main function to run the demonstration"""
    try:
        await demo_memory_pruning_and_reordering()
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print(f"\n❌ Error: {e}")
        print("Please check your environment variables and Cosmos DB connection.")
        print("\nRequired environment variables:")
        print("  - COSMOS_ENDPOINT")
        print("  - COSMOS_KEY") 
        print("  - COSMOS_DB")
        print("  - COSMOS_CONTAINER")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_API_VERSION")
        print("  - AZURE_OPENAI_KEY")
        print("  - AZURE_OPENAI_CHAT_DEPLOYMENT")
        print("  - AZURE_OPENAI_EMBED_DEPLOYMENT")

if __name__ == "__main__":
    asyncio.run(main())

