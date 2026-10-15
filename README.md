# TEAD AI V1.6.1 — Connected Conditional Investigation Flow

**Latest presentation refinement.** The Platform Overview now has a genuinely connected infographic: SP01 health and localisation → conditional Healthy / Cell-Site / CU routes → one Supervisor → recorded RCA. The six cell/site specialists are explicitly sequential, SP08 is an alternative CU investigation, and the healthy control goes directly to review. Supporting tools, knowledge and evaluation are shown separately from execution. All V1.6.0 performance and learnings content, the preserved original technical architecture, the V1.5.0 unified cockpit and all recorded data remain unchanged. See `V1_6_1_RELEASE_NOTES.md` for test and deployment information. **Live Streamlit acceptance remains pending.**

---

# TEAD AI V1.6.0 — End-to-End Flow, Recorded Performance & Engineering Learnings

**Latest packaged public presentation release.** Rebrands the visible interface from TREAD AI to **TEAD AI** while preserving the V1.5.0 Unified Investigation Cockpit, all recorded synthetic-network cases and the eight existing pages. New Platform Overview sections clarify the conditional agent orchestration, show measured minimum/maximum execution phase times, and explain investigation and engineering learnings from M05_06C/M05_06D development. The previous detailed architecture and professional value explanation remain accessible.

See `V1_6_0_RELEASE_NOTES.md` for corrected timing ranges, tests, limitations and deployment; `CV_EVIDENCE_BRIEF.md` for professionally scoped CV-ready claims. The existing app URL can remain unchanged. Historical V1.5.0 and earlier release notes refer to the project's former TREAD AI brand for traceability.

---

# TEAD AI V1.5.0 — Unified Investigation Cockpit

**Latest packaged presentation release.** The Guided Operations Demo now displays the replay controls, current agent route and recorded input/action/output summaries in one compact desktop theatre. The platform remains an **offline, synthetic-network investigation replay**; no live network or AI model calls occur from the public app. For complete source messages, specialist inspection and the full route, expand the corresponding disclosures beneath the cockpit.

The viewer can still choose Executive / Full Engineering and Healthy → Incident / Incident-only modes. All 136 frozen data files are unchanged from V1.4.3. See `V1_5_0_RELEASE_NOTES.md` for changes, QA limitations, and deployment guidance.

# TEAD AI — Telecom AI Engineering Platform

## V1.4.3 — Post-Restart Timeline & Acceptance Readiness (13 October 2026)

- Guided and standalone playback sliders now use Streamlit `on_change` callbacks to preserve user-selected stage positions across fragment refreshes. Playback controls explicitly synchronise slider position; automatic timed replay still updates both position and evidence.
- Mobile-focused workflow cards use compact role names for legibility without discarding full accessible roles; frame height and native auto-sized full-route panels remain unchanged.
- The CU-processing and congestion RCA summaries now contain concise qualifications of the **recorded** causal and ML-confidence language; source evidence is not edited.
- **211 local automated tests** passed, including event-simulation regressions for seek after Restart. Twelve Chromium **component-only** checks at exact requested viewport sizes passed. These results do **not** replace live Streamlit acceptance or resolve the independent reviewer’s provisional release hold by themselves.
- See [`V1_4_3_RELEASE_NOTES.md`](V1_4_3_RELEASE_NOTES.md) for the precise diagnosis, test limits, deployment and acceptance procedure.

## V1.4 — External visitor experience and recorded-execution integrity

- **Branding:** Public interface and browser tab use TEAD AI; internal module numbers and trace IDs are retained only for provenance and source-code linkage.
- **Observed orchestration:** All four cell/site incident recordings execute SP02 through SP07 **sequentially**. Parallel execution was the original engineering objective but was deferred because large payloads caused freezes. The replay graph, routing descriptions, timing notes and README reflect the recorded order, without altering underlying trace data.
- **Two experiences:** A concise executive presentation (~84–96 seconds at 6 seconds per frame, scenario dependent) and the complete recorded engineering playback. Both use one source of original compressed evidence and allow investigation drill-down.
- **RCA comprehension:** A compact source-backed conclusion, scope and recorded limitations appear ahead of detailed Supervisor evidence. The detailed report remains accessible.
- **Playback and presentation:** Stable slider identifiers, compact evidence cards, longer engineer pacing, improved readable labels, and uniquely labelled evidence selector entries. Interactive browser testing remains required after each Streamlit deployment.
- **Evaluation:** Post-run aggregate scores remain separate from operational performance. Full field-level grading rubrics or accurate token accounting must not be inferred from the packaged summary if absent.
- **Scope:** Replay only; no live polling, model serving, new LangGraph execution, RAG retrieval, network remediation or production MTTR claim.

# TEAD AI — Telecom AI Engineering Platform · Recorded Investigation Replay

**Release:** V1.4 Executive & Engineering Showcase (recorded offline replay) — 12 October 2026  
**Source project:** `module_5_telecom_ai`, internal project module, M05_06D  
**Scope:** Nine recorded end-to-end 5G RAN accessibility investigations on **synthetic** network scenarios.

## What this delivers

An interactive **Streamlit evidence-grounded replay** of nine executions that have already completed. The application never performs new model inference, agent execution, telemetry retrieval, LangSmith requests, or paid API calls. It uses 126 frozen evidence records extracted from nine selected LangSmith JSON exports, plus the saved investigation-stage outputs and run timelines.

Eight sections:

1. **Platform Overview** — the visitor landing page explains the network problem, three measured milestones and the full conceptual architecture: localisation agent → dual ML/dual telemetry → evidence assessment → specialists or healthy route → RAG-supported Supervisor → RCA. Start the animation with the prominently labelled button.
2. **Guided Operations Demo** — narrated health assessment → separate incident investigation with playback controls, dual ML/telemetry reveal, incident routing, accurate original runtime indicators, and agent-level evidence drill-down.
3. **Network Overview** — recorded network topology, scenario-level KPI trends, portfolio of cases, and selected-case Curated Telecom Knowledge Base query.
4. **Scenario Library** — select a completed investigation and see its recorded scope, fault family, and outcome.
5. **Agentic Replay** — step through saved SP01 localization, specialist analyses, supervisor correlation and final report, including the Supervisor’s explicit RAG contribution record. The recorded SP02–SP07 specialist runs executed sequentially to maintain stability with large input payloads; concurrent execution is a deferred engineering optimisation.
6. **Root Cause Analysis** — preserved supervisor finding, supporting evidence, alternatives, residual uncertainty, recommendations, and the knowledge-informed query → mechanism → hypothesis → discriminating-observation reasoning chain.
7. **Engineering Evidence** — inspect 15-minute formal accessibility KPIs, affected-cell series, and recorded operational tool measurements with source evidence identifiers.
8. **Evaluation & Performance** — recorded trace duration, individual run-node timings, trace provenance, and saved post-run evaluation for the matching execution, separated from operational evidence.
The network observed in each scenario is an **independent synthetic snapshot**; data from different case dates should **not** be interpreted as one continuous network trend.

## V1.3.1 — Visitor Onboarding and UI Reliability Fixes

This hotfix addresses user acceptance findings from the hosted V1.3 application without changing the recorded data or investigation results:

- **Scenario selector contrast:** replaces the global white-text rule that made the sidebar scenario selection invisible on a pale control; the selected value and dropdown chevron are now styled with a strong contrasting background and border. The selector is explicitly labelled **Select scenario ▾**.
- **Dedicated, visible Platform Overview landing page:** introduces the business purpose, 9/9 and 8/8 recorded experimental results, and a readable architecture that begins with the Network Health & Localisation Agent invoking the two ML and two telemetry services. It explains incident/healthy routing, sequential specialists, the Curated Telecom Knowledge Base and RCA Supervisor. A prominent button starts the animation.
- **Playback visibility (V1.3.1):** the Guided Operations Demo links back to the detailed architecture page. In V1.4, repetitive introduction cards are removed above the player for improved visibility.
- **Duplicate widget prevention:** removes a duplicate engineer drill-down block that rendered the same keyed Streamlit selectors twice and could raise a duplicate-key runtime exception.
- **Visitor-friendly agent labels:** the main playback and routing diagram now display meaningful role names rather than raw `SP01`–`SP08` codes. Original IDs remain accessible in technical evidence and trace provenance for engineering users.

**Historical V1.3.1 validation:** 142 local automated checks passed. This release uses a larger regression suite. Live browser acceptance remains required after redeployment.

## V1.3 — Visitor Experience, Agent Presentation & Measured Outcomes

**The dedicated Platform Overview landing page now explains the system before playback.** A short description, four-stage conceptual architecture and three trace-verified investigation-performance headlines introduce the solution. The architecture correctly shows the **Network Health & Localisation Agent (SP01) invoking two ML predictions and the Network Overview / Event telemetry tools**. ML is supporting probabilistic evidence, not an independent autonomous monitoring agent.

| Demonstrated milestone | Based on the included original runs | Boundary |
|---|---:|---|
| **Fault / network-health assessment in under 1 minute** | **9 of 9** SP01 runs, maximum **24.3 seconds** | SP01 top-level chain completion, healthy control included |
| **Affected fault scope localised within 2 minutes** | **8 of 8** recorded incident runs | SP01-supported scope/handover, **not** a separately timed specialist localisation milestone |
| **Root cause assessment in under 5 minutes** | **8 of 8** incident runs; longest **4m 33s** | LangGraph root end-to-end duration, includes specialist and Supervisor stages |

These are **selected synthetic-network investigation experiments** and do **not** prove a production MTTR reduction, guaranteed SLA or cost saving. The app computes its headline pass counts from the included cases rather than keeping benchmark numbers disconnected from source records. The healthy-to-incident storyline remains two independent traces.

**Presentation improvements:**

- **Scenario Library:** the selected scenario is now plainly visible in an on-page dropdown, preselected to M05I0003 (Single-site radio resource congestion) for new sessions. Selectors on other pages remain available in the sidebar.
- **Public agent naming:** the interface and animated diagram use descriptive engineering names, such as *Radio Analysis Agent*, *CU-Domain & Boundary Analysis Agent* and *RCA Supervisor & Evidence Synthesis*. Source identifiers (`SP01`–`SP08`) remain available for engineer-level correlation and exact evidence references.
- **Animation theatre:** the recorded routing diagram and the selected input, action and outcome panels appear together in a compact two-column desktop layout. A detailed stage expander and existing engineer drill-down preserve complete saved data. Smaller screens can still require scrolling; verify layout in the deployed browser.
- **Gentler playback:** the full engineering replay default interval is **7 seconds per presentation beat**, adjustable to 3/5/7/10/14 seconds. Handover, finding, decision, RAG and report beats remain on screen **1.5× longer** to improve comprehension. The executive cut defaults to **6 seconds per scene** and targets approximately 90 seconds. This is *presentation timing*, entirely separate from trace timing.
- **Human-readable durations:** RCA summary durations and the portfolio show minutes-and-seconds formatting when appropriate (`2m 48s`, not `168 s`).
- **RCA specialist summary:** displays each participating agent's mission, **wall-clock execution duration**, separately summed **recorded LLM inference spans**, and the names of recorded tool outputs. Individual agent durations correspond to recorded chain spans; individual inference spans are not whole-agent elapsed durations.
- **Closing value:** frames potential operational benefits—faster evidence correlation, consistent causal assessments and wider access to specialist expertise—without implying measured production savings or automated remediation.

The demonstration is still fully offline. It performs **no** new ML inference, LLM generation, RAG retrieval, network calls, telemetry polls or network modification. Model weights are not shipped. The exact same 9 cases and 126 evidence files from V1.2 remain in `data/` without changes.

**Updating GitHub / Streamlit Community Cloud:** extract the ZIP; copy its `Telecom_AI_Replay_V1` contents over your existing `telecom-ai-engineering-demo` project, retaining the `.git` folder. Run:

```powershell
git add .
git status
git commit -m "Fix scenario selector, architecture intro and replay drill-down"
git push origin main
```

Keep the same `app.py` entry point; no additional Python dependency or API key is required. Full source/data checks: `python -m pytest -q tests`. **Automated source and Streamlit-stub checks passed; live browser interaction and mobile layout are not confirmed by these tests.**

---

## Run on your own machine

Requirements: Python 3.11+ and access to pip install packages.

```bash
cd Telecom_AI_Replay_V1
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS or Linux
# source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, normally `http://localhost:8501`. No secrets configuration is required. The demonstration displays **completed** runs; it never reruns the costly notebooks. On Windows, you may alternatively run `./run_windows.ps1` from PowerShell to set up the venv and launch the app. On Linux/macOS, use `./run_unix.sh`.

**Note:** A browser acceptance pass on your deployed Streamlit app is still necessary. The Python/data contract and Streamlit-stub tests passed, but actual interactive browser acceptance testing has not been run here. After deployment, verify animation pacing, panel visibility, the Scenario Library selector and agent drill-down on your target screen size.

## Source selection and corrections

Exactly nine cases are included. For four cases, the later corrected export replaces the previous trace; the earlier export is **not** bundled:

| Case | Selected source export timestamp (UTC) | Status |
|---|---|---|
| M05I0017 | 2026-10-10 20:45:51 | Original |
| M05I0002 | 2026-10-10 22:14:00 | Original |
| M05I0006 | 2026-10-10 22:29:08 | Original |
| M05I0003 | 2026-10-10 22:36:29 | Original |
| M05I0019 | 2026-10-10 22:45:41 | Original |
| M05I0004 | 2026-10-11 00:02:45 | Corrected |
| M05I0005 | 2026-10-10 23:54:43 | Corrected |
| M05I0008 | 2026-10-10 23:49:23 | Corrected |
| M05I0016 | 2026-10-10 23:33:37 | Corrected |

The updated notebook supplied with the corrected traces, `M05_06D_GPT_Luna_10102026_1912 (2).ipynb`, contains **new saved post-run evaluations and matching LangSmith export receipts for all four corrected traces**. The replay links each of the nine evaluation scores to its corresponding selected export timestamp. Grading remains post-run assessment, segregated from operational evidence in the replay. The original full-length JSON files and notebook are *not* included in the lightweight distributable ZIP (their SHA-256 provenance is recorded in `data/manifest.json`).

## Evidence handling and integrity

- All formal/accessibility KPI plots come from `telemetry_network_overview`; **48** subnetwork KPI rows and **1,440** per-cell KPI records per case, with original 15-minute spacing.
- Measured operational evidence is extracted from the completed SP02–SP08 telemetry tool calls and is stored as compressed JSON grouped by original evidence ID. The `LOSSLESS_COLUMNAR_TIME_SERIES` format is preserved rather than replaced with random data or example chart values.
- The recorded Supervisor outcome is **not recomputed**, reworded as a new conclusion, or trained on post-run labels. No ground truth is fed into replay stages.
- ML outputs are left explicitly **UNCALIBRATED** and interpreted as supporting evidence, never as deterministic network truth.
- The SHA-256 hash for each original selected trace and for the updated notebook is recorded in `data/manifest.json`.
- **Curated telecom knowledge-base RAG reasoning is showcased explicitly** in Network Overview, the Supervisor final replay stage, and Root Cause Analysis. The Supervisor's original `knowledge_base_contribution` record is preserved: **agent query, mechanism summary, supported and competing hypotheses, expected discriminating observations, incident observations, missing evidence, contribution type, supporting-evidence weight and limitations**. This illustrates how the recorded RAG reasoning informed fault-mechanism assessment without inventing causal performance uplift.
- **Raw curated knowledge-base retrieval passages remain excluded** from the public distributable app. Retrieval metadata (source, query, method, and result count) remains available for provenance; original third-party/restricted excerpt text is not redistributed. **The contribution reasoning is not excluded.** The original Supervisor's analysis is a recorded attribution of reasoning, not a formal document-by-document citation nor proof that RAG independently identified the root cause.
- For the healthy control (M05I0017), the saved Supervisor record explicitly reports **no knowledge-base use**; the demo does not fabricate a query or contribution.
- The original LangSmith identifier `supervisor_private_knowledge_search` is retained as immutable trace provenance, while the application presents it as **Curated Telecom Knowledge Base Search**. This is a naming update, not a change to the recorded investigation or the knowledge source.
- The replay package contains neither original model prompts nor authentication credentials, API tokens, raw cloud configurations or the gigabyte-sized full trace exports.
- Before any public deployment, independently review output summaries, telemetry and presentation copy for disclosure permissions and scenario confidentiality.

## Cost and hosting

Local execution uses only a Streamlit UI with compressed data. **No LLM, LangSmith API, external RAG service, LangGraph/MCP server, database, GPU, or inference backend is needed.** This removes *inference/API* costs for the demo, but cloud hosting (including free-tier eligibility or idle compute) depends on the chosen provider. Do not assume that a deployed service is free. Avoid unattended GCP Cloud Run instances without cost controls.

## V2 — planned, not built here

V2 would replace the read-only source adapter with authenticated retrieval and live LangGraph investigation, Telemetry MCP adapters, access control, auditability, rate limits and budget guardrails. **No V2 live functionality is included** in this V1 package.

## Validate the replay dataset (no Streamlit required)

```bash
python -m pytest tests -q
```

Tests check selected corrections, scenario identities, all source evidence references, 15-minute KPI inventory, recorded graph routes, preservation of all nine Supervisor knowledge-base contribution records, post-run evaluation isolation, and withholding of raw third-party retrieval passages.

## Directory structure

```text
Telecom_AI_Replay_V1/
  app.py                    # Read-only Streamlit UI, guided and full replay
  presentation.py           # Public agent names, per-agent timing, benchmark audit
  operational_demo.py       # Pure trace-backed guided storyline and exact timing helpers
  storyboard.py             # Animated LangGraph routing and beat construction
  requirements.txt
  README.md
  build_replay.py           # Offline source-ingest script; requires original exports alongside this project
  data/
    manifest.json           # Selected source SHA-256, identity, timing, correction markers
    cases/                  # 9 compressed stage records
    evidence/               # 126 compressed tool evidence records by case
  tests/
    test_replay_contract.py
    test_storyboard.py
    test_operational_demo.py
    test_ui_smoke_without_streamlit.py
```

**Important:** `build_replay.py` is a reproducibility script and expects the original uploads to be available in its parent folder. The generated app uses the already-included `data/` folder and **does not need the original JSON files** at runtime. Never execute the source notebook in order to operate the V1 demo.

## Animated agentic investigation workflow (V1.1)

The **Agentic Replay** page now opens in **Animated workflow** mode. This is a
read-only cinematic walkthrough of the **saved** LangGraph investigation,
not new network activity.

- **Play / Pause / Back / Next / Restart** controls; select a **2, 3, 5 or 8
  seconds per beat** presentation pace, or scrub the timeline.
- A **scenario-specific animated workflow diagram** highlights network
  localisation (SP01), the recorded specialist branch, the join, the Supervisor
  and final report. Cell/site incidents fan out to SP02–SP07; CU-domain incidents
  use SP08; the healthy control routes directly to the Supervisor.
- Each highlighted event displays a **saved input/handover**, **tool call or
  agent action**, and **recorded output/feedback**. Tool calls carry original
  evidence IDs and, where matched, original LangSmith tool-start timestamps.
  Specialist findings show recorded `assessment_feedback`, including the Radio
  Analysis Agent's radio-link analysis, rather than fabricated messages.
- A recorded **Curated Telecom Knowledge Base question, mechanism and
  observations** is shown only when its contribution exists in the completed
  Supervisor output. Raw passages remain excluded; no new RAG retrieval occurs.
- The **Recorded-stage inspector** toggle preserves detailed inspection of
  every original SP01, specialist and Supervisor stage and trace-node table.

**Important engineering interpretation:** SP02–SP07 comprise a sequential
analytical branch in the original graph. For presentation clarity, the
storyboard introduces each agent's recorded tools and conclusions one at a time.
This is **presentation order, not proof of execution order or actual timings**.
Playback speed is illustrative; source timestamps and durations remain in the
raw trace/inspector and evaluation views. The workflow diagram lights up the
record **being presented**, not an agent presently executing. The animation
requires Streamlit 1.41+ for automatic fragment updates, and does not require
JavaScript packages, telemetry/network credentials or paid model calls.

To update an already-deployed Streamlit Community Cloud app, commit and push
`app.py`, `storyboard.py`, `requirements.txt`, `README.md`, and `tests/` to the
same GitHub repository. The included `data/` and `build_replay.py` are preserved.

---

## Guided Operations Demo — Animated Monitoring-to-RCA Experience (V1.2)

The application now **opens on Guided Operations Demo**, a curated, cinematic presentation of the underlying completed investigation. It **does not perform real-time network monitoring**. The original six pages remain unchanged and accessible from the sidebar; the guided view is a seventh page.

### Two presentation formats

- **Healthy check → Separate incident (default):** Plays the completed M05I0017 healthy-control trace, including SP01's ML and telemetry evidence, its *no material issue* finding, and its direct Supervisor route. It then transitions to a **clearly marked, separate** recorded incident (selected in the sidebar), with new SP01 evidence, applicable specialist branches, knowledge-grounded Supervisor reasoning and final RCA. This is an editorial presentation of **two different runs**, not a claim that an incident occurred later in the same live network or that SP01 kept monitoring between runs.
- **Incident investigation only:** Starts directly from the chosen incident. Select M05I0003 (site congestion) to showcase six sequential specialist branches, or M05I0005 (CU-CP processing pressure) to foreground dual ML outputs, CU-domain analysis and RAG-assisted competing-hypothesis discrimination. All eight incident scenarios are supported. Selecting M05I0017 gives the healthy-only replay.

### What appears during the guided animation

1. **SP01 initiates the assessment** with recorded scenario context, topology and model metadata.
2. **SP01 invokes four crucial outputs:** an ML fault-family prediction (WHAT), an ML scope prediction (WHERE), Network Overview Telemetry (15-minute PM measurements), and Network Event Telemetry. Each output remains *awaiting SP01* until its own recorded call appears in the playback. ML scores remain explicitly **uncalibrated supporting evidence**, not network truth.
3. **SP01 assesses materiality and locality** and routes a material incident to SP02–SP07 (sequential cell/site analysis) or SP08 (CU/boundary analysis); the healthy control goes directly to the Supervisor. The workflow diagram reflects the selected recorded route.
4. **Specialists receive the handover, call telemetry tools, and return feedback.** For pacing the guided version shows one representative tool response per specialist; the existing full Agentic Replay and the drill-down retain **all** original calls and stage outputs.
5. **Supervisor assesses hypotheses and evidence.** Where the recorded knowledge-base contribution was used, its actual question, mechanism summary, hypothesis discrimination, confirming observations and limitations appear. Raw retrieved third-party passages remain excluded.
6. **Final recorded verdict** presents the Supervisor's diagnosis and direct link to the full Root Cause Analysis page.

### Playback and transparency

- **Play / Pause / Back / Next / Restart / Scrub** and adjustable cinematic pace (2, 3, 5 or 8 seconds per presentation beat).
- **Presentation timer** measures elapsed viewing time. This is **not** the time needed by the original agents to complete their work.
- **Recorded SP01 duration** comes directly from the SP01 LangSmith top-level chain. **Recorded end-to-end duration** comes from the original LangGraph root run. **Recorded event offset** is shown **only when the selected tool start or agent completion has an exact saved timestamp**; `—` otherwise. The presentation does not invent per-beat durations, concurrency or elapsed runtime.
- **Engineer drill-down** allows selection of any agent in the active recorded run, inspection of its analytical stages, representative outputs, relevant tool evidence identifiers and original execution timing. Detailed original KPI plots remain available in Engineering Evidence. No original source is edited.
- **Independent scenario snapshots:** different scenarios have independent recorded observation windows. The static replay cannot claim recurring fresh scans at one-, two-, or five-minute intervals, even if the interface resembles an operational console. The PM data's 15-minute measurement interval is separate from the investigation execution time and the video pacing.

The demonstrated runtimes are from individual synthetic experiments, not production MTTR results, service-level guarantees or evidence of achieved OPEX savings. The demo never modifies network nodes or runs remediation workflows.

### Updating an existing Streamlit deployment

Extract the ZIP and **copy its contained files** into the existing GitHub repository (`telecom-ai-engineering-demo`) **without deleting the `.git` folder**. Stage and commit all changed application and test files:

```powershell
git add app.py operational_demo.py storyboard.py README.md tests
# If copied from the ZIP, verify all tracked data files are unchanged with git status.
git status
git commit -m "Add SP01-led guided operational investigation demo"
git push origin main
```

Streamlit Community Cloud normally redeploys after the GitHub push. The deployment still uses `app.py`, `requirements.txt` and the bundled `data/` folder; no additional API tokens, cloud services or paid model calls are required.

Run the complete offline validation suite:

```bash
python -m pytest -q tests
```

**QA limitation:** Automated source-contract and framework-stub page tests can run without Streamlit. Actual Play/Pause interaction, browser layout, chart rendering, and mobile responsiveness should be accepted on the deployed Streamlit instance.


## V1.4.1 — Readable animated workflow

The Guided Operations Demo and Agentic Replay now highlight a larger **Previous → Current → Next** recorded agent transition instead of shrinking the complete route into a miniature diagram. The complete recorded route is accessible in an expander. Recorded data, timings, investigation order, ML outputs, RCA conclusions, and playback controls are unchanged. See `V1_4_1_RELEASE_NOTES.md`.

### V1.4.2 follow-up browser review corrections

V1.4.2 fixes cross-page scenario synchronisation, replaces the fixed-height full-route iframe with auto-sized HTML, and hides empty alternatives headings in the RCA summary. See `V1_4_2_RELEASE_NOTES.md`. All historical investigation evidence is preserved.
