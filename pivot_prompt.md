We are pivoting our aon-hr-agent and will copy it into a new project.
*   **New Customer Name**: UHG
*   **New Use Case / Persona**: The Chief Financial Officer
*   **Target Service Name**: uhg-finance-agent
*   **Additional Context**: 
the CFO is frustrated because he currently relies on the IT organization for reports and requires weeks or multiple days for small data tweaks, but they are looking for the ability to query their data in the United Data Warehouse.

talk to your data essentially. Could you give me a summary top likely 3 MECE queries (12 words or less each) that he would find highest value and realistically use more frequently? each query should come with its underlying dataset(s) used with a short description and format 

ideally this shows how we connect claims data, policy change data, and external trends (e.g., third-party sources/internet trends) to show cross-data insights, though the primary focus remains on showing how their world can be transformed through what can be done with these capabilities

I'm thinking queries and datasets may be good. lmk if you're aligned.
Simplified, high-value queries an M&R CFO would use to bypass IT bottlenecks, alongside the specific datasets needed to fuel them.

highlight Google's ability to pull external context like weather or public internet data and combine it with their internal data.

## 1. Correlate regional claim spikes with viral external health trends.

* Dataset 1 (Claims): JSON/CSV. Contains medical encounters, diagnosis codes, and paid amounts.
* Dataset 2 (External Trends): JSON/CSV. Includes search volume data for symptoms or regional illness outbreaks.

## 2. Predict member churn following specific premium or benefit changes.

* Dataset 1 (Policy): JSON/CSV. Tracks historical plan benefits, co-pays, and premium adjustments.
* Dataset 2 (Enrollment): JSON/CSV. Records member demographics, plan IDs, and disenrollment dates.

## 3. Identify MLR leakage caused by shifting provider billing behaviors.

* Dataset 1 (Claims): JSON/CSV. Provides raw encounter data and procedure-level billing codes.
* Dataset 2 (Provider Master): JSON/CSV. Links individual providers to tax IDs, specialties, and locations.

---

**Role**: Principal Architect and Lead AI Coder
**Objective**: Pivot the current codebase from the **Aon HR Agent** to a new customized instance for the **New Use Case / Persona** defined above.

### **1. Context & Architecture Reference**
*   Read the `README.md` in `/Users/rtejada/Workspace/aon-hr-agent` to understand the current implementation.
*   **Core Paradigm**: We are using a custom executor (`AdkAgentToA2AExecutor` in `agent_executor.py`) that intercepts Python tool responses directly to eliminate LLM hallucination. Tools return structured A2UI lists or `CustomView` dictionaries. The agent simply outputs the returned JSON preceded by the delimiter `---a2ui_JSON---`.
*   **Templates**: Custom views are rendered via iframes using templates in `backend/templates/` (e.g., `workday_portal.html`).
*   **Logos**: Logos are pulled via an absolute authenticated GCS URL or proxied via the agent's `/logos` endpoint to avoid CORS issues in Gemini Enterprise.

### **2. Deployment & Execution Notes (Missing in README)**
*   To deploy, I usually `cd /backend/` then `./deploy.sh` (The script handles setting the `AGENT_URL` environment variable automatically after deployment).
*   Local testing is actively running via `adk web ./ --port 8081` and `adk-web-react` on port `5173`.
*   We pivoted monitoring from Reasoning Engines to simple **Cloud Logging**. Use `[AGENT_PLATFORM]` as the bracketed tag in `stdout` print statements to flag actions for the UI.

### **3. Exhaustive Pivot Checklist**
You must perform a comprehensive audit and refactor to remove all HR leftovers and establish the new persona defined in the header:

*   **Branding & References**: Search for and replace all instances of *"HR Agent"*, *"Workday"*, *"John Doe"*, *"Bob"*, and *"Commuter Benefit"*.
*   **Data Migration**: 
    *   Analyze `backend/data/` and remove or replace `employee_profile.json`, `performance_reviews.json`, and `benefits_summary.json` adjusting it to the new use case.
    *   **Note**: `sales_data.py` was preserved in the `backend` folder as a starting point for this exact pivot! Review its functions and adapt them to the new deterministic JSON return paradigm.
*   **Templates**: Create a new high-fidelity portal template for the new persona (or adapt `workday_portal.html`) but removing Workday aesthetics if appropriate.
*   **Components**: Ensure you choose the right components to show A2UI's flexibility. Use standard/native components (form, card, image, dropdown selector, etc) and custom templates (map with weather overlays + routes, dashboards with novel graphs embedded, etc.)to show A2UI's flexibility. 
*   **Documentation**: Rewrite the `README.md` completely to outline the new demo flow and queries.
*   **deploy.sh**:  Adjust the script to deploy to a new service name (e.g., "uhg-finance-agent") to avoid overwriting the existing HR service.
*   **Agent Card**: Update `agent_card.json` to replace the HR skills with the new Finance-specific parameters.
*   **Project Hygiene**: Check `.gcloudignore` and `.gitignore` to ensure no local state files (`.adk/` or `media_cache/`) leak into the build image.

Draft your Strategic Plan (`plan.md`) according to our protocol before modifying any code.
