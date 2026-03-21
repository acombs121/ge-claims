import uuid
import json
import uvicorn
import logging
import os
from fastapi import FastAPI, Request
from google.adk.runners import Runner
from google.genai import types, Client
from google.adk.models.google_llm import Gemini
import google.auth

# Standard A2A Servicing Engine
from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from agent_executor import AdkAgentToA2AExecutor
import a2a.types as a2a_types
from agent import root_agent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# MONKEY PATCH: Force google-adk into Vertex AI mode for Cloud Run deployment
# ------------------------------------------------------------------------------
def get_gcp_project_id():
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        _, project = google.auth.default()
    return project or "YOUR_DEFAULT_PROJECT_ID"

def patched_api_client(self):
    if not hasattr(self, '_patched_client'):
         self._patched_client = Client(
             vertexai=True,
             project=get_gcp_project_id(),
             location="global",
             http_options=types.HttpOptions(
                 headers=self._tracking_headers(),
                 retry_options=self.retry_options,
                 base_url=self.base_url,
             )
         )
    return self._patched_client

def patched_live_api_client(self):
    if not hasattr(self, '_patched_live_client'):
         self._patched_live_client = Client(
             vertexai=True,
             project=get_gcp_project_id(),
             location="global",
             http_options=types.HttpOptions(
                 headers=self._tracking_headers(), api_version=self._live_api_version
             )
         )
    return self._patched_live_client

# Override descriptor hooks
Gemini.api_client = property(patched_api_client)
Gemini._live_api_client = property(patched_live_api_client)

AGENT_URL = os.environ.get("AGENT_URL", "http://127.0.0.1:8080")

# ------------------------------------------------------------------------------
# AgentCard Declaration (Adjust values for specific Customer/Use Cases)
# ------------------------------------------------------------------------------
agent_card = a2a_types.AgentCard(
    name=root_agent.name,
    description=root_agent.description,
    url=AGENT_URL,
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain", "application/json"],
    capabilities=a2a_types.AgentCapabilities(streaming=True),
    skills=[
        a2a_types.AgentSkill(
            id="analysis",
            name="Generic Smart Analyst",
            description="Abstractions for diverse industry analytical data flows.",
            tags=["generic"],
            examples=["Give me a summary report"],
        )
    ]
)

request_handler = DefaultRequestHandler(
    agent_executor=AdkAgentToA2AExecutor(agent=root_agent),
    task_store=InMemoryTaskStore(),
)

import os
from starlette.staticfiles import StaticFiles

app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
).build()

# Make the /tmp/a2ui_media directory serve static media directly!
os.makedirs("/tmp/a2ui_media", exist_ok=True)
app.mount("/media", StaticFiles(directory="/tmp/a2ui_media"), name="media")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
