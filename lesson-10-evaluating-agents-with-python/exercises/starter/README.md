# Exercise

Implement the rule-based evaluation logic in `eval/judge.py` to validate agent responses.

### **Prerequisites**

* Understanding of Pydantic models and response validation
* Familiarity with Python dictionaries and boolean logic
* Lessons 1–9 completed

### **Instructions**

In `eval/judge.py`, complete the `evaluate()` function:

1. **Check response validity** (line 42):
   - Set `valid_json = response is not None`

2. **Check structured data** (line 43):
   - Set `has_structured_data = hasattr(response, 'structured_data') and response.structured_data is not None`

3. **Check tools used** (line 44):
   - Set `has_tools_used = hasattr(response, 'tools_used') and len(response.tools_used) > 0`

4. **Check confidence score** (line 45):
   - Set `has_confidence_score = hasattr(response, 'confidence_score') and response.confidence_score > 0`

5. **Return evaluation results** (line 61):
   - Return a dictionary with all five boolean fields:
     ```python
     return {
         "valid_json": valid_json,
         "has_structured_data": has_structured_data,
         "has_tools_used": has_tools_used,
         "has_confidence_score": has_confidence_score,
         "appropriate_tools": appropriate_tools
     }
     ```

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
