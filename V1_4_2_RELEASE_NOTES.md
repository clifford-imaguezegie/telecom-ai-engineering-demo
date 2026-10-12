# TREAD AI V1.4.2 — Scenario Consistency and Replay Presentation Reliability

## Scope

Focused response to the independent 12 October 2026 V1.4.1 live browser review. No changes to original saved agent investigations, ML inference outputs, telemetry, evaluation values or RAG evidence.

### F01 — Scenario identity mismatch (High)

The selected scenario is now persisted independently of individual Streamlit widget keys. The sidebar selector is displayed consistently on every page, and the Scenario Library selector synchronises with the same authoritative scenario identifier through change callbacks. Widget disposal when navigating cannot replace the selected case. The active case is resolved only from that persistent value before loading any chart, RCA or evidence.

Regression tests simulate Scenario Library → Engineering Evidence → RCA → Scenario Library navigation for the healthy control, radio congestion and CU processing cases, including disposal of the Library widget's state.

### F02 — Complete-route footer clipping (Medium)

The full recorded route in Agentic Replay and Guided Operations Demo now uses Streamlit's auto-sizing `st.html` presentation rather than a fixed 405px iframe. The route's colour and font styles are scoped to its component. Responsive CSS permits 1–4 columns as space permits. The displayed stages and labels still follow actual sequential recorded execution.

Standalone Chromium layout checks of the full ten-stage route at widths 270, 320, 390, 480, 540, 648 and 860px found no clipped footer or horizontal overflow. Full application-browser tests at 1366×768 and 1440×900 remain pending.

### F03 — Empty CU alternatives heading (Low)

The executive RCA summary now displays “Weakened competing explanations” only when its corresponding `contradictory_evidence` list is populated. The full recorded Supervisor diagnostic output is unchanged and remains available below.

### Small terminology refinement

The workflow's position counter now says “Stage N of N”, because joins and the final report are presentation stages rather than additional AI agents.

## Validation

- Automated Python suite: 190 tests passed.
- Rendered route HTML in Chromium: footer visible and no horizontal overflow at seven viewport widths listed above. This is not the same as testing a live deployed Streamlit app.
- All 136 packaged data files match V1.4.1 byte-for-byte (manifest, nine recorded cases, 126 evidence records).
- No live model, telemetry, vector-search or LLM calls performed.

## Deployment and acceptance

Extract the application directory into the existing local `telecom-ai-engineering-demo` Git checkout, retaining `.git`, then commit and push to `main`. Do not upload the ZIP itself as the Streamlit app.

After Streamlit redeploys, verify in an actual browser:
1. Select Radio Congestion in Scenario Library. Navigate to Engineering Evidence, RCA and back; all visible titles, selector and plotted times must belong to Radio Congestion.
2. Repeat with CU-Domain Processing Pressure and Healthy Network Control.
3. Expand the full 10-stage congestion route; final stage, footer and panel boundary must be visible at 1366×768, 1440×900 and a supported mobile width.
4. Confirm the CU RCA summary has no empty headings, and full original Supervisor details remain available.
5. Run both executive and full engineering autoplay with route expanders open and closed; verify no jumps, hidden active node or clipped panels.

This release does not establish production readiness, live monitoring, or model accuracy beyond the saved investigations.
