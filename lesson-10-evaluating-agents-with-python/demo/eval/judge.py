import csv
from eval.agent_runtime import run_request
from pydantic import ValidationError

# Define test scenarios for sports analyst agent
TEST_CASES = [
    {
        "name": "Player Statistics Query",
        "input": {
            "query": "What are LeBron James' stats this season?",
            "query_type": "player_stats"
        }
    },
    {
        "name": "Team Performance Query",
        "input": {
            "query": "How is the Lakers' performance this season?",
            "query_type": "team_performance"
        }
    },
    {
        "name": "Game Analysis Query",
        "input": {
            "query": "Analyze the Lakers vs Warriors game from last night",
            "query_type": "game_analysis"
        }
    },
    {
        "name": "General Sports Query",
        "input": {
            "query": "What's the latest news in basketball?",
            "query_type": "general"
        }
    }
]

def evaluate(case):
    try:
        response = run_request(**case["input"])
        
        # Check if response is valid and has required fields
        valid_json = response is not None
        has_structured_data = hasattr(response, 'structured_data') and response.structured_data is not None
        has_tools_used = hasattr(response, 'tools_used') and len(response.tools_used) > 0
        has_confidence_score = hasattr(response, 'confidence_score') and response.confidence_score > 0
        
        # Check for appropriate tool usage based on query type
        query_type = case["input"].get("query_type", "")
        appropriate_tools = False
        
        if query_type == "player_stats" and any("player" in tool.lower() or "stats" in tool.lower() for tool in response.tools_used):
            appropriate_tools = True
        elif query_type == "team_performance" and any("team" in tool.lower() or "performance" in tool.lower() for tool in response.tools_used):
            appropriate_tools = True
        elif query_type == "game_analysis" and any("game" in tool.lower() or "analysis" in tool.lower() for tool in response.tools_used):
            appropriate_tools = True
        elif query_type == "general":
            appropriate_tools = True  # General queries can use any tools
        
        return {
            "valid_json": valid_json,
            "has_structured_data": has_structured_data,
            "has_tools_used": has_tools_used,
            "has_confidence_score": has_confidence_score,
            "appropriate_tools": appropriate_tools
        }
    except (ValidationError, Exception) as e:
        print(f"❌ Failed to parse agent output: {e}")
        return {
            "valid_json": False,
            "has_structured_data": False,
            "has_tools_used": False,
            "has_confidence_score": False,
            "appropriate_tools": False
        }

def main():
    results = []
    
    for case in TEST_CASES:
        print(f"Running test: {case['name']}")
        outcome = evaluate(case)
        print(f"Test outcome: {outcome}")
        results.append({**case["input"], **outcome})
    
    # Write results to CSV
    with open("eval/results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    print("Evaluation complete. Results saved to eval/results.csv")

if __name__ == "__main__":
    main()