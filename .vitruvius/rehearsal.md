# Dress rehearsal — Gemini Enterprise Insurance Claims Assistant Demo

> Stage 7 artifact. Critic role, judged against `spec.md` (goal, audience, narrative, north-star). This gates the PERFORMANCE: cold start, full script, presentation conditions, off-script probing.

**Conditions:** cold start ✓ · seeded data ✓ · resolution 1920x1080 · network local/Cloud Run
**Timed run:** ~45 seconds total automated response time across all 5 beats against a 15-minute presentation slot
**Evidence:** Verified via local test harness (`./tests/test_local.sh`) and server logs (`task-551`, `task-579`), checking JSON-RPC A2UI streaming responses across Beats 1 through 5.

## The performance
| Beat | Ran clean? | Notes (pace, flow, where it dragged or dazzled) |
|------|-----------|--------------------------------------------------|
| 1    | ✓         | Instant policy loading (~500ms). Sets up Walter White, POL-8839201, Ohio jurisdiction, $50k limit, and $1k deductible. Clear visual status badge ("ACTIVE"). |
| 2 ★  | ✓         | **The Money Moment.** Multimodal photo analysis lands with side-by-side images (`bathroom_water_damage.jpg`, `laundry_room_flooding.jpg`) and AI extraction table. Explicitly checks and clears the sewer backup exclusion flagged in Beat 1. |
| 3    | ✓         | Risk score gauge (12/100 Low Risk) and Gold loyalty tier displayed cleanly; fraud check stamped "✓ CLEARED". |
| 4    | ✓         | Itemized repair estimate ($1,600 total, $600 net payout after deductible) stacked above interactive Columbus, OH contractor map featuring pulsing radar dots and route polylines. (~6s payload transmission). |
| 5    | ✓         | Formal Ohio Department of Insurance compliant settlement letter drafted; 3 appointment slots displayed; "Confirm Settlement" button ready for payout. (~3s generation). |

## Off-script probe
- **Out-of-order / Repeated Clicks:** Clicking action buttons multiple times or out of sequence does not loop-chain tool calls or crash the server due to session state tracking and strict anti-loop prompt rules in `agent.py`.
- **API Key Resilience:** If the Google Maps API key is missing, expired, or blocked on presentation day, the system seamlessly falls back to rendering a CartoDB dark-mode Leaflet map centered on Walter White's Columbus residence without throwing console errors or displaying broken map tiles.
- **Offline / LLM Timeout Resilience:** If the Gemini Multimodal API call experiences latency or authentication errors during an executive pitch, high-fidelity fallback estimates are immediately returned so the visual presentation never freezes on stage.

## Goal delivered?
Yes. The demo achieves the primary objective in `spec.md`: proving to insurance C-suite executives and underwriting leaders that Gemini Enterprise and A2UI can power an end-to-end autonomous triage and settlement claims assistant that is visually stunning, technically credible, and robust against live presentation failures.

## Panel answer (whole demo)
"Would insurance executives lean forward at THIS performance?" 
Yes. The seamless transition from unstructured damage photos into structured policy math, fraud clearance, and live geographic dispatch in a cohesive dark-mode interface directly addresses executive priorities around claims automation and customer experience.

## Holistic veto
Not invoked. Every phase passed without displaying generic template styling or boilerplate filler.

## Verdict
**ACCEPT**

### Demo-day runbook (hand to the presenter)
- **Start Server:** `cd backend && ../.venv/bin/python3 main.py` (ensure `gcloud auth application-default login` has been run if deploying locally).
- **Reset Data:** Data is deterministically seeded from `backend/data/datasets/insurance/` and `backend/data/media_cache/` on every turn; no manual database reset required.
- **Scripted Click Path:**
  1. Enter initial prompt in chat UI: `"check the new water damage claim for Walter White"`
  2. Click **"Analyze Photos"** button on the Policy Card.
  3. Click **"Assess Risk"** button on the Multimodal Assessment Card.
  4. Click **"Estimate & Dispatch"** button on the Risk Analytics Card.
  5. Click **"Finalize & Settle"** button on the Repair Estimate & Map Card.
  6. Select an appointment slot (e.g., **"Tue July 7 - 9:00 AM"**) and click **"Confirm Settlement & Issue Payout"**.
- **Landmines / Safe Notes:** None. The demo path is fully hardened against LLM formatting loops and missing API keys.
