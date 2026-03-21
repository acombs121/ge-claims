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

1.  **Cloud Run Service Account**:
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

## 🧰 A2UI Component Inventory

When configuring your Agent's `SYSTEM_INSTRUCTION`, it's critical to explicitly map specific intents to specific UI components. This Seed supports two primary rendering pathways:

1. **Native A2UI Arrays (For generic layout components)**
   - **`DataGrid`**: Use for raw tabular data. Instruct the LLM to output a Native A2UI Array containing the DataGrid component.
   - **`VegaChart`**: Use for isolated charts or basic trends. Instruct the LLM to output a Native A2UI Array containing a VegaChart, including responsive `width` and `height` container declarations.

2. **WebFrame `CustomView` Overlays (The Dynamic Hybrid Engine)**
   The core A2UI engine resides in `backend/templates/dashboard.html`. It mathematically iterates over a `grid` array populated by your LLM to render responsive panels. Available dynamic block `types` include:
   - **`chart`**: Generates a standard Chart.js Bar/Pie/Line visualization natively.
   - **`table`**: Constructs a styled HTML table fitted properly onto the CustomView card logic to prevent awkward A2UI stretching behavior.
   - **`form`**: Generates a beautiful HTML `<form>` based on `fields`. The `submit` button natively bridges a postMessage back to Agent-Stage/GE for true bi-directional functionality.
   - **`d3-network`**: Summons a premium, animated, interactive force-directed `d3.js` graph utilizing complex `nodes` and `edges` logic.
   - **`map-heatmap`**: Spawns a dedicated CARTO basemap via Leaflet projecting density hot-spots from `points` arrays.

   *(Other older templates like `map.html` and `inventory.html` serve as modular scaffolding if you need strictly disconnected routing endpoints).*

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
