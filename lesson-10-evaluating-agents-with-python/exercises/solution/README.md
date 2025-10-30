# Exercise Solution

[VIDEO_PLACEHOLDER: Evaluating Agents — Rule-Based and LLM-as-Judge]

### **Solution Walkthrough**

We add a rule-based evaluator that checks structural criteria against canned cases, and an optional LLM-as-judge path if Azure OpenAI is configured.

```python
# Rule-based evaluation (excerpt)
from eval.judge import evaluate, TEST_CASES
results = []
for case in TEST_CASES:
    outcome = evaluate(case)
    results.append({**case["input"], **outcome})
```

The LLM judge is created only when environment vars exist; otherwise we skip gracefully.

```python
# Conditional kernel setup for LLM-as-judge
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
key = os.getenv("AZURE_OPENAI_KEY")
if all([endpoint, key, os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")]):
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(...))
else:
    kernel = None  # judge skipped
```

We then prepare structured cases using a mock agent and ask the LLM judge to score them, emitting a concise report.

```python
agent = MockAgent()
llm_cases = []
for case in TEST_CASES:
    agent_resp = await agent.process_query(case["input"]["query"], case["input"]["query_type"])
    llm_cases.append({
        "user_query": case["input"]["query"],
        "agent_response": agent_resp.human_readable_response,
        "structured_output": agent_resp.model_dump(),
        "tool_calls": [{"name": t, "arguments": {}} for t in agent_resp.tools_used],
        "citations": [],
        "reference_facts": [f"Reference hint for '{case['input']['query_type']}'"],
    })
```

```
📊 Combined report shows rule-based pass rate and LLM judge metrics
```

[IMAGE_PLACEHOLDER: Screengrab of terminal report for both evaluators]

### **Key Takeaway**

> The solution adds automated evaluation via rules and (optionally) an LLM judge, producing a compact report for quick comparison.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
