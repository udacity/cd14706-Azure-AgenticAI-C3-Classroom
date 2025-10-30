# Exercise

Extend the Lesson 1 kernel by prompting for strict JSON and validating responses with Pydantic models to produce reliable structured outputs.

### **Prerequisites**

* Ability to add functions to a Semantic Kernel and invoke them

* Basic Pydantic understanding (models, enums, validation)

* Azure OpenAI environment configured and Lesson 1 completed

### **Instructions**

1. In `create_customer_service_prompt()`, ensure the prompt clearly instructs the model to return valid JSON matching the provided schemas for `order_status` and `product_info`.

2. In `process_customer_query(...)`, create a SK function from that prompt and invoke it to obtain `response_text`.

3. In `parse_and_validate_response(...)`, extract the JSON substring from `response_text` using the first `{` and last `}`; parse it with `json.loads`.

4. Still in `parse_and_validate_response(...)`, validate the parsed dictionary by constructing `CustomerServiceResponse(**response_data)`.

5. If `structured_data` is present, validate it against the appropriate model by constructing `OrderResponse(**...)` when `query_type == "order_status"` or `ProductResponse(**...)` when `query_type == "product_info"`.

6. In `process_customer_query(...)`, determine `query_type` heuristically from the user query (e.g., contains "order"/"tracking" → `order_status`; contains "product"/"price" → `product_info`) before calling `parse_and_validate_response`.

7. In `run_demo_scenarios(...)`, iterate over the provided demo queries and log: human-readable response, tools used, confidence score, follow-up suggestions, and (if present) the JSON `structured_data`.

8. Leave the kernel setup as in Lesson 1 (already provided); ensure both `order_status` and `product_info` plugins are registered.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`