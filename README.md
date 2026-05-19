# A2UI Seed Agent

This repository serves as a completely customer-agnostic, highly aesthetic, production-grade A2UI (Agent-to-Agent User Interface) Seed Agent (`a2ui_seed_agent`). 

It demonstrates the full spectrum of A2UI 0.8 native standard components and custom high-fidelity dynamic maps and metrics dashboards, deployed securely onto Google Cloud Run utilizing Application Default Credentials (ADC) under a dedicated service account identity.

For a comprehensive architectural breakdown, please refer to [architecture.md](file:///Users/rtejada/Workspace/a2ui-seed-agent/architecture.md) and [plan.md](file:///Users/rtejada/Workspace/a2ui-seed-agent/plan.md).

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
*   load D3 network dashboard

---

## Google Cloud IAM Service Account & Security Strategy

This agent uses Google Cloud Application Default Credentials (ADC). Secure your terminal locally using `gcloud auth application-default login`, and the deployed Cloud Run instance automatically inherits Vertex AI and GCS storage access via the attached least-privileged service account `a2ui-seed-run-identity@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com` without managing any physical JSON key files.

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
