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
            id="hr_self_service",
            name="Aon HR Assistant",
            description="Helps with performance reviews, benefits information, and vacation requests via Workday integration.",
            tags=["aon", "hr", "workday", "performance_review"],
            examples=["Let's look at my HR portal.", "Help me prepare for my performance review.", "How many vacation days do I have left?"],
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

from starlette.responses import Response
from starlette.routing import Route

async def serve_media(request):
    media_id = request.path_params.get("media_id")
    
    # Local Fallback Check (Safety feature)
    if not os.environ.get("K_SERVICE"):
        local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'media_cache')
        local_path = os.path.join(local_dir, media_id)
        if os.path.exists(local_path):
            try:
                with open(local_path, "rb") as f:
                    bytes_data = f.read()
                ext = media_id.split(".")[-1].lower()
                media_type = "image/png" if ext == "png" else "image/jpeg"
                if ext == "webp": media_type = "image/webp"
                return Response(content=bytes_data, media_type=media_type)
            except Exception as e:
                logger.error(f"Error serving media from local cache: {e}")
                # Fallback to GCS if local read fails
                
    try:
        from google.cloud import storage
        client = storage.Client(project="sandbox-426014")
        bucket = client.bucket("sandbox-426014-a2ui-media-cache")
        blob = bucket.blob(f"generated_ads/{media_id}")
        
        if not blob.exists():
             return Response(content="Media not found or expired from persistent GCS cache.", status_code=404)
             
        bytes_data = blob.download_as_bytes()
        ext = media_id.split(".")[-1].lower()
        media_type = "image/png" if ext == "png" else "image/jpeg"
        if ext == "webp": media_type = "image/webp"
        
        return Response(content=bytes_data, media_type=media_type)
    except Exception as e:
        logger.error(f"Error serving media dynamically from GCS: {e}")
        return Response(content=f"Internal Server Error: {str(e)}", status_code=500)

app.routes.append(Route("/media/{media_id}", serve_media, methods=["GET"]))

from starlette.responses import HTMLResponse
from fastapi import Request
from starlette.routing import Route
import urllib.request
import json

async def handle_erp_submit(request: Request):
    try:
        form_data = await request.form()
        payload_data = json.loads(form_data.get("payload_data", "{}"))
        erp_url = os.environ.get("SAP_MOCK_URL", "https://sap-erp-mock-157865322412.us-central1.run.app").rstrip("/")
        api_endpoint = f"{erp_url}/api/interactions"
        
        encoded_payload = json.dumps(payload_data).encode('utf-8')
        req = urllib.request.Request(
            api_endpoint, 
            data=encoded_payload, 
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            pass
            
        return HTMLResponse(content="""
            <html>
                <body style="font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100vh; margin: 0;">
                    <svg style="width: 48px; height: 48px; color: #10b981; margin: 0 auto 16px auto;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <h3 style="margin: 0 0 8px 0; font-size: 1.25rem;">Sync Successful!</h3>
                    <p style="margin: 0; color: #94a3b8; font-size: 0.875rem;">Benefit registration verified & pushed to Workday.</p>
                </body>
                    </html>
        """)
    except Exception as e:
        return HTMLResponse(content=f"""
            <html>
                <body style="font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100vh; margin: 0;">
                    <h3 style="color: #ef4444; margin-bottom: 8px;">Sync Error</h3>
                    <p style="color: #94a3b8;">{str(e)}</p>
                </body>
            </html>
        """)

app.routes.append(Route("/submit_erp", handle_erp_submit, methods=["POST"]))

async def serve_logo(request):
    filename = request.path_params.get("filename")
    
    if not os.environ.get("K_SERVICE"):
        local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'logos')
        local_path = os.path.join(local_dir, filename)
        if os.path.exists(local_path):
            from starlette.responses import Response
            with open(local_path, "rb") as f:
                return Response(content=f.read(), media_type="image/png")
            
    try:
        from google.cloud import storage
        client = storage.Client(project="sandbox-426014")
        bucket = client.bucket("sandbox-426014-a2ui-media-cache")
        blob = bucket.blob(f"logos/{filename}")
        
        from starlette.responses import Response
        if not blob.exists():
             return Response(content="Logo not found in GCS", status_code=404)
             
        bytes_data = blob.download_as_bytes()
        return Response(content=bytes_data, media_type="image/png")
    except Exception as e:
        from starlette.responses import Response
        return Response(content=f"Internal Server Error: {str(e)}", status_code=500)

app.routes.append(Route("/logos/{filename}", serve_logo, methods=["GET"]))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=120)
