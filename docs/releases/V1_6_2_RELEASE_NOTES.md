# TEAD AI V1.6.2 — Single-Frame Architecture Overview

**Release type:** Focused Platform Overview presentation refinement, based on V1.6.1.

## Purpose

Make the essential investigation architecture visible together in a single **1366×768 laptop viewport** when the architecture section is brought into view. Preserve the existing detailed V1.6.1 connected infographic and the V1.6.0 engineering learning, evidence and execution performance sections.

## What changed

- Added a **compact first-view investigation map** using responsive HTML/CSS. It shows SP01 and its two ML / two telemetry tools, the SP01-informed routing decision, three **alternative** paths (Healthy; sequential SP02 → SP07; CU SP08), convergence on one Supervisor, and final recorded RCA.
- The compact card shows supporting knowledge/RAG, LangSmith traces and post-run evaluation as supporting resources rather than falsely implying new agents or runtime phases.
- The complete **V1.6.1 infographic is not discarded**: it remains inside the *Detailed investigation flow — full agents, tools, and provenance* expandable section.
- Existing *Detailed Architecture — original technical explanation (preserved)* remains available separately. The existing introductory value proposition, source-derived timing cards, telecom learnings, engineering learnings, value narrative, eight application pages and V1.5.0 Guided Operations cockpit are preserved.
- The public cockpit label is updated to V1.6.2. No new agents, live calls, network integrations, changed ML/RAG inference, or modified source investigations.

## Local QA and limits

- **231 tests passed**: `PYTHONPATH=. python -m pytest -q tests` in the prepared release folder. Includes the V1.4.3 seek regression, V1.5.0 cockpit, V1.6.0 measured performance and engineering learning, V1.6.1 route contracts and the V1.6.2 compact architecture checks.
- The **136 frozen case/evidence/manifest data files** were compared using SHA-256 with the V1.5.0 source package: identical.
- Standalone Chromium HTML/CSS **component** checks: 1366×768, 1440×900, 1920×1080, 1024×768, 768×1024 and 390×844. No horizontal overflow, and no card clipping in the tested model.
- At **1366×768** with a simulated 280px sidebar and a representative header, the entire *compact flow component* measured approximately **470px high** and was visible within the viewport once navigated to. Exact deployment rendering can vary with Streamlit sidebar width, app padding, browser zoom, system font and top navigation.
- Mobile 390×844 intentionally **stacks vertically** and needs vertical scrolling; no problematic horizontal overflow in component testing.
- This is **not** a full live Streamlit browser acceptance run, a cross-browser audit, or proof that the entire Platform Overview (hero + architecture + performance + learnings) fits one screen. Visitors may scroll down from the first page content to reach this architecture section; the diagram itself is designed to fit within a single laptop screen at the specified size.

## Windows PowerShell deployment (works from V1.5.0 or later)

Download the V1.6.2 complete release ZIP and save it in Downloads. From the existing Git repository:

```powershell
cd C:\Users\Hp\projects\telecom-ai-engineering-demo

git status --short
# Ensure the working tree is clean or save your local edits before overwriting files.

$zip = "$env:USERPROFILE\Downloads\TEAD_AI_V1_6_2_Single_Frame_Architecture.zip"
$folder = "$env:TEMP\tead-v162"
Expand-Archive -LiteralPath $zip -DestinationPath $folder -Force
$src = "$folder\Telecom_AI_Replay_V1"

Copy-Item "$src\app.py" . -Force
Copy-Item "$src\presentation.py" . -Force
Copy-Item "$src\README.md" . -Force
Copy-Item "$src\CV_EVIDENCE_BRIEF.md" . -Force
Copy-Item "$src\V1_6_0_RELEASE_NOTES.md" . -Force
Copy-Item "$src\V1_6_1_RELEASE_NOTES.md" . -Force
Copy-Item "$src\V1_6_2_RELEASE_NOTES.md" . -Force
Copy-Item "$src\tests\test_v14_release.py" .\tests\ -Force
Copy-Item "$src\tests\test_v150_cockpit.py" .\tests\ -Force
Copy-Item "$src\tests\test_v160_overview_learnings.py" .\tests\ -Force
Copy-Item "$src\tests\test_v161_flow_infographic.py" .\tests\ -Force
Copy-Item "$src\tests\test_v162_oneframe_architecture.py" .\tests\ -Force

python -m pytest -q tests
git diff --stat
git status --short
git add app.py presentation.py README.md CV_EVIDENCE_BRIEF.md V1_6_0_RELEASE_NOTES.md V1_6_1_RELEASE_NOTES.md V1_6_2_RELEASE_NOTES.md tests/test_v14_release.py tests/test_v150_cockpit.py tests/test_v160_overview_learnings.py tests/test_v161_flow_infographic.py tests/test_v162_oneframe_architecture.py
git diff --cached --stat
git commit -m "Add single-frame TEAD AI architecture view V1.6.2"
git push origin main
```

Do **not** replace `data/` or `storyboard.py` for a repo already at V1.5.0; those source files are unchanged. The ZIP includes the complete application for clean installation if needed.

## Live acceptance after deployment

1. Reload Streamlit and confirm **TEAD AI** brand plus V1.6.2 cockpit label.
2. Open Platform Overview, scroll once to the End-to-End Investigation Flow section at 1366×768, and confirm that **the complete compact diagram (including supporting-capability strip and footer) is visible together**, readable and not clipped. Distinguish initial page scrolling from scrolling *within* the diagram.
3. Expand **Detailed investigation flow** and confirm the original V1.6.1 connected infographic remains readable and represents the three route alternatives correctly.
4. Check 1440×900 and 390×844. Mobile vertical stacking is acceptable; horizontal overflow is not.
5. Confirm measured timings and Key Learnings remain on Overview; verify Executive and Full Engineering guided runs, Restart → Seek, inspectors, original evidence and RCA are intact.

**Scope statement:** Nine synthetic-network recorded investigations. The public app performs no live agent inference, RAG retrieval, telemetry polling or remediation. Timing and experimental quality metrics are not production MTTR/cost guarantees.
