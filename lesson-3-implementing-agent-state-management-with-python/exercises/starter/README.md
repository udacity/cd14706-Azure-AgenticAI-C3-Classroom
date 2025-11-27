# Exercise: Implement Agent State Management with State Machine

Build a customer service agent with a finite state machine that manages workflow through defined phases.

## Prerequisites

* Familiarity with Semantic Kernel functions and invocation
* Comfort defining enums/classes and handling JSON parsing
* Understanding of structured output validation with Pydantic

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file with Azure OpenAI credentials
3. Run: `python main.py`

## Code Structure

```
├── main.py              # Main implementation (fully implemented)
├── state.py             # Agent state management (with 2 TODOs for phase descriptions)
├── models.py            # Pydantic models for structured outputs
├── tools/               # Semantic Kernel tools
│   ├── order_status.py     # Order status lookup tool
│   └── product_info.py     # Product information tool
└── requirements.txt     # Dependencies
```

## Tasks

Your task is to add phase descriptions in `state.py`:

1. **Add Phase descriptions to the `Phase` enum**: Define descriptive comments for all 8 phases (Init, ClarifyRequirements, PlanTools, ExecuteTools, AnalyzeResults, ResolveIssues, ProduceStructuredOutput, Done)

2. **Add Phase descriptions to `get_phase_description()` method**: Populate the `descriptions` dictionary with human-readable descriptions for each phase

All other functionality (state transitions, tool execution, auto-progression, etc.) is already fully implemented.

## Example Scenarios

Your implementation should handle scenarios like:

**Order Status Query:**
- Customer: "I need to check on my order"
- Agent: "What's your order ID?"
- Customer: "ORD-2024-001"
- Expected: Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ProduceStructuredOutput → Done

**Product Information Query:**
- Customer: "Tell me about product PROD-123"
- Expected: Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ProduceStructuredOutput → Done

## Tools Reference

- **OrderStatusTools**: Looks up order status by order_id. Returns order status, tracking number, estimated delivery
- **ProductInfoTools**: Retrieves product information by product_id. Returns name, price, availability, stock quantity
