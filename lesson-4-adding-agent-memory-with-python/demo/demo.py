# demo.py - Sports Analyst Agent Memory Management Demo
"""
Sports Analyst Agent Memory Management Demo

This demo showcases:
- Short-term memory implementation for sports analysis
- Memory persistence and context management
- Sports analyst agent with memory capabilities
- Pydantic model validation
- Structured JSON output generation
"""

import asyncio
import logging
from main import create_kernel, run_memory_demo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main demo function"""
    try:
        logger.info("=" * 80)
        logger.info("🏀 Sports Analyst Agent Memory Management Demo")
        logger.info("=" * 80)
        
        # Create the kernel
        logger.info("🚀 Creating Semantic Kernel...")
        kernel = create_kernel()
        
        # Run the memory demo
        logger.info("🎭 Starting memory demo scenarios...")
        await run_memory_demo(kernel)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Demo completed successfully!")
        logger.info("🎉 All memory features demonstrated!")
        logger.info("🧠 Sports analyst agent memory capabilities showcased!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
