# TEAD AI V1.7.5 RC2.1 — Scenario Initialisation Hotfix

**Release candidate, 16 October 2026. Not yet accepted or deployed by this package.**

## Why this revision exists

A controlled independent RC2 Work browser evaluation observed two intermittent initial-state violations after selecting scenarios, despite nine successful end-of-playback Restart cycles:

- M05I0003 Executive initially presented `Chapter 1/6 · Scene 1/13`, paused at 8%, instead of `Ready 0/13`.
- M05I0017 Healthy later initially presented `1/7`, paused at 14%, instead of `Ready 0/7`.

These observations establish an initialisation contract failure. They do **not** independently prove its internal cause or that the RC2 Restart correction caused it.

## Targeted correction

- The original `app.py` is updated in place. A `_activate_guided_context` guard runs before the Guided Operations fragment is mounted.
- The guard identifies a real change of selected scenario, selected source recording, presentation (incident/healthy/comparison), or visitor experience (Executive/Engineering).
- If the newly selected view was visited before, its **cached player state** is reset via the existing `_restart_guided_player` implementation. This sets the scene to Ready, clears elapsed time and completion, pauses playback, and advances the scene-slider generation so in-flight old slider callbacks cannot restore an old scene.
- Ordinary Streamlit rerenders or navigation away and back to the **same active selection** continue to preserve intentional progress and seek position. Recorded evidence, orchestration, output text and route timings are untouched.
- The existing explicit Restart logic and destination scroll restoration are unchanged.

## Local testing and integrity

- **320/320** tests passed with `python -X utf8 -m pytest -q tests` in the assembled V1.7.5 RC2.1 worktree.
- Tests include scenario switching over all nine recorded cases in both visitor experiences; revisiting previously selected cases; experience switching; stale slider callback handling; preservation during ordinary rerenders; and all prior replay/measurement regressions.
- One existing `SyntaxWarning: invalid escape sequence '\\d'` is emitted by an older architectural test; no tests failed.
- The **136 bundled evidence/data files** from the V1.7.4 baseline were left untouched; no telemetry, case, or LangSmith source files are included in this hotfix archive.
- New deterministic source fingerprint: **`b00e1fef8f89`**. Note: this is a SHA-256-derived application-source fingerprint, **not the Git commit SHA**.

## Required live acceptance

1. Verify public sidebar **V1.7.5 RC2.1 · build b00e1fef8f89**, after deployment.
2. Select Healthy → Congestion A → CU Processing → Congestion A → Healthy and record the **initial** Ready, 0% and Play-enabled state after *each selection*, with no Restart/Play/Next/seek.
3. Repeat the sequence after deliberately leaving one scenario paused at scene 1 (to exercise old cached state), in both Executive and Engineering experiences.
4. Recheck end-of-completion Restart, including prior failures Healthy Executive and Congestion A Full Engineering, plus seek/mode change.
5. Recheck representative all-nine-page smoke/navigation, original 5QI evidence and Guided Operations regression because a shared app file changed.

**Acceptance note:** No local test substitutes for live-browser confirmation. Previous RC2 Work observations do not attest a different source fingerprint; re-evaluate the affected gates on the new build before formal V1 closeout.

## Baselines

- V1.7.5 RC2 starting Git commit on `main` (verified via GitHub): `3ad68342960fa81724da59a9512a5f15605eca46`.
- Protected human-approved V1.7.4 branch: `backup/v1.7.4-human-go`, commit `4c63d230b7c41b6f46f372992dcb73d3d4878a02`.

Unrelated technical-terminology/glossary improvements and Live Retrieval work remain deferred to their separate development tracks.
