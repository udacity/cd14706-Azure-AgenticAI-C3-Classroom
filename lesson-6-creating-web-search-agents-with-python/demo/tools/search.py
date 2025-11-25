# tools/search.py

from semantic_kernel.functions import kernel_function
import os
import json
import re
import sys
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
                content=f"Search for sports information: {query}. Return the results as a JSON array only, with each item containing 'title', 'url', and 'snippet' fields. Do not include any additional text or explanation, only return the JSON array."
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

            # Print with safe encoding handling
            try:
                print("\n🧪 RAW Bing Assistant Response:\n", raw_json[:300])
            except UnicodeEncodeError:
                # Fallback for systems with limited encoding support
                safe_text = raw_json[:300].encode('ascii', 'ignore').decode('ascii')
                print("\nRAW Bing Assistant Response:\n", safe_text)
            raw_json = raw_json.strip()
            if raw_json.startswith("```"):
                lines = raw_json.split('\n')
                if lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                raw_json = '\n'.join(lines).strip()
            results = json.loads(raw_json)
            return results[:max_results]

        except Exception as e:
            # Handle encoding issues in error messages
            error_msg = str(e)
            try:
                # Try to encode to check if it's safe
                error_msg.encode('utf-8')
            except UnicodeEncodeError:
                # Remove non-ASCII characters if encoding fails
                error_msg = error_msg.encode('ascii', 'ignore').decode('ascii')
            
            return [{
                "title": "Search error",
                "url": "",
                "snippet": f"Failed to retrieve sports search results: {error_msg}"
            }]