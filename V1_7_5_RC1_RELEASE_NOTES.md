# TEAD AI V1.7.5 RC1 — Independent-Evaluation Closeout Candidate

**Status:** RELEASE CANDIDATE ONLY. Not deployed and not independently signed off.

**Protected human-approved baseline:** TEAD AI V1.7.4 at Git commit
`4c63d230b7c41b6f46f372992dcb73d3d4878a02`.

**Candidate fingerprint:** `V1.7.5 RC1 · build 35828a0a0905`.
This is a SHA-256 fingerprint of the six deployment source modules (listed in
`release_identity.py`), **not** a Git commit ID. The application calculates
it from its actual running source files so release identity is inspectable.

## Addressed independent assessment findings

- **R01 (P1) — Measurement identity:** All per-observation `dimension_5qi`,
  `dimension_cause`, `dimensions_json` and other recorded dimensions are now
  retained in the operational-measurement chart selection. Distinct series
  are never connected into one line; unresolved duplicate timestamp/identity
  collisions are shown as source rows with the chart suppressed.
  Source-based audit: **1,120 affected groups**, **53,760 observations**,
  **3,360 unique dimension series** across the nine recorded cases; zero
  ambiguous series after dimension reconstruction. This does **not** certify
  physical network ground truth, only faithful decoded chart semantics.
- **R02 (P2) — Restart:** Each Restart resets the viewing timer, progress,
  completion and playhead and remounts the scene-seek control under a new
  generation key. Simulated regressions cover five repeats in each of three
  principal cases and both visitor modes. Intermittent live-browser behavior
  **must be retested independently**.
- **R03 (P2) — Observation window:** The two diagram labels no longer call
  one PM reporting interval the entire scenario observation window.
- **R04 (P2) — RCA readability:** Removes CSS line clamps and maximum heights
  on final Supervisor cards, preserves the full conclusion and changes the
  terminal guidance to Restart/review rather than disabled Next. The combined
  comparison journey labels the combined progress as 'Overall scene'.
- **R05 (P2) — Release identity:** Sidebar displays version, a runtime source
  fingerprint and candidate date, separate from LangSmith export timestamps.
  Release documentation links that fingerprint to this code package.
- **R08 (P2) — Entry/orientation:** Primary guided-demo CTA appears before the
  long explanatory content. Scenario selector options begin with the unique
  M05I case ID; navigating case sources and stage drill-down remains intact.
- **R07 (P2) — Evaluation metrics:** Clearly states that exact-match and
  post-run judge scores are reported from notebook exports and cannot be
  independently recalculated without field-level comparisons and rubrics.
  This is an **explicitly documented unresolved methodology limit**, not a
  claim of reproducibility.

## Open acceptance gates

- **R06:** Actual deployed browser tests at **1366×768, 1440×900, and
  390×844** remain required. Tests of static layouts are not equivalent.
- **R02:** Live repeated Restart checks in six principal guided journeys.
- **R01:** Live confirmation that the SP08 `DRB.EstabAtt.5QI` series shows
  separate 5QI 1, 5 and 9 selections and valid original values; verify other
  dynamic cause dimensions in a representative case.
- **R04/R08:** Live readable cards, completed-state wording, top-level CTA,
  scenario IDs and page navigation.
- **R07:** A later field-level evaluation artifact is needed for full
  independent reproducibility; until then preserve the visible limitation.
- **Live release verification:** Compare sidebar source fingerprint against
  `35828a0a0905` after deployment.

## Non-changes

No synthetic data files, ML models, LangGraph/LangSmith recordings, source
measurement values, Supervisor decisions, RAG outputs, or original evidence
files were edited. No production telemetry, actions or LLM calls are added.
The prior V1.7.4 human-approved application remains available at its
GitHub commit and in a separate local rollback ZIP.

## Test evidence

- Baseline reconstructed source before modification: **268 tests passed**.
- Updated candidate: **279 tests passed**.
- All nine recordings audited for dynamic identity using their packaged
  source measurement objects.
- No live Streamlit Cloud evaluation has yet been performed for this RC.
