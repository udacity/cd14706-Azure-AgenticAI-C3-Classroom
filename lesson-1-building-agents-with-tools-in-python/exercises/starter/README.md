# Exercise

Set up a Semantic Kernel `Kernel` and register Azure OpenAI services and tool plugins so the agent can enumerate callable capabilities.

### **Prerequisites**

* Semantic Kernel basics (creating a `Kernel` and adding services)

* Azure OpenAI environment variables configured (`AZURE_OPENAI_*`)

* Python 3.8+ and the demo dependencies installed

### **Instructions**

1. In `create_kernel()`, instantiate the kernel by replacing the `# TODO CREATE KERNEL` with a `Kernel()` instance assigned to `kernel`.

2. In `create_kernel()`, add the Azure Chat service by replacing `# TODO ADD AZURE CHAT COMPLETION SERVICE` with a call to `kernel.add_service(AzureChatCompletion(...))` using `DEPLOYMENT_CHAT`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, and `AZURE_OPENAI_API_VERSION` from the existing environment variables.

3. In `create_kernel()`, add the Azure Text Embedding service by replacing `# TODO ADD AZURE TEXT EMBEDDING SERVICE` with a call to `kernel.add_service(AzureTextEmbedding(...))` using `DEPLOYMENT_EMBED`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, and `AZURE_OPENAI_API_VERSION`.

4. In `create_kernel()`, register the tools by replacing `# TODO ADD ORDER STATUS TOOLS` with `kernel.add_plugin(OrderStatusTools(), "order_status")` and replacing `# TODO ADD PRODUCT INFO TOOLS` with `kernel.add_plugin(ProductInfoTools(), "product_info")`.

5. At the end of `create_kernel()`, replace `# TODO RETURN KERNEL` with `return kernel`.

6. Keep `main()` as-is; after the above changes, running it should list the registered plugins and functions from `kernel.plugins`.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`