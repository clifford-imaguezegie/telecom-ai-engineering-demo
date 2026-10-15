# TEAD AI V1.7.2 — Network Overview & Scenario Navigation

**Scope:** Presentation-only enhancement. Baseline: V1.7.1a. No changes to saved LangGraph runs, scenario data, ML outputs, RCA conclusions, model inference, network access, or authentication.

## Network Overview

- The top section now shows a topology derived **directly from the recorded SP01 `telemetry_topology` evidence**: ten modeled gNodeB sites (`SITE_001`–`SITE_010`), three logical NR cells per site (30), two CU domains, observed DU and F1 objects, CU-CP/CU-UP, E1, N2, and AMF peers.
- The recorded input does not contain a separate `gnb_id` field. “gNodeB site” is therefore explicitly a *logical presentation label*, not an invented managed-object ID. The 30 CU-cell and 30 DU-cell objects are two management representations of **30 logical cells**, not 60 distinct cells. All nine frozen scenarios have an identical topology entity inventory.
- Network Overview now prioritizes the common synthetic-network structure, evidence categories, and a **nine-agent capability matrix (SP01–SP08 and Supervisor)** using tools actually observed across all nine saved investigations.
- Public-facing labels describe tool responsibilities without exposing prompts, credentials, or private knowledge passages. A collapsed table contains exact recorded tool IDs for research provenance.
- High-level copy uses **PM telemetry** without implying an observation window of only 15 minutes. The actual PM reporting interval remains in Engineering Evidence and recorded metadata, where it has an unambiguous technical meaning.

## Scenario Library and Guided Operations

- Moves the selected-case accessibility chart, cross-case portfolio, and curated-knowledge contribution from Network Overview to **Scenario Library**. Recorded chart values and selected trace identities remain unmodified.
- **Guided Operations Demo** explicitly directs visitors to **Select scenario ▾** in the sidebar to inspect another frozen investigation, without implying a new live run.
- **Agentic Replay** now explains its distinct purpose as a deep technical inspection of original saved agent/tool stages rather than a second guided narrative.

## Validation

- **257 local pytest checks passed** (including five new source-grounding/navigation tests).
- **136 of 136 recorded data files byte-identical** to baseline.
- Chromium **component-only** previews at 1366×768, 1440×900 and 390×844; all 10 sites and 30 cell tiles render without horizontal overflow. Mobile network graph stacks vertically.
- Existing deprecation warning in `tests/test_v162_oneframe_architecture.py` for regex `\d` remains non-blocking.
- **Not** a full hosted Streamlit browser acceptance test. Validate the live site after pushing.

## Files to deploy

- `app.py`
- `network_overview.py` (new)
- `tests/test_v172_network_context.py` (new)
- `V1_7_2_RELEASE_NOTES.md` (this file)

Do not replace `README.md`, `data/`, or other tests or Python modules. The new `app.py` imports `network_overview.py`; both must be deployed in the same commit.
