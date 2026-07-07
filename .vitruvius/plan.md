# Plan — Gemini Enterprise Insurance Claims Assistant Demo

**Deadline check:** 6 phases total. Expected build time is ~3-4 hours, well within meeting schedule.

## Phase 1 — Seeding & Policy Triage (Beats 1)
- **Scope:**
  - Create the `insurance` dataset folder and mock CRM/Policy JSON files containing Walter White's data ($50k limits, $1k deductible, Ohio-registered policy).
  - Copy the uploaded laundry room and bathroom damage photos into the project's static assets directory.
  - Implement a Policy Triage tool in the backend that resolves the claim context, reads Walter's mock data, and flags exclusions.
  - Expose the first action buttons (e.g. "Analyze Photos") on the Policy Card.
- **Deliverable:** The GECX Claims Assistant agent can respond to `"check the new water damage claim for Walter White"` by displaying a high-fidelity Policy Card with policy details, status, exclusions, and action buttons.
- **Dependencies:** None.

## Phase 2 — Multimodal Damage Assessment (Beat 2 — ★ Money Moment)
- **Scope:**
  - Build the image analysis function using the Google GenAI SDK. Set up a multimodal prompt that analyzes the laundry and bathroom flood images.
  - Extract: estimated water depth (~1.5 inches), flooring material (wood/laminate/tile), source (clean pipe burst vs backup), and consistency check text.
  - Create/register the `Analyze Photos` tool.
  - Return a CustomView payload displaying a side-by-side assessment component containing the images and the AI-extracted table.
  - Include an "Assess Risk" action button on the assessment widget.
- **Deliverable:** Clicking "Analyze Photos" or prompting `"analyze damage photos"` renders the side-by-side Multimodal Damage Assessment panel.
- **Dependencies:** Phase 1 (mock data & images).

## Phase 3 — Risk Analytics Gauge (Beat 3)
- **Scope:**
  - Create the `Assess Risk` backend tool. It queries historical claim metrics (0 claims in 5 years, low risk score: 12/100, cleared fraud checks).
  - Design a beautiful visual Gauge/Analytics card widget using A2UI dashboard components.
  - Expose the "Estimate & Dispatch" action button on the risk widget.
- **Deliverable:** Clicking "Assess Risk" or prompting `"run risk analysis"` returns a visual Low-Risk gauge overlay card with a green cleared stamp.
- **Dependencies:** Phase 2.

## Phase 4 — Repair Estimation & Live Google Map (Beat 4)
- **Scope:**
  - Create the `Estimate & Dispatch` backend tool.
  - Implement a cost calculator returning itemized water damage repair costs ($1,600 total, $600 net payout after deductible).
  - Implement a location search for Columbus, OH approved contractors.
  - Update the `google_map.html` template to dynamically center on Columbus, OH (123 E. Main St.) and overlay pulsing pins for two contractors with their real-time availability.
  - Deliver a CustomView returning the itemized estimate table and the live Google Map.
  - Expose the "Finalize" action button.
- **Deliverable:** Clicking "Estimate & Dispatch" or prompting `"draft repair estimate"` returns the itemized cost table and live Google Map with contractor pins.
- **Dependencies:** Phase 3.

## Phase 5 — Settlement & Appointment Scheduler (Beat 5)
- **Scope:**
  - Create the finalization tool. It generates the Ohio-compliant settlement letter and returns an interactive scheduling appointment card.
- **Deliverable:** Clicking "Finalize" returns the final Settlement Letter Card and booking widget.
- **Dependencies:** Phase 4.

## Phase 6 — Rehearsal & Polish
- **Scope:**
  - Perform a complete dress rehearsal walking through the presenter path.
  - Verify styling aesthetics, loading times, and error handling for missing Google Maps API keys (ensure smooth fallback).
- **Deliverable:** Production-grade flagship demo ready for executive presentation.

## Spikes
- **Spike A — Dynamic Google Maps A2UI integration:** Verify that the `a2ui-seed-agent` iframe orchestration resolves the environment key and renders the route correctly on a different address (Columbus, OH) instead of the hardcoded Boston address. If it fails, fallback to rendering a static custom map frame.

## Revisions from pre-mortem
- **2026-07-06/Pass 1**: Added automated Leaflet map fallback to Phase 4 to handle missing/invalid Google Maps API keys on stage.
- **2026-07-06/Pass 1**: Added a Pydantic validation step to Phase 2 to prevent any LLM malformed JSON formatting from reaching the A2UI client.
- **2026-07-06/Pass 1**: Seeded realistic Columbus, OH contractor coordinates and names into Phase 1 datasets to ensure geographic consistency.
- **2026-07-06/Pass 1**: Added backend session/state tracking in Phase 1 to allow off-script/non-sequential button clicks without losing active claim context.

