# Exercise Solution

[VIDEO_PLACEHOLDER: Evaluating Agents — Rule-Based Evaluation]

### **Solution Walkthrough**

The solution implements rule-based evaluation logic in `eval/judge.py` to validate agent responses against specific criteria.

#### **Step 1: Check Response Validity**

```python
valid_json = response is not None
```

This checks if the agent returned a valid response object (not None).

#### **Step 2: Check Structured Data**

```python
has_structured_data = hasattr(response, 'structured_data') and response.structured_data is not None
```

This verifies that the response has a `structured_data` attribute and it's not empty.

#### **Step 3: Check Tools Used**

```python
has_tools_used = hasattr(response, 'tools_used') and len(response.tools_used) > 0
```

This confirms the agent used at least one tool to answer the query.

#### **Step 4: Check Confidence Score**

```python
has_confidence_score = hasattr(response, 'confidence_score') and response.confidence_score > 0
```

This validates that the agent provided a confidence score greater than 0.

#### **Step 5: Return Evaluation Results**

```python
return {
    "valid_json": valid_json,
    "has_structured_data": has_structured_data,
    "has_tools_used": has_tools_used,
    "has_confidence_score": has_confidence_score,
    "appropriate_tools": appropriate_tools
}
```

The function returns a dictionary with all five boolean evaluation criteria.

### **Expected Output**

When you run `python main.py`, you should see:

```
🚀 Lesson 10 – Evaluation demo

================================================================================
🔍 Rule-Based Evaluation
================================================================================

📋 Test 1/4: Order Status Query
   Query: What's the status of my order ORD-001?
   Type : order_status
   ✅ PASSED
   ✅ valid_json: True
   ✅ has_structured_data: True
   ✅ has_tools_used: True
   ✅ has_confidence_score: True
   ✅ appropriate_tools: True

[... similar for tests 2-4 ...]

📊 Rule-Based Summary
   Passed 4/4  (100.0%)

================================================================================
⚖️  LLM-as-Judge Evaluation
================================================================================
🔄 Running LLM judge on 4 cases...

📊 LLM-as-Judge Summary
   Total: 4
   Avg Score: 3.95/5.0
   Pass Rate: 100.0%
   Case 1: ✅ PASSED  (Score 4.00)
   Case 2: ✅ PASSED  (Score 4.00)
   Case 3: ✅ PASSED  (Score 4.00)
   Case 4: ✅ PASSED  (Score 3.80)

================================================================================
📒 Combined Report
================================================================================
🔍 Rule-based pass rate: 100.0%
⚖️  LLM judge avg score: 3.95/5.0
⚖️  LLM judge pass rate: 100.0%

🎯 Overall blended score: 1.00

✅ Done. CSV from rule-based saved by judge.py (eval/results.csv).
```

[IMAGE_PLACEHOLDER: Screengrab of terminal showing evaluation output]

### **Key Takeaway**

> The solution demonstrates how to implement rule-based evaluation criteria to validate agent responses systematically. Combined with LLM-as-judge, this provides comprehensive quality assurance for AI agents.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
