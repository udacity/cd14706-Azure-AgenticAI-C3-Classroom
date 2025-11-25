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

### Part 1: Enable Automatic Function Calling

1. **In `process_customer_query(...)`**, implement automatic function calling:
   - Create a `ChatHistory` object
   - Add the system message using `create_customer_service_prompt()`
   - Add the user message (query)
   - Get the chat completion service: `kernel.get_service(type=ChatCompletionClientBase)`
   - Get execution settings from the service
   - Set `execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()`
   - Call `chat_service.get_chat_message_contents()` with chat history, settings, and kernel

### Part 2: Structured Output Prompt

2. **In `create_customer_service_prompt()`**, ensure the prompt clearly instructs the model to return valid JSON matching the provided schemas for `order_status` and `product_info`. The prompt should specify the exact JSON structure expected.

### Part 3: Pydantic Validation

3. **In `parse_and_validate_response(...)`**, extract the JSON substring from `response_text` using the first `{` and last `}`; parse it with `json.loads`.

4. **Still in `parse_and_validate_response(...)`**, validate the parsed dictionary by constructing `CustomerServiceResponse(**response_data)`.

5. **If `structured_data` is present**, validate it against the appropriate model by constructing `OrderResponse(**...)` when `query_type == "order_status"` or `ProductResponse(**...)` when `query_type == "product_info"`.

### Part 4: Query Processing

6. **In `process_customer_query(...)`**, determine `query_type` heuristically from the user query (e.g., contains "order"/"tracking" → `order_status`; contains "product"/"price" → `product_info`) before calling `parse_and_validate_response`.

### Part 5: Demo Scenarios

7. **In `run_demo_scenarios(...)`**, iterate over the provided demo queries and log: human-readable response, tools used, confidence score, follow-up suggestions, and (if present) the JSON `structured_data`.

### Part 6: Verify Setup

8. **Verify the kernel setup**: ensure both `order_status` and `product_info` plugins are registered with `kernel.add_plugin()`.

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