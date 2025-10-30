# tools/search.py (updated for sports focus)

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

    @kernel_function(name="sports_web_search", description="Search for sports news and stats using Azure AI Agent with Bing grounding")
    def sports_web_search(self, query: str, max_results: int = 5):
        """
        Search for live basketball or sports news using Azure AI Agent connected to Bing.
        Returns structured results with title, URL, and snippet.
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
                content=f"Search for sports information: {query}"
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
                "snippet": f"Failed to retrieve sports search results: {e}"
            }]