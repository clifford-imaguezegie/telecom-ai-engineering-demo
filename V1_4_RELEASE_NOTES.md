# TREAD AI — V1.4 Executive & Engineering Showcase

**Release date:** 12 October 2026  
**Purpose:** Correct recorded-execution presentation and improve the independent visitor experience while preserving every packaged investigation output.

## Included

1. **Recorded sequential execution:** The four cell/site investigations executed SP02 → SP03 → SP04 → SP05 → SP06 → SP07 in non-overlapping runs. Workflow connections, storyboards, tool handovers, and explanatory captions now describe the sequential recorded path. Parallelism was deferred because large input payloads made concurrent orchestration unstable. No historical timestamps or results were edited.
2. **Executive and engineering experiences:** The guided player supports a compact executive cut (up to 16 selected recorded scenes, normally about 84–96 seconds at 6 seconds per scene) and the original full engineering replay with all specialist detail. Both use the same original events and evidence records; neither performs live inference.
3. **TREAD AI branding:** Module numbers are removed from public banners, sidebar and footer. Scenario titles are displayed before technical reference IDs; original names remain in source records and provenance.
4. **RCA executive summary:** Introduces the recorded diagnosis, affected sites/cells/domains, supporting observations, alternatives, limitations, recommendations and original investigation time. No synthetic RCA conclusions are created.
5. **Usability improvements:** The guided player opens without the repetitive full intro, scene updates use stable playback-slider identifiers, RCA metric labels wrap rather than truncate, and repeated telemetry tool replies have unique source-backed display labels.
6. **More precise performance / evaluation language:** The nine health assessments include a healthy control; assessment and preliminary localisation share the SP01 completion milestone. Post-run score summaries are not claimed to establish independent diagnostic accuracy; token/cost fields are not represented as measured zero-cost inference.

## Scope and verification

- Original **9 case files, 126 compressed evidence files and manifest are byte-for-byte unchanged** (136 packaged data files in total).
- **159 offline automated tests passed**, including all eight page render branches and a new sequential-timestamp and executive-cut contract suite.
- Python source compilation passed.
- **Browser acceptance remains outstanding**: Streamlit is not installed in the build environment. Validate at 1366×768, 1440×900, and mobile 390×844. Exercise the full animation, executive cut, Play/Pause/Seek, scenario changes, and all evidence panels.
- The demo remains a **recorded synthetic-network replay**. It does not call live ML, network telemetry, LangGraph, an LLM or the knowledge-base retriever and does not remediate faults. Investigation durations are original experimental trace measurements, not production SLAs or demonstrated MTTR savings.

## Deploy to existing Streamlit Community Cloud app

1. Extract this ZIP.
2. Copy the contents of `Telecom_AI_Replay_V1` into the existing `telecom-ai-engineering-demo` repository, preserving the repository's `.git` folder and your deployment-specific configuration.
3. Run:

```powershell
git add .
git status
git commit -m "Release TREAD AI V1.4 executive engineering showcase"
git push origin main
```

4. After Streamlit auto-redeploys, open https://tread-ai.streamlit.app/ and complete browser acceptance before sharing the link publicly as the revised release.
