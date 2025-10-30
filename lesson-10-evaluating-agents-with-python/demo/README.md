# Lesson 10: Evaluating Agents with Python

## Module Overview

**Module Title:** Evaluating Agents with Python  
**Module Type:** Implementation  
**Subskill:** Agent Evaluation and Quality Assurance with Python, OpenAI, and Reflection Patterns  
**Primary Learning Objective:** Develop comprehensive evaluation strategies for AI agents using rule-based and LLM-as-judge approaches; demonstrate the reflection pattern for iterative agent improvement based on evaluation feedback.

## Learning Objectives

By the end of this lesson, you will be able to:

1. **Implement rule-based evaluation** for AI agent responses with specific validation criteria
2. **Build LLM-as-judge systems** to evaluate agent quality using AI feedback
3. **Apply the reflection pattern** for iterative agent improvement based on evaluation results
4. **Create comprehensive test suites** for sports analyst agent capabilities
5. **Measure and track agent performance** across multiple evaluation dimensions
6. **Implement feedback loops** that enable agents to learn from their mistakes

## Key Concepts

### 1. Evaluation Approaches

#### Rule-Based Evaluation
- **Deterministic Testing**: Checks for specific, expected outputs
- **Structural Validation**: Ensures responses match required schemas
- **Tool Usage Verification**: Validates appropriate tool selection
- **Fast and Consistent**: Provides immediate, reproducible results

#### LLM-as-Judge Evaluation
- **Semantic Understanding**: Evaluates meaning and quality of responses
- **Flexible Assessment**: Adapts to different query types and contexts
- **Multi-dimensional Scoring**: Assesses accuracy, completeness, relevance, structure
- **Human-like Evaluation**: Provides nuanced feedback similar to human reviewers

### 2. The Reflection Pattern

The **reflection pattern** is a powerful technique where an agent uses evaluation feedback to iteratively improve its responses. This creates a feedback loop:

```
1. Generate Response → 2. Evaluate with LLM Judge → 3. Reflect on Feedback → 4. Regenerate Improved Response
```

**Key Benefits:**
- **Self-improvement**: Agents learn from mistakes without human intervention
- **Quality Enhancement**: Multiple iterations refine responses to meet quality standards
- **Adaptive Behavior**: Agents adjust based on specific feedback
- **Reduced Manual Review**: Automated quality assurance through self-reflection

**Implementation Strategy:**
1. Agent generates initial response
2. LLM judge evaluates response and provides detailed feedback
3. If score is below threshold, agent reflects on the feedback
4. Agent regenerates response incorporating feedback insights
5. Process repeats until quality threshold is met or max iterations reached

### 3. Evaluation Criteria

This demo evaluates sports analyst agents across six dimensions:

1. **Accuracy (25%)**: Correctness of sports statistics and analysis
2. **Completeness (20%)**: Thoroughness in addressing user query
3. **Relevance (20%)**: Pertinence to user's needs and context
4. **Tool Usage (15%)**: Appropriate selection and use of tools
5. **Structure (10%)**: Clear organization and presentation
6. **Citations (10%)**: Proper source attribution and references

### 4. Test Case Design

Effective test cases cover:
- **Player Statistics Queries**: Testing player data retrieval and analysis
- **Team Performance Queries**: Evaluating team analysis capabilities
- **Game Analysis Queries**: Assessing game-specific insights
- **General Sports Queries**: Testing broad sports knowledge

## Implementation Features

### Rule-Based Evaluator (`judge.py`)

The rule-based evaluator provides fast, deterministic validation:

```python
def evaluate(case):
    """
    Evaluates agent response against specific rules:
    - Valid JSON structure
    - Presence of structured data
    - Tool usage recorded
    - Appropriate tools for query type
    - Confidence score provided
    """
    response = run_request(**case["input"])
    
    return {
        "valid_json": response is not None,
        "has_structured_data": response.structured_data is not None,
        "has_tools_used": len(response.tools_used) > 0,
        "appropriate_tools": check_tool_appropriateness(response, case),
        "has_confidence_score": response.confidence_score > 0
    }
```

**Outputs:**
- ✅/❌ Pass/fail for each validation criterion
- CSV report with detailed results
- Summary statistics (pass rate, failure patterns)

### LLM-as-Judge System (`llm_judge.py`)

The LLM-as-judge provides nuanced, semantic evaluation:

```python
class LLMJudge:
    """
    Uses LLM to evaluate agent responses with:
    - Multi-dimensional scoring (0-5 scale per criterion)
    - Weighted overall score
    - Detailed reasoning for each score
    - Specific improvement recommendations
    - Pass/fail determination (threshold: 3.0/5.0)
    """
    
    async def evaluate_response(
        self,
        user_query: str,
        agent_response: str,
        structured_output: Dict[str, Any],
        tool_calls: List[Dict[str, Any]],
        citations: List[str],
        reference_facts: Optional[List[str]] = None
    ) -> EvaluationResult
```

**Key Features:**
- Contextual understanding of sports domain
- Identification of subtle quality issues
- Actionable improvement recommendations
- Consistent evaluation across test cases

### The Reflection Pattern Implementation

The reflection pattern enables agents to improve based on evaluation feedback:

#### Basic Reflection Loop

```python
async def generate_with_reflection(
    agent: Agent,
    judge: LLMJudge,
    query: str,
    max_iterations: int = 3,
    quality_threshold: float = 4.0
) -> Tuple[Response, EvaluationResult]:
    """
    Generate response with iterative improvement via reflection.
    
    Process:
    1. Agent generates initial response
    2. Judge evaluates and provides feedback
    3. If below threshold, agent reflects on feedback
    4. Agent regenerates improved response
    5. Repeat until quality threshold met or max iterations
    """
    
    for iteration in range(max_iterations):
        # Generate response
        response = await agent.process_query(query)
        
        # Evaluate with LLM judge
        evaluation = await judge.evaluate_response(
            user_query=query,
            agent_response=response.human_readable_response,
            structured_output=response.structured_data,
            tool_calls=response.tools_used,
            citations=[]
        )
        
        # Check if quality threshold met
        if evaluation.overall_score >= quality_threshold:
            return response, evaluation
        
        # Reflect on feedback and regenerate
        reflection_prompt = f"""
        Your previous response scored {evaluation.overall_score}/5.0.
        
        Feedback: {evaluation.reasoning}
        
        Recommendations:
        {chr(10).join(f"- {rec}" for rec in evaluation.recommendations)}
        
        Specific criterion scores:
        {json.dumps(evaluation.criteria_scores, indent=2)}
        
        Please regenerate your response addressing these issues.
        Focus especially on criteria with scores below 4.0.
        """
        
        # Agent incorporates feedback (implementation depends on agent architecture)
        response = await agent.process_query_with_reflection(
            query=query,
            reflection=reflection_prompt,
            previous_response=response
        )
    
    # Return best attempt after max iterations
    return response, evaluation
```

#### Advanced Reflection with Memory

For more sophisticated implementations, the agent can maintain memory of past reflections:

```python
class ReflectiveAgent:
    """Agent with built-in reflection capabilities"""
    
    def __init__(self):
        self.reflection_memory = []
        self.quality_threshold = 4.0
    
    async def process_with_reflection(
        self,
        query: str,
        judge: LLMJudge
    ) -> Response:
        """Process query with automatic reflection loop"""
        
        iteration = 0
        while iteration < 3:
            # Generate response (informed by previous reflections)
            response = await self._generate_response(
                query=query,
                reflection_context=self.reflection_memory
            )
            
            # Evaluate
            eval_result = await judge.evaluate_response(...)
            
            # Store evaluation in memory
            self.reflection_memory.append({
                "iteration": iteration,
                "score": eval_result.overall_score,
                "feedback": eval_result.reasoning,
                "recommendations": eval_result.recommendations
            })
            
            # Check if quality met
            if eval_result.overall_score >= self.quality_threshold:
                break
            
            iteration += 1
        
        return response
```

## Usage Examples

### Running Rule-Based Evaluation

```bash
# Run rule-based evaluation only
python -m eval.judge

# Output:
# ✅ PASSED: Player Statistics Query
# ✅ valid_json: True
# ✅ has_structured_data: True
# ✅ has_tools_used: True
# ✅ appropriate_tools: True
# 
# Results saved to eval/results.csv
```

### Running LLM-as-Judge Evaluation

```bash
# Run LLM-as-judge evaluation
python main.py

# Output:
# ⚖️ LLM-as-Judge Evaluation
# Case 1: ✅ PASSED (Score 4.2)
# Case 2: ✅ PASSED (Score 4.5)
# Case 3: ❌ FAILED (Score 2.8)
# Case 4: ✅ PASSED (Score 4.0)
#
# Avg Score: 3.9/5.0
# Pass Rate: 75.0%
```

### Running Combined Evaluation

```bash
# Run both evaluators and generate combined report
python main.py

# Output includes:
# 🔍 Rule-Based Evaluation
# ⚖️ LLM-as-Judge Evaluation
# 📒 Combined Report with blended scores
```

### Implementing Reflection Pattern

```python
# Example: Using reflection to improve response quality
from eval.llm_judge import LLMJudge
from eval.agent_runtime import MockAgent

async def demo_reflection():
    agent = MockAgent()
    judge = LLMJudge(kernel)
    
    query = "What are LeBron James' stats this season?"
    
    # Initial response
    response_v1 = await agent.process_query(query, "player_stats")
    eval_v1 = await judge.evaluate_response(...)
    print(f"V1 Score: {eval_v1.overall_score}/5.0")
    
    if eval_v1.overall_score < 4.0:
        # Reflect and improve
        print("Reflecting on feedback...")
        print(f"Issues: {eval_v1.reasoning}")
        print(f"Recommendations: {eval_v1.recommendations}")
        
        # Agent regenerates with reflection
        response_v2 = await agent.process_with_reflection(
            query=query,
            feedback=eval_v1.reasoning,
            recommendations=eval_v1.recommendations
        )
        
        eval_v2 = await judge.evaluate_response(...)
        print(f"V2 Score: {eval_v2.overall_score}/5.0")
        print(f"Improvement: +{eval_v2.overall_score - eval_v1.overall_score}")
```

## Prerequisites

1. **Azure OpenAI Resource**: For LLM-as-judge functionality
   - Chat completion deployment (e.g., gpt-4o-mini)
2. **Python Environment**: Python 3.8 or higher
3. **Dependencies**: Install with `pip install -r requirements.txt`

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `semantic-kernel`: AI orchestration framework
- `pydantic`: Data validation and modeling
- `python-dotenv`: Environment variable management
- `nest-asyncio`: Async event loop support

### 2. Set Environment Variables

Create a `.env` file in the demo directory:

```bash
# Azure OpenAI Configuration (required for LLM-as-judge)
AZURE_OPENAI_ENDPOINT=https://your-aoai-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_KEY=your_azure_openai_key_here
```

**Note:** Rule-based evaluation works without Azure OpenAI configuration.

### 3. Run the Demo

```bash
# Run complete evaluation demo (rule-based + LLM-as-judge)
python main.py

# Run rule-based evaluation only
python -m eval.judge

# Run custom test cases
python -c "from eval.judge import evaluate, TEST_CASES; print(evaluate(TEST_CASES[0]))"
```

## Expected Output

### Rule-Based Evaluation Output

```
🔍 Rule-Based Evaluation
================================================================================

📋 Test 1/4: Player Statistics Query
   Query: What are LeBron James' stats this season?
   Type : player_stats
   ✅ PASSED
   ✅ valid_json: True
   ✅ has_structured_data: True
   ✅ has_tools_used: True
   ✅ appropriate_tools: True
   ✅ has_confidence_score: True

📋 Test 2/4: Team Performance Query
   Query: How is the Lakers' performance this season?
   Type : team_performance
   ✅ PASSED
   [...]

📊 Rule-Based Summary
   Passed 4/4  (100.0%)
```

### LLM-as-Judge Evaluation Output

```
⚖️ LLM-as-Judge Evaluation
================================================================================

🔄 Running LLM judge on 4 cases...

📊 LLM-as-Judge Summary
   Total: 4
   Avg Score: 4.2/5.0
   Pass Rate: 100.0%
   Case 1: ✅ PASSED  (Score 4.50)
   Case 2: ✅ PASSED  (Score 4.20)
   Case 3: ✅ PASSED  (Score 4.00)
   Case 4: ✅ PASSED  (Score 4.10)
```

### Combined Report Output

```
📒 Combined Report
================================================================================
🔍 Rule-based pass rate: 100.0%
⚖️ LLM judge avg score: 4.2/5.0
⚖️ LLM judge pass rate: 100.0%

🎯 Overall blended score: 1.00
```

### Reflection Pattern Output

```
🔄 Reflection Iteration 1
   Initial Score: 2.8/5.0
   Issues Identified:
   - Insufficient statistical depth
   - Missing context for performance trends
   - No comparison to league averages

🔄 Reflection Iteration 2
   Improved Score: 3.9/5.0
   Improvement: +1.1
   Remaining Issues:
   - Could add more recent game analysis

🔄 Reflection Iteration 3
   Final Score: 4.3/5.0
   Total Improvement: +1.5
   ✅ Quality threshold met!
```

## Code Structure

```
demo/
├── main.py                    # Main runner orchestrating both evaluators
├── eval/
│   ├── judge.py              # Rule-based evaluation logic
│   ├── llm_judge.py          # LLM-as-judge implementation
│   ├── agent_runtime.py      # Mock agent for testing
│   └── results.csv           # Generated evaluation results
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment configuration
└── README.md                # This file
```

## Evaluation Criteria Details

### 1. Accuracy (Weight: 25%)
- **What it measures**: Correctness of sports statistics, facts, and analysis
- **Pass criteria**: No factual errors, statistics are plausible and consistent
- **Common issues**: Wrong player stats, incorrect team records, outdated information

### 2. Completeness (Weight: 20%)
- **What it measures**: How thoroughly the response addresses the user's query
- **Pass criteria**: All aspects of query answered, no important gaps
- **Common issues**: Missing key statistics, incomplete analysis, partial answers

### 3. Relevance (Weight: 20%)
- **What it measures**: How well the response matches user intent and needs
- **Pass criteria**: On-topic, focused, no unnecessary information
- **Common issues**: Tangential information, off-topic analysis, over-broad responses

### 4. Tool Usage (Weight: 15%)
- **What it measures**: Appropriate selection and execution of tools
- **Pass criteria**: Right tools chosen, called correctly, results used effectively
- **Common issues**: Wrong tools selected, tools not used when needed, tool errors ignored

### 5. Structure (Weight: 10%)
- **What it measures**: Organization, clarity, and presentation quality
- **Pass criteria**: Logical flow, clear sections, easy to read
- **Common issues**: Poor organization, unclear structure, wall of text

### 6. Citations (Weight: 10%)
- **What it measures**: Proper attribution of sources and data
- **Pass criteria**: Sources cited, data origins clear, transparent about limitations
- **Common issues**: No citations, unclear data sources, unjustified claims

## Best Practices

### Evaluation Strategy

1. **Start with Rule-Based**: Fast feedback for basic validation
2. **Add LLM-as-Judge**: Deeper quality assessment for production readiness
3. **Implement Reflection**: Enable continuous improvement through feedback loops
4. **Track Metrics Over Time**: Monitor score trends to catch regressions
5. **Iterate on Test Cases**: Expand coverage as agent capabilities grow

### Reflection Pattern Best Practices

1. **Set Appropriate Thresholds**: Balance quality vs. iteration cost
2. **Limit Max Iterations**: Prevent infinite loops (typically 2-3 iterations)
3. **Provide Specific Feedback**: More actionable than generic critiques
4. **Track Improvement**: Log score changes to validate reflection effectiveness
5. **Cache Evaluations**: Avoid redundant LLM calls for identical responses

### Test Case Design

1. **Cover Edge Cases**: Include challenging, ambiguous queries
2. **Test All Query Types**: Ensure comprehensive capability coverage
3. **Include Expected Failures**: Test error handling and graceful degradation
4. **Use Real Examples**: Base test cases on actual user queries when possible
5. **Update Regularly**: Keep test cases aligned with agent evolution

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **LLM judge times out** | Reduce test case complexity or increase timeout settings |
| **Inconsistent LLM scores** | Lower temperature in evaluation prompt (current: 0.1) |
| **Rule-based tests fail** | Check agent response format matches expected schema |
| **Reflection not improving** | Review feedback specificity and agent's ability to incorporate it |
| **Azure OpenAI errors** | Verify credentials and deployment configuration |

### Debug Tips

1. **Enable Verbose Logging**: Set `logging.level=DEBUG` for detailed output
2. **Test Individual Cases**: Run single test case to isolate issues
3. **Inspect Raw Responses**: Log full LLM judge responses for debugging
4. **Check Token Limits**: Ensure evaluation prompts fit within context windows
5. **Validate Mock Agent**: Confirm test agent behaves as expected

## Advanced Topics

### Custom Evaluation Criteria

Add domain-specific criteria for your use case:

```python
custom_criteria = [
    EvaluationCriteria(
        name="sports_insights",
        description="Depth of sports analysis and expert insights",
        weight=0.20
    ),
    EvaluationCriteria(
        name="timeliness",
        description="Use of recent data and current context",
        weight=0.10
    )
]

judge = LLMJudge(kernel)
judge.criteria.extend(custom_criteria)
```

### Multi-Model Evaluation

Use multiple LLMs for ensemble evaluation:

```python
async def ensemble_evaluate(response, judges):
    """Evaluate with multiple LLMs and average scores"""
    evaluations = []
    for judge in judges:
        eval_result = await judge.evaluate_response(...)
        evaluations.append(eval_result)
    
    avg_score = sum(e.overall_score for e in evaluations) / len(evaluations)
    return avg_score, evaluations
```

### A/B Testing Agent Versions

Compare different agent implementations:

```python
async def compare_agents(test_cases, agent_a, agent_b, judge):
    """Compare two agent versions on same test suite"""
    scores_a, scores_b = [], []
    
    for case in test_cases:
        response_a = await agent_a.process(case)
        response_b = await agent_b.process(case)
        
        eval_a = await judge.evaluate_response(response_a)
        eval_b = await judge.evaluate_response(response_b)
        
        scores_a.append(eval_a.overall_score)
        scores_b.append(eval_b.overall_score)
    
    print(f"Agent A average: {sum(scores_a)/len(scores_a):.2f}")
    print(f"Agent B average: {sum(scores_b)/len(scores_b):.2f}")
```

### Continuous Evaluation Pipeline

Integrate evaluation into CI/CD:

```python
def regression_test():
    """Run evaluation suite and fail if scores drop"""
    baseline_score = 4.0  # minimum acceptable score
    
    results = run_evaluation_suite()
    avg_score = results['average_score']
    
    if avg_score < baseline_score:
        raise ValueError(f"Regression detected: {avg_score} < {baseline_score}")
    
    print(f"✅ Tests passed: {avg_score:.2f}/5.0")
```

## Learning Outcomes

After completing this lesson, you will understand:

1. **Evaluation Fundamentals**: How to systematically assess AI agent quality
2. **Dual Evaluation Strategy**: Combining rule-based and LLM-based approaches
3. **The Reflection Pattern**: Enabling agents to improve through feedback loops
4. **Quality Metrics**: Measuring agent performance across multiple dimensions
5. **Production Readiness**: Building robust evaluation pipelines for deployment
6. **Continuous Improvement**: Creating feedback mechanisms for ongoing enhancement

## Real-World Applications

### Production Monitoring

Use evaluation to monitor deployed agents:
- Track quality metrics over time
- Detect regressions automatically
- Alert on quality threshold violations
- Generate quality reports for stakeholders

### Agent Development Workflow

Integrate evaluation into development:
1. Develop new agent capability
2. Create test cases for new features
3. Run rule-based validation
4. Use LLM-as-judge for quality check
5. Apply reflection pattern for refinement
6. Deploy when quality thresholds met

### User Feedback Loop

Connect evaluation to user satisfaction:
- Correlate LLM judge scores with user ratings
- Use reflection to address common complaints
- A/B test improvements before full rollout
- Build confidence in agent recommendations

## Next Steps

1. **Extend Test Coverage**: Add more diverse and challenging test cases
2. **Implement Reflection**: Build reflection loop into your agent architecture
3. **Track Quality Metrics**: Set up monitoring dashboard for evaluation scores
4. **Customize Criteria**: Tailor evaluation criteria to your domain needs
5. **Production Deploy**: Integrate evaluation pipeline into deployment process

## Additional Resources

- [LLM-as-Judge Paper](https://arxiv.org/abs/2306.05685): Research on using LLMs for evaluation
- [Reflection Pattern](https://www.promptingguide.ai/techniques/reflection): Guide to reflection techniques
- [Agent Evaluation Best Practices](https://docs.microsoft.com/azure/ai): Microsoft's agent evaluation guide
- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel): Framework documentation

---

This lesson provides a comprehensive foundation for evaluating AI agents with both automated and AI-powered approaches, with special emphasis on the powerful reflection pattern for continuous agent improvement.
