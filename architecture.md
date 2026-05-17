# ADK Agent Architecture

## 1. Context & Architecture

### Overview
This agent is built using the **Agent Development Kit (ADK)** and is designed to be **A2UI-enabled**. It is deployed as a containerized service on **Google Cloud Run** and integrated into **Gemini Enterprise (GE)** via the **A2A (Agent-to-Agent)** protocol. This integration provides the rich "agent card" experience in the GE interface.

### Constraints & Environment
*   **A2UI 0.8 Compatibility**: The deployed environment in GE strictly requires compliance with **A2UI schema version 0.8**. All rich UI components (DataGrids, Charts, Maps, Forms) must conform to this specific version's schema.
*   **Reference Libraries**: While local copies of `adk-python`, `a2a`, and `a2ui` may be available in the workspace, they serve as references. The actual agent implementations may vary to accommodate specific demo requirements and the A2UI 0.8 constraint.

---

## 2. Current Approach: Decoupled Data & Declarative UI

To address the complexity of building and cloning these agents, we use a design that **decouples data from presentation** and uses a **declarative manifest** to control the execution flow and UI rendering.

### 1. "Pure Data" Tools
Tools are strictly focused on fetching and returning business facts (raw data). They do not construct UI component trees or reference templates. This isolates the impact of data schema changes and makes tools reusable.

### 2. Component Library & Mappers
For scenarios where a low-overhead, native experience is preferred, we use a **Component Library** (`component_library.py`) to generate Native A2UI JSON payloads safely and consistently. Specialized **Mapper Functions** take the pure data from tools and use the library to build the specific card structure.

### 3. Declarative Demo Manifest
The `demo_manifest.json` file acts as the orchestration layer. It maps specific user queries to tools and defines the rendering strategy without hardcoding Python logic.

### 4. Dual-Tier Execution Engine & In-Memory Data Capture
To guarantee 100% reliable UI and data rendering across exact demo scripts and natural user variations, `agent_executor.py` operates a dual-tier architecture:
*   **Tier 1 (Fast-Path Interception)**: When a user query matches a `trigger_queries` substring exactly (ignoring punctuation), the server instantly executes the mapped tool in Python and emits the UI card directly. Zero LLM latency.
*   **Tier 2 (In-Memory Data Capture on LLM Fallback)**: When a query misses manifest triggers, the turn passes to the LLM for semantic tool selection. To eliminate JSON data truncation over chat streams, all registered Python tools are dynamically wrapped upon initialization. Whenever any tool executes in Python during an LLM turn, the wrapper captures the exact returned data dictionary directly in backend server memory (`self._last_tool_data`). During payload packaging, the server inspects the active tool against the manifest and passes the captured memory dictionary directly into the UI mapper (`native` or `iframe`), guaranteeing zero token overhead and flawless UI data hydration every single time.

## 3. Manifest Flexibility & Capabilities

The `demo_manifest.json` is highly flexible and supports the following options for each step:

*   **`trigger_queries`**: A list of strings to match against the user's input. The matching is a **simple substring check** (case-insensitive). It does not use regex or semantic matching.
*   **`output_mode`**:
    *   `"native"`: Renders low-overhead Native A2UI components (Cards, Tables, Text, ProductSelection) using mapper functions.
    *   `"iframe"`: Renders a rich custom dashboard inside a `WebFrameSrcdoc` using an HTML template.
    *   `"url"`: Renders an external allowlisted web URL directly in a `WebFrameUrl` (e.g. Google Maps embed).
    *   `"text"`: Bypasses UI generation and returns only text.

### Default Behavior
If a user query does not match any `trigger_queries` in the manifest, the system **defaults to running the LLM agent normally**. The LLM will then decide to call tools or generate a text response based on its system instructions.

### Note on Phases and Demo Flexibility
The `phase` field in `demo_manifest.json` is strictly **descriptive** and is **not enforced** by the executor. This allows the presenter to change the sequence of queries or repeat queries during a live demo without getting blocked by strict state transitions.

### Component Taxonomy: Standard vs. Custom
In Gemini Enterprise (A2UI 0.8), UI capabilities are strictly organized into two architectural layers:

#### 1. Standard Components (Core A2UI 0.8 Specification)
These native elements work out of the box with zero external template overhead. They are fully supported in `component_library.py`:
*   **Structural**: `Column`, `Row`, `Card`, `Divider`, `Surface`, `Root`, `UI`, `Styles`
*   **Content & Media**: `Text`, `Icon`, `Image`, `Video`, `AudioPlayer`
*   **Navigation & Overlays**: `List`, `Tabs`, `Modal`
*   **Input & Controls**: `Button`, `TextField`, `CheckBox`, `Slider`, `MultipleChoice`, `DateTimeInput`

#### 2. Custom Components (Specialized Extensions)
These are advanced domain-specific web components or sandboxed containers:
*   **`WebFrame` (`WebFrameSrcdoc` & `WebFrameUrl`)**:
    *   `WebFrameSrcdoc`: Renders sandboxed custom HTML/JS strings (like our `universal_dashboard` or `base_map` templates). It strictly enforces a CSP header (`connect-src 'none'`).
    *   `WebFrameUrl`: Renders allowlisted external URLs directly in an iframe (like Google Maps or YouTube embeds).
*   **`ProductSelection`**: A native custom component that renders editable tables with picklists and numerical validation.
*   **`DataGrid`**: High-performance tabular data viewer.
*   **`VegaChart`**: Declarative animated visual charts.
*   **`GeSduiViewer`**: Server-driven UI viewer. *(Note: In A2UI 0.8, this component is currently disabled/stubbed in the frontend code pending dynamic import support in Gemini Enterprise).*

### Advanced Visual Demos (Geographic Maps)
For complex geographic maps requiring heatmaps, pulsing CSS marker rings, and animated polyline routes, the agent uses `WebFrameSrcdoc` paired with the specialized `base_map.html` Leaflet pack. The manifest specifies `"output_mode": "iframe"` and `"template": "base_map"`, and the tool returns raw data (`heatmap_points`, `markers`, `routes`). For simple static or interactive maps without custom overlays, the agent can use `WebFrameUrl` pointing directly to Google Maps.

### Note on Templates
*   `universal_dashboard.html`: The secure, branded version for common components (Table, Chart, Image).
*   `dashboard.html`: Legacy template with advanced components (Vega, Simulator) but less strict security guards.
*   `base_map.html`: Specialized for map visualizations.

## 4. Supported Component Data Schemas

When returning pure data from tools to be rendered in `universal_dashboard.html`, follow these JSON structures for the `grid` array items:

### 1. Table
*   **`type`**: `"table"`
*   **`data`**:
    ```json
    {
      "headers": ["Header 1", "Header 2"],
      "rows": [
        ["Row 1 Col 1", "Row 1 Col 2"],
        ["Row 2 Col 1", "Row 2 Col 2"]
      ]
    }
    ```

### 2. Chart
*   **`type`**: `"chart"`
*   **`data`**:
    ```json
    {
      "type": "bar", 
      "labels": ["Jan", "Feb", "Mar"],
      "data": [10, 20, 30],
      "label": "Monthly Sales"
    }
    ```

### 3. Image
*   **`type`**: `"image"`
*   **`data`**: `"https://url-to-image.png"` OR `{"src": "...", "alt": "..."}`

### 4. Map (Heatmap & Points)
*   **`type`**: `"map-heatmap"`
*   **`data`**:
    ```json
    {
      "zoom": 11,
      "centerLat": 42.3601,
      "centerLng": -71.0589,
      "points": [
        {"lat": 42.36, "lng": -71.05, "weight": 1.0, "tooltip": "Info"}
      ]
    }
    ```

### 5. Simulator
*   **`type`**: `"simulator"`
*   **`data`**:
    ```json
    {
      "controls": [
        {"label": "Variable 1", "min": 0, "max": 100, "value": 50, "step": 1}
      ],
      "chartConfig": { },
      "onUpdateBody": "function body string..."
    }
    ```

### 6. Product Selection Table (Native Web Component)
*   **`type`**: `"product-selection"`
*   **`data`**:
    ```json
    {
      "columns": [
        {"key": "name", "label": "Product", "type": "string"},
        {"key": "category", "label": "Category", "type": "picklist", "editable": true, "options": ["Basic", "Premium", "Enterprise"]},
        {"key": "price", "label": "Price ($)", "type": "number", "editable": true}
      ],
      "rows": [
        {"name": "HR Platform License", "category": "Premium", "price": 5000}
      ],
      "title": "Included Products",
      "confirm_label": "Save",
      "cancel_label": "Reset"
    }
    ```

---

## 5. Multi-Step Cloning Protocol

When cloning an agent for a new customer or use case, avoid doing it in a single turn. Follow this structured protocol:

### Step 1: Narrative & Schema Design (Alignment Phase)
1.  Define the new target customer, industry, and persona.
2.  Map out the 4-5 steps of the demo flow (Queries -> Expected UI).
3.  Define the data schema needed for each step.
4.  *Stop and verify alignment.*

### Step 2: Synthetic Data Generation
1.  Generate the mock JSON data files in the `backend/data/` directory based on the approved schema.
2.  Ensure data is realistic and fits the narrative.

### Step 3: Core Logic & UI Adaptation
1.  Update `agent.py` with the new system instructions, triggers, and tools.
2.  Adapt the tools to fetch the new data and return it via `CustomView` or standard payloads.
3.  Update the HTML templates in `backend/templates/` if specific custom views are needed.

### Step 4: Meta-Files & Verification
1.  Update `deploy.sh` with the new service name.
2.  Update `agent_card.json` with new descriptions and metadata.
3.  Update `README.md` to reflect the new scenario and queries.
4.  Verify the execution flow locally before deployment.
