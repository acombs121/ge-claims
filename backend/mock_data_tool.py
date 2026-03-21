import os
import base64
from google.adk.tools import ToolContext

# Conditional bindings for GenAI 3.1 Imaging
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

def fetch_comprehensive_dashboard_data(tool_context: ToolContext = None) -> dict:
    """Fetches a mock dataset designed to test all major A2UI components (DataGrid, VegaChart, KPIs, WebFrame maps)."""
    return {
        "title": "Comprehensive Analytics Overview",
        "description": "Mock dataset for Acme Corp testing UI widgets including DataGrid, VegaChart, Map, and basic KPIs.",
        "kpis": [
            {"title": "Total Revenue", "value": "$124,500", "status": "success"},
            {"title": "Active Users", "value": "12,430", "status": "neutral"},
            {"title": "Bounce Rate", "value": "45%", "status": "warning"}
        ],
        "sales_tabular_data": {
            "columns": [
                {"field": "id", "headerName": "ID", "width": 90},
                {"field": "region", "headerName": "Region", "width": 150},
                {"field": "sales", "headerName": "Sales ($)", "width": 150, "type": "number"},
                {"field": "status", "headerName": "Status", "width": 110}
            ],
            "rows": [
                {"id": 1, "region": "North America", "sales": 45000, "status": "Above Target"},
                {"id": 2, "region": "Europe", "sales": 32000, "status": "On Target"},
                {"id": 3, "region": "Asia Pacific", "sales": 28500, "status": "Below Target"},
                {"id": 4, "region": "South America", "sales": 19000, "status": "Below Target"}
            ]
        },
        "growth_chart_spec": {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "A simple bar chart with embedded data.",
            "data": {
                "values": [
                    {"month": "Jan", "growth": 2.5},
                    {"month": "Feb", "growth": 3.8},
                    {"month": "Mar", "growth": -1.2},
                    {"month": "Apr", "growth": 5.4},
                    {"month": "May", "growth": 6.1},
                    {"month": "Jun", "growth": 4.0}
                ]
            },
            "mark": "bar",
            "encoding": {
                "x": {"field": "month", "type": "nominal", "sort": None, "axis": {"labelAngle": 0}},
                "y": {"field": "growth", "type": "quantitative"},
                "color": {
                    "condition": {"test": "datum.growth < 0", "value": "#ef4444"},
                    "value": "#3b82f6"
                }
            }
        },
        "hq_location": {
            "lat": 37.4220,
            "lng": -122.0841,
            "name": "Acme Corp Global HQ",
            "address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043"
        }
    }

def describe_storage_assets(tool_context: ToolContext = None) -> dict:
    """Returns sample URLs for cloud-hosted images, videos, audio, and pdfs to test frontend media rendering."""
    return {
        "sample_video_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "sample_audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "sample_image_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/woman.jpg",
        "sample_pdf_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    }

def process_form_submission(payload: dict, tool_context: ToolContext = None) -> str:
    """Mocks a backend system logging an ingested payload correctly piped via Agent-Stage `a2a.action`."""
    print(f"--- BACKEND API RECEIVED FORM PAYLOAD ---")
    print(payload)
    print(f"-----------------------------------------")
    return f"Successfully processed payload containing keys: {list(payload.keys())}!"

def generate_demo_living_room_image(tool_context: ToolContext = None) -> str:
    """Generates an image via Gemini 3.1 Flash Image Preview from a complex set of Google Cloud Storage asset attachments. Returns a Base64 string for direct CustomView rendering."""
    if not genai:
        return "Error: google-genai SDK is not installed or available."
    
    try:
        # vertexai=True uses ADC (gcloud auth) under the hood if GOOGLE_CLOUD_API_KEY isn't present.
        client = genai.Client(
            vertexai=True,
            api_key=os.environ.get("GOOGLE_CLOUD_API_KEY", None),
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        )

        image1 = types.Part.from_uri(file_uri="gs://cloud-samples-data/generative-ai/image/woman.jpg", mime_type="image/jpeg")
        image2 = types.Part.from_uri(file_uri="gs://cloud-samples-data/generative-ai/image/suitcase.png", mime_type="image/png")
        image3 = types.Part.from_uri(file_uri="gs://cloud-samples-data/generative-ai/image/armchair.png", mime_type="image/png")
        image4 = types.Part.from_uri(file_uri="gs://cloud-samples-data/generative-ai/image/man-in-field.png", mime_type="image/png")
        image5 = types.Part.from_uri(file_uri="gs://cloud-samples-data/generative-ai/image/shoes.jpg", mime_type="image/jpeg")
        image6 = types.Part.from_uri(file_uri="gs://cloud-samples-data/generative-ai/image/living-room.png", mime_type="image/png")
        text1 = types.Part.from_text(text="Generate an image of a woman sitting in a living room with a man. The man is wearing the brown sneakers. The woman is wearing a red version of the sneakers. The woman is sitting in a white armchair with a blue suitcase next to her.")

        contents = [types.Content(role="user", parts=[image1, image2, image3, image4, image5, image6, text1])]

        generate_content_config = types.GenerateContentConfig(
            temperature = 1,
            top_p = 0.95,
            response_modalities = ["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="auto", image_size="1K", output_mime_type="image/png")
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=contents,
            config=generate_content_config,
        )

        # Retrieve bytes natively across part bindings
        for candidate in response.candidates:
            if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        b64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                        return f"data:{part.inline_data.mime_type};base64,{b64}"
                    elif hasattr(part, 'image') and part.image:
                        b64 = base64.b64encode(part.image.image_bytes).decode('utf-8')
                        return f"data:image/png;base64,{b64}"

        return "Error: Generated response did not contain inline image bytes."

    except Exception as e:
        import traceback
        return f"Image generation failed natively: {str(e)}\n\n{traceback.format_exc()}"
