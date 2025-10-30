# Exercise Solution

[VIDEO_PLACEHOLDER: Kernel and Tools Setup in Semantic Kernel (Azure OpenAI)]

### **Solution Walkthrough**

We enable the agent by wiring the Semantic Kernel to Azure OpenAI and registering tool plugins. This turns the stubbed starter into a runnable setup that can call functions.

```python
# Create the kernel and register Azure services
kernel = Kernel()

kernel.add_service(
    AzureChatCompletion(
        deployment_name=DEPLOYMENT_CHAT,
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )
)

kernel.add_service(
    AzureTextEmbedding(
        deployment_name=DEPLOYMENT_EMBED,
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )
)
```

We expose business functionality by registering the tool classes as Semantic Kernel plugins so they are callable.

```python
# Register custom tools as plugins
kernel.add_plugin(OrderStatusTools(), "order_status")
kernel.add_plugin(ProductInfoTools(), "product_info")
```

Finally, we return the configured kernel and enumerate plugins/functions for visibility.

```python
# Return the configured kernel
return kernel

# ... later in main()
for plugin_name, plugin in kernel.plugins.items():
    logger.info(f"  Plugin: {plugin_name}")
    for function_name, function in plugin.functions.items():
        logger.info(f"    Function: {function_name}")
```

```
✅ Azure Chat Completion service added successfully
✅ Azure Text Embedding service added successfully
✅ OrderStatusTools plugin added successfully
✅ ProductInfoTools plugin added successfully
```

[IMAGE_PLACEHOLDER: Screengrab of console listing order_status and product_info plugins with their functions]

### **Key Takeaway**

> The solution instantiates an SK `Kernel`, wires Azure OpenAI chat/embeddings, and registers tools as plugins to enable callable capabilities.

[INSTRUCTIONS FOR ACCESSING THE SOLUTION ENVIRONMENT]
