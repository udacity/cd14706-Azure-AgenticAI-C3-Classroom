#!/usr/bin/env python3
"""
Lesson 10: Evaluating Agents with Python – Runner

This script:
- runs the rule-based evaluator (judge.py) on canned test cases
- runs the LLM-as-judge (ll_judge.py) on the same inputs
- prints a concise report

Requires:
- judge.py  (importing run_request from agent_runtime.py)
- ll_judge.py
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
    print("\n" + "=" * 80)
    print("🔍 Rule-Based Evaluation")
    print("=" * 80)

    results: List[Dict[str, Any]] = []
    total = len(TEST_CASES)
    passed = 0

    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n📋 Test {i}/{total}: {case['name']}")
        print(f"   Query: {case['input']['query']}")
        print(f"   Type : {case['input']['query_type']}")
        outcome = evaluate(case)
        results.append({**case["input"], **outcome})

        ok = all([
            outcome.get("valid_json", False),
            outcome.get("has_structured_data", False),
            outcome.get("has_tools_used", False),
            outcome.get("appropriate_tools", False),
        ])
        print(f"   {'✅ PASSED' if ok else '❌ FAILED'}")
        for k, v in outcome.items():
            print(f"   {'✅' if v else '❌'} {k}: {v}")
        if ok:
            passed += 1

    print("\n📊 Rule-Based Summary")
    print(f"   Passed {passed}/{total}  ({(passed/total)*100:.1f}%)")
    return results


# -------------------- LLM-AS-JUDGE --------------------

def _maybe_create_kernel() -> Kernel | None:
    """Return a Kernel with Azure OpenAI chat service if env is configured, else None."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

    if not all([endpoint, key, deployment]):
        logger.warning("Azure OpenAI env vars missing; skipping LLM-as-judge.")
        return None

    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(
        deployment_name=deployment,
        endpoint=endpoint,
        api_key=key,
        api_version=api_version,
    ))
    return kernel


async def run_llm_judge() -> Dict[str, Any] | None:
    print("\n" + "=" * 80)
    print("⚖️  LLM-as-Judge Evaluation")
    print("=" * 80)

    kernel = _maybe_create_kernel()
    if kernel is None:
        print("⚠️  LLM judge skipped (missing Azure OpenAI configuration).")
        return None

    judge = LLMJudge(kernel)
    agent = MockAgent()

    # Prepare LLM judge inputs by actually calling the (mock) agent
    llm_cases: List[Dict[str, Any]] = []
    for case in TEST_CASES:
        query = case["input"]["query"]
        qtype = case["input"]["query_type"]
        agent_resp = await agent.process_query(query, qtype)

        llm_cases.append({
            "user_query": query,
            "agent_response": agent_resp.human_readable_response,
            "structured_output": agent_resp.model_dump(),  # pydantic BaseModel -> dict
            "tool_calls": [{"name": t, "arguments": {}} for t in agent_resp.tools_used],
            "citations": [],  # none in this mock
            "reference_facts": [f"Reference hint for '{qtype}'"]  # optional
        })

    print(f"🔄 Running LLM judge on {len(llm_cases)} cases...")
    batch = await judge.evaluate_batch(llm_cases)

    if "error" in batch:
        print(f"❌ LLM-as-judge failed: {batch['error']}")
        return None

    print("\n📊 LLM-as-Judge Summary")
    print(f"   Total: {batch['total_cases']}")
    print(f"   Avg Score: {batch['average_score']:.2f}/5.0")
    print(f"   Pass Rate: {batch['pass_rate']:.1f}%")
    for i, r in enumerate(batch["results"], 1):
        ev = r["evaluation"]
        status = "✅ PASSED" if ev.passed else "❌ FAILED"
        print(f"   Case {i}: {status}  (Score {ev.overall_score:.2f})")

    return batch


# -------------------- REPORT --------------------

def combined_report(rule_results: List[Dict[str, Any]], llm_results: Dict[str, Any] | None):
    print("\n" + "=" * 80)
    print("📒 Combined Report")
    print("=" * 80)

    rule_pass = sum(1 for r in rule_results if all([
        r.get("valid_json"), r.get("has_structured_data"),
        r.get("has_tools_used"), r.get("appropriate_tools")
    ]))
    rule_rate = (rule_pass / len(rule_results)) * 100 if rule_results else 0.0

    print(f"🔍 Rule-based pass rate: {rule_rate:.1f}%")

    if llm_results:
        print(f"⚖️  LLM judge avg score: {llm_results['average_score']:.2f}/5.0")
        print(f"⚖️  LLM judge pass rate: {llm_results['pass_rate']:.1f}%")
        overall = (rule_rate / 100 + llm_results['pass_rate'] / 100) / 2
        print(f"\n🎯 Overall blended score: {overall:.2f}")
    else:
        print("⚠️  LLM judge skipped; overall reflects rule-based only.")


# -------------------- ENTRY --------------------

async def _amain():
    print("🚀 Lesson 10 – Evaluation demo")
    rule = run_rule_based()
    llm = await run_llm_judge()
    combined_report(rule, llm)
    print("\n✅ Done. CSV from rule-based saved by judge.py (eval/results.csv).")

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_amain())

if __name__ == "__main__":
    main()
