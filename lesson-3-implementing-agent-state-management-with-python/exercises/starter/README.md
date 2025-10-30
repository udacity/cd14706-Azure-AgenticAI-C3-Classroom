# Exercise

Implement a finite state machine to manage the agent workflow, add a state-aware prompt, update state from LLM JSON, and execute tools based on requirements until reaching Done.

### **Prerequisites**

* Familiarity with Semantic Kernel functions and invocation

* Comfort defining enums/classes and handling JSON parsing

* Lesson 2 structured output validation completed

### **Instructions**

1. Create a `Phase` enum and an `AgentState` class (in `state.py`) to track `phase`, `session_id`, `requirements`, `tools_called`, `issues`, `data_completeness`, and timestamps.

2. In `create_state_aware_prompt(state)`, build a base prompt that interpolates the current state (phase, description, completeness, tools, issues) and appends phase‑specific guidance, followed by a strict JSON response schema that includes `next_phase` and `state_updates`.

3. In `process_state_transition(...)`, construct the state‑aware prompt, add a SK function (`state_processor`), invoke it, then extract the JSON substring and parse it into `response_data`.

4. Implement `update_agent_state(...)` to:
   - Set required fields from `query_type`.
   - Merge `requirements`, `issues`, and `clarification_questions` from `state_updates`.
   - Record `tools_used` into `state.tools_called`.
   - Apply `next_phase` if valid; otherwise advance intelligently or call `advance_state_automatically`.

5. Implement `advance_state_automatically(...)` to progress through phases (Init → ClarifyRequirements → PlanTools → ExecuteTools → AnalyzeResults → ResolveIssues/ProduceStructuredOutput → Done) based on response data and issues.

6. Implement `execute_tools_for_state(...)` to call `OrderStatusTools` and/or `ProductInfoTools` using collected `requirements`, storing results back on the state for analysis.

7. In `run_state_machine_demo(...)`, iterate the provided scenarios, calling `process_state_transition(...)` for each utterance; if `state.phase == Phase.ExecuteTools`, call `execute_tools_for_state(...)`; break when `Phase.Done` is reached.

8. Keep the kernel setup and lesson 2 validation in place; ensure the new state functions are imported and exercised from `main()`.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`}ёв```}어요