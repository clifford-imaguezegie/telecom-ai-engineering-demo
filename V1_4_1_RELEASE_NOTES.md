# TREAD AI V1.4.1 — Workflow Readability Update

**Release date:** 12 October 2026  
**Baseline:** V1.4 Executive & Engineering Showcase  
**Scope:** Targeted presentation correction to the animated agent workflow, particularly on laptop screens.

## Change summary

- Replaced the miniature full-route SVG in the primary workflow panel with a **large, readable Previous → Current → Next** presentation. The active agent is highlighted and its actual investigation purpose is shown.
- The display is driven by the existing scenario-specific recorded story order. Healthy cases, CU-domain investigations, and sequential six-specialist cell/site investigations remain distinct.
- Added an expandable **View complete recorded agent route** for context, with labels that wrap rather than shrink to tiny text. Internal SP identifiers remain in technical provenance and are not needed to understand the workflow.
- Applied the new renderer to both the Guided Operations Demo and Agentic Replay. The surrounding timers, player controls, input/action/output cards, all nine scenarios, root-cause conclusions and performance figures remain unchanged.
- No additional ML, LLM, RAG, telemetry or LangGraph execution occurs.

## Verification

- **178 offline automated tests passed**, including all existing scenario/page tests and new stage-by-stage workflow contracts.
- Chromium layout inspection of healthy, congestion and CU-processing cases at **648 px and 540 px workflow viewport widths** found no horizontal overflow or clipped agent cards. Additional initial-card check at **390 px** also fit.
- All **136 packaged data files** are byte-for-byte identical to V1.4 (nine compressed cases, 126 recorded evidence records and the manifest).
- These are **source, render-stub and isolated browser layout checks**, not yet acceptance testing of the redeployed Streamlit Cloud application. Have a browser agent check the published guided and technical replays after deployment.

## Deployment

1. Extract this ZIP and copy the contents of `Telecom_AI_Replay_V1` into the existing GitHub repository, retaining `.git` and any deployment-specific configuration.
2. From the repository folder, run:

```powershell
git add .
git status
git commit -m "Improve TREAD AI replay workflow readability V1.4.1"
git push origin main
```

3. Review on `https://tread-ai.streamlit.app/`, especially at laptop resolution, and expand the complete recorded route to ensure layout and focus selection remain coherent during autoplay.
