# GE A2UI Agent Seed Project (Acme Corp)

This repository serves as a generic, reusable **"seed"** for building Gemini Enterprise (GE) agents that leverage the **A2UI (Agent-to-Agent User Interface)** engine. It comes pre-configured with industry-agnostic widgets and clean, minimalist styling.

---

## 🏗️ Architecture

The seed project uses a **Server-Side Rendering (SSR)** approach for A2UI components:

1.  **Agent Orchestration**: The AI agent (Gemini) generates a `CustomView` JSON structure.
2.  **Template Injection**: The Python backend (`main.py`) reads modular HTML from `backend/templates/`, injects data from the tool context into `window.INJECTED_DATA`, and serves it via a `WebFrame`.
3.  **Cross-App Actions**: Supports bi-directional communication between the agent and external apps via `a2a.action` event triggers.

---

## 📂 Project Structure

-   `backend/templates/dashboard.html`: The core A2UI engine. Supports dynamic rendering of:
    -   `map-heatmap`: Integrated Google Maps with density layers.
    -   `d3-network`: Force-directed relationship graphs.
    -   `simulator`: Interactive logic-bound tradeoff modeling.
    -   `action-plan`: A generic, editable form-to-sync workflow.
-   `backend/agent.py`: Generic system instructions and tool routing for **Acme Corp**.
-   `backend/mock_data_tool.py`: Industry-agnostic data generators (Revenue, Growth, Regions).

---

## 🚀 Getting Started

### 1. Clone & Customize
Clone this repository and replace "Acme Corp" with your client's name in `agent.py` and `mock_data_tool.py`.

### 2. Configure Google Maps
To use the heatmap widget:
- Enable the **Maps JavaScript API**.
- Update the API Key in `backend/templates/dashboard.html`.

### 3. Deploy to Cloud Run
```bash
cd backend
./deploy.sh <YOUR_PROJECT_ID> <SERVICE_NAME>
```

---

## 🧩 A2UI Widget Specifications

### Map Heatmap
Plot density or hotspots with interactive tooltips.
- **Data Type**: `map-heatmap`
- **Fields**: `lat`, `lng`, `weight`, `entity_name`, `tooltip`.

### D3 Relationship Graph
Visualize complex node-edge connectivity with physics clamping.
- **Data Type**: `d3-network`
- **Fields**: `id`, `label`, `color`, `radius`, `external_id`.

### Scenario Simulator
Model tradeoffs with interactive sliders and non-linear logic.
- **Data Type**: `simulator`
- **Variables**: Fully customizable sliders.
- **Logic**: Injected via Javascript `onUpdateBody`.

### Action Plan
Bridge conversational planning into deterministic execution.
- **Data Type**: `action-plan`
- **Actions**: Packages form state into a `COMMIT_ACTION_PLAN` payload.

---

## 🛡️ Security & Best Practices
- **Allowlisting**: Always ensure your Cloud Run service URL is allowlisted in your GE Organization settings.
- **OAuth 2.0**: For multi-tenant production agents, refer to the `OAuth Register` guide in the root directory.
- **Least Privilege**: Grant only `roles/aiplatform.user` to the service account.
