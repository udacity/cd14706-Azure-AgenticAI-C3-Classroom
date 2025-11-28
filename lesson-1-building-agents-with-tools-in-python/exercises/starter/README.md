# Exercise

Set up a Semantic Kernel `Kernel` and register Azure OpenAI services and tool plugins so the agent can enumerate callable capabilities.

### **Prerequisites**

* Semantic Kernel basics (creating a `Kernel` and adding services)

* Azure OpenAI environment variables configured (`AZURE_OPENAI_*`)

* Python 3.8+ and the demo dependencies installed

### **Instructions**

1. In `create_kernel()`, instantiate the kernel by replacing the `# TODO CREATE KERNEL` with a `Kernel()` instance assigned to `kernel`.

2. In `create_kernel()`, add the Azure Chat service by replacing `# TODO ADD AZURE CHAT COMPLETION SERVICE`. Your implementation should call `kernel.add_service()` with an `AzureChatCompletion` instance, using the existing environment variables.

3. In `create_kernel()`, add the Azure Text Embedding service by replacing `# TODO ADD AZURE TEXT EMBEDDING SERVICE`. Your implementation should call `kernel.add_service()` with an `AzureTextEmbedding` instance, using the existing environment variables.

4. In `create_kernel()`, register the tools by replacing `# TODO ADD ORDER STATUS TOOLS` and `# TODO ADD PRODUCT INFO TOOLS`. Your implementation should call `kernel.add_plugin()` for each tool, providing the correct tool class instance and a unique plugin name.

5. At the end of `create_kernel()`, replace `# TODO RETURN KERNEL` with a statement that returns the kernel instance.

6. Keep `main()` as-is; after the above changes, running it should list the registered plugins and functions from `kernel.plugins`.

`[INSTRUCTIONS FOR ACCESSING THE EXERCISE ENVIRONMENT]`