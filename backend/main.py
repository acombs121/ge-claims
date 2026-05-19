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

# ------------------------------------------------------------------------------
# PROACTIVE ENV LOAD: Load local .env file variables automatically
# ------------------------------------------------------------------------------
def load_env():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")
load_env()

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
            id="standard_widgets_showcase",
            name="Standard Components Showcase",
            description="Demonstrates dynamic form elements, sliders, modals, checkboxes, and tabs.",
            tags=["widgets", "inputs", "tabs"],
            examples=["let's see standard widgets overview"],
        ),
        a2a_types.AgentSkill(
            id="interactive_maps_overlay",
            name="Geographic Maps and Overlays",
            description="Visualizes routing paths, pulsing priority anchors, and density layers dynamically.",
            tags=["maps", "leaflet", "overlays"],
            examples=["show map visualization"],
        ),
        a2a_types.AgentSkill(
            id="universal_dashboard_metrics",
            name="Universal Metrics Dashboard",
            description="Displays KPI boxes, responsive D3 org network graphs, and interactive simulator variables.",
            tags=["dashboard", "d3-network", "charts"],
            examples=["show universal dashboard"],
        ),
        a2a_types.AgentSkill(
            id="seekable_audio_tts",
            name="Transcoded Speech WAV Summarizer",
            description="Provides customizable podcast voice briefings read dynamically.",
            tags=["audio", "tts", "podcast"],
            examples=["give me an audio summary"],
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
import re

def get_range_response(file_path: str, media_type: str, request_headers: dict) -> Response:
    file_size = os.path.getsize(file_path)
    range_header = request_headers.get("range")
    
    cors_headers = {
        "Access-Control-Allow-Origin": request_headers.get("origin", "*"),
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Range, Content-Type",
        "Access-Control-Expose-Headers": "Content-Range, Content-Length, Accept-Ranges",
        "Accept-Ranges": "bytes",
    }

    if not range_header:
        with open(file_path, "rb") as f:
            content = f.read()
        return Response(
            content=content,
            status_code=200,
            media_type=media_type,
            headers=cors_headers
        )

    match = re.match(r"bytes=(\d+)-(\d*)", range_header)
    if not match:
        return Response(
            content="Invalid range header",
            status_code=400,
            headers=cors_headers
        )

    start = int(match.group(1))
    end_str = match.group(2)
    end = int(end_str) if end_str else file_size - 1

    if start >= file_size:
        cors_headers["Content-Range"] = f"bytes */{file_size}"
        return Response(
            status_code=416,
            headers=cors_headers
        )

    end = min(end, file_size - 1)
    chunk_size = end - start + 1

    with open(file_path, "rb") as f:
        f.seek(start)
        data = f.read(chunk_size)

    cors_headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    cors_headers["Content-Length"] = str(chunk_size)

    return Response(
        content=data,
        status_code=206,
        media_type=media_type,
        headers=cors_headers
    )

async def serve_media(request):
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Range, Content-Type",
                "Access-Control-Expose-Headers": "Content-Range, Content-Length, Accept-Ranges",
            }
        )

    media_id = os.path.basename(request.path_params.get("media_id"))
    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'media_cache')
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, media_id)
    
    ext = media_id.split(".")[-1].lower()
    if ext == "wav":
        media_type = "audio/wav"
    elif ext == "mp3":
        media_type = "audio/mpeg"
    elif ext == "png":
        media_type = "image/png"
    elif ext == "webp":
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    if os.path.exists(local_path):
        try:
            return get_range_response(local_path, media_type, request.headers)
        except Exception as e:
            logger.error(f"Error serving local file: {e}")

    try:
        from google.cloud import storage
        client = storage.Client()
        project_id = client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
        bucket_name = os.environ.get("A2UI_MEDIA_BUCKET") or f"{project_id}-a2ui-media-cache"
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"generated_ads/{media_id}")
        
        if not blob.exists():
             cors_headers = {
                 "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                 "Access-Control-Expose-Headers": "Content-Range, Content-Length, Accept-Ranges",
             }
             return Response(content="Media not found or expired from persistent GCS cache.", status_code=404, headers=cors_headers)
             
        blob.download_to_filename(local_path)
        return get_range_response(local_path, media_type, request.headers)
    except Exception as e:
        logger.error(f"Error serving media dynamically from GCS: {e}")
        cors_headers = {
             "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
             "Access-Control-Expose-Headers": "Content-Range, Content-Length, Accept-Ranges",
        }
        return Response(content=f"Internal Server Error: {str(e)}", status_code=500, headers=cors_headers)

app.routes.append(Route("/media/{media_id}", serve_media, methods=["GET", "OPTIONS"]))

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
    filename = os.path.basename(request.path_params.get("filename"))
    
    if not os.environ.get("K_SERVICE"):
        local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'logos')
        local_path = os.path.join(local_dir, filename)
        if os.path.exists(local_path):
            from starlette.responses import Response
            with open(local_path, "rb") as f:
                return Response(content=f.read(), media_type="image/png")
            
    try:
        from google.cloud import storage
        client = storage.Client()
        project_id = client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
        bucket_name = os.environ.get("A2UI_MEDIA_BUCKET") or f"{project_id}-a2ui-media-cache"
        bucket = client.bucket(bucket_name)
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
