# TEAD AI V1.6.0 — Investigation Flow, Performance & Engineering Learnings

**Release type:** presentation-only enhancement on V1.5.0 unified investigation cockpit  
**Scope:** Streamlit recorded synthetic-network demonstration; no new live inference or operational control.

## Changes

1. **TEAD AI branding:** visible public interface branding and browser page title changed from *TREAD AI* to *TEAD AI*. Internal historical release notes, original case IDs, trace hashes, evidence identifiers and CSS implementation selectors are preserved.
2. **Clear five-step investigation flow:** SP01 assessment (two ML tools and two telemetry services) → conditional routing → healthy bypass / sequential SP02–SP07 / SP08 → Supervisor synthesis (knowledge-base support when applicable) → saved RCA. The three exclusive route families converge on Supervisor. Original technical architecture remains accessible in a disclosure; it has not been deleted.
3. **Data-derived phase performance:** four `< HH:MM` upper-bound headline cards with actual minimum, maximum and sample count derived from the depth-one saved LangSmith chain spans. Includes separate healthy-control end-to-end timing and a case-level timing table under Evaluation & Performance.
4. **Network investigation learnings:** fast localisation, conditional routing, multi-domain corroboration, evidence-synthesis latency, provenance and uncertainty, all framed as experimental observations.
5. **Engineering learnings:** deterministic evidence preparation, historical SP08 representation-size reduction, token-context issue in historical SP02 runs, inference-cost safeguards, model-task qualification and bounded recovery. This section clearly distinguishes historical optimisation experiments from the nine public replay traces, and explicitly does **not** claim a verified saving in billed tokens or dollars.
6. **Preservation:** Introductory solution explanation, established `<1 minute` / `≤2 minute` / `<5 minute` milestones, Guided Operations Demo, scenario navigation, the original detailed architecture, value proposition, RCA, evidence and evaluation screens remain in place. Playback state callbacks are untouched.

## Precision correction

A previous conversational summary gave the minimum incident end-to-end time as **03:22.0**, inadvertently excluding the CU-domain processing case. The correct range across **all eight incident cases** is **02:48.2–04:32.9**, independently recomputed from packaged saved root durations. Other observed ranges are:

| Metric | Minimum observed | Maximum observed | Headline bound | n |
|---|---:|---:|---:|---:|
| SP01 Network Assessment & Localisation | 00:15.0 | 00:24.3 | < 00:25 | 9 |
| Specialist Investigation | 00:42.1 | 01:51.6 | < 01:52 | 8 |
| Supervisor Evidence Synthesis & RCA | 01:38.8 | 02:53.4 | < 02:54 | 8 |
| End-to-end incident investigation | 02:48.2 | 04:32.9 | < 04:33 | 8 |
| Healthy end-to-end (no specialist) | 00:17.2 | 00:17.2 | — | 1 |

Phase minima and maxima can arise from different cases. Specialist time sums only sequential agents actually present in the route. Root runtime includes the small orchestration overhead. Post-run judging is separate. All performance is derived from frozen synthetic-network experiments, not production SLAs, commercial outcomes or verified production accuracy.

## Validation

- `python -m pytest -q tests`: **226 passed** in local environment.
- 4 Chromium **overview-component** checks at 1366×768, 1440×900, 1920×1080 and 390×844: zero horizontal overflow and zero clipped content cards in this limited standalone HTML preview.
- Case/evidence data: identical to the V1.5.0 package, including all 136 frozen `data/` files (SHA-256 comparison conducted during packaging).
- The full Streamlit runtime and deployed browser were **not** independently tested here; Streamlit is unavailable in this local QA environment. No change to the V1.5.0 playback implementation is intended.

## Deployment from the release ZIP

Extract the ZIP, then in your existing local Git repository (confirm your working tree is clean first):

```powershell
cd C:\Users\Hp\projects\telecom-ai-engineering-demo
$zip = "$env:USERPROFILE\Downloads\TEAD_AI_V1_6_0_Presentation_Engineering_Learnings.zip"
$folder = "$env:TEMP\tead-v160"
Expand-Archive -Path $zip -DestinationPath $folder -Force
$src = "$folder\Telecom_AI_Replay_V1"
Copy-Item "$src\app.py" . -Force
Copy-Item "$src\presentation.py" . -Force
Copy-Item "$src\README.md" . -Force
Copy-Item "$src\V1_6_0_RELEASE_NOTES.md" . -Force
Copy-Item "$src\CV_EVIDENCE_BRIEF.md" . -Force
Copy-Item "$src\tests\test_v160_overview_learnings.py" .\tests\ -Force
Copy-Item "$src\tests\test_v14_release.py" .\tests\ -Force
Copy-Item "$src\tests\test_v150_cockpit.py" .\tests\ -Force
python -m pytest -q tests
git status
git diff --stat
git add app.py presentation.py README.md V1_6_0_RELEASE_NOTES.md CV_EVIDENCE_BRIEF.md tests/test_v160_overview_learnings.py tests/test_v14_release.py tests/test_v150_cockpit.py
git diff --cached --stat
git commit -m "Present TEAD AI investigation flow and engineering learnings V1.6.0"
git push origin main
```

After Streamlit deployment, acceptance should include a fresh launch, Platform Overview desktop/mobile visual check, one complete Executive and Engineering guided run, timeline seeking after Restart, and the case-level performance table. Keep the existing URL unless and until a separately approved Streamlit app/domain rename is planned.
