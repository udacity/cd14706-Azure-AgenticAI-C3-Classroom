#!/usr/bin/env python3
"""
Demo script for Lesson 10: Evaluating Agents with Python - Sports Analyst Agent

This script demonstrates the key learning objectives:
- Evaluate sports analyst agent performance using rule-based evaluation
- Demonstrate LLM-as-Judge evaluation for sports analysis queries
- Show comprehensive evaluation reporting and metrics
- Test different types of sports analysis queries and responses
"""

import asyncio
import logging
import os
from typing import Dict, Any, List

from eval.judge import evaluate, TEST_CASES
from eval.llm_judge import LLMJudge
from eval.agent_runtime import MockAgent

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from dotenv import load_dotenv
load_dotenv()

import nest_asyncio
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sports_analyst_demo")

# -------------------- RULE-BASED EVALUATION --------------------

def run_rule_based_evaluation() -> List[Dict[str, Any]]:
    """Run rule-based evaluation on sports analyst agent test cases"""
    print("\n" + "=" * 80)
    print("🔍 Rule-Based Evaluation - Sports Analyst Agent")
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

# -------------------- LLM-AS-JUDGE EVALUATION --------------------

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

async def run_llm_judge_evaluation() -> Dict[str, Any] | None:
    """Run LLM-as-Judge evaluation on sports analyst agent test cases"""
    print("\n" + "=" * 80)
    print("⚖️  LLM-as-Judge Evaluation - Sports Analyst Agent")
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
            "structured_output": agent_resp.model_dump(),
            "tool_calls": [{"name": t, "arguments": {}} for t in agent_resp.tools_used],
            "citations": [],
            "reference_facts": [f"Sports analysis reference for '{qtype}'"]
        })

    print(f"🔄 Running LLM judge on {len(llm_cases)} sports analysis cases...")
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

# -------------------- COMBINED REPORT --------------------

def combined_evaluation_report(rule_results: List[Dict[str, Any]], llm_results: Dict[str, Any] | None):
    """Generate comprehensive evaluation report for sports analyst agent"""
    print("\n" + "=" * 80)
    print("📒 Sports Analyst Agent - Combined Evaluation Report")
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
        
        if overall >= 0.8:
            print(f"   Status: ✅ EXCELLENT - Sports analyst agent performing very well")
        elif overall >= 0.6:
            print(f"   Status: ✅ GOOD - Sports analyst agent performing adequately")
        elif overall >= 0.4:
            print(f"   Status: ⚠️ FAIR - Sports analyst agent needs improvement")
        else:
            print(f"   Status: ❌ POOR - Sports analyst agent requires significant improvement")
    else:
        print("⚠️  LLM judge skipped; overall reflects rule-based only.")
    
    print(f"\n💡 Sports Analyst Agent Recommendations:")
    if rule_pass < len(rule_results):
        print(f"   • Improve sports analysis response structure and tool usage")
    if llm_results and llm_results.get('average_score', 0) < 3.0:
        print(f"   • Enhance sports analysis accuracy and depth")
    print(f"   • Add more comprehensive sports statistics and insights")
    print(f"   • Implement real-time sports data integration")
    print(f"   • Consider adding predictive analytics capabilities")

# -------------------- MAIN DEMO FUNCTION --------------------

async def demo_sports_analyst_evaluation():
    """
    Demonstrate sports analyst agent evaluation using multiple methods.
    This showcases the core learning objectives of the lesson.
    """
    print("🏈 Lesson 10: Evaluating Agents with Python - Sports Analyst Agent")
    print("=" * 80)
    print("🎯 Learning Objectives:")
    print("   • Evaluate sports analyst agent performance using rule-based evaluation")
    print("   • Demonstrate LLM-as-Judge evaluation for sports analysis queries")
    print("   • Show comprehensive evaluation reporting and metrics")
    print("   • Test different types of sports analysis queries and responses")
    print("=" * 80)
    
    try:
        # Run rule-based evaluation
        rule_results = run_rule_based_evaluation()
        
        # Run LLM-as-Judge evaluation
        llm_results = await run_llm_judge_evaluation()
        
        # Generate combined report
        combined_evaluation_report(rule_results, llm_results)
        
        print(f"\n🏆 Sports Analyst Agent Evaluation Demo Complete!")
        print("=" * 80)
    print("✅ Key Learning Objectives Achieved:")
        print("   ✓ Evaluated sports analyst agent performance using rule-based evaluation")
        print("   ✓ Demonstrated LLM-as-Judge evaluation for sports analysis queries")
        print("   ✓ Showed comprehensive evaluation reporting and metrics")
        print("   ✓ Tested different types of sports analysis queries and responses")
        print("   ✓ Applied evaluation techniques to sports analytics domain")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Sports analyst evaluation demo failed: {e}")
        print(f"\n❌ Error: {e}")
        print("Please check your environment variables and Azure OpenAI connection.")
        print("\nRequired environment variables:")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_API_VERSION")
        print("  - AZURE_OPENAI_KEY")
        print("  - AZURE_OPENAI_CHAT_DEPLOYMENT")

async def main():
    """Main function to run the sports analyst evaluation demonstration"""
    try:
        await demo_sports_analyst_evaluation()
    except Exception as e:
        logger.error(f"❌ Sports analyst evaluation demo failed: {e}")
        print(f"\n❌ Error: {e}")
        print("Please check your environment variables and Azure OpenAI connection.")
        print("\nRequired environment variables:")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_API_VERSION")
        print("  - AZURE_OPENAI_KEY")
        print("  - AZURE_OPENAI_CHAT_DEPLOYMENT")

if __name__ == "__main__":
    asyncio.run(main())

