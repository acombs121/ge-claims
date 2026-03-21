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
        "sample_pdf_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    }

async def generate_synthetic_image(prompt: str, tool_context: ToolContext = None) -> str:
    """Generates an image via Gemini 3.1 Flash Image Preview based on the provided text prompt. If the user uploaded images, they are natively injected into the generation payload automatically. Returns a Base64 string for direct CustomView rendering."""
    if not genai:
        return "Error: google-genai SDK is not installed or available."
    
    try:
        client = genai.Client(
            vertexai=True,
            api_key=os.environ.get("GOOGLE_CLOUD_API_KEY", None),
        )

        contents_parts = []

        # Autonomously bind user-uploaded image fragments from the active context
        if tool_context:
            try:
                artifact_keys = await tool_context.list_artifacts()
                for key in artifact_keys:
                    if key.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        image_part = await tool_context.load_artifact(key)
                        if image_part:
                            contents_parts.append(image_part)
            except Exception as e:
                pass
        
        # Append target text prompt
        contents_parts.append(types.Part.from_text(text=prompt))
        contents = [types.Content(role="user", parts=contents_parts)]

        generate_content_config = types.GenerateContentConfig(
            temperature = 0.5,
            response_modalities = ["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="auto", image_size="1K", output_mime_type="image/jpeg")
        )

        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=contents,
                config=generate_content_config,
            )

            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            b64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                            return f"data:{part.inline_data.mime_type};base64,{b64}"
                        elif hasattr(part, 'image') and part.image:
                            b64 = base64.b64encode(part.image.image_bytes).decode('utf-8')
                            return f"data:image/jpeg;base64,{b64}"

        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                # Graceful degradation fallback if the user's GCP project is not yet whitelisted 
                # for the experimental multimodal Gemini Image Previews.
                imagen_resp = client.models.generate_images(
                    model="imagen-3.0-generate-002",
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1, 
                        output_mime_type="image/jpeg",
                        aspect_ratio="1:1"
                    )
                )
                if imagen_resp.generated_images:
                    img = imagen_resp.generated_images[0]
                    b64 = base64.b64encode(img.image.image_bytes).decode('utf-8')
                    return f"data:image/jpeg;base64,{b64}"
            
            raise e

        return "Error: Generated response did not contain inline image bytes."

    except Exception as e:
        import traceback
        return f"Image generation failed natively: {str(e)}"
