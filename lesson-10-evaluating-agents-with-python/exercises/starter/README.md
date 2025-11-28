# Exercise

Implement the rule-based evaluation logic in `eval/judge.py` to validate agent responses.

### **Prerequisites**

* Understanding of Pydantic models and response validation
* Familiarity with Python dictionaries and boolean logic
* Lessons 1–9 completed

### **Instructions**

In `eval/judge.py`, complete the `evaluate()` function:

1.  **Check response validity** (line 42):
    *   Determine if the `response` object itself is not `None`.

2.  **Check structured data** (line 43):
    *   Verify if the `response` has a `structured_data` attribute and if that attribute is not `None`.

3.  **Check tools used** (line 44):
    *   Ascertain if the `response` has a `tools_used` attribute and if the list of `tools_used` is not empty.

4.  **Check confidence score** (line 45):
    *   Confirm if the `response` has a `confidence_score` attribute and if its value is greater than 0.

5.  **Return evaluation results** (line 61):
    *   Construct a dictionary that includes all five boolean evaluation fields: `valid_json`, `has_structured_data`, `has_tools_used`, `has_confidence_score`, and `appropriate_tools`.


### **Running the Exercise**

After implementing the TODOs in `judge.py`, run:

```bash
python main.py
```

You should see:
- Rule-based evaluation results for 4 test cases
- LLM-as-judge evaluation (if Azure OpenAI is configured)
- Combined report with pass rates

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`
