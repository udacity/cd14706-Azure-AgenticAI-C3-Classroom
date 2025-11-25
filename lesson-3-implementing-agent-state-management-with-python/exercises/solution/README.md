# Exercise Solution: Agent State Management with State Machine

[VIDEO_PLACEHOLDER: Agent State Machine for Customer Support]

### **Solution Walkthrough**

This solution implements a state machine where the agent progresses through phases (Init → Clarify → PlanTools → ExecuteTools → AnalyzeResults → ResolveIssues → ProduceStructuredOutput → Done). The prompt is state-aware to drive targeted behavior.

```python
# State-aware prompt (excerpt)
base_prompt = """
You are a helpful customer service agent ...
Current session state:
- Phase: {phase}
- Phase Description: {phase_description}
- Session ID: {session_id}
- Data Completeness: {data_completeness:.1%}
- Tools Called: {tools_called}
- Issues: {issues}

Based on the current state, respond appropriately:
"""
```

The solution parses the model's JSON to update `AgentState` (requirements, issues, next phase) and auto-advances when needed.

```python
# Update state from model response (excerpt)
updates = response_data.get("state_updates", {})
if "requirements" in updates:
    state.set_requirements(updates["requirements"])
if "issues" in updates:
    for issue in updates["issues"]:
        state.add_issue(issue)
next_phase = response_data.get("next_phase")
if next_phase:
    state.phase = phase_map.get(next_phase, state.phase)
else:
    advance_state_automatically(state, response_data)
```

During `ExecuteTools`, the agent calls tools based on collected requirements and records results for later analysis.

```python
# Execute tools for state (excerpt)
if "order_id" in state.requirements:
    result = OrderStatusTools().get_order_status(state.requirements["order_id"])
    state.add_tool_call("order_status", result)

if "product_id" in state.requirements:
    result = ProductInfoTools().get_product_info(state.requirements["product_id"])
    state.add_tool_call("product_info", result)
```

```
✅ Scenario completed — Agent reached Done state
```

[IMAGE_PLACEHOLDER: Screengrab of logs showing phase transitions and state summary]

### **State Management Features**

The solution includes comprehensive state tracking:

**Phase Transition History**
- Every state change is recorded with timestamp and explicit, descriptive trigger
- All phase changes use `transition_to()` or `advance()` - never direct phase assignment
- Track what caused each transition with detailed triggers:
  - `query_type_identified` - User's query type determined (order_status, product_info)
  - `requirements_complete` - All required fields gathered
  - `tools_planned` - Tool execution plan created
  - `tools_executed` / `auto_tools_complete` - Customer service tools completed
  - `issues_detected` - Problems found requiring resolution
  - `analysis_complete` - Analysis validated with no issues
  - `issues_resolved` - All problems successfully handled
  - `output_complete` / `output_generated` - Final structured output generated
  - `llm_suggested_{phase}` - LLM suggested specific phase transition
  - `invalid_phase_suggestion` - LLM suggestion invalid, using fallback
  - `error_fallback` - Exception occurred, using recovery path
- Get human-readable timeline with `state.get_transition_summary()`

```python
# Example transition history
State Transition Timeline:
============================================================
1. Init                      (initialized) at 14:32:01
2. Init                      → ClarifyRequirements      (query_type_identified) at 14:32:02
3. ClarifyRequirements       → PlanTools                (requirements_complete) at 14:32:03
4. PlanTools                 → ExecuteTools             (tools_planned) at 14:32:03
5. ExecuteTools              → AnalyzeResults           (tools_executed) at 14:32:04
6. AnalyzeResults            → ProduceStructuredOutput  (analysis_complete) at 14:32:04
7. ProduceStructuredOutput   → Done                     (output_generated) at 14:32:04
============================================================
Total transitions: 7
Session duration: 3.2s
```

**State Debugging**
- `state.snapshot()` - Get complete state for inspection
- `state.print_snapshot()` - Print formatted state summary
- `state.get_phase_duration(phase)` - Calculate time spent in each phase
- `state.advance(trigger="auto_advance")` - Progress to next phase with optional trigger recording
- `state.transition_to(phase, trigger="manual_transition")` - Explicit non-linear transitions with optional trigger

### **Code Structure**

```
├── main.py              # Main solution implementation with state machine
├── state.py             # Agent state management and state machine
├── models.py            # Pydantic models (CustomerServiceResponse, OrderResponse, ProductResponse)
├── tools/               # Semantic Kernel tools
│   ├── order_status.py     # Order status lookup tool
│   └── product_info.py     # Product information tool
└── requirements.txt     # Dependencies
```

### **Demo Scenarios**

The solution runs through three customer service scenarios:

**1. Order Status Query**
- Customer: "I need to check on my order"
- Agent: "What's your order ID?"
- Customer: "ORD-2024-001"
- State progression: Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ProduceStructuredOutput → Done

**2. Product Information Query**
- Customer: "Tell me about a product"
- Agent: "Which product ID are you interested in?"
- Customer: "PROD-123"
- State progression: Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ProduceStructuredOutput → Done

**3. Complex Multi-Step Query**
- Customer: "I have questions about my order and a product"
- Agent asks for order ID and product ID
- Executes both tools
- State progression: Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ResolveIssues → ProduceStructuredOutput → Done

### **Key Takeaways**

> This solution implements a state machine that structures tool planning, execution, and validation into reliable phases, with comprehensive tracking for debugging and analysis.

**State Management Best Practices:**
- ✅ **Always use `transition_to()` or `advance()`** - Never directly assign `state.phase` (bypasses history)
- ✅ **Provide explicit, descriptive triggers** - Avoid generic triggers like "auto_advance"
- ✅ **Track LLM suggestions** - Use `llm_suggested_{phase}` trigger when LLM suggests phase changes
- ✅ **Handle errors gracefully** - Use explicit error triggers like `error_fallback`, `invalid_phase_suggestion`
- ✅ **Complete audit trail** - Every transition should be traceable in `phase_history`

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
