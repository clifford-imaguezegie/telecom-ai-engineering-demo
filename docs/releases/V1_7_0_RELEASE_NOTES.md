# TEAD AI V1.7.0 — Guided Operations Demo: Recorded Investigation Story

**Status:** Local redesign candidate. Automated tests and standalone Chromium component-viewport reviews completed; full live Streamlit browser acceptance remains pending.

## Why this release exists

An independent visitor (and the original developer) could not reliably follow the former Guided Operations Demo. It opened with a healthy-control trace and then silently changed to a separate incident. The Previous / Current / Next agent blocks were not a full connected architecture, and three simultaneously populated input/action/output panels made evidence arrivals difficult to perceive. The heading sometimes appeared clipped after navigation.

## What changed

1. **Default: a single recorded incident.** The selected incident now opens in a clearly labelled **Ready** state. A standalone healthy control and a comparison of the two independent recordings remain available through **Presentation** options. The comparison stops at an explicit transition and requires the user to continue; no live causal link is implied.
2. **Narrated six-chapter investigation.** The incident covers initial assessment → ML/telemetry → decision and conditional routing → specialist evidence → Supervisor synthesis → RCA outcome. The healthy control uses a truthful three-chapter sequence. The scene heading and one large recorded observation reduce cognitive load.
3. **Connected conditional flow in the guided page.** SP01 → alternative Healthy / Cell-Site (sequential SP02–SP07) / CU (SP08) routes → Supervisor → RCA, with the active route and agent visibly highlighted as the saved sequence advances. The route is not selected before the recorded SP01 decision.
4. **Progressive evidence disclosure.** Four initially blank tiles show ML fault-family, ML affected-scope, network KPI, and event evidence. Each becomes available only when the matching recorded SP01 tool-result beat is reached. The newly arrived result is visibly distinct. The original model probabilities remain explicitly uncalibrated.
5. **Healthy control evidence in Executive cut.** Includes the four recorded SP01 evidence results before the no-material-incident conclusion; the longer optional comparison is no longer described as an approximately 90-second presentation.
6. **Reduced presentation competition.** A single evidence-highlight panel replaces the old simultaneously populated three-pane focus. The complete original route, full stage messages, tool payloads, supporting 15-minute KPI charts and engineer drill-down remain in existing expanders below.
7. **Safe top heading clearance.** Increased top spacing on the Guided Operations Demo only. Other page layouts are unchanged.

## Invariants

- No source evidence, synthetic scenario, saved Supervisor output, original execution duration, evaluation result or provenance record is modified.
- This is an **offline saved-trace replay**, not real inference, telemetry polling, remediation, or a production MTTR demonstration.
- The original source `storyboard.py`, 136 `data/*` artifacts, `presentation.py`, and all other eight-page platform sections are unchanged.
- Full Engineering remains the recorded director-cut story, not a claim that all specialist tools run in the visitor playback.

## Local QA

- **241 automated tests passed** (existing regression coverage adjusted for intentional UX changes plus 7 new guided-story contracts).
- **136/136 recorded data files verified byte-identical** with V1.6.3 baseline.
- Standalone Chromium component previews inspected at **1366×768**, **1440×900**, and **390×844**; the desktop route, progressive evidence row and focus panel fit within the provided component viewport with no horizontal overflow. Mobile intentionally stacks vertically.
- **Not yet verified:** a complete live Streamlit deployment journey, scroll position after sidebar navigation, all form/input interactions on real Streamlit, and full mobile touch behaviour. These require acceptance after deployment.

## Compatibility and safe deployment

The update contains only changed source files, updated regression tests and this note. **Do not copy an old README over the user's updated portfolio-first README.** No requirements or recorded data assets change.

Because some local tests and release notes may already contain uncommitted edits, create backups and stage only the files in this package. Use `python -X utf8 -m pytest -q tests` on Windows to avoid cp1252 JSON reading errors and install the existing `requirements.txt` first if needed.
