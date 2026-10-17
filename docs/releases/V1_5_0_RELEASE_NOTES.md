# TREAD AI V1.5.0 — Unified Investigation Cockpit

**Prepared:** 13 October 2026  
**Baseline:** V1.4.3, independently scored 3.89/5 (provisional; responsive acceptance incomplete).  
**Release type:** Deliberate Guided Operations Demo layout improvement (N04), with one low-severity evaluation-copy correction (N03).  
**Deployment:** Not deployed by this preparation. User must publish and independently verify the hosted app.

## 1. Reason for this release

The user observed during an actual replay that relevant information was spread across three vertical screen locations: playback controls at the top, current agent/workflow in the middle, and detailed evidence below. An unattended player could advance while a visitor scrolled to find current evidence. The previous browser assessment did not adequately cover this **single-screen demonstration** requirement.

### Target design at 1366 × 768

Visitors should normally see **(1) replay mode and incident selection, (2) Play/Pause/Back/Next/Restart and seek, (3) replay progress and original-versus-viewing timing, (4) Previous → In Focus → Next agent view, and (5) short source-grounded incoming/action/output summaries simultaneously**, without scrolling. The long original records need not fit within the same 768 pixels, but must remain accessible on demand and must not reset the replay.

## 2. Implemented changes

- Removed the large hero banner **only from the Guided Operations Demo**. The full platform identity remains on other pages and in the persistent sidebar.
- Positioned the two replay mode selectors side by side on laptop/desktop, preserving the existing mode names and state semantics.
- Replaced the large live-status banner and four vertically bulky Streamlit metric blocks with a compact dark status strip displaying scenario ID, case name, recorded status, viewing timer, SP01 time, total original time and recorded timestamp offset.
- Retained the native Streamlit player buttons and timeline callback (`_seek_from_widget`) rather than rebuilding a new playback controller.
- Kept the accessible **Previous → In Focus → Next** graph at 250px height and placed **incoming evidence, agent action/tool and recorded output** in a synchronized neighbouring panel. Summaries use the existing stored beat fields; they do not invent explanations or leak future tool results.
- Moved the complete recorded route beneath the main cockpit, followed by original current-stage messages, conditional SP01 ML/telemetry cards, engineer drill-down and source provenance. These expand on demand, do not participate in playback state, and preserve the historical evidence transparency.
- Kept mobile stacking for legibility rather than trying to force three columns across 390px. On mobile the detailed evidence can require vertical scrolling; the no-scroll goal applies to the baseline **1366×768 laptop** experience.
- Marked the cockpit with a visible **V1.5.0** version indicator.
- Corrected prior N03 evaluation copy: the explanatory text now uses the selected trace's stored exact-match rate (100.0% in congestion A, 75.0% in CU Processing), rather than using a generic unlabeled 75% sentence. Original score data is unchanged.

## 3. Evidence and regression integrity

- **219 Python tests passed** (211 prior tests plus eight new cockpit/HTML/escape/state/evaluation-copy contracts).
- All 136 original data records/files remain byte-identical to V1.4.3: `data/manifest.json`, nine `data/cases/*.json.gz`, and 126 `data/evidence/**/*.json.gz`.
- Four required guided journeys, original timed stages, Executive and Engineering modes, all eight pages, specialist routing, RAG/RCA data, and standalone replay are not modified at the source-data level.
- No LLM, LangSmith, telemetry, RAG, cloud API or live network call is triggered by the demo.

### Component-only browser layout QA — *not hosted-app certification*

A Chromium HTML harness used **the actual `workflow_svg` HTML and the new cockpit HTML helpers**, with representative Streamlit-like toolbar/sidebar styles. The results at 1366×768, 1440×900 and 1920×1080 show the focus workflow, agent evidence and controls simultaneously within the viewport. No horizontal overflow or clipped iframe content was detected. A 390×844 check showed no horizontal overflow; the stacked evidence extends below the fold as expected.

**Important limitation:** Streamlit was unavailable in this environment and package-network access was disabled; the actual hosted app, genuine Streamlit widget dimensions, browser autoplay, mobile tap controls and exact viewport acceptance **have not** been verified by this package. Source-code simulation and component measurements do not replace hosted browser tests. Keep the previously identified D02/responsive sign-off conditions open until live verification.

## 4. Installation (Windows PowerShell)

Extract the ZIP separately from your working Git repository, then copy **only** changed files; do not overwrite the 136 recorded data files unnecessarily:

```powershell
$zip = "$env:USERPROFILE\Downloads\TREAD_AI_Demo_V1_5_0_Unified_Investigation_Cockpit.zip"
$folder = "$env:TEMP\tread-v150"
Expand-Archive -Path $zip -DestinationPath $folder -Force
$src = "$folder\Telecom_AI_Replay_V1"
Copy-Item "$src\app.py" . -Force
Copy-Item "$src\README.md" . -Force
Copy-Item "$src\V1_5_0_RELEASE_NOTES.md" . -Force
Copy-Item "$src\tests\test_v150_cockpit.py" .\tests\ -Force
python -c "from storyboard import workflow_svg, workflow_overview_html; print('IMPORT PASS')"
git status
git add app.py README.md V1_5_0_RELEASE_NOTES.md tests/test_v150_cockpit.py
git diff --cached --stat
git commit -m "Add unified replay cockpit V1.5.0"
git push origin main
```

If Streamlit serves inconsistent modules after the GitHub deployment, use **Manage app → Reboot app** before changing source code. For a proper test, visit the live URL after the new commit has deployed, open in an incognito tab, and repeat the checks below.

## 5. Mandatory post-deployment acceptance

1. **1366×768 (highest priority):** Select CU Processing (incident only) and Congestion A (Healthy → Incident), test in both Executive and Full Engineering modes. On the actual Streamlit page, check that buttons, seek control, current case/status, agent workflow, current action and recorded output stay visible together without manual scrolling during normal playback. Avoid changing browser zoom to manufacture a pass; record zoom/device pixel scale.
2. **Other exact viewports:** Independently test 1440×900, 1920×1080, and 390×844. Mobile may scroll to deeper details, but no primary-control horizontal overflow or clipped active card is permitted. Report unsupported dimensions **UNVERIFIED**.
3. **Playback state:** Repeat the original N02 sequence: CU Full Engineering → Pause/Complete → Restart → drag seek; repeat with expanders open/closed; check stage, agent, evidence and timeline alignment after rerender. Test Play/Pause, Back/Next, speed and Restart in the other modes.
4. **Scenario coherence:** Both healthy and incident phase present their own recorded context; no cross-case leakage or invented continuous network monitoring. Confirm independent switching is editorial.
5. **Inspectability:** Expanded full route shows final footer and all stages; original messages, SP01's two ML predictions/two telemetry services, specialist evidence, RAG and RCA remain accessible.
6. **N03:** Congestion A 100% versus CU Processing 75% labels are consistent with each selected case's saved post-run metric. No field-level methodology is invented.
7. **All-pages smoke:** Eight pages load, nine scenarios can be selected, principal case identity persists across the Library/Evidence/RCA/Overview/Replay chain, no startup exceptions or deprecation fatal errors.

**Release sign-off remains conditional** until actual-browser one-screen behaviour and responsive usability are verified. The 3.89/5 independent V1.4.3 score is historical; no new live independent V1.5.0 score is asserted.
