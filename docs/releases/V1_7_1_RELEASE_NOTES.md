# TEAD AI V1.7.1 — Contextual Investigation Results & Trace-Aligned Timing

**Release type:** Presentation-only follow-up to V1.7.0. **No new model inference, agent execution, live telemetry or remediation.** The public app continues to replay nine saved synthetic-network investigations.

## Scope of this release

- Restores visible **presentation scene progress, progress bar, accumulated presentation playback time and original recorded trace time**. These measurements are explicitly distinguished. Intermediate original times appear only where a source event timestamp or node-completion marker exists; otherwise the last known marker is labelled as such.
- Renames the SP01 prediction tiles **WHAT** and **WHERE** (without the prominent “ML” prefix). Displays original model prediction labels and uncalibrated probabilities at their recorded tool offsets; adds the actual affected SITE/CELL/CU domain and SP01 end timestamp **only when the original localisation handover occurs**. This intentionally does not treat a model's predicted scope class as a confirmed network entity.
- Reuses four result cards contextually for three phases: **Network Assessment**, **Specialist Investigation** (current domain, evidence, conclusion, handover plus retained completed-agent timeline), and **Supervisor RCA** (root cause, decisive evidence, impact/scope, confidence/remaining gaps). Cards show results progressively, not before they were recorded.
- Makes **SP04 radio** visible in the Executive cell/site cut because the selected congestion evidence often depends on radio evidence. The Executive sequence continues to be an editorial subset; Full Engineering and original evidence remain inspectable.
- Places specialist and Supervisor result cards **ahead of the connected workflow** for immediate comprehension at laptop resolution. Preserves the connected route and underlying full engineering drill-down below.
- Makes the Supervisor's exact saved conclusion clearly visible and holds the final RCA view; reaching the last scene disables Play until the visitor deliberately chooses Restart or navigates. Healthy-control recordings correctly show a health outcome, not an invented root cause.
- Aligns the non-guided page hero to **Agentic Telecom Network Investigation & RCA Platform**, adds explicit strategic operational value to the Platform Overview introduction, and adds safe top clearance for the Guided heading.

## Integrity and qualification

- Recorded source cases, compressed evidence and metadata are **not edited or repackaged**. This incremental archive contains **no `data/` files and no `README.md`**; the portfolio-first README remains untouched.
- Supervisor diagnosis, detailed supporting and contradictory evidence, RAG contribution, confidence and residual uncertainty remain sourced from the original stored Supervisor outputs. Confidence is a recorded judgement, **not calibrated**.
- The application shows **saved investigation time** separately from a visitor's **presentation playback time**. A simulated per-agent clock or fabricated timestamp is never used.
- No production MTTR reduction, paid-token savings, production-grade SLA or autonomous remediation is claimed.

## Validation and limitations

- **250 local Python regression tests passed**, including SP01 source-time and scope-gating checks, complete case-specific RCA board checks, independent healthy-control routing, repeated seeking, comparison boundaries, and terminal RCA hold.
- Local Chromium **component** previews checked 1366×768, 1440×900 and 390×844. No horizontal page overflow; final RCA cards visible inside 1366×768. Mobile naturally stacks vertically and requires scrolling.
- **Live deployed Streamlit browser acceptance has not yet been performed**. Check the hosted app after deployment: top heading clearance, Play/Pause/Next/Restart, progress/timers, SP01 predicted-versus-confirmed scope, per-agent results, Supervisor RCA and both Executive/Full Engineering paths.

## Deployment

Copy only the source and test files included in this archive over the same paths in the existing Git repository. Check `git status` first; back up any local edits to those specific files. Run `python -X utf8 -m pytest -q tests`; stage **only** the named source, release notes and tests. Do not run `git add .` where unrelated uncommitted work is present. Do not force-push.
