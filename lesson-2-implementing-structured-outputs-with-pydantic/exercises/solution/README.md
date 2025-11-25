# Exercise Solution: Structured Outputs with Pydantic

[VIDEO_PLACEHOLDER: Validated Structured Outputs with Pydantic]

## Solution Overview

This solution demonstrates how to combine **automatic tool invocation** with **Pydantic validation** to ensure reliable, structured outputs from your customer service agent.

### **Key Implementation Steps**

### Step 1: Enable Automatic Function Calling

```python
# Create chat history
chat_history = ChatHistory()
chat_history.add_system_message(create_customer_service_prompt())
chat_history.add_user_message(query)

# Get the chat completion service
chat_service = kernel.get_service(type=ChatCompletionClientBase)

# Configure execution settings with automatic function calling
execution_settings = kernel.get_prompt_execution_settings_from_service_id(
    service_id=chat_service.service_id
)
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

# Get the chat completion with automatic tool invocation
result = await chat_service.get_chat_message_contents(
    chat_history=chat_history,
    settings=execution_settings,
    kernel=kernel
)
```

**Key Point:** Using `FunctionChoiceBehavior.Auto()` allows Semantic Kernel to automatically invoke the registered tools (`get_order_status`, `get_product_info`) when the LLM needs data.

### Step 2: Parse and Validate with Pydantic

We then parse the JSON substring and validate it against Pydantic models. This ensures downstream code can rely on a typed shape.

```python
# Parse and validate
json_start = response_text.find('{')
json_end = response_text.rfind('}') + 1
json_str = response_text[json_start:json_end]
response_data = json.loads(json_str)

# Validate the main response structure
customer_response = CustomerServiceResponse(**response_data)

# Validate nested structured data
if customer_response.structured_data:
    if query_type == "order_status":
        OrderResponse(**customer_response.structured_data)
    elif query_type == "product_info":
        ProductResponse(**customer_response.structured_data)
```

### Step 3: Run Demo Scenarios

After invoking a few demo queries, we log the validated results for inspection.

```
🔧 Executing with automatic function calling enabled...
Getting order status for order ID: ORD-001
✅ Order data validated: ORD-001 - shipped
🎉 All Pydantic validation passed!
```

[IMAGE_PLACEHOLDER: Screengrab of console showing tool invocation logs, human-readable response, and validated JSON block]

## What Makes This Solution Work

### ✅ Automatic Tool Invocation
- Tools are automatically called when the LLM needs data
- Real data from `get_order_status` and `get_product_info`
- Semantic Kernel manages the function calling workflow

### ✅ Pydantic Validation
- Guarantees response structure matches schemas
- Type safety for all fields
- Clear error messages when validation fails

### ✅ Structured + Human-Readable
- JSON for programmatic access
- Natural language for users
- Combined approach for optimal user experience

### **Key Takeaway**

> This solution combines automatic function calling with Pydantic validation to ensure LLMs return real, structured data that downstream code can rely on.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
