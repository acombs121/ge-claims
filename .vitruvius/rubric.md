# Rubrics — Gemini Enterprise Insurance Claims Assistant Demo

This document defines the acceptance rubrics for each build phase.

## Phase 1 — Seeding & Policy Triage (Beats 1)

### Must-pass gates
- [ ] G1. Presenter can type `"check the new water damage claim for Walter White"` and receive the Policy & Coverage Card.
- [ ] G2. Zero placeholder content or "Lorem Ipsum" visible in the Policy Card.
- [ ] G3. No console errors on this beat.
- [ ] G4. Coordinates and details for Walter White are Ohio-based and consistent.

### Quality dimensions
| Dim | Dimension              | Weight | Floor | Evidence to gather |
|-----|------------------------|--------|-------|--------------------|
| Q1  | Wow / first impression | 0.15   | 3     | Screenshot of Policy & Coverage Card |
| Q2  | Narrative flow         | 0.25   | 3     | Presenter click-through test of first beat |
| Q3  | Data credibility       | 0.35   | 4     | Audit of policy numbers, limits ($50k), and deductibles ($1k) |
| Q4  | Polish & taste         | 0.15   | 3     | Card typography and status layout sweep |
| Q5  | Perceived performance  | 0.10   | 3     | Response time of tool execution (≤ 1.5s) |

### Panel question
"Would the adjuster find the Policy Card instantly informative and trust the deduplication of rules (e.g. sewer backup exclusion clear)? Where does it feel like a generic chatbot?"

---

## Phase 2 — Multimodal Damage Assessment (Beat 2 — ★ Money Moment)

### Must-pass gates
- [ ] G1. Clicking "Analyze Photos" or prompting `"analyze the damage photos"` displays the side-by-side Multimodal Assessment Panel.
- [ ] G2. Actual uploaded bathroom and laundry room photos are displayed.
- [ ] G3. No malformed JSON or raw AST code block is outputted to the UI.
- [ ] G4. Consistent check clearly states: "No signs of sewer backup; consistent with pipe burst."

### Quality dimensions
| Dim | Dimension              | Weight | Floor | Evidence to gather |
|-----|------------------------|--------|-------|--------------------|
| Q1  | Wow / first impression | 0.40   | 4     | Visual wow of side-by-side images + extracted details |
| Q2  | Narrative flow         | 0.15   | 3     | Time taken to transition from Policy Card to Photos Panel |
| Q3  | Data credibility       | 0.25   | 4     | AI-extracted water depth (~1.5") and flooring materials accuracy |
| Q4  | Polish & taste         | 0.10   | 3     | Table alignment and image borders quality |
| Q5  | Perceived performance  | 0.10   | 2     | Vertex AI multimodal analysis response latency (≤ 4.5s) |

### Panel question
"Does the side-by-side comparison feel like a premium, enterprise-grade automated review? Does the AI's visual reasoning feel genuine or fake?"

---

## Phase 3 — Risk Analytics Gauge (Beat 3)

### Must-pass gates
- [ ] G1. Clicking "Assess Risk" or prompting `"run risk analysis"` returns the Risk Analytics Card.
- [ ] G2. Risk Score is clearly visible as a Low Risk gauge (Score: 12/100).
- [ ] G3. Green "Fraud Check: Cleared" status badge is correctly rendered.

### Quality dimensions
| Dim | Dimension              | Weight | Floor | Evidence to gather |
|-----|------------------------|--------|-------|--------------------|
| Q1  | Wow / first impression | 0.20   | 3     | KPI boxes and Gauge visual alignment |
| Q2  | Narrative flow         | 0.20   | 3     | Smooth transition and next action button placement |
| Q3  | Data credibility       | 0.25   | 3     | Plausibility of historical claims (0 in 5 years) and tenure (4 years) |
| Q4  | Polish & taste         | 0.25   | 4     | Gauge colors, status badge typography |
| Q5  | Perceived performance  | 0.10   | 3     | Risk tool execution latency (≤ 1.0s) |

---

## Phase 4 — Repair Estimation & Live Google Map (Beat 4)

### Must-pass gates
- [ ] G1. Clicking "Estimate & Dispatch" or prompting `"draft repair estimate"` returns the Estimation & Map View.
- [ ] G2. Live Google Map successfully renders, centered on 123 E. Main St, Columbus, OH.
- [ ] G3. Two contractor marker pins are visible with info overlays on hover/click.
- [ ] G4. Itemized costs in the table sum up correctly ($1,600 total, $600 net payout).

### Quality dimensions
| Dim | Dimension              | Weight | Floor | Evidence to gather |
|-----|------------------------|--------|-------|--------------------|
| Q1  | Wow / first impression | 0.35   | 4     | Wow factor of live Google Map with custom pulsing/availability pins |
| Q2  | Narrative flow         | 0.15   | 3     | Layout integration of estimate table alongside the map frame |
| Q3  | Data credibility       | 0.20   | 3     | Plausible local Columbus contractor names and Ohio phone formats |
| Q4  | Polish & taste         | 0.15   | 3     | Dark style map aesthetics matching the GECX slate template |
| Q5  | Perceived performance  | 0.15   | 3     | Google Maps API connection and load latency (≤ 2.0s) |

---

## Phase 5 — Settlement & Appointment Scheduler (Beat 5)

### Must-pass gates
- [ ] G1. Clicking "Finalize" or prompting `"finalize claim"` returns the Settlement Finalization Card.
- [ ] G2. Ohio-compliant draft text contains correct policy/deductible numbers.
- [ ] G3. Appointment booking slots are interactive.

### Quality dimensions
| Dim | Dimension              | Weight | Floor | Evidence to gather |
|-----|------------------------|--------|-------|--------------------|
| Q1  | Wow / first impression | 0.15   | 3     | Layout of letter draft and booking component |
| Q2  | Narrative flow         | 0.30   | 4     | Complete walkthrough from claim intake to finalization |
| Q3  | Data credibility       | 0.30   | 4     | Legal/compliance tone of draft letter |
| Q4  | Polish & taste         | 0.15   | 3     | Action button states (e.g. booked/sent states) |
| Q5  | Perceived performance  | 0.10   | 3     | Response latency (≤ 1.0s) |

---

## Pass condition
PASS iff: all gates pass AND all prior phases' gates + beats still pass (demo-path regression) AND weighted score ≥ 3.5 AND no dimension below floor AND holistic veto not invoked.
