# Exercise

Add a rule‑based evaluator and an optional LLM‑as‑judge path, then produce a combined report comparing both.

### **Prerequisites**

* Ability to write small evaluation functions and print reports

* Optional: Azure OpenAI configured for LLM judge

* Lessons 1–9 completed

### **Instructions**

1. Implement `run_rule_based()` that iterates `TEST_CASES`, calls `evaluate(case)`, prints per‑case pass/fail and criteria flags, and returns the list of outcomes.

2. Implement `_maybe_create_kernel()` that returns a configured `Kernel` with `AzureChatCompletion` only when `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, and `AZURE_OPENAI_CHAT_DEPLOYMENT` are available; otherwise return `None` and log a warning.

3. Implement `run_llm_judge()`:
   - Call `_maybe_create_kernel()` and skip if it returns `None`.
   - Build `llm_cases` by calling `MockAgent().process_query(query, query_type)` per test to capture a realistic agent output; include `human_readable_response`, `structured_output` (as dict), `tool_calls`, and optional reference facts.
   - Invoke `LLMJudge(kernel).evaluate_batch(llm_cases)` and print a brief summary (total, average score, pass rate, per‑case status).

4. Implement `combined_report(rule_results, llm_results)` to print the rule‑based pass rate and, if available, LLM judge averages and a blended score.

5. In `_amain()`, run the rule‑based evaluator, then the LLM judge, and pass both to `combined_report(...)`. Ensure the script prints a final done message.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`