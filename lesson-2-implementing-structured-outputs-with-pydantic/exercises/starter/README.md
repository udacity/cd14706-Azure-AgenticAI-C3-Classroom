# Exercise: Implementing Structured Outputs with Pydantic

Build a customer service agent using Semantic Kernel with automatic tool invocation and Pydantic validation for structured outputs.

## **Learning Objectives**

By the end of this exercise, you will:
- Enable automatic function calling with `FunctionChoiceBehavior.Auto()`
- Use `ChatHistory` to manage conversation context
- Prompt LLMs to return structured JSON output
- Validate LLM responses with Pydantic models
- Integrate real tool execution with customer service queries

## **Prerequisites**

* Ability to add functions to a Semantic Kernel and invoke them
* Basic Pydantic understanding (models, enums, validation)
* Azure OpenAI environment configured and Lesson 1 completed

## **Instructions**

### Part 0: Define Pydantic Models

1.  **In `models.py`**, complete the `OrderStatus` enum by adding common order status values.
2.  **Still in `models.py`**, complete the `ProductAvailability` enum by adding relevant product availability states.
3.  **In `models.py`**, define the necessary fields for the `OrderResponse` BaseModel to represent order details.
4.  **Still in `models.py`**, define the necessary fields for the `ProductResponse` BaseModel to represent product information.

### Part 1: Structured Output Prompt

1.  **In `create_customer_service_prompt()`**, ensure the prompt clearly instructs the model to return valid JSON matching the provided schemas for `order_status` and `product_info`. The prompt should specify the exact JSON structure expected.

### Part 2: Pydantic Validation

2.  **In `parse_and_validate_response(...)`**, extract the JSON substring from `response_text` using the first `{` and last `}`; parse it with `json.loads`.
3.  **Still in `parse_and_validate_response(...)`**, validate the parsed dictionary by constructing `CustomerServiceResponse(**response_data)`.

### Part 3: Query Processing

4.  **In `process_customer_query(...)`**, determine `query_type` heuristically from the user query (e.g., contains "order"/"tracking" → `order_status`; contains "product"/"price" → `product_info`) before calling `parse_and_validate_response`.

### Part 4: Demo Scenarios

5.  **In `run_demo_scenarios(...)`**, iterate over the provided demo queries and log: human-readable response, tools used, confidence score, follow-up suggestions, and (if present) the JSON `structured_data`.

### Part 5: Verify Setup

6.  **Verify the kernel setup**: ensure both `order_status` and `product_info` plugins are registered with `kernel.add_plugin()`.

## **Success Criteria**

When you run the exercise, you should see:
```
🔧 Executing with automatic function calling enabled...
Getting order status for order ID: ORD-001
✅ Order data validated: ORD-001 - shipped
🔧 Tools used: get_order_status
```

This confirms that:
- Tools are being automatically invoked by Semantic Kernel
- Real data is retrieved from the tools
- Pydantic validation passes on the structured output

## **Key Concepts**

### Automatic Function Calling
`FunctionChoiceBehavior.Auto()` enables Semantic Kernel to automatically invoke registered tools when the LLM determines it needs data to answer a query.

### ChatHistory
Manages the conversation context, including system messages (instructions) and user messages (queries).

### Pydantic Validation
Ensures the LLM's JSON response matches the expected schema, providing type safety and data integrity.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`