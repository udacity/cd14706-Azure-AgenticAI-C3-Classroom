# Exercise Solution: Integrating External APIs with Semantic Kernel

[VIDEO_PLACEHOLDER: Integrating External APIs with Semantic Kernel]

## **Solution Walkthrough**

This solution demonstrates how to integrate external API tools into your Semantic Kernel agent by registering the RecommendationTools plugin and implementing structured return dictionaries for both success and failure cases.

## **Task 1: Register the RecommendationTools Plugin (main.py)**

```python
kernel.add_plugin(RecommendationTools(), "recommendations")
logger.info("✅ RecommendationTools plugin added successfully")
```

This registers the RecommendationTools class as a plugin named "recommendations", making all its methods available to the Semantic Kernel agent.

## **Task 2: Implement Return Dictionaries (tools/recommendations.py)**

### **get_product_recommendations()**

**Success case:**
```python
return {
    "api_source": "Product Recommendation Engine API",
    "api_endpoint": f"{self.recommendation_api_base}/v1/recommendations",
    "recommendation_results": recommendation_api_response["recommendations"]
}
```

**Failure case:**
```python
return {
    "api_source": "Product Recommendation Engine API",
    "api_endpoint": f"{self.recommendation_api_base}/v1/recommendations",
    "recommendation_results": {
        "customer_id": customer_id,
        "product_id": product_id,
        "error": f"API call failed: {e}",
        "products": []
    }
}
```

### **get_trending_products()**

**Success case:**
```python
return {
    "api_source": "Analytics and Trending API",
    "api_endpoint": f"{self.analytics_api_base}/v1/trending",
    "trending_analysis": trending_api_response["trending_analysis"]
}
```

**Failure case:**
```python
return {
    "api_source": "Analytics and Trending API",
    "api_endpoint": f"{self.analytics_api_base}/v1/trending",
    "trending_analysis": {
        "category": category,
        "time_period": time_period,
        "error": f"API call failed: {e}",
        "trending_products": []
    }
}
```

### **get_cross_sell_recommendations()**

**Success case:**
```python
return {
    "api_source": "Cross-Sell Recommendation API",
    "api_endpoint": f"{self.recommendation_api_base}/v1/cross-sell",
    "cross_sell_analysis": cross_sell_api_response["cross_sell_analysis"]
}
```

**Failure case:**
```python
return {
    "api_source": "Cross-Sell Recommendation API",
    "api_endpoint": f"{self.recommendation_api_base}/v1/cross-sell",
    "cross_sell_analysis": {
        "product_id": product_id,
        "customer_segment": customer_segment,
        "error": f"API call failed: {e}",
        "recommendations": []
    }
}
```

## **Key Takeaways**

- **Consistent Structure**: All return dictionaries follow the same pattern with `api_source`, `api_endpoint`, and a results key
- **Error Handling**: Failure cases maintain the same structure as success cases but include error messages and empty data
- **Plugin Registration**: Using `kernel.add_plugin()` makes external API tools available to the agent
- **Metadata Tracking**: Including API source and endpoint information helps with debugging and monitoring

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
