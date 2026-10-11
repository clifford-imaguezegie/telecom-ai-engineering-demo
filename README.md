# Telecom AI Engineering — M05_06D Recorded Investigation Replay

**Release:** V1.2 animated Guided Operations Demo (recorded offline replay) — October 2026  
**Source project:** `module_5_telecom_ai`, Module 5, M05_06D  
**Scope:** Nine recorded end-to-end 5G RAN accessibility investigations on **synthetic** network scenarios.

## What this delivers

An interactive **Streamlit evidence-grounded replay** of nine executions that have already completed. The application never performs new model inference, agent execution, telemetry retrieval, LangSmith requests, or paid API calls. It uses 126 frozen evidence records extracted from nine selected LangSmith JSON exports, plus the saved investigation-stage outputs and run timelines.

Seven sections:

1. **Guided Operations Demo** — narrated health assessment → separate incident investigation with playback controls, dual ML/telemetry reveal, incident routing, accurate original runtime indicators, and agent-level evidence drill-down.
2. **Network Overview** — recorded network topology, scenario-level KPI trends, portfolio of cases, and selected-case Curated Telecom Knowledge Base query.
3. **Scenario Library** — select a completed investigation and see its recorded scope, fault family, and outcome.
4. **Agentic Replay** — step through saved SP01 localization, specialist analyses, supervisor correlation and final report, including the Supervisor’s explicit RAG contribution record. The local SP02–SP07 branch ran in parallel, but its saved outputs are presented sequentially for easier review.
5. **Root Cause Analysis** — preserved supervisor finding, supporting evidence, alternatives, residual uncertainty, recommendations, and the knowledge-informed query → mechanism → hypothesis → discriminating-observation reasoning chain.
6. **Engineering Evidence** — inspect 15-minute formal accessibility KPIs, affected-cell series, and recorded operational tool measurements with source evidence identifiers.
7. **Evaluation & Performance** — recorded trace duration, individual run-node timings, trace provenance, and saved post-run evaluation for the matching execution, separated from operational evidence.

The network observed in each scenario is an **independent synthetic snapshot**; data from different case dates should **not** be interpreted as one continuous network trend.

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

**Note:** The development environment used to package the project does not have Streamlit installed and has no external package access. The Python/data contract tests passed; an actual interactive browser startup has **not** been run here. Run the command above on a computer with Streamlit to complete UI acceptance testing.

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

**Important engineering interpretation:** SP02–SP07 comprise a parallel
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
- **Incident investigation only:** Starts directly from the chosen incident. Select M05I0003 (site congestion) to showcase six parallel specialist branches, or M05I0005 (CU-CP processing pressure) to foreground dual ML outputs, CU-domain analysis and RAG-assisted competing-hypothesis discrimination. All eight incident scenarios are supported. Selecting M05I0017 gives the healthy-only replay.

### What appears during the guided animation

1. **SP01 initiates the assessment** with recorded scenario context, topology and model metadata.
2. **SP01 invokes four crucial outputs:** an ML fault-family prediction (WHAT), an ML scope prediction (WHERE), Network Overview Telemetry (15-minute PM measurements), and Network Event Telemetry. Each output remains *awaiting SP01* until its own recorded call appears in the playback. ML scores remain explicitly **uncalibrated supporting evidence**, not network truth.
3. **SP01 assesses materiality and locality** and routes a material incident to SP02–SP07 (parallel cell/site analysis) or SP08 (CU/boundary analysis); the healthy control goes directly to the Supervisor. The workflow diagram reflects the selected recorded route.
4. **Specialists receive the handover, call telemetry tools, and return feedback.** For pacing the guided version shows one representative tool response per specialist; the existing full Agentic Replay and the drill-down retain **all** original calls and stage outputs.
5. **Supervisor assesses hypotheses and evidence.** Where the recorded knowledge-base contribution was used, its actual question, mechanism summary, hypothesis discrimination, confirming observations and limitations appear. Raw retrieved third-party passages remain excluded.
6. **Final recorded verdict** presents the Supervisor's diagnosis and direct link to the full Root Cause Analysis page.

### Playback and transparency

- **Play / Pause / Back / Next / Restart / Scrub** and adjustable cinematic pace (2, 3, 5 or 8 seconds per presentation beat).
- **Presentation timer** measures elapsed viewing time. This is **not** the time needed by the original agents to complete their work.
- **Recorded SP01 duration** comes directly from the SP01 LangSmith top-level chain. **Recorded end-to-end duration** comes from the original LangGraph root run. **Recorded event offset** is shown **only when the selected tool start or agent completion has an exact saved timestamp**; `—` otherwise. The presentation does not invent per-beat durations or imply parallel agents executed sequentially.
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
