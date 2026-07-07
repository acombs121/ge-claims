# Spec — Gemini Enterprise Insurance Claims Assistant Demo

**Config:** `mode` = full
**Config:** `phase_gate_signoff` = on

## Goal (one sentence)
Showcase how Gemini Enterprise, integrated as an Agentic UI (A2UI) custom agent, empowers claims handlers and adjusters to instantly verify coverage, analyze damage photos multimodally, assess historical risk, and generate repair estimates directly within their chat workspace.

## Audience
- **Insurance Claims Handlers & Adjusters** — Cares about processing claims quickly, checking policy exclusions accurately, assessing fraud risks, and estimating costs. Skeptical of AI hallucinating policy rules or missing key visual damage cues.
- **Decision at stake:** Adoption of Gemini Enterprise as the primary unified workspace for insurance claim operations and triage.

## Demo narrative (the script)
| Beat | Presenter says / does | What appears on screen |
|------|-----------------------|------------------------|
| 1    | **Intake / FNOL Overview**<br>Presenter: "We start after our policyholder, Walter White, has filed a water damage claim for a plumbing leak at his property (123 E. Main St, Columbus, OH), uploading two damage photos. In the backend, the claims handler opens Gemini Enterprise and engages the GECX Claims Assistant Agent to investigate the claim."<br>Action: Types `"check the new water damage claim for Walter White"` or clicks the claim notification. | Conversational response confirming search, followed by a **Policy & Coverage Card** widget showing Walter's active policy status, policy number, $1,000 deductible, $50,000 limit, and flagging that standard water damage is covered but sewer backup is excluded. |
| 2 ★  | **Multimodal Damage Assessment (★ Money Moment)**<br>Presenter: "Next, the adjuster needs to verify the physical damage against the written report. Rather than using external image viewing software, the adjuster prompts the agent to analyze the uploaded damage photos."<br>Action: Types `"analyze the damage photos for this claim"` or clicks "Analyze Photos" button. | A **Multimodal Assessment Panel** displaying the uploaded photos of the flooded bathroom and laundry room side-by-side. The panel shows structured AI insights: estimated water depth (~1.5 inches), affected flooring material (hardwood/laminate), likely source (clean water pipe burst), and an automated consistency check confirming "No signs of sewer backup; consistent with pipe burst." |
| 3    | **Risk & Historical Claims Analytics**<br>Presenter: "To prevent fraud and ensure compliance, we query the customer's historical claims and assess overall risk profile."<br>Action: Types `"run fraud and claim history check"` or clicks "Assess Risk". | A **Risk Analytics Card** with a clean visual gauge showing a Low Risk rating (Score: 12/100). It highlights Walter White's history: 0 prior claims in 5 years, policy tenure of 4 years, and a green "Fraud Check: Cleared" stamp. |
| 4    | **Itemized Estimation & Contractor Dispatch**<br>Presenter: "Finally, we draft an itemized repair estimate based on the average costs for water extraction and flooring repairs in Columbus, OH, and look up approved local contractors to schedule immediate dispatch."<br>Action: Types `"draft repair estimate and find local contractors"` or clicks "Estimate & Dispatch". | An **Estimation & Contractor Map** viewport showing:<br>1. An itemized **Draft Estimate Table** (Water extraction: $500, Floor drying & remediation: $800, Baseboard replacement: $300, Less Deductible: -$1,000, Proposed Net Payout: $600).<br>2. An **Interactive Map** centered around 123 E. Main St, Columbus, OH, showing two approved repair contractors marked with pulsing pins and their real-time availability. |
| 5    | **Settlement Letter & Booking**<br>Presenter: "Once approved, the agent automatically drafts the settlement letter according to regional insurance regulations and generates an appointment booking card for the customer."<br>Action: Types `"approve and finalize claim"` or clicks "Finalize". | A **Settlement Finalization Card** containing the drafted letter text (complying with Ohio insurance guidelines) and a booking scheduler widget showing the contractor's open slots. |

- **Money moment (★):** Multimodal damage reasoning displaying the actual photos side-by-side with localized flood depth and consistency analysis.
- **Who drives:** Presenter click-through / chat interaction.
- **Slot length:** 5-7 minutes.

## Demo context
- **Display:** Screen-shared or laptop (1920×1080 resolution).
- **Network:** Available (Cloud Run live deployment).

## Data story
- **Domain & entities:** Policyholders, Claims, Policies, Visual Evidence (Photos), Estimations, Contractors.
- **Magnitudes & ranges:**
  - Water Damage Limits: $50,000
  - Deductible: $1,000
  - Estimated Damage Cost: $1,600 (net payout: $600)
  - Location: 123 E. Main St. Columbus, OH 43215
- **Narrative beats in the data:**
  - Customer name: Walter White.
  - Policy status: Active.
  - Claims history: 0 claims (low risk, high loyalty).
  - Images: `laundry_room_flooding.jpg`, `bathroom_water_damage.jpg`.
- **Seeding:** Deterministic local JSON files to simulate CRM and Policy Management lookup.

## Non-goals
- Real payment processing or live banking integration.
- Live integration with real insurance CRM (all data is mocked/seeded via JSON files).
- Mobile responsive layout (the presentation is desktop/laptop-focused for claims handlers).

## Constraints
- **Stack / platform:** Python/FastAPI/Uvicorn, Google GenAI SDK (Vertex AI), `a2a-sdk` (A2UI), Google Maps API.
- **Deadline:** Upcoming executive review.
- **Systems to appear integrated with:** GECX Policy Management, GECX Customer CRM, and Columbus Contractor Dispatch Registry.
- **Brand guidelines:** GECX Insurance brand colors (Deep Slate/Ocean Blue, Clean accents).

## References
- Uploaded PDF describing GECX insurance triage, coverage verification, damage assessment, estimation, and settlement.
- A2UI Seed Agent repository: [a2ui-seed-agent](file:///Users/alexcombs/Projects/ge-insurance-claims)

## Taste north-star
- **Linear:** restrained UI, clean borders, high visual contrast.
- **Stripe:** clean tables, clear status badge overlays (e.g. "Fraud Check: Cleared").

## Design spec
- Clean, professional backend dashboard. Dark theme or modern light theme (selectable). Uses Tailwind-like layout styling or pure CSS.

## Resolved Questions
1. **Existing User-Facing App:** The app will use a pre-seeded static state/file to load Walter White's claim and image references.
2. **Interactive Elements:** The GECX agent will output A2UI widgets containing buttons (e.g. "Analyze Photos", "Assess Risk", "Estimate & Dispatch") to trigger actions.
3. **Google Maps API Key:** A live Google Maps API key will be retrieved from the environment / secrets to power a real Google Map visualization for local contractors.

