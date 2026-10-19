"""TEAD AI presentation-only Network Observatory visitor experience.

No model calls, network requests, telemetry changes, case mutations or
assumptions about unobserved operational savings. Designed to be imported by
app.py while all original nine workspaces and recorded evidence remain intact.
"""
from html import escape

OBSERVATORY_CSS = r"""<style>
:root{--ob-navy:#0c1630;--ob-deep:#111f43;--ob-blue:#3557e9;--ob-lime:#c9f271;--ob-ice:#8ddcf0;--ob-cloud:#f4f6fb;--ob-ink:#14213e}
/* Theme: midnight observatory, electric cobalt and lime. No cream, plum or coral. */
.block-container{padding-top:2.35rem!important;max-width:1450px}
[data-testid="stSidebar"]{background:#0c1630!important;color:#f2f6ff!important}
[data-testid="stSidebar"] :is(h1,h2,h3,p,label,span){color:#e5edfc}
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#172854!important;border-color:#5c7cff!important}
[data-testid="stSidebar"] [data-baseweb="select"]:focus-within>div{outline:2px solid #c9f271!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){background:rgba(201,242,113,.10);border-radius:7px}
.hero{background:linear-gradient(118deg,#0b1634,#233f91)!important;border-color:#4265bc!important;border-radius:20px!important;box-shadow:0 16px 38px rgba(12,22,48,.13)}
.hero .eyebrow{color:#c9f271!important}.hero .sub{color:#d4e3ff!important}
.ops-hero{background:linear-gradient(115deg,#101c3c,#233f91)!important;border-color:#4168bb!important}
.ops-compact,.ops-stage{background:#13234a!important;border-color:#3d57a4!important}
.ops-milestone{background:#fff!important;border-color:#c7d3ed!important;border-radius:15px!important}
.ops-milestone .number{color:#3557e9!important}
.ops-value{background:#eef3ff!important;border-color:#b7c7f0!important;color:#152b59!important}
.ops-value p{color:#415579!important}
.tead-oneframe,.tead-flow{border-color:#c0cdec!important;box-shadow:0 9px 26px rgba(34,50,94,.07)!important}
.tead-performance-card,.tead-lesson{border-radius:13px!important}
[data-testid="stButton"] button[kind="primary"]{background:#3557e9!important;color:#fff!important;border:1px solid #3557e9!important;border-radius:11px!important}
[data-testid="stButton"] button[kind="primary"]:hover{background:#213fb9!important}
[data-testid="stButton"] button{border-radius:11px!important}
.hero:has(> .ob-root > .ob-hero){background:transparent!important;border:0!important;padding:0!important;box-shadow:none!important;margin:0!important}
.ob-product-name{font-size:.86rem;line-height:1.4;letter-spacing:.02em;color:#dce9ff;font-weight:740;margin:9px 0 0}
.ob-root{font-family:inherit;color:var(--ob-ink)}
.ob-root *{box-sizing:border-box}
.ob-hero{position:relative;overflow:hidden;border-radius:23px;background:radial-gradient(circle at 86% 15%,rgba(80,106,249,.50),transparent 34%),linear-gradient(125deg,#0c1630 0%,#172956 64%,#1a367e 100%);padding:clamp(24px,3.6vw,52px);color:#fff;border:1px solid #2f4990;min-height:280px;box-shadow:0 20px 45px rgba(12,22,48,.17)}
.ob-hero:after{content:'';position:absolute;inset:0;pointer-events:none;opacity:.24;background-image:linear-gradient(rgba(144,170,250,.20) 1px,transparent 1px),linear-gradient(90deg,rgba(144,170,250,.20) 1px,transparent 1px);background-size:34px 34px;mask-image:linear-gradient(90deg,transparent,black)}
.ob-hero>*{position:relative;z-index:1}
.ob-eyebrow{display:inline-flex;align-items:center;gap:7px;text-transform:uppercase;letter-spacing:.15em;font-weight:800;font-size:.70rem;color:#d3ed9d}
.ob-eyebrow .ob-dot{width:8px;height:8px;border-radius:50%;background:#c9f271;box-shadow:0 0 0 4px rgba(201,242,113,.15)}
.ob-hero h1{font-size:clamp(2.15rem,3.7vw,3.55rem);color:#fff;letter-spacing:-.045em;line-height:1.09;max-width:920px;margin:17px 0 13px;font-weight:800}
.ob-hero h1 em{font-style:normal;color:#c9f271}
.ob-lead{max-width:780px;line-height:1.64;color:#d8e4fa;font-size:1.02rem}
.ob-hero-foot{display:flex;flex-wrap:wrap;gap:9px;margin-top:23px}
.ob-hero-foot span{border:1px solid rgba(175,197,246,.38);border-radius:50px;padding:7px 11px;background:rgba(255,255,255,.07);font-size:.78rem;color:#f3f7ff}
.ob-section{margin:25px 0 12px}
.ob-kicker{font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;font-weight:800;color:#3557e9}
.ob-section h2{font-size:clamp(1.45rem,2.1vw,2rem);font-weight:800;line-height:1.18;letter-spacing:-.035em;margin:6px 0 8px;color:#172447}
.ob-intro{font-size:.92rem;line-height:1.6;color:#4a5c7d;max-width:860px}
.ob-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:11px;margin:14px 0 23px}
.ob-card{background:#fff;border:1px solid #cdd8ee;border-radius:15px;padding:18px 17px;min-width:0;box-shadow:0 5px 17px rgba(26,44,94,.045)}
.ob-card .ob-index{font-size:.68rem;letter-spacing:.13em;color:#3557e9;font-weight:850}
.ob-card h3{font-size:1.05rem;color:#1c2e58;margin:8px 0 6px;line-height:1.25}
.ob-card p{font-size:.82rem;line-height:1.54;color:#4d607d;margin:0}
.ob-card.accent{background:#112046;border-color:#293e7b}.ob-card.accent h3{color:#c9f271}.ob-card.accent p{color:#d7e1f3}.ob-card.accent .ob-index{color:#98aef6}
.ob-flow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin:15px 0 12px}
.ob-step{position:relative;background:#eef2fe;border:1px solid #cad5f5;border-radius:13px;padding:14px 15px;min-width:0}
.ob-step:not(:last-child):after{content:'→';position:absolute;right:-13px;top:calc(50% - 13px);z-index:2;color:#3557e9;background:#f4f6fb;padding:1px 3px;font-size:1.2rem;font-weight:900}
.ob-step b{font-size:.90rem;display:block;color:#1d3473;line-height:1.35}.ob-step p{font-size:.77rem;line-height:1.4;margin:5px 0 0;color:#556884}
.ob-branches{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 6px}
.ob-branches span{border-radius:9px;padding:8px 11px;background:#e5eefa;color:#203f7d;font-size:.78rem;font-weight:700;border:1px solid #c9d6ee}
.ob-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin:15px 0 10px}
.ob-stat{padding:17px 18px;background:#fff;border:1px solid #cad5ea;border-top:4px solid #3557e9;border-radius:13px}
.ob-stat b{display:block;font-size:1.7rem;letter-spacing:-.045em;line-height:1.2;color:#112557}
.ob-stat span{display:block;font-size:.77rem;line-height:1.5;color:#506483;margin-top:6px}
.ob-boundary{margin:12px 0 19px;border-left:4px solid #3557e9;padding:11px 14px;background:#e8effd;border-radius:0 9px 9px 0;font-size:.79rem;color:#344b77;line-height:1.5}
.ob-final{margin:22px 0 14px;background:#112046;border-radius:16px;padding:18px 20px;border:1px solid #304b8d;color:#e5ebf8}
.ob-final strong{display:block;color:#c9f271;font-size:.92rem;margin-bottom:6px}
.ob-final p{margin:0;font-size:.83rem;line-height:1.55}
@media(max-width:990px){.ob-grid,.ob-flow{grid-template-columns:repeat(2,minmax(0,1fr))}.ob-step:after{display:none}}
@media(max-width:600px){.ob-grid,.ob-flow,.ob-metrics{grid-template-columns:1fr}.ob-hero{border-radius:16px;padding:22px}.ob-hero h1{font-size:2.03rem}.ob-hero-foot span{font-size:.72rem}.ob-card{padding:15px}}
</style>"""


def render_observatory_home(st, cases):
    """Plain-English orientation derived only from saved case metadata."""
    total = len(cases)
    incidents = sum(bool(c.get('derived_display', {}).get('incident_present')) for c in cases)
    healthy = total - incidents
    st.markdown('''<div class="hero"><div class="ob-root"><section class="ob-hero">
      <div class="ob-eyebrow"><span class="ob-dot"></span> TEAD AI / NETWORK INVESTIGATION &amp; RCA</div>
      <div class="ob-product-name">TEAD AI — Agentic Telecom Network Investigation &amp; Root Cause Analysis</div>
      <h1>Network incidents are complex.<br><em>The diagnosis should be clear.</em></h1>
      <div class="ob-lead">When 5G performance degrades, engineers must bring together symptoms, events,
      radio conditions, network resources and specialist knowledge. TEAD AI explores how
      machine-learning-assisted localisation and coordinated AI agents can produce
      a traceable Root Cause Analysis (RCA) for engineering review.</div>
      <div class="ob-hero-foot"><span>Recorded agent investigations</span><span>Evidence-led analysis</span><span>No network actions executed</span></div>
    </section></div></div>''', unsafe_allow_html=True)
    if st.button('▶ Watch a recorded network investigation',type='primary',use_container_width=True,key='tead_hero_watch'):
        st.session_state['selected_scenario']='M05I0003'
        st.session_state['requested_page']='Guided Operations Demo'
        st.rerun()
    st.caption('Start with a representative recorded congestion investigation. Other recorded cases are selectable in the sidebar.')
    st.markdown('''<div class="ob-root"><div class="ob-section"><div class="ob-kicker">01 / THE OPERATIONAL CHALLENGE</div>
      <h2>Getting from an alarm to a defensible diagnosis takes work.</h2>
      <p class="ob-intro">A network problem can span multiple domains. The difficult part is correlating observations,
      eliminating competing explanations, finding the affected scope and documenting why a root cause is plausible.</p>
      </div><div class="ob-grid">
      <div class="ob-card"><div class="ob-index">01 / TRIAGE</div><h3>Identify what matters</h3><p>Distinguish healthy conditions from a material incident before expensive investigation.</p></div>
      <div class="ob-card"><div class="ob-index">02 / LOCALISE</div><h3>Find the affected scope</h3><p>Combine ML predictions with recorded performance and event evidence to locate the suspected domain.</p></div>
      <div class="ob-card"><div class="ob-index">03 / INVESTIGATE</div><h3>Cross-check the evidence</h3><p>Use appropriate specialists to examine KPI, radio, transport, processing, configuration and CU evidence.</p></div>
      <div class="ob-card accent"><div class="ob-index">04 / EXPLAIN</div><h3>Produce a reviewable RCA</h3><p>Bring findings, competing explanations and uncertainties into a Supervisor-led engineering conclusion.</p></div>
      </div></div>''', unsafe_allow_html=True)
    st.markdown('''<div class="ob-root"><div class="ob-section"><div class="ob-kicker">02 / THE AGENTIC JOURNEY</div>
      <h2>One investigation. The right specialists. A traceable answer.</h2></div>
      <div class="ob-flow">
      <div class="ob-step"><b>1. Assess health</b><p>SP01 uses two ML prediction tools alongside network and event telemetry.</p></div>
      <div class="ob-step"><b>2. Choose the route</b><p>Healthy, cell/site and Central Unit (CU) cases do not follow the same path.</p></div>
      <div class="ob-step"><b>3. Investigate the cause</b><p>Sequential domain specialists or the CU specialist examine supporting and competing evidence.</p></div>
      <div class="ob-step"><b>4. Form the RCA</b><p>The Supervisor synthesises findings, domain knowledge and remaining uncertainties.</p></div>
      </div><div class="ob-branches"><span>Healthy → direct Supervisor review</span><span>Cell/site → SP02–SP07</span><span>CU domain → SP08</span></div>
    </div>''', unsafe_allow_html=True)
    st.markdown('''<div class="ob-root"><div class="ob-section"><div class="ob-kicker">03 / POTENTIAL OPERATOR VALUE</div>
       <h2>Designed to support better-informed engineering decisions.</h2>
       <p class="ob-intro">The intended value is shorter evidence-assembly effort, more consistent investigation practice,
       knowledge reuse and better-supported handovers. These benefits remain to be measured against real operator workflows.</p></div>
       </div>''', unsafe_allow_html=True)
    st.markdown('''<div class="ob-root"><div class="ob-grid">
      <div class="ob-card"><div class="ob-index">A / DECISION SUPPORT</div><h3>Earlier triage</h3><p>Help engineers prioritise an investigation with a recorded health and scope assessment.</p></div>
      <div class="ob-card"><div class="ob-index">B / EFFORT</div><h3>Less fragmented analysis</h3><p>Bring several domain observations into a coordinated specialist workflow.</p></div>
      <div class="ob-card"><div class="ob-index">C / ENGINEERING QUALITY</div><h3>More reviewable conclusions</h3><p>Show the reasoning trail, supporting measurements, alternatives and evidence gaps.</p></div>
      <div class="ob-card"><div class="ob-index">D / KNOWLEDGE</div><h3>Reusable expertise</h3><p>Make curated mechanisms and specialist methods accessible within investigations.</p></div>
      </div></div>''', unsafe_allow_html=True)
    st.markdown(f'''<div class="ob-root"><div class="ob-section"><div class="ob-kicker">04 / RECORDED PROOF OF CONCEPT</div>
      <h2>Explore the original evidence, not a live simulation.</h2></div><div class="ob-metrics">
      <div class="ob-stat"><b>{total}</b><span>Independent recorded synthetic-network scenarios ({incidents} incidents, {healthy} healthy control).</span></div>
      <div class="ob-stat"><b>&lt; 25 sec</b><span>Observed initial health and affected-scope assessment across the saved cases.</span></div>
      <div class="ob-stat"><b>&lt; 5 min</b><span>Observed full RCA completion for the recorded incident cases.</span></div>
      </div><div class="ob-boundary">All timings are experimental, derived from saved executions. The public app runs no agents, sends no network commands and does not demonstrate production MTTR reductions or cost savings.</div></div>''', unsafe_allow_html=True)
