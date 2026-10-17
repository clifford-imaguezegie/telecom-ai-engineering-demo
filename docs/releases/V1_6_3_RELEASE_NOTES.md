# TEAD AI V1.6.3 — Overview Introduction & SP01 Milestone Correction

**Scope:** Focused Platform Overview copy and data-backed milestone correction from V1.6.2. The connected one-frame architecture, full expandable technical flow, unified replay cockpit, evidence and evaluation pages remain unchanged.

## Changes

- Replaces generic opening copy with a concise challenge, differentiator and eight-incident / one-healthy-control experimental boundary. No human-vs-AI time-saving percentage is claimed.
- Changes the Network Health Assessment headline from `< 1 min` to **`< 25 sec`**, matching the observed maximum SP01 wall duration of **24.3 seconds** across **9/9** frozen scenarios.
- Replaces the misleading second `≤ 2 min` timing card with an **8/8 incident affected-scope localisation** coverage card. Its caption makes explicit that localisation occurs in the same SP01 execution as health assessment. They are not independently measured latency improvements.
- Retains **`< 5 min`** incident investigation and RCA for **8/8** incident cases. The precise measured range is 2m 48.2s–4m 32.9s in the performance section.
- Keeps the experimental/not-production qualification.
- Adds focused regression tests. All recorded data files remain byte-identical to V1.6.2.

## Deployment (from existing GitHub repository)

After extracting the ZIP, replace only `app.py`, `presentation.py`, `README.md` and the new `V1_6_3_RELEASE_NOTES.md` and `tests/test_v163_intro_milestones.py` in the repository. Do not replace `data/` or other modules.

```powershell
$zip = "$env:USERPROFILE\Downloads\TEAD_AI_V1_6_3_Overview_Milestone_Correction.zip"
$dest = "$env:TEMP\tead-v163"
Expand-Archive -LiteralPath $zip -DestinationPath $dest -Force
$src = "$dest\Telecom_AI_Replay_V1"
Copy-Item "$src\app.py" . -Force
Copy-Item "$src\presentation.py" . -Force
Copy-Item "$src\README.md" . -Force
Copy-Item "$src\V1_6_3_RELEASE_NOTES.md" . -Force
Copy-Item "$src\tests\test_v163_intro_milestones.py" .\tests\ -Force
python -X utf8 -m pytest -q tests
# If tests pass:
git add app.py presentation.py README.md V1_6_3_RELEASE_NOTES.md tests/test_v163_intro_milestones.py
git commit -m "Correct TEAD AI SP01 assessment milestone V1.6.3"
git pull --rebase origin main
git push origin main
```

**Environment reminder:** Install dependencies with `python -m pip install -r requirements.txt` if the local Python environment lacks Plotly; `python -X utf8` avoids Windows cp1252 decoding failures in legacy test fixtures. Do not claim browser acceptance from source-level test results.
