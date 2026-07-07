# GECX Insurance Claims Assistant Agent for Gemini Enterprise

GECX Insurance Claims Assistant is an MCA (Model Context Protocol) agent designed to work with **Gemini Enterprise** to automate claims triage, damage verification, risk analysis, contractor mapping, and settlement workflows.

It implements the entire claims handler experience through a series of five structured interactive reports rendered inside Gemini Enterprise's wide side panel (`"canvas-surface"`).

---

## Key Beats & Features

1. **Policy Verification & Triage (Beat 1):** Automates the review of coverage limits, policy status, and exclusions based on the specific First Notice of Loss (FNOL) inputs.
2. **Damage Visual Forensics (Beat 2):** Extracts key damage indicators from uploaded photos (e.g. water depth extraction, flooring materials) using Gemini Multimodal reasoning.
3. **Risk & Fraud Assessment (Beat 3):** Performs historical audit checks (tenure, loyalty tier, and prior claim frequency) to generate a verified fraud risk score.
4. **Itemized Estimate & Contractor Map (Beat 4):** Itemizes repair costs, deductibles, and net settlement payouts alongside an interactive dark map pinpointing the closest available local emergency responders.
5. **Regulatory Settlement Letter & Dispatch Booking (Beat 5):** Outlines a formal regulatory approval letter complying with Ohio state regulations and provides an interactive appointment scheduler to dispatch emergency water restoration.

---

## Tech Stack & Architecture

* **Backend:** Python + FastAPI / WSGI server.
* **UI Renderer:** Agent-to-UI (A2UI) protocol.
* **Frontend Panels:** Full-height scrollable HTML frames (`WebFrameSrcdoc`) styled in a luxury dark monochrome palette matching Gemini Enterprise UI standards.
* **Geospatial Services:** Leaflet and Google Maps API for contractor dispatch routing.

---

## Environment Variables

Ensure the following variables are configured in your environment or local `.env` file (not committed to git):

| Variable | Description | Example |
| :--- | :--- | :--- |
| `GEMINI_MODEL` | Mandatory LLM deployment target (defaults to `gemini-3.5-flash`). | `gemini-3.5-flash` |
| `GOOGLE_MAPS_API_KEY` | Key used to authorize and render Google Maps. | `AIzaSy...` |
| `AGENT_URL` | The public endpoint of your deployed service. | `https://ge-insurance-claims-...` |

---

## Deployment & Setup

### 1. Local Run
To run the server locally:
```bash
python3 backend/agent.py
```

### 2. Deploy to Cloud Run
To build and deploy the container to GCP Cloud Run, ensure your GCP SDK is configured and run:
```bash
./backend/deploy.sh
```

---

## Security & Exclusions

* **Git Exclusion:** A robust `.gitignore` prevents logs, local virtual environments, and `.env` credentials from being committed.
* **Secure Auth:** No hardcoded API keys exist in the codebase. All sensitive API keys are parsed securely from GCP Cloud Run environment settings at runtime.
