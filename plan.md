# Implementation Plan - Codebase Simplification

## Phase 1: Strategic Planning & Discovery

### 1. Objective
Simplify the `aon-hr-agent` codebase by implementing recommendations from Section 3 of the `architecture_and_cloning_guide.md`:
*   Standardize tools to return "Pure Data".
*   Introduce a declarative `demo_manifest.json`.
*   Move towards a Universal Dashboard approach.

### 2. Technical Approach & File Modifications

#### Step 1: Refactor Tools to Return "Pure Data"
*   **File**: `/Users/rtejada/Workspace/aon-hr-agent/backend/hr_data.py`
    *   Modify `get_benefits_summary` to return a structured dict containing lists/dicts of benefits data instead of Native A2UI components.
    *   Modify `register_benefit` to return a simple success/failure status dict instead of Native A2UI components.
*   **File**: `/Users/rtejada/Workspace/aon-hr-agent/backend/agent.py`
    *   Modify `generate_hr_graphic` to return a dict with the image URL and metadata instead of direct A2UI operations.

#### Step 2: Create Declarative Demo Manifest
*   **File**: `/Users/rtejada/Workspace/aon-hr-agent/backend/demo_manifest.json`
    *   Create this file to define the steps, triggers, and expected outputs/templates for the demo flow.

#### Step 3: Update Agent Executor for Manifest & Pure Data
*   **File**: `/Users/rtejada/Workspace/aon-hr-agent/backend/agent_executor.py`
    *   Update `AdkAgentToA2AExecutor` to load `demo_manifest.json`.
    *   Update `_process_response_content` or add a new method to map pure data from tools to the appropriate `CustomView` template based on the manifest or tool output.
    *   Implement `_handle_intercepted_action` to use the manifest for flow control if applicable.

#### Step 4: Universal Dashboard Template
*   **File**: `/Users/rtejada/Workspace/aon-hr-agent/backend/templates/universal_dashboard.html`
    *   Create a new template (or refactor `dashboard.html`) that can handle various component types (Table, Chart, Image, Network) dynamically, supporting the "Pure Data" returned by refactored tools.
    *   Ensure compliance with secure coding rules (avoid `innerHTML` where possible, use `textContent`).

### 3. Risks & Architectural Trade-offs
*   **Risk**: Refactoring tools may temporarily break the UI until the executor and templates are updated to handle the new data format.
*   **Mitigation**: We will implement changes incrementally and verify each step.
*   **Trade-off**: A declarative manifest adds a layer of abstraction in the executor but simplifies the agent prompt and cloning process.

### 4. Security Section (Mandatory)
*   **XSS Prevention**: We will ensure that the `universal_dashboard.html` uses safe DOM manipulation methods (like `textContent` and `createElement`) instead of `innerHTML` to prevent XSS when rendering data.
*   **Input Validation**: We will ensure that data processed by the executor is validated against expected schemas.

## Phase 2: Directed Implementation
(To be executed after approval)
