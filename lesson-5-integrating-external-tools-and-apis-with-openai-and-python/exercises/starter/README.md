# Exercise: Integrating External APIs with Semantic Kernel

[VIDEO_PLACEHOLDER: Integrating External APIs with Semantic Kernel]

## **Overview**

In this exercise, you'll integrate external API tools into your Semantic Kernel agent by implementing the RecommendationTools class and registering it as a plugin. This exercise focuses on understanding how to structure API responses for both success and failure cases.

## **Learning Objectives**

- Register external API tools as Semantic Kernel plugins
- Structure API response dictionaries with proper metadata
- Implement consistent error handling patterns
- Understand the difference between success and failure response formats

## **Tasks**

### **Implement Return Dictionaries in tools/recommendations.py**

Complete the 6 TODO sections with return dictionaries. Each method has two cases to implement:

#### **Success Case Pattern:**

Your return dictionary should include:
- `"api_source"`: The name of the API being used (e.g., "Product Recommendation Engine API").
- `"api_endpoint"`: The full endpoint URL.
- A results key containing the data from the API response. For example, in `get_product_recommendations`, this would be `"recommendation_results": recommendation_api_response["recommendations"]`.

#### **Failure Case Pattern:**

Your return dictionary should include:
- `"api_source"`: The name of the API being used.
- `"api_endpoint"`: The full endpoint URL.
- A results dictionary with error information and empty data lists. For example, in `get_product_recommendations`, the `recommendation_results` dictionary should contain an `error` field with the exception message and an empty `products` list.

#### **Methods to Implement (6 TODOs):**

1. `get_product_recommendations()` - Success case
2. `get_product_recommendations()` - Failure case (in `except` block)
3. `get_trending_products()` - Success case
4. `get_trending_products()` - Failure case (in `except` block)
5. `get_cross_sell_recommendations()` - Success case
6. `get_cross_sell_recommendations()` - Failure case (in `except` block)

Apply similar patterns for `get_trending_products()` and `get_cross_sell_recommendations()`.

## **Hints**

- Review the docstrings in each method for expected return structure
- Look at how other tools (inventory, shipping, pricing) format their responses
- The mock API response data is already provided - you just need to structure the return dictionary
- Success responses should include the API response data
- Failure responses should maintain the same structure but with error messages and empty data

## **Testing Your Implementation**

Run the exercise:
```bash
python main.py
```

You should see output showing:
- All plugins registered successfully
- Test results from each external API
- Integration scenarios combining multiple APIs

## **Expected Output**

```
✅ RecommendationTools plugin added successfully
🎯 Testing Recommendation Engine API
   API Source: Product Recommendation Engine API
   Products Recommended: 5 recommendations
✅ External API Integration Testing completed successfully!
```

[INSTRUCTIONS FOR ACCESSING THE STARTER ENVIRONMENT]
