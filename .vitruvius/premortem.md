# Pre-mortem — Gemini Enterprise Insurance Claims Assistant Demo

Critic pass assessing risks to the demo-day experience.

## Pass 1
| # | Axis | Risk | Severity | Mitigation → plan change |
|---|------|------|----------|--------------------------|
| 1 | On-stage failure | Google Maps API key is missing or invalid in the Cloud Run deployment environment, leading to a blank map frame or Javascript error. | Critical | Implement an automated fallback in the map rendering logic: if the API key is not present or maps fail to load, automatically render a clean Leaflet/OpenStreetMap widget with Columbus markers. |
| 2 | Data credibility | Contractor locations or names default to Boston (from the seed agent) instead of Columbus, OH, showing a geographic mismatch with 123 E. Main St. | High | Seed the local contractor dataset with real Columbus, OH business names and coordinates (e.g. within 3 miles of 43215). |
| 3 | Narrative | Multimodal photo analysis fails on Vertex AI call or returns generic, generic summaries that don't match the specific details of the uploaded laundry/bathroom photos. | High | Write a precise system prompt for the multimodal Gemini tool, directing it to output estimated water depth, flooring material (wood/tile), and leak source from the image bytes. Run tests to verify the outputs are specific and realistic. |
| 4 | Technical | LLM generates malformed JSON or trailing commas in the A2UI payload, causing the client-side parser to crash and show raw code. | High | Programmatically wrap all tool responses in Pydantic models or validate them using `json.loads` in the agent executor before sending to the client. |
| 5 | Off-script | Presenter clicks buttons in a non-sequential order, causing the agent to lose context and fail to answer. | Medium | Add a state tracker in the backend that maps the active claim ID and session state so the agent can respond coherently even if the presenter skips a step or double-clicks. |

## Pass 2
- No new material risks identified. The mitigations in Pass 1 cover the major failure modes.

## Stop reason
- [x] Converged (a pass found no new material risk)
- [ ] Hit cap (~3 passes)
