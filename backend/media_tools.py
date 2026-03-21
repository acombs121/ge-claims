import os
import base64
from google.adk.tools import ToolContext

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

def describe_storage_assets(tool_context: ToolContext = None) -> dict:
    """Returns sample URLs for cloud-hosted images, videos, audio, and pdfs to test frontend media rendering."""
    return {
        "sample_video_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "sample_audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "sample_image_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/image/woman.jpg",
        "sample_pdf_url": "https://storage.googleapis.com/cloud-samples-data/generative-ai/pdf/2403.05530.pdf"
    }

async def generate_synthetic_image(prompt: str, tool_context: ToolContext = None) -> str:
    """Generates an image via Gemini 3.1 Flash Image Preview based on the provided text prompt. If the user uploaded images, they are natively injected into the generation payload automatically. Returns a Base64 string for direct CustomView rendering."""
    if not genai:
        return "Error: google-genai SDK is not installed or available."
    
    try:
        client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "sandbox-426014"),
            location="global"
        )

        contents_parts = [types.Part.from_text(text=prompt)]
        
        if tool_context:
            try:
                artifact_keys = await tool_context.list_artifacts()
                for key in artifact_keys:
                    if key.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        image_bytes = await tool_context.load_artifact(key)
                        if image_bytes:
                            ext = key.lower().split('.')[-1]
                            mime_type = f"image/{'jpeg' if ext == 'jpg' else ext}"
                            vision_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                            contents_parts.append(vision_part)
            except Exception as e:
                pass
        
        # print boundary logic natively to Cloud Run logging
        print(f"A2UI-IMAGE-DEBUG | Executing Vertex Payload. Text: '{prompt}'. Encoded Vision Parts: {len(contents_parts)-1}")

        contents = [types.Content(role="user", parts=contents_parts)]

        generate_content_config = types.GenerateContentConfig(
            temperature = 1,
            top_p = 0.95,
            max_output_tokens = 32768,
            response_modalities = ["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
              aspect_ratio="1:1",
              image_size="1K",
              output_mime_type="image/png",
            )
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=contents,
            config=generate_content_config,
        )

        for candidate in response.candidates:
            if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    import uuid
                    os.makedirs('/tmp/a2ui_media', exist_ok=True)
                    media_id = str(uuid.uuid4())
                    agent_root = os.environ.get("AGENT_URL", "")

                    if hasattr(part, 'inline_data') and part.inline_data:
                        ext = part.inline_data.mime_type.split('/')[-1] if '/' in part.inline_data.mime_type else 'png'
                        filepath = f"/tmp/a2ui_media/{media_id}.{ext}"
                        with open(filepath, "wb") as f:
                            f.write(part.inline_data.data)
                        return f"{agent_root}/media/{media_id}.{ext}"

                    elif hasattr(part, 'image') and part.image:
                        filepath = f"/tmp/a2ui_media/{media_id}.jpeg"
                        with open(filepath, "wb") as f:
                            f.write(part.image.image_bytes)
                        return f"{agent_root}/media/{media_id}.jpeg"

    except Exception as e:
        import traceback
        err_out = traceback.format_exc()
        print(f"IMAGE GEN FATAL ERROR: {err_out}")
        return f"Image generation explicitly failed against the Vertex global endpoint: {str(e)}. Please inform the user of this exact error string in your output so they can debug it."

    return "Error: Generated response did not contain inline image bytes."
