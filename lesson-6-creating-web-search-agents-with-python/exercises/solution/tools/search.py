# tools/search.py (updated for ecommerce focus)

from semantic_kernel.functions import kernel_function
import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

class SearchTools:
    def __init__(self):
        self.project_endpoint = os.getenv("PROJECT_ENDPOINT")
        self.agent_id = os.getenv("AGENT_ID")
        self.connection_id = os.getenv("BING_CONNECTION_ID")
        self.cred = DefaultAzureCredential()

    @kernel_function(name="product_web_search", description="Search for product information, reviews, and pricing using Azure AI Agent with Bing grounding")
    def product_web_search(self, query: str, max_results: int = 5):
        """
        Search for product information, reviews, pricing, and ecommerce data using Azure AI Agent connected to Bing.
        Returns structured results with title, URL, and snippet for product research.
        """
        if not all([self.project_endpoint, self.agent_id, self.connection_id]):
            return [{
                "title": "Missing configuration",
                "url": "https://bing.com",
                "snippet": "Missing: PROJECT_ENDPOINT, AGENT_ID, or BING_CONNECTION_ID."
            }]

        try:
            client = AIProjectClient(endpoint=self.project_endpoint, credential=self.cred)
            thread = client.agents.threads.create()

            client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"""Search for product information and ecommerce data: {query}

CRITICAL: You MUST return your response as a valid JSON array ONLY. Do not include any explanation, text, or commentary.
Return ONLY a JSON array in this exact format:
[
  {{"title": "result title", "url": "https://example.com", "snippet": "description"}},
  {{"title": "result title 2", "url": "https://example2.com", "snippet": "description 2"}}
]

Return the JSON array and nothing else."""
            )

            client.agents.runs.create_and_process(thread_id=thread.id, agent_id=self.agent_id)

            messages = list(client.agents.messages.list(thread_id=thread.id))
            assistant_msgs = [m for m in messages if m.role == "assistant"]
            content_blocks = assistant_msgs[-1].content if assistant_msgs else []

            raw_json = None
            if (
                isinstance(content_blocks, list)
                and content_blocks
                and content_blocks[0]["type"] == "text"
            ):
                raw_json = content_blocks[0]["text"]["value"]

            client.agents.threads.delete(thread_id=thread.id)

            if not raw_json:
                return [{
                    "title": "No results",
                    "url": "",
                    "snippet": "No JSON returned by Agent. Check agent instructions or Bing grounding setup."
                }]

            print("\n🧪 RAW Bing Assistant Response:\n", raw_json[:300])
            results = json.loads(raw_json)
            return results[:max_results]

        except Exception as e:
            return [{
                "title": "Search error",
                "url": "",
                "snippet": f"Failed to retrieve product search results: {e}"
            }]

    @kernel_function(name="price_comparison_search", description="Search for price comparison data across multiple retailers")
    def price_comparison_search(self, product_name: str, max_results: int = 5):
        """
        Search for price comparison data across multiple retailers for a specific product.
        Returns structured results with retailer, price, and availability information.
        """
        if not all([self.project_endpoint, self.agent_id, self.connection_id]):
            return [{
                "title": "Missing configuration",
                "url": "https://bing.com",
                "snippet": "Missing: PROJECT_ENDPOINT, AGENT_ID, or BING_CONNECTION_ID."
            }]

        try:
            client = AIProjectClient(endpoint=self.project_endpoint, credential=self.cred)
            thread = client.agents.threads.create()

            client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"""Search for price comparison for {product_name} across different retailers and marketplaces

CRITICAL: You MUST return your response as a valid JSON array ONLY. Do not include any explanation, text, or commentary.
Return ONLY a JSON array in this exact format:
[
  {{"title": "retailer name - price", "url": "https://example.com", "snippet": "price and availability details"}},
  {{"title": "retailer name 2 - price", "url": "https://example2.com", "snippet": "price and availability details"}}
]

Return the JSON array and nothing else."""
            )

            client.agents.runs.create_and_process(thread_id=thread.id, agent_id=self.agent_id)

            messages = list(client.agents.messages.list(thread_id=thread.id))
            assistant_msgs = [m for m in messages if m.role == "assistant"]
            content_blocks = assistant_msgs[-1].content if assistant_msgs else []

            raw_json = None
            if (
                isinstance(content_blocks, list)
                and content_blocks
                and content_blocks[0]["type"] == "text"
            ):
                raw_json = content_blocks[0]["text"]["value"]

            client.agents.threads.delete(thread_id=thread.id)

            if not raw_json:
                return [{
                    "title": "No results",
                    "url": "",
                    "snippet": "No price comparison data found. Check agent instructions or Bing grounding setup."
                }]

            print("\n🧪 RAW Bing Assistant Response:\n", raw_json[:300])
            results = json.loads(raw_json)
            return results[:max_results]

        except Exception as e:
            return [{
                "title": "Search error",
                "url": "",
                "snippet": f"Failed to retrieve price comparison results: {e}"
            }]

    @kernel_function(name="product_review_search", description="Search for product reviews and ratings from various sources")
    def product_review_search(self, product_name: str, max_results: int = 5):
        """
        Search for product reviews, ratings, and customer feedback from various sources.
        Returns structured results with review sources, ratings, and key feedback points.
        """
        if not all([self.project_endpoint, self.agent_id, self.connection_id]):
            return [{
                "title": "Missing configuration",
                "url": "https://bing.com",
                "snippet": "Missing: PROJECT_ENDPOINT, AGENT_ID, or BING_CONNECTION_ID."
            }]

        try:
            client = AIProjectClient(endpoint=self.project_endpoint, credential=self.cred)
            thread = client.agents.threads.create()

            client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"""Find web articles and pages about "{product_name} reviews" and "{product_name} ratings". Search for expert reviews, user opinions, and product feedback available online.

CRITICAL: You MUST return your response as a valid JSON array ONLY. Do not include any explanation, text, or commentary.
Return ONLY a JSON array in this exact format:
[
  {{"title": "review source - rating", "url": "https://example.com", "snippet": "review summary and rating"}},
  {{"title": "review source 2 - rating", "url": "https://example2.com", "snippet": "review summary and rating"}}
]

Return the JSON array and nothing else."""
            )

            client.agents.runs.create_and_process(thread_id=thread.id, agent_id=self.agent_id)

            messages = list(client.agents.messages.list(thread_id=thread.id))
            assistant_msgs = [m for m in messages if m.role == "assistant"]
            content_blocks = assistant_msgs[-1].content if assistant_msgs else []

            raw_json = None
            if (
                isinstance(content_blocks, list)
                and content_blocks
                and content_blocks[0]["type"] == "text"
            ):
                raw_json = content_blocks[0]["text"]["value"]

            client.agents.threads.delete(thread_id=thread.id)

            if not raw_json:
                return [{
                    "title": "No results",
                    "url": "",
                    "snippet": "No review data found. Check agent instructions or Bing grounding setup."
                }]

            print("\n🧪 RAW Bing Assistant Response:\n", raw_json[:300])
            results = json.loads(raw_json)
            return results[:max_results]

        except Exception as e:
            return [{
                "title": "Search error",
                "url": "",
                "snippet": f"Failed to retrieve product review results: {e}"
            }]