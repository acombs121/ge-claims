import vertexai
from vertexai.preview import reasoning_engines
import os

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
LOCATION = "us-central1"
STAGING_BUCKET = os.environ.get("A2UI_STAGING_BUCKET") or f"gs://{PROJECT_ID}-a2ui-media-cache"

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

class DummyReasoner:
    def query(self, input: str) -> str:
        return f"Dummy response to: {input}"

try:
    print("Creating dummy Reasoning Engine...")
    # Passing the class instance as a positional argument to satisfy the method checks
    engine = reasoning_engines.ReasoningEngine.create(
        DummyReasoner(),
        display_name="Dummy Reasoning Engine for Session Storage",
    )
    print(f"Reasoning Engine created successfully!")
    print(f"Resource ID: {engine.resource_name}")
except Exception as e:
    print(f"Error creating Reasoning Engine: {e}")
