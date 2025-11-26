#!/usr/bin/env python3
"""
Lesson 10: Evaluating Agents with Python – Runner

This script:
- runs the rule-based evaluator (judge.py) on canned test cases
- runs the LLM-as-judge (llm_judge.py) on the same inputs
- prints a concise report

Requires:
- judge.py  (importing run_request from agent_runtime.py)
- llm_judge.py
- agent_runtime.py (provided below)
"""

import asyncio
import logging
import os
from typing import Dict, Any, List

from eval.judge import evaluate, TEST_CASES                  # rule-based
from eval.llm_judge import LLMJudge                           # LLM-as-judge
from eval.agent_runtime import MockAgent                     # our mock agent for LLM judge

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from dotenv import load_dotenv
load_dotenv()

import nest_asyncio
nest_asyncio.apply()



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("runner")


# -------------------- RULE-BASED --------------------

def run_rule_based() -> List[Dict[str, Any]]:
    # TODO: Implement run_rule_based()
    # 1. Print header with "Rule-Based Evaluation"
    # 2. Initialize results list, total count, and passed counter
    # 3. Loop through TEST_CASES with enumerate(TEST_CASES, 1):
    #    a. Print test number, name, query, and query_type
    #    b. Call evaluate(case) to get outcome
    #    c. Append {**case["input"], **outcome} to results
    #    d. Check if all criteria pass: valid_json, has_structured_data, has_tools_used, appropriate_tools
    #    e. Print PASSED or FAILED status
    #    f. Print each outcome criterion with checkmark/X
    #    g. If passed, increment passed counter
    # 4. Print summary: "Passed X/Y (Z%)"
    # 5. Return results list
    pass


# -------------------- LLM-AS-JUDGE --------------------

def _maybe_create_kernel() -> Kernel | None:
    # TODO: Implement _maybe_create_kernel()
    # 1. Get environment variables:
    #    - AZURE_OPENAI_ENDPOINT
    #    - AZURE_OPENAI_KEY
    #    - AZURE_OPENAI_API_VERSION (default: "2024-02-15-preview")
    #    - AZURE_OPENAI_CHAT_DEPLOYMENT
    # 2. Check if all required vars (endpoint, key, deployment) exist
    # 3. If not all present:
    #    - Log warning: "Azure OpenAI env vars missing; skipping LLM-as-judge."
    #    - Return None
    # 4. Otherwise:
    #    - Create Kernel instance
    #    - Add AzureChatCompletion service with the env vars
    #    - Return the kernel
    pass


async def run_llm_judge() -> Dict[str, Any] | None:
    # TODO: Implement run_llm_judge()
    # 1. Print header with "LLM-as-Judge Evaluation"
    # 2. Call _maybe_create_kernel() to get kernel
    # 3. If kernel is None:
    #    - Print warning: "LLM judge skipped (missing Azure OpenAI configuration)."
    #    - Return None
    # 4. Create LLMJudge instance with kernel
    # 5. Create MockAgent instance
    # 6. Build llm_cases list:
    #    - Loop through TEST_CASES
    #    - For each case, extract query and query_type
    #    - Call: agent_resp = await agent.process_query(query, qtype)
    #    - Append dict to llm_cases with:
    #      * "user_query": query
    #      * "agent_response": agent_resp.human_readable_response
    #      * "structured_output": agent_resp.model_dump()
    #      * "tool_calls": [{"name": t, "arguments": {}} for t in agent_resp.tools_used]
    #      * "citations": []
    #      * "reference_facts": [f"Reference hint for '{qtype}'"]
    # 7. Print: "Running LLM judge on X cases..."
    # 8. Call: batch = await judge.evaluate_batch(llm_cases)
    # 9. If "error" in batch:
    #    - Print error message
    #    - Return None
    # 10. Print summary:
    #     - Total cases
    #     - Average score (formatted to 2 decimals)
    #     - Pass rate (formatted to 1 decimal)
    #     - For each result, print case number, PASSED/FAILED, and score
    # 11. Return batch
    pass


# -------------------- REPORT --------------------

def combined_report(rule_results: List[Dict[str, Any]], llm_results: Dict[str, Any] | None):
    # TODO: Implement combined_report()
    # 1. Print header with "Combined Report"
    # 2. Calculate rule_pass: count results where all 4 criteria are True
    # 3. Calculate rule_rate as percentage
    # 4. Print: "Rule-based pass rate: X.X%"
    # 5. If llm_results is not None:
    #    - Print LLM judge avg score (formatted to 2 decimals)
    #    - Print LLM judge pass rate (formatted to 1 decimal)
    #    - Calculate overall blended score: average of rule_rate/100 and llm pass_rate/100
    #    - Print: "Overall blended score: X.XX"
    # 6. Else:
    #    - Print: "LLM judge skipped; overall reflects rule-based only."
    pass


# -------------------- ENTRY --------------------

async def _amain():
    # TODO: Implement _amain()
    # 1. Print: "Lesson 10 – Evaluation demo"
    # 2. Call run_rule_based() and store in rule variable
    # 3. Call await run_llm_judge() and store in llm variable
    # 4. Call combined_report(rule, llm)
    # 5. Print: "Done. CSV from rule-based saved by judge.py (eval/results.csv)."
    pass

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_amain())

if __name__ == "__main__":
    main()
