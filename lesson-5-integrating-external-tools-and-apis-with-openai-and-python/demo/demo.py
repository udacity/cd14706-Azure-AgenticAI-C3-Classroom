# demo.py - Sports Analyst Agent with External APIs Demo Runner
"""
Simple demo runner for the Sports Analyst Agent with External APIs

This file provides a simple way to run the sports analyst demo
without needing to understand the full implementation.
"""

from main import main

if __name__ == "__main__":
    print("🏀 Starting Sports Analyst Agent with External APIs Demo")
    print("=" * 60)
    print("This demo showcases:")
    print("  • External API integration for sports data")
    print("  • Memory management for sports conversations")
    print("  • Real-time sports news and analytics")
    print("  • Team standings and player statistics")
    print("=" * 60)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("Please check your environment variables and try again.")
