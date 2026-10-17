# TEAD AI V1.7.5 RC2 — Independent Regression Follow-up

**Status:** release candidate for independent live-browser retest. NOT signed off for unrestricted self-guided public use or experimental V1 closeout.

**Starting point:** V1.7.5 RC1; 18/18 Guided autoplay journeys passed independently, original R01 CU-5QI reproduction corrected. Protected human GO rollback: V1.7.4, commit `4c63d230b7c41b6f46f372992dcb73d3d4878a02`.

## Code changes

- **R02 recovery:** Handle Guided Operations Restart using a Streamlit `on_click` callback (runs before drawing controls). Rebuild the player as a new state object; zero old slider state; allocate a new seek generation; reject stale callbacks from retired seek widgets. The explicit Restart control triggers a full-app rerun instead of fragment-only rerun. Playback pacing survives reset, while scene, watch time, completion, awaiting evidence and Play state restart from Ready. This design addresses the particular stale-finished-screen mechanism suspected from the independent browser observations but is not yet certified in Streamlit Cloud.
- **R08 navigation:** Mark workspace-radio and programmatic page changes. On the next destination render, a one-time zero-height, read-only HTML component attempts to reset the Streamlit scroll container and window to the top. Browsers with restrictive iframe parent access may ignore it; direct live testing is required. No URLs, source data or credentials enter this component.
- **R01 assurance:** Retain the original series-aware CU measurement renderer; add negative fixtures for incomplete 5QI identity and contradictory dimension keys. The existing nine-record audit still checks 1,120 duplicate-timestamp source groups, 3,360 partitioned series and 53,760 preserved observations. No source evidence is changed.
- **Visible release ID:** update V1.7.5 RC2 in `release_identity.py`; the displayed build fingerprint regenerates deterministically from the shipped application source.

## Local validation

- **289/289 tests passed in separated file groups**: 142 + 52 + 40 + 44 + 11. A monolithic pytest invocation exceeded the execution limit in the evaluation container; no monolithic pass is claimed.
- Source payloads, cases, saved tool evidence, LangSmith traces, model conclusions and the nine replay outcomes are unchanged.
- No live Streamlit acceptance, mobile test or original field-level judge recomputation has yet been completed for RC2.

## Final independent acceptance remains mandatory

1. Repeat R02 on Healthy, Congestion A and CU Processing, Executive and Engineering, at end + intermediate scenes, Jump open/closed, at least five consecutive resets per tested combination.
2. Confirm R08 navigation across all nine pages after scrolling low in the previous page; heading and selected scenario must be visible upon arrival.
3. Run exact 1366x768, 1440x900 and 390x844 screenshots where actual browser viewport control exists, and full critical UI journeys.
4. Retain R01 source-wide and negative-case acceptance evidence; recognize the published judge percentages as non-independent until R07 can be recomputed or a formal scope deferral is accepted.
5. Do not merge Live Retrieval development into replay `main` until separately designed, secured, evaluated and approved.
