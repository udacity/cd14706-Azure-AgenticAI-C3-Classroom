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
├── main.py              # Main implementation (with TODOs)
├── state.py             # Agent state management (with TODOs)
├── models.py            # Pydantic models for structured outputs
├── tools/               # Semantic Kernel tools
│   ├── order_status.py     # Order status lookup tool
│   └── product_info.py     # Product information tool
└── requirements.txt     # Dependencies
```

## Tasks

1. **Complete the `Phase` enum** (in `state.py`): Define all 8 phases for the state machine workflow

2. **Implement phase transition tracking** (in `state.py`): Add phase history tracking with timestamps and triggers

3. **Build state-aware prompt** (in `main.py`): Implement `create_state_aware_prompt(state)` that includes current state information and phase-specific instructions

4. **Handle state transitions** (in `main.py`): Implement `process_state_transition(...)` to invoke LLM with state-aware prompt and parse JSON response

5. **Update agent state** (in `main.py`): Implement `update_agent_state(...)` to:
   - Set required fields from query_type
   - Merge requirements, issues, and clarification_questions from state_updates
   - Record tools_used
   - Handle next_phase transitions

6. **Implement automatic state progression** (in `main.py`): Implement `advance_state_automatically(...)` to progress through phases based on response data and issues

7. **Execute tools based on state** (in `main.py`): Implement `execute_tools_for_state(...)` to call OrderStatusTools and ProductInfoTools using collected requirements

8. **Run state machine demo** (in `main.py`): Implement `run_state_machine_demo(...)` to iterate through scenarios and process state transitions

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
