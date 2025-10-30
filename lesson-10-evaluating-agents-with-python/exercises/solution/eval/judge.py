import csv
from eval.agent_runtime import run_request
from pydantic import ValidationError

# Define test scenarios for e-commerce customer service agent
TEST_CASES = [
    {
        "name": "Order Status Query",
        "input": {
            "query": "What's the status of my order ORD-001?",
            "query_type": "order_status"
        }
    },
    {
        "name": "Product Information Query",
        "input": {
            "query": "Tell me about product PROD-001",
            "query_type": "product_info"
        }
    },
    {
        "name": "Product Recommendations Query",
        "input": {
            "query": "Can you recommend some products similar to PROD-002?",
            "query_type": "recommendations"
        }
    },
    {
        "name": "General Customer Service Query",
        "input": {
            "query": "I need help with my recent purchase",
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
        
        if query_type == "order_status" and any("order" in tool.lower() for tool in response.tools_used):
            appropriate_tools = True
        elif query_type == "product_info" and any("product" in tool.lower() for tool in response.tools_used):
            appropriate_tools = True
        elif query_type == "recommendations" and any("recommendation" in tool.lower() for tool in response.tools_used):
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