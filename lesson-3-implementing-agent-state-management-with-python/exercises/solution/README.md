# Exercise Solution

[VIDEO_PLACEHOLDER: Agent State Machine for Customer Support]

### **Solution Walkthrough**

We introduce a state machine so the agent progresses through phases (Init → Clarify → PlanTools → ExecuteTools → AnalyzeResults → ResolveIssues → ProduceStructuredOutput → Done). The prompt becomes state-aware to drive targeted behavior.

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

We parse the model's JSON to update `AgentState` (requirements, issues, next phase) and auto-advance when needed.

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

### **Key Takeaway**

> The solution adds a state machine that structures tool planning, execution, and validation into reliable phases.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
