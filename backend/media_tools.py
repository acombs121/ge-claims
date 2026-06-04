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
    """Generates a synthetic image based on the provided text prompt. If the user uploaded images, they are natively injected into the generation payload automatically. Returns a Base64 string for direct CustomView rendering."""
    if not genai:
        return "Error: google-genai SDK is not installed or available."
    
    try:
        from google.cloud import storage
        storage_client = storage.Client()
        resolved_project = storage_client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
        
        client = genai.Client(
            vertexai=True,
            project=resolved_project,
            location="global"
        )

        contents_parts = []
        
        # Singleton Intercept: Retrieve the exact binary footprint cached by agent_executor natively from GCS
        try:
            from google.cloud import storage
            storage_client = storage.Client()
            project_id = storage_client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
            bucket_name = os.environ.get("A2UI_MEDIA_BUCKET") or f"{project_id}-a2ui-media-cache"
            bucket = storage_client.bucket(bucket_name)
            
            blob = bucket.blob("a2ui_latest_vision_bytes.bin")
            
            if blob.exists():
                image_bytes = blob.download_as_bytes()
            
                if image_bytes:
                    mime_type = "image/jpeg"
                    if image_bytes.startswith(b'\x89PNG'):
                        mime_type = "image/png"
                    elif image_bytes.startswith(b'RIFF'):
                        mime_type = "image/webp"
                    
                    # Construct rigid URI binding to force the model into restrictive visual processing loops
                    gcs_uri = f"gs://{bucket_name}/a2ui_latest_vision_bytes.bin"
                    vision_part = types.Part.from_uri(file_uri=gcs_uri, mime_type=mime_type)
                    
                    # CRITICAL: For Gemini 3.1 Flash Image Preview multimodal composition,
                    # the image Part MUST precede the explicit text instruction.
                    contents_parts.append(vision_part)
                    
                    # Prepend a strict, agnostic system command to force visual subject cohesion 
                    # based on the uploaded attachment, without assuming it is a logo.
                    prompt = f"[Target Context: You have been provided with an explicit source image attachment. You MUST use this attached image exactly as it appears as the primary visual reference for your generation, conforming to the prompt. Do not hallucinate or substitute visual elements for the source content; use the actual image data provided.]\n{prompt}"
            
                    print(f"A2UI-IMAGE-DEBUG | Successfully loaded transient image cache via GCS struct array: {gcs_uri}")

        except Exception as e:
            print(f"A2UI-IMAGE-DEBUG | Cache extraction error or missing GCS bucket mapping: {e}")
            pass # Fallback to standard text prompt handling
        
        contents_parts.append(types.Part.from_text(text=prompt))

        if tool_context:
            try:
                artifact_keys = await tool_context.list_artifacts()
                for key in artifact_keys:
                    image_bytes = await tool_context.load_artifact(key)
                    if image_bytes:
                        mime_type = "image/jpeg"
                        if image_bytes.startswith(b'\x89PNG'):
                            mime_type = "image/png"
                        elif image_bytes.startswith(b'RIFF'):
                            mime_type = "image/webp"
                        
                        vision_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                        contents_parts.append(vision_part)
                        print(f"A2UI-IMAGE-DEBUG | Successfully instantiated GenAI Part from natively hosted UI ToolContext artifact: {key}")
            except Exception as e:
                print(f"A2UI-IMAGE-DEBUG | WARNING: Native ToolContext load failure: {e}")
                pass

        # print boundary logic natively to Cloud Run logging
        debug_types = [str(type(p)) for p in contents_parts]
        print(f"A2UI-IMAGE-DEBUG | Executing Vertex Payload. Text: '{prompt}'. Encoded Vision Parts: {len(contents_parts)-1}")
        print(f"A2UI-IMAGE-DEBUG | Structured Polymorphic Array Blueprint: {debug_types}")

        # Execute wrapped strictly inside role Context bypassing standard text fallback
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

        print(f"A2UI-IMAGE-DEBUG | Calling generate_content with model: gemini-3.1-flash-image-preview")
        print(f"A2UI-IMAGE-DEBUG | Contents: {contents}")
        print(f"A2UI-IMAGE-DEBUG | Config: {generate_content_config}")
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=contents,
                config=generate_content_config,
            )
            print(f"A2UI-IMAGE-DEBUG | Response received successfully.")
        except Exception as e:
            import traceback
            print(f"A2UI-IMAGE-DEBUG | Error calling generate_content: {str(e)}")
            print(f"A2UI-IMAGE-DEBUG | Traceback: {traceback.format_exc()}")
            raise e

        for candidate in response.candidates:
            if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    import uuid
                    media_id = str(uuid.uuid4())
                    agent_root = os.environ.get("AGENT_URL", "")
                    
                    # Local Fallback Check
                    if not os.environ.get("K_SERVICE"):
                        local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'media_cache')
                        os.makedirs(local_dir, exist_ok=True)
                        
                        if hasattr(part, 'inline_data') and part.inline_data:
                            ext = part.inline_data.mime_type.split('/')[-1] if '/' in part.inline_data.mime_type else 'png'
                            with open(os.path.join(local_dir, f"{media_id}.{ext}"), "wb") as f:
                                f.write(part.inline_data.data)
                            return f"{agent_root}/media/{media_id}.{ext}"
                            
                        elif hasattr(part, 'image') and part.image:
                            with open(os.path.join(local_dir, f"{media_id}.jpeg"), "wb") as f:
                                f.write(part.image.image_bytes)
                            return f"{agent_root}/media/{media_id}.jpeg"
                            
                    # Original GCS path (only if K_SERVICE is present)
                    from google.cloud import storage
                    storage_client = storage.Client()
                    project_id = storage_client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
                    bucket_name = os.environ.get("A2UI_MEDIA_BUCKET") or f"{project_id}-a2ui-media-cache"
                    bucket = storage_client.bucket(bucket_name)

                    if hasattr(part, 'inline_data') and part.inline_data:
                        ext = part.inline_data.mime_type.split('/')[-1] if '/' in part.inline_data.mime_type else 'png'
                        blob = bucket.blob(f"generated_ads/{media_id}.{ext}")
                        blob.upload_from_string(part.inline_data.data, content_type=part.inline_data.mime_type)
                        return f"{agent_root}/media/{media_id}.{ext}"

                    elif hasattr(part, 'image') and part.image:
                        blob = bucket.blob(f"generated_ads/{media_id}.jpeg")
                        blob.upload_from_string(part.image.image_bytes, content_type="image/jpeg")
                        return f"{agent_root}/media/{media_id}.jpeg"

    except Exception as e:
        import traceback
        err_out = traceback.format_exc()
        print(f"IMAGE GEN FATAL ERROR: {err_out}")
        return f"Image generation explicitly failed against the Vertex global endpoint: {str(e)}. Please inform the user of this exact error string in your output so they can debug it."

    return "Error: Generated response did not contain inline image bytes."


async def generate_synthetic_audio(context_summary: str, tool_context: ToolContext = None) -> str:
    """Generates a synthetic audio podcast summary based on the current context using gemini-3.1-flash-tts-preview. Returns the public URL to the generated audio file."""
    if not genai:
        return "Error: google-genai SDK is not installed or available."
        
    try:
        from google.cloud import storage
        storage_client = storage.Client()
        resolved_project = storage_client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
        
        client = genai.Client(
            vertexai=True,
            project=resolved_project,
            location="global"
        )

        # Load manifest configuration for customizable audio voice settings
        audio_mode = "single"
        voices = ["Aoede"]
        speakers = ["Host"]
        
        import json
        try:
            manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'demo_manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                steps = manifest.get("steps", [])
                audio_step = next((s for s in steps if s.get("action_tool") == "generate_audio_summary"), None)
                if audio_step and "audio_config" in audio_step:
                    cfg = audio_step["audio_config"]
                    audio_mode = cfg.get("mode", "single")
                    voices = cfg.get("voices", ["Aoede"])
                    speakers = cfg.get("speakers", ["Host"])
        except Exception as e:
            print(f"A2UI-TTS-CONFIG | Failed loading custom audio config, using defaults: {e}")
            
        if audio_mode == "podcast" and len(voices) >= 2 and len(speakers) >= 2:
            transcript_prompt = f"Generate a professional 150-word audio summary discussing this context: {context_summary}. The speakers are {speakers[0]} (an expert) and {speakers[1]} (a specialist). Keep it friendly, highly contextual, and informative as a podcast conversation."
        else:
            transcript_prompt = f"Generate a professional 150-word audio briefing discussing this context: {context_summary}. Keep it friendly, clear, highly contextual, and informative as a single speaker presentation."
        
        transcript_res = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=transcript_prompt
        )
        transcript_text = transcript_res.text if transcript_res and hasattr(transcript_res, 'text') else context_summary
        
        if audio_mode == "podcast" and len(voices) >= 2 and len(speakers) >= 2:
            audio_config = types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(speaker=speakers[0], voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voices[0]))),
                            types.SpeakerVoiceConfig(speaker=speakers[1], voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voices[1])))
                        ]
                    )
                )
            )
        else:
            audio_config = types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voices[0])
                    )
                )
            )
        
        audio_res = client.models.generate_content(
            model="gemini-3.1-flash-tts-preview",
            contents=transcript_text,
            config=audio_config
        )
        
        audio_bytes = None
        mime_type = None
        if audio_res and hasattr(audio_res, 'candidates'):
            for candidate in audio_res.candidates:
                if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            audio_bytes = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            break
                        elif hasattr(part, 'audio_data') and part.audio_data:
                            audio_bytes = part.audio_data.audio_bytes
                            break
                            
        if not audio_bytes:
            return "Error: TTS model did not return audio bytes."
            
        # Transcode L16 raw PCM to browser-seekable WAV format
        if mime_type and "audio/l16" in mime_type.lower():
            import re
            import struct
            
            rate_match = re.search(r'rate=(\d+)', mime_type)
            channels_match = re.search(r'channels=(\d+)', mime_type)
            rate = int(rate_match.group(1)) if rate_match else 24000
            channels = int(channels_match.group(1)) if channels_match else 1
            
            print(f"A2UI-TTS-TRANSCODE | Transcoding raw L16 PCM ({rate}Hz, {channels}ch) to standard seekable WAV.")
            
            # WAV RIFF header construction
            num_channels = channels
            bytes_per_sample = 2 # 16-bit
            block_align = num_channels * bytes_per_sample
            byte_rate = rate * block_align
            data_size = len(audio_bytes)
            riff_size = 36 + data_size
            
            wav_header = struct.pack(
                '<4sI4s4sIHHIIHH4sI',
                b'RIFF',
                riff_size,
                b'WAVE',
                b'fmt ',
                16,             # Subchunk1Size
                1,              # AudioFormat (1 = PCM)
                num_channels,
                rate,
                byte_rate,
                block_align,
                16,             # BitsPerSample
                b'data',
                data_size
            )
            audio_bytes = wav_header + audio_bytes
            
        import uuid
        media_id = str(uuid.uuid4())
        agent_root = os.environ.get("AGENT_URL", "")
        
        if not os.environ.get("K_SERVICE"):
            local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'media_cache')
            os.makedirs(local_dir, exist_ok=True)
            with open(os.path.join(local_dir, f"{media_id}.wav"), "wb") as f:
                f.write(audio_bytes)
            return f"{agent_root}/media/{media_id}.wav"
            
        from google.cloud import storage
        storage_client = storage.Client()
        project_id = storage_client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
        bucket_name = os.environ.get("A2UI_MEDIA_BUCKET") or f"{project_id}-a2ui-media-cache"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"generated_ads/{media_id}.wav")
        blob.upload_from_string(audio_bytes, content_type="audio/wav")
        return f"{agent_root}/media/{media_id}.wav"
        
    except Exception as e:
        import traceback
        print(f"AUDIO GEN FATAL ERROR: {traceback.format_exc()}")
        return f"Audio generation explicitly failed against Vertex endpoint: {str(e)}."

def load_image_bytes(image_url_or_b64: str) -> bytes:
    """Helper to fetch and extract raw image bytes from URL, base64, GCS path, or local path."""
    if not image_url_or_b64:
        return None
    # If base64 data URI format
    if "," in image_url_or_b64:
        _, encoded = image_url_or_b64.split(",", 1)
        import base64
        try:
            return base64.b64decode(encoded)
        except Exception as e:
            print(f"Failed to decode base64 URI image: {e}")
    # If standard raw base64 string
    if len(image_url_or_b64) > 1000 and not image_url_or_b64.startswith("http") and not image_url_or_b64.startswith("/"):
        import base64
        try:
            return base64.b64decode(image_url_or_b64)
        except Exception as e:
            print(f"Failed to decode raw base64 image: {e}")
    # If local path or local route media path
    if image_url_or_b64.startswith("/") or "/media/" in image_url_or_b64:
        path = image_url_or_b64
        if "/media/" in image_url_or_b64:
            media_id = image_url_or_b64.split("/media/")[-1]
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "media_cache", media_id)
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return f.read()
            except Exception as e:
                print(f"Failed to read local image file at {path}: {e}")
    # If http or https URL
    if image_url_or_b64.startswith("http"):
        import urllib.request
        try:
            with urllib.request.urlopen(image_url_or_b64) as response:
                return response.read()
        except Exception as e:
            print(f"Failed to fetch image from URL {image_url_or_b64}: {e}")
    # If GCS URI format
    if image_url_or_b64.startswith("gs://"):
        try:
            from google.cloud import storage
            storage_client = storage.Client()
            bucket_part, blob_part = image_url_or_b64[5:].split("/", 1)
            bucket = storage_client.bucket(bucket_part)
            blob = bucket.blob(blob_part)
            return blob.download_as_bytes()
        except Exception as e:
            print(f"Failed to download image from GCS URI {image_url_or_b64}: {e}")
    return None

async def generate_veo_video(image_url: str = None, prompt: str = "Premium retail fashion modeling walking preview. Subject walking gracefully forward, elegant Outfit, high quality 720p video.", tool_context = None) -> str:
    """Generates a premium 4-second video preview via veo-2.0-generate-001 (supporting prompt customization and input image references)."""
    agent_root = os.environ.get("AGENT_URL", "http://127.0.0.1:8080")
    if not genai:
        print("google-genai SDK is not installed or available. Falling back to default mock walkthrough.")
        return f"{agent_root}/media/sample_walk.mp4"

    try:
        from google.cloud import storage
        storage_client = storage.Client()
        resolved_project = storage_client.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
        
        # Target us-central1 or appropriate Veo endpoint region
        client = genai.Client(
            vertexai=True,
            project=resolved_project,
            location="us-central1"
        )

        input_image = None
        img_bytes = load_image_bytes(image_url)
        if img_bytes:
            mime_type = "image/png"
            if img_bytes.startswith(b'\xff\xd8'):
                mime_type = "image/jpeg"
            elif img_bytes.startswith(b'\x89PNG'):
                mime_type = "image/png"
            elif img_bytes.startswith(b'RIFF'):
                mime_type = "image/webp"
            input_image = types.Image(image_bytes=img_bytes, mime_type=mime_type)

        print(f"A2UI-VEO-DEBUG | Invoking Veo model=veo-2.0-generate-001 with prompt: '{prompt}'")
        print(f"A2UI-VEO-DEBUG | Specs: duration=4, resolution=720p, aspect_ratio=16:9, has_input_image={input_image is not None}")
        
        kwargs = {
            "model": "veo-2.0-generate-001",
            "prompt": prompt,
            "config": types.GenerateVideosConfig(
                duration_seconds=4,
                aspect_ratio="16:9",
                person_generation="allow_adult"
            )
        }
        if input_image:
            kwargs["image"] = input_image

        operation = client.models.generate_videos(**kwargs)
        
        # Polling loop
        import time
        while not operation.done:
            print(f"A2UI-VEO-DEBUG | Polling Veo operation: {operation.name}...")
            time.sleep(5)
            operation = client.operations.get(operation=operation)
            
        if operation.error:
            raise Exception(f"Veo operation failed: {operation.error}")
            
        print(f"A2UI-VEO-DEBUG | Operation completed successfully. done={operation.done}, error={operation.error}")
            
        video_bytes = None
        response_obj = getattr(operation, 'response', None) or getattr(operation, 'result', None)
            
        if response_obj and hasattr(response_obj, 'generated_videos') and response_obj.generated_videos:
            generated_video = response_obj.generated_videos[0]
            if hasattr(generated_video, 'video') and generated_video.video:
                video_obj = generated_video.video
                if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                    video_bytes = video_obj.video_bytes
                elif hasattr(video_obj, 'uri') and video_obj.uri:
                    print(f"A2UI-VEO-DEBUG | Veo returned GCS URI: '{video_obj.uri}'. Downloading bytes...")
                    uri = video_obj.uri
                    if uri.startswith("gs://"):
                        bucket_part, blob_part = uri[5:].split("/", 1)
                        storage_client = storage.Client()
                        bucket = storage_client.bucket(bucket_part)
                        blob = bucket.blob(blob_part)
                        video_bytes = blob.download_as_bytes()
                
        if not video_bytes:
            raise ValueError("Veo operation did not return video_bytes or uri")
            
        import uuid
        media_id = str(uuid.uuid4())
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        if not os.environ.get("K_SERVICE"):
            local_dir = os.path.join(base_dir, 'data', 'media_cache')
            os.makedirs(local_dir, exist_ok=True)
            with open(os.path.join(local_dir, f"{media_id}.mp4"), "wb") as f:
                f.write(video_bytes)
            return f"{agent_root}/media/{media_id}.mp4"
        else:
            client_storage = storage.Client()
            p_id = client_storage.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
            bucket_name = os.environ.get("A2UI_MEDIA_BUCKET") or f"{p_id}-a2ui-media-cache"
            bucket = client_storage.bucket(bucket_name)
            blob = bucket.blob(f"generated_ads/{media_id}.mp4")
            blob.upload_from_string(video_bytes, content_type="video/mp4")
            return f"{agent_root}/media/{media_id}.mp4"

    except Exception as e:
        print(f"A2UI-VEO-DEBUG | Error calling Veo: {e}. Falling back to default mock walkthrough.")
        return f"{agent_root}/media/sample_walk.mp4"


