# A2UI Seed Agent

This repository serves as a completely customer-agnostic, highly aesthetic, production-grade A2UI (Agent-to-Agent User Interface) Seed Agent (`a2ui_seed_agent`). 

It demonstrates the full spectrum of A2UI 0.8 native standard components and custom high-fidelity dynamic maps and metrics dashboards, deployed securely onto Google Cloud Run utilizing Application Default Credentials (ADC) under a dedicated service account identity.

For an architectural breakdown including how the agent reasons, please refer to [architecture.md](file:///Users/rtejada/Workspace/a2ui-seed-agent/architecture.md).

---

## The Core Capability Tour

### Standard A2UI Native Components
*   show standard widgets
*   give me an audio summary
*   generate custom visual graphic
*   give me a button
*   give me a dropdown list
*   give me tabs
*   show a modal

### Custom Viewport Extensions (WebFrames)
*   show a map visualization
*   give me a simple google map
*   show the universal dashboard
*   give me a network dashboard
*   show the team sprint task backlog
*   show the checkout register

---

## Google Cloud IAM Service Account & Security Strategy

This agent uses Google Cloud Application Default Credentials (ADC). Secure your terminal locally using `gcloud auth application-default login`, and the deployed Cloud Run instance automatically inherits Vertex AI and GCS storage access via the attached least-privileged service account `a2ui-seed-run-identity@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com` without managing any physical JSON key files.

---

## Prerequisites

To deploy or run this seed agent template in a new Google Cloud environment, verify the following prerequisites are fully configured:

### 1. Enable Google Cloud APIs
Run the following command inside your gcloud authenticated terminal to enable all required Vertex AI, storage, and maps orchestration APIs:
```bash
gcloud services enable \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    directions.googleapis.com \
    places.googleapis.com
```

### 2. Provision Cloud Storage Bucket
* Create a Google Cloud Storage bucket named **`{YOUR_GCP_PROJECT_ID}-a2ui-media-cache`** in the same region as your deployment (e.g., `us-central1`).
* This bucket is dynamically resolved at runtime to securely cache seekable WAV summaries and visual preview graphics.

### 3. Provision IAM Service Account Identity
Create a dedicated least-privileged service account named **`a2ui-seed-run-identity`** in your active project:
* **Service Account Email:** `a2ui-seed-run-identity@{YOUR_GCP_PROJECT_ID}.iam.gserviceaccount.com`
* **Assign Roles:**
  1. `roles/aiplatform.user` (Vertex AI User)
  2. `roles/storage.objectAdmin` (Storage Object Admin) on the media cache bucket.

### 4. Google Maps API Credentials
* Acquire a **Google Maps API Key** with both **Directions API** and **Places API** enabled.
* For local development runs, save this key inside a local `.env` file inside the `backend/` directory:
  ```env
  GOOGLE_MAPS_API_KEY=your_maps_api_key_here
  ```

---

## Getting Started

### 1. Running the Agent Locally
From the workspace root directory:
```bash
cd backend
python3 main.py
```
The server will start listening on `http://127.0.0.1:8080`.
Verify local tests are fully green before executing deploy scripts:
```bash
python3 -m unittest discover -s tests
```

### 2. Deploying to Cloud Run

To securely deploy this capability showcase template to Google Cloud Run, follow these step-by-step instructions:

1. **Configure your active terminal GCP project ID:**
   ```bash
   gcloud config set project YOUR_GCP_PROJECT_ID
   ```
2. **Deploy the container live using the secure deploy script:**
   ```bash
   cd backend
   ./deploy.sh
   ```
The deploy script dynamically extracts your active GCP project ID from your gcloud configurations, packages the agent, attaches the dedicated least-privileged IAM Service Account (`a2ui-seed-run-identity@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com`), configures the serverless environment, and updates the Cloud Run AGENT_URL parameter dynamically for seamless A2A header routing.

---

## How to Clone & Customize for New Demos

This repository is built as a highly modular, reusable seed template. To clone and customize this agent for a new industry, customer, or use-case specific visual showcase:

### 1. Clone the Repository
Clone the template codebase into your new custom repository name:
```bash
git clone https://github.com/cloud-ai-transformation-team/a2ui-seed-agent.git your-custom-agent
cd your-custom-agent
```

### 2. Customize the Agent Card & Identity
* **Agent Card Registration:** Open [agent_card.json](file:///Users/rtejada/Workspace/a2ui-seed-agent/agent_card.json) and update the `"name"`, `"description"`, and `"skills"` lists to match your custom persona.
* **LLM System Instructions:** Open [agent.py](file:///Users/rtejada/Workspace/a2ui-seed-agent/backend/agent.py) and modify the `SYSTEM_INSTRUCTION` string to adapt the agent's conversational guidelines and role constraints.

### 3. Customize the Visual Showcase & Scripts
* **Manifest Script Triggers:** Open [demo_manifest.json](file:///Users/rtejada/Workspace/a2ui-seed-agent/backend/demo_manifest.json) and change the step triggers under `trigger_queries` to align with your exact presentation script.
* **Widgets & Map Data:** Modify the mock coordinates, heatmaps, sliders, and modal options inside [showcase_widgets.json](file:///Users/rtejada/Workspace/a2ui-seed-agent/backend/data/showcase_widgets.json) and [map_showcase.json](file:///Users/rtejada/Workspace/a2ui-seed-agent/backend/data/map_showcase.json).
* **Vibrant HTML/CSS Styles:** Adjust color tokens and layout specifications inside the custom viewport templates ([universal_dashboard.html](file:///Users/rtejada/Workspace/a2ui-seed-agent/backend/templates/universal_dashboard.html) and [base_map.html](file:///Users/rtejada/Workspace/a2ui-seed-agent/backend/templates/base_map.html)) to fit your custom brand design.
