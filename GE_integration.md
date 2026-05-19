# Gemini Enterprise (GE) A2A Integration Guide

This guide outlines the macro-level configuration steps to register and integrate this rebranded A2UI Seed Agent template (`a2ui_seed_agent`) dynamically into the Gemini Enterprise workspace.

---

## 1. Cloud Run Public Access Configuration

Ensure the deployed Cloud Run instance is publicly accessible to allow inbound A2A calls from the Gemini Enterprise network:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **Cloud Run** and select the `a2ui-seed-agent` service.
3. Click on the **Security** tab.
4. Under **Authentication**, check **Allow unauthenticated invocations** (Allow public access).
5. *Alternative CLI Method:* If the IAM binding fails during deployment, execute this command in your authenticated terminal to grant public ingress permissions:
   ```bash
   gcloud run services add-iam-policy-binding a2ui-seed-agent \
       --region=us-central1 \
       --member="allUsers" \
       --role="roles/run.invoker"
   ```

---

## 2. Agent Card JSON Preparation

1. Copy the active, public Cloud Run Service URL from your terminal deploy output or Cloud Console.
2. Open the [agent_card.json](file:///Users/rtejada/Workspace/a2ui-seed-agent/agent_card.json) file in the repository root.
3. Paste your Cloud Run URL into the `"url"` field on line 4:
   ```json
   "url": "https://a2ui-seed-agent-g2u64mk5wq-uc.a.run.app"
   ```
4. Save the changes and commit/push to your remote repository if desired.

---

## 3. Gemini Enterprise Console Registration

1. Navigate to your Gemini Enterprise developer application console.
2. Click on the **Agents** tab in the sidebar menu.
3. Click **Add Agent** -> select **Custom Agent via A2A** -> click **Add**.
4. Paste the complete contents of your prepared `agent_card.json` file into the JSON text field.
5. Select **SKIP Authorization** (no token verification required for A2UI showcase ingress).
6. Save and complete the registration.

---

## 4. Workspace Activation & Testing

1. Open your standard Gemini Enterprise chat workspace.
2. Go to the **Agents** panel in the visual interface.
3. Locate the newly registered **A2UI Seed Agent** under custom agents and click the **Pin** icon to anchor it.
4. Start a conversation by typing one of the pre-wired showcase example prompts:
   * `"let's see standard widgets overview"` (Dynamic widgets dashboard tabs, modals, and sliders)
   * `"show map visualization"` (pronounced clouds/wind, dynamic OSM traffic, and glowing Google Places POI circles)
   * `"show universal dashboard"` (KPI analytics counter cards, Allocation trend Vega-Lite graphs, and interactive risk simulator controls)
   * `"give me an audio summary"` (WAV seekable voice summaries)
