# TREAD AI V1.4.3 — Playback Persistence & Release-Readiness Corrections

**Prepared:** 13 October 2026  
**Baseline:** V1.4.2, independent live assessment score 3.67/5 (provisional)  
**Deployment status:** Package prepared and locally tested; **not deployed** by this release preparation.  
**Scope:** Correct N02 and tighten evidence interpretation without changing any original evidence or recorded run.

## 1. N02 — Timeline position resets following Restart (Medium)

**Independent finding:** In CU-domain Full Engineering, Restart followed by a drag to beats 11, 16 or 15 resulted in the UI returning to beat 1/22, without updating the active-stage evidence. The behaviour was observed with inspectors open and closed. The exact introduction version was unknown.

**Technical diagnosis:** Both guided and standalone players unconditionally assigned their saved index into the slider widget's `st.session_state` entry on every fragment render. That assignment could overwrite incoming slider changes. The correction:

- Registers `on_change` callbacks for both sliders, consuming the changed widget value into the canonical replay index **before** the fragment rerenders.
- Removes unconditional widget-key resets during normal fragment refreshes.
- Synchronises the slider value explicitly only for player-originated movements: Back, Next, Restart, playback completion/restart, or timed autoplay.
- Pauses playback and resets its timer carry on a manual seek; the selected stage and associated evidence are then sourced from the updated replay index.
- Retains scenario/mode-specific widget IDs and existing presentation timing semantics.

**Regression coverage:** Simulated full page/fragment invocations exercise Restart → slider drag → idle rerender → keyboard-equivalent increment → Back/Next, for healthy, radio congestion and CU-processing scenarios in Executive and Full Engineering modes, including incident-only mode. Standalone Agentic Replay seek and autoplay synchronisation are covered. This test mimics Streamlit callback event ordering; it is **not** a substitute for live Streamlit browser verification.

## 2. Narrow-screen workflow frame

The focused workflow uses a fixed-size HTML component. Chromium checks exposed text wrapping and possible bottom clipping in narrow-width agent labels. The mobile presentation now uses **short, readable role aliases** for the focused Previous → Current → Next cards while preserving full names in desktop text, accessibility labels and recorded-route details. Both replay frames remain at their existing **250px** height, avoiding unnecessary blank desktop space. Native full-route expanders remain auto-height and unchanged.

**Component-only Chromium checks** used a representative Streamlit-like page harness, the actual HTML returned by `workflow_svg` and `workflow_overview_html`, and the exact **1366×768**, **1440×900**, **1920×1080**, and **390×844** browser sizes for healthy, radio congestion and CU-processing cases. In all 12 checks: no document-level horizontal overflow, no expanded-route footer clipping, and no focus-frame horizontal or vertical overflow. This is **not a test of the actual hosted Streamlit application** or the autoplay scroll behaviour. The V1.4.2 assessor's exact-viewport acceptance gap remains open until a live-browser run.

## 3. More disciplined RCA interpretation

Added short visitor-facing interpretation notes to the radio congestion and CU-processing RCA **summary**, without editing the recorded Supervisor diagnoses:

- The saved congestion fault-family support of **0.525** is described as modest, uncalibrated model support rather than certainty; actual radio resource / accessibility evidence has higher diagnostic weight, with unavailable DRB failure-cause codes disclosed.
- CU processing-pressure indicators are separated from conclusive resource-exhaustion or specific RRC-cause proof. Missing RRC NoReply/MaxRetrans counters and unknown initiating trigger are stated explicitly.

The original detailed Supervisor outputs, specialist evidence, inference scores, RAG contributions and evaluations remain intact and inspectable.

## 4. Validation and source integrity

- **211 automated Python tests passed**, including the V1.4.2 regression suite and new event-based seek tests.
- **12 component-level viewport checks** in Chromium passed, as qualified above.
- **All 136 data files** (manifest, nine compressed recorded cases, 126 compressed evidence records) preserve the **same bytes** as V1.4.2.
- Existing page navigation, recorded specialists, timing evidence, RAG descriptions and evaluation metrics are not changed.
- No new LLM calls, ML inference, telemetry queries, LangGraph runs, paid APIs or live network connections are introduced.

**Environment limitation:** This build environment could not install Streamlit due to unavailable package-network access, so a hosted end-to-end interaction acceptance check could not be executed here. Local tests were executed against a Streamlit-compatible test stub plus Chromium HTML components. The independent live browser reviewer must verify the released application.

## 5. Deployment instructions

From your existing Windows Git checkout `C:\Users\Hp\projects\telecom-ai-engineering-demo`, extract the release ZIP **into a separate temporary directory** and copy the release application contents into the repository root, retaining `.git`. Then verify source import and run your available local tests if installed:

```powershell
python -c "from storyboard import workflow_svg, workflow_overview_html; print('IMPORT PASS')"
git status
git add app.py README.md V1_4_3_RELEASE_NOTES.md tests
# Review staged changes, then commit and push.
git diff --cached --stat
git commit -m "Fix replay seek persistence V1.4.3"
git push origin main
```

This correction changes `app.py`, `README.md`, test code and release notes. **Do not re-upload the evidence/data directory or repackage original traces.** A complete application ZIP is provided for convenient installation; copying the full package is safe, but it is not necessary to alter existing recorded data.

**Streamlit deployment note:** In the prior V1.4.2 deployment the GitHub files were correct while a running Streamlit process raised an import error. A full **Reboot app** restored it. If the newly updated app exhibits a similar startup error after a push, use Manage app → Reboot app; do not create dummy Git commits or remove functions.

## 6. Independent release acceptance — required after deployment

**N02 priority (must pass):**

1. Open Guided Operations Demo → CU-domain Processing Pressure → Full Engineering → Incident only.
2. Complete or pause the journey; select **Restart**. Confirm stage **1/22** and 00:00 presentation timer.
3. Drag the playback slider to stages 11, 16 and 15 in separate repetitions. Confirm selected stage *persists*, the highlighted Previous / Current / Next agents match the recorded route, and the visible evidence matches the beat.
4. Repeat with evidence and drill-down panels expanded, then collapsed. Use arrow keys or Home/End where browser support permits.
5. Repeat a representative scrub after Restart in Executive mode, Healthy → Congestion Full Engineering, and the standalone Agentic Replay.
6. Confirm Pause, Play, Resume, Back, Next, Restart, speed change, timers, provenance and RCA remain functional.

**Viewport acceptance (must be actual app):** Verify **1366×768, 1440×900, 1920×1080 and 390×844** wherever the browser supports exact emulation. Report unsupported dimensions as unverified, not passed. Check stage/card visibility during autoplay and while opening the full route or evidence expanders. Test keyboard focus on scrubber.

**Readiness decision:** Until the live N02 and exact-viewport acceptance gates pass, use for **facilitated demonstrations** with Next/Back as alternatives; do not claim formal self-guided acceptance or production readiness. No revised numerical assessment score is assigned by this implementation release.
