# TEAD AI V1.6.1 — Connected Investigation Flow Visual Enhancement

**Release type:** focused **Platform Overview presentation** refinement of V1.6.0.

## Objective

Make the agreed end-to-end investigation diagram immediately understandable, including conditional routing and real execution ordering, while preserving the previous V1.6.0 content and V1.5.0 unified cockpit. This is **not** a change to LangGraph, the saved investigations, analysis, playback state, model calls or source data.

## What changed

- Replaced the text-heavy five-card flow on **Platform Overview** with an infographic-style connected flow.
- **SP01** is visibly first; its two ML predictions and the network/event telemetry sources are shown as subordinate capabilities.
- Decision node asks whether an incident exists and routes into exactly one of three **alternative** paths:
  - **Healthy:** direct to Supervisor; **no** specialist escalation.
  - **Cell/Site:** **SP02 → SP03 → SP04 → SP05 → SP06 → SP07**, sequentially.
  - **CU-domain:** **SP08**, an alternative to the six-specialist route, not an additional step.
- Each route points to **the same Supervisor**, showing evidence synthesis, competing explanations, RAG support when recorded and preservation of uncertainty.
- Clear final **Recorded Root Cause Analysis** output is stage 5.
- Below the flow, supporting capabilities are **not** depicted as an extra execution phase. Source records and evaluation remain separate.
- Responsive CSS: horizontal connected flow on suitable desktop widths; stacked readable flow at tablet/mobile widths. Mobile branch labels explicitly lead to the common Supervisor and are not sequential connectors.
- No misleading "live tool" or "live example" statements. The graphic describes **completed synthetic-network recorded investigations**.

## Content preserved

The previous Platform Overview value proposition, detailed architecture expander, execution-performance min/max cards, five network investigation learnings, six engineering learnings, future limitations and demo call-to-action remain. Other app pages, including Guided Operations Demo (Executive/Full Engineering), Network Overview, Scenario Library, Replay, RCA, Engineering Evidence and Evaluation, remain functionally unchanged. The cockpit's release label is updated to V1.6.1.

## Validation performed locally

- **229 automated tests passed** using `PYTHONPATH=. python -m pytest -q tests` (includes V1.4.3 replay seeking and all V1.6.0 performance and learning contracts, plus new flow structure checks).
- Chromium **HTML/CSS component-only** checks at **1366×768, 1440×900, 1920×1080, 1024×768, 768×1024 and 390×844**: no horizontal overflow, no source-content cards clipping, six ordered specialist nodes present.
- All **136 bundled frozen data files** compared against V1.6.0 by SHA-256: **identical**.
- Full deployed Streamlit browser acceptance and live page/mobile interaction **not yet completed**; the design's component previews must not be presented as deployment certification.

## Focused acceptance after deployment

1. At 1366×768 and 1440×900, the Platform Overview diagram must render with *three distinct incoming routes* into one Supervisor. The healthy route must visibly bypass all specialists; CU must not appear after SP07.
2. At 390×844, route labels and six sequential cell/site agents must be readable, no lateral scrolling/overlap, and each stacked alternative route must point to the common Supervisor.
3. Verify the unchanged headline performance values: **<00:25**, **<01:52**, **<02:54**, **<04:33**; min/max still match the nine-case data. The incident minimum is **02:48.2**.
4. Verify existing value proposition, original technical architecture expander, network learnings, engineering learnings and CV-supported claims all remain.
5. Re-run Executive and Full Engineering demos, including Restart → Seek → Inspector expand/collapse, and review original evidence and final RCA.

## Windows PowerShell deployment

Extract the release ZIP, then from your existing clean Git repository:

```powershell
cd C:\Users\Hp\projects\telecom-ai-engineering-demo
git status --short

$zip = "$env:USERPROFILE\Downloads\TEAD_AI_V1_6_1_Connected_Investigation_Flow.zip"
$folder = "$env:TEMP\tead-v161"
Expand-Archive -Path $zip -DestinationPath $folder -Force
$src = "$folder\Telecom_AI_Replay_V1"

Copy-Item "$src\app.py" . -Force
Copy-Item "$src\README.md" . -Force
Copy-Item "$src\V1_6_1_RELEASE_NOTES.md" . -Force
Copy-Item "$src\tests\test_v150_cockpit.py" .\tests\ -Force
Copy-Item "$src\tests\test_v160_overview_learnings.py" .\tests\ -Force
Copy-Item "$src\tests\test_v161_flow_infographic.py" .\tests\ -Force

python -m pytest -q tests
git diff --stat
git add app.py README.md V1_6_1_RELEASE_NOTES.md tests/test_v150_cockpit.py tests/test_v160_overview_learnings.py tests/test_v161_flow_infographic.py
git diff --cached --stat
git commit -m "Clarify conditional TEAD AI investigation flow V1.6.1"
git push origin main
```

This release does not require replacement of `data/`, `presentation.py`, `storyboard.py` or `operational_demo.py` when the repository is already at V1.6.0. The ZIP nevertheless contains the complete application and data for reproducibility.
