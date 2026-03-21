# Gemini Enterprise (GE) A2UI Agent Seed

This repository is a **Seed Template** designed by the CAIT team to rapidly spin up and deploy custom AI strategy agents with advanced interactive **A2UI visualizations** served via `WebFrame` components.

---

## 🏗️ Architecture: Dynamic HTML Injection

To bypass constraints where custom widgets (like Maps or rich interactive charts) are not bundled into local workspaces, this agent leverages **Backend Orchestration**:

1.  The **LLM** yields a simple JSON payload declared as a `CustomView`.
    ```json
    {
      "CustomView": {
        "template": "inventory",
        "data": { "kpis": [...], "table": [...] }
      }
    }
    ```
2.  The **Python Executor** intercepts this payload, reads `backend/templates/{template_name}.html`, injects the data directly into the header script variables (`window.INJECTED_DATA`), and wraps it in a standard `WebFrame` component frame.
3.  The dashboard loads seamlessly in client views with **Lightweight loading tiers**.

---

## 📋 Prerequisites & Permissions (Allowlist Setup)

To run A2UI agents on Argolis:

1.  **Vertex AI API**:
    - Ensure the `aiplatform.googleapis.com` (Vertex AI API) is fully enabled in your Google Cloud Project: `gcloud services enable aiplatform.googleapis.com`. This is strictly required for the Gemini Image Generation models to function properly natively.
2.  **Cloud Run Service Account**:
    Ensure the Service account deployed with has correct permissions to query Vertex AI:
    - `roles/aiplatform.user`
    - `roles/storage.objectViewer` (If pulling unstructured data assets)

---

## 📂 Folder Structure

-   `backend/templates/`: Contains modular HTML framing injection points.
    -   `dashboard.html`: Generic KPIs + visually rich Analysis Charts.
    -   `inventory.html`: Grid layout for Supply Chain/Tracking view structures.
    -   `map.html`: Interactive Leaflet Map placeholders.
-   `backend/agent_executor.py`: Orchestrated layout handler resolving template bridging overlays.
-   `backend/prompt_builder.py`: Instructions advising the agent on which template framing structure is optimal to avoid syntax crash dependencies.

---

## ⚙️ Cloning & Deploying Guidelines

### Step 1: Clone
Copy this structure into your target repository path context.

### Step 2: Configure Display metadata
Update `backend/main.py` inside the `AgentCard` declarations with your specific descriptive metadata naming anchors.

### Step 3: Deploy
Execute to push direct updates aligned with Cloud Run bridging constraints:
```bash
./deploy.sh
```

---

## 📑 Model Card Placement Guideline
Inside your cloned documentation framework, create a `MODEL_CARD.md` tracking model calibration:

```markdown
# Model Card: [Agent Name]
- **Base Model**: Gemini-3-Flash-Preview
- **Persona**: [Describe intent e.g., Supply Chain Advisor]
- **Data Groundings**: [List BQ datasets, Vertex Search indexes]
- **Safety Thresholds**: Strict boundary conditions declaring safe alignment transparent outputs.
```

---

## 🔌 A2UI Agent Card Specification
When registering your endpoint inside Gemini Enterprise (GE), you **must** supply specific A2A bridging protocols, transport configurations, and formal A2UI extension dictionaries within your JSON profile. 

If you do not declare `"protocolVersion": "0.3.0"` and the default I/O modes, GE will reject the payload. 

Use this verified template:
```json
{
  "name": "YOUR_AGENT_NAME",
  "description": "YOUR_AGENT_DESCRIPTION",
  "url": "https://YOUR-DEPLOYED-APP.run.app",
  "version": "1.0.0",
  "protocolVersion": "0.3.0",
  "preferredTransport": "JSONRPC",
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain",
    "application/json"
  ],
  "capabilities": {
    "streaming": true,
    "extensions": [
      {
        "uri": "https://a2ui.org/a2a-extension/a2ui/v0.8",
        "description": "Ability to render A2UI",
        "required": false,
        "params": {
          "supportedCatalogIds": [
            "https://a2ui.org/specification/v0_8/standard_catalog_definition.json"
          ],
          "acceptsInlineCatalogs": true
        }
      }
    ]
  },
  "skills": [
    {
      "id": "chat",
      "name": "Base Chat Interaction",
      "description": "YOUR_SKILL_DESCRIPTION",
      "tags": ["your_tag"],
      "examples": [
        "Example User Query..."
      ]
    }
  ]
}
```

---

## 🌟 Summary of Engine Capabilities

This agent seed is pre-configured with a powerful `CustomView` frontend engine mapping natively to backend tools, giving your LLM an advanced toolbelt for rendering rich interactions and multimodal data.

### 1. The Dynamic Hybrid UI Engine
The core rendering environment revolves around `backend/templates/dashboard.html`. Your LLM can construct a flexible JSON `grid` spanning the following components:
- **`d3-network`**: Instantiates a premium, interactive D3.js force-directed physics graph (with cursor tooltips) using `nodes` and `edges` logic.
- **`map-heatmap`**: Spawns a Leaflet + CARTO dark/light basemap projecting dense geospatial hot-spots from lat/lng `points`.
- **`form`**: Constructs a completely dynamic HTML `<form>`. The `submit` button natively bridges a postMessage payload *back* up to Agent-Stage/GE for true bi-directional functionality.
- **`chart` / `table`**: Standard Chart.js panels and HTML tabular arrays.

*(For simple, isolated elements, the Agent is also instructed on basic Native A2UI Arrays for `DataGrid` and `VegaChart`).*

### 2. Generative Media Pipelines
The seed securely mounts the `google-genai` Python SDK. You can instruct the agent to generate completely new images via **Gemini 3.1 Flash Image Preview**. 
- The backend parses the byte stream, base64 encodes it, and hands the LLM a clean `data:image/` string.
- The LLM injects that string into an `image` grid block in the dashboard, rendering generative media *instantly*.

### 3. Cloud Storage Asset Mounting
The backend provides architectural tooling designed to authenticate with Google Cloud Storage (`storage.Client()`). The dashboard engine has native wrappers `video`, `audio`, and `pdf`. The agent can seamlessly query a bucket dataset and pass the resultant cloud URLs directy into the dashboard for users to playback or verify.

---

## 🚀 Cloning Instructions for Antigravity IDE

When you are ready to expand this seed into a new industry or use case, copy the following prompt, fill in your brackets `[...]`, and paste it into a new Antigravity session:

```markdown
I want to expand the `ge-agent-seed` repository into a brand new agent for [TARGET INDUSTRY / USE CASE].

Please follow these exact execution steps:

1. **Clone the Repository**:
   - Recursively copy `/Users/rtejada/Workspace/ge-agent-seed` into a new directory named `[new-agent-directory]`. 
   - Work entirely within the new directory for the remainder of this prompt.

2. **Service Name & Deployment Configuration**:
   - Open `backend/deploy.sh`.
   - Update `SERVICE_NAME` to `[new-agent-name]`.
   - *Do not execute the deployment just yet.*

3. **Tool & Data Configuration**:
   - Open `backend/mock_data_tool.py`.
   - Delete the generic Acme Corp data. 
   - Build new tool functions returning comprehensive mock data for [TARGET INDUSTRY]. Include at least:
     - A tabular dataset (`columns` and `rows`) for a Native DataGrid.
     - A valid Vega-Lite chart `spec` object for a Native VegaChart.
     - A JSON schema payload containing an array of `fields` (with labels/types) intended for a dynamic HTML `<form>`.
     - Relational JSON payloads mapping `nodes` and `edges` intended for a `d3-network` physics simulator.
     - A geospatial heatmap dataset mapping `[lat, lng, density]` pairings intended for a Leaflet `map-heatmap`.
     - High-level metric objects for dashboard KPIs.

4. **Agent & Prompt Mapping Configuration (CRITICAL)**:
   - Open `backend/agent.py`.
   - Update `SYSTEM_INSTRUCTION` to reflect the new persona: **[PERSONA DESCRIPTION]**.
   - Carefully map the new tools to specific A2UI outputs. 
   - **Pitfall Avoidance**: Explicitly state the following routing logic directly into the persona: 
      *"If asked for [X], output a Native A2UI Array containing a DataGrid. 
      If asked for [Y], output a Native A2UI Array containing a VegaChart. 
      If asked for [Z], output a CustomView dashboard template. 
      If asked for an interactive submission form, output a CustomView dashboard template explicitly declaring a `form` type panel in your layout grid. 
      If asked for network configurations, output a CustomView dashboard template explicitly declaring a `d3-network` type panel in your layout grid.
      If asked for hotspots, output a CustomView dashboard explicitly declaring a `map-heatmap` type panel in your layout grid."*

5. **Generate the Agent Card Artifact**:
   - Create a `[agent_name]_agent_card.json` artifact in our chat context.
   - It must securely follow the A2UI Agent Card Specification (Protocol Version `0.3.0`, `JSONRPC` transport, A2UI `v0.8` extension capabilities).
   - Generate relevant skill examples for my new use case spanning Native Charts, DataGrids, Forms, D3 Networks, and Map Heatmaps.

6. **Deploy**:
   - Make `deploy.sh` executable and run it to push the new container to Cloud Run. Be prepared for the script's silent environment-variable auto-update.
```
