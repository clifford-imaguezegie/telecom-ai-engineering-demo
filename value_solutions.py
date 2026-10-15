"""Public-facing business value and solution opportunities for TEAD AI.

Presentation only. Synthetic trace performance is derived from the nine
frozen investigation cases; suggested operator benefits and derivative
solutions are clearly identified as prospective, not measured outcomes.
"""
from html import escape
from presentation import phase_execution_ranges

BENEFITS = (
    ('Accelerated diagnosis', 'Reduce time spent manually assembling PM, event and multi-domain evidence before engineering review.'),
    ('Engineering productivity', 'Give operations teams a consistent investigation sequence and reusable specialist analysis.'),
    ('Traceable RCA decisions', 'Bring causal hypotheses, supporting observations, alternatives and evidence gaps into one reviewable assessment.'),
    ('Operational governance', 'Create a foundation for human approval, validation and policy-controlled automation before acting on a network.'),
)

SOLUTIONS = (
    ('AI-assisted incident triage', 'Network health assessment, ML-supported fault family and affected-scope identification, and conditional routing.', 'Demonstrated experimentally', 'Validate against real alarms, cases and engineering-labelled incidents.'),
    ('Multi-domain investigation copilot', 'Agent-led review of KPI, cell/peer, radio, processing, transport, configuration and CU-domain evidence.', 'Demonstrated experimentally', 'Assess domain coverage, missing evidence and engineer acceptance on operator data.'),
    ('Evidence-grounded RCA drafting', 'Supervisor synthesis of recorded agent findings, competing explanations and knowledge-based mechanism checks.', 'Demonstrated experimentally', 'Benchmark RCA quality and approval time against independent engineer reviews.'),
    ('Proactive network assurance', 'Extend network observations and predictive models towards early risk identification and preventive investigation.', 'Proposed extension', 'Build prospective monitoring, prediction lead-time and false-alarm evaluation.'),
    ('Network knowledge and evidence services', 'Provide governed retrieval, structured engineering knowledge and reusable evidence access for other workflows.', 'Proposed extension', 'Qualify corpus coverage, access controls and citation-level source sufficiency.'),
    ('Policy-governed closed-loop operations', 'Connect verified diagnosis to proposed corrective action, impact checks, approvals and controlled execution.', 'Long-term research', 'Add safe action interfaces, policy enforcement, pre/post validation and operator-authorised trials.'),
)

STYLE = """<style>
.vs-root{color:#173d52;max-width:100%}
.vs-root *{box-sizing:border-box}
.vs-lead{padding:18px 22px 19px;border:1px solid #c4dce4;border-radius:15px;background:linear-gradient(112deg,#f1fbfb,#eef7fd);margin:4px 0 14px}
.vs-eyebrow{font-size:.70rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:#257889}
.vs-lead h2{margin:6px 0 8px;font-size:1.42rem;line-height:1.24;color:#113b50;font-weight:820}
.vs-lead p{margin:0;font-size:.88rem;line-height:1.57;max-width:920px;color:#375d6d}
.vs-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:11px 0 6px}
.vs-metric{border:1px solid #c7dfe7;background:#fff;border-radius:11px;padding:12px 13px;min-width:0}
.vs-metric strong{display:block;font-size:1.37rem;line-height:1.15;font-weight:820;color:#0e5967;white-space:normal}
.vs-metric .vs-unit{font-size:.71rem;font-weight:750;color:#1e5368;margin-top:6px;line-height:1.3}
.vs-metric small{font-size:.67rem;color:#668190;line-height:1.3;display:block;margin-top:3px}
.vs-foot{font-size:.72rem;line-height:1.42;color:#5b7684;margin:7px 0 16px}
.vs-section{margin:13px 0 10px}.vs-section h3{margin:0 0 4px;font-size:1.21rem;color:#113e56}.vs-section p{margin:0;font-size:.79rem;line-height:1.5;color:#577382}
.vs-benefits{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:11px 0 20px}
.vs-benefit{border:1px solid #d4e4e9;background:#f8fcfd;border-radius:12px;padding:14px 16px}
.vs-benefit b{display:block;color:#175868;font-size:.88rem;margin-bottom:5px}
.vs-benefit p{margin:0;color:#456b78;font-size:.77rem;line-height:1.49}
.vs-solutions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin:10px 0 16px}
.vs-solution{min-width:0;border:1px solid #cbdfe7;border-radius:12px;background:#fff;padding:15px;display:flex;flex-direction:column;gap:7px}
.vs-solution h4{font-size:.88rem;margin:0;color:#133f55;line-height:1.28;font-weight:810}
.vs-solution p{font-size:.74rem;line-height:1.48;margin:0;color:#496a79;flex:1}
.vs-status{font-size:.65rem;font-weight:800;border-radius:6px;padding:5px 7px;align-self:flex-start;color:#125c4f;background:#e5f8ee;border:1px solid #b5dfcc}
.vs-status.proposed{color:#70551f;background:#fdf4de;border-color:#efdca8}
.vs-status.future{color:#605484;background:#f3f0fd;border-color:#dcd3f3}
.vs-next{border-top:1px solid #deebee;padding-top:7px;font-size:.68rem!important;color:#607987!important}
.vs-path{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin:11px 0 16px}
.vs-step{background:#edf7fa;border:1px solid #cce0e8;border-radius:10px;padding:12px}
.vs-step b{font-size:.78rem;color:#1c5667;display:block;margin-bottom:4px}.vs-step p{font-size:.72rem;line-height:1.42;color:#4f6e7b;margin:0}
.vs-caution{font-size:.72rem;line-height:1.5;color:#5b7480;border-top:1px solid #d0e2e8;padding:11px 0;margin-top:8px}
@media(max-width:1000px){.vs-solutions{grid-template-columns:repeat(2,minmax(0,1fr))}.vs-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.vs-lead{padding:14px}.vs-lead h2{font-size:1.18rem}.vs-metric strong{font-size:1.13rem}.vs-benefits,.vs-solutions,.vs-path{grid-template-columns:1fr}.vs-metrics{gap:7px}.vs-metric{padding:10px}}
</style>"""


def _duration(seconds):
    n = round(float(seconds))
    return f'{n//60}m {n%60:02d}s'


def page_html(cases):
    """Render solely from documented outcomes; never extrapolate production savings."""
    cases = list(cases)
    spans = phase_execution_ranges(cases)
    sp = spans['sp01']
    incidents = spans['incident']
    if not sp or not incidents:
        raise ValueError('Trace-backed SP01 and incident phase measurements are required')
    n_incident = incidents['count']
    n_healthy = len(cases)-n_incident
    cards = (
        (f'{sp["min"]:.1f}–{sp["max"]:.1f}s', 'Network health assessment', f'{sp["count"]}/{len(cases)} trace-backed SP01 stages'),
        (f'{_duration(incidents["min"])}–{_duration(incidents["max"])}', 'Investigation + draft RCA', f'{n_incident}/{n_incident} recorded incidents'),
        (str(len(cases)), 'Experimental recordings', f'{n_incident} incidents + {n_healthy} healthy control'),
        ('98.7%', 'CU evidence payload reduction', 'Separate representation-size experiment; not a token or cost metric'),
    )
    metrics = ''.join('<div class="vs-metric"><strong>'+escape(val)+'</strong><div class="vs-unit">'+escape(name)+'</div><small>'+escape(note)+'</small></div>' for val,name,note in cards)
    benefits = ''.join('<div class="vs-benefit"><b>'+escape(title)+'</b><p>'+escape(desc)+'</p></div>' for title,desc in BENEFITS)
    solutions = ''
    for title,capability,maturity,next_step in SOLUTIONS:
        css = 'proposed' if maturity=='Proposed extension' else 'future' if maturity=='Long-term research' else ''
        solutions += ('<article class="vs-solution"><span class="vs-status '+css+'">'+escape(maturity)+'</span>'
                      '<h4>'+escape(title)+'</h4><p>'+escape(capability)+'</p>'
                      '<p class="vs-next"><b>Next validation:</b> '+escape(next_step)+'</p></article>')
    return '''<section class="vs-root" aria-label="TEAD AI Value Proposition and Solution Opportunities">
<div class="vs-lead"><div class="vs-eyebrow">Value proposition · for telecom engineering and operations</div>
<h2>From evidence-grounded investigation to operational opportunity</h2>
<p>TEAD AI combines ML-assisted localisation, conditional specialist-agent investigations and Supervisor evidence synthesis to demonstrate a faster, more structured way to investigate complex 5G network incidents. The same capabilities may enable wider network-assurance and engineering decision-support services, subject to operator-grade validation.</p></div>
<div class="vs-section"><h3>Demonstrated engineering outcomes</h3><p>Measured in completed synthetic-network experiments; these are not operator SLAs or measured reductions in production MTTR.</p></div>
<div class="vs-metrics">'''+metrics+'''</div>
<div class="vs-foot">The experimental evidence-size reduction is from development work on CU specialist evidence representation, separate from the nine final investigation timings. Formal RCA approval and operational financial benefits were not measured.</div>
<div class="vs-section"><h3>Potential operational benefits</h3><p>Benefits that operator pilots could evaluate — not savings already demonstrated in a production network.</p></div>
<div class="vs-benefits">'''+benefits+'''</div>
<div class="vs-section"><h3>Solutions enabled by the TEAD AI architecture</h3><p>Six credible applications of the reusable architecture, with maturity stated explicitly. The first three exist as experimental capabilities; the remainder require additional engineering and validation.</p></div>
<div class="vs-solutions">'''+solutions+'''</div>
<div class="vs-section"><h3>Path from demonstration to operator adoption</h3><p>Separate the completed experiment from the additional work required to establish production value.</p></div>
<div class="vs-path">
<div class="vs-step"><b>01 · Completed experimental validation</b><p>Nine synthetic recordings, inspectable evidence, conditional agent execution and draft RCA.</p></div>
<div class="vs-step"><b>02 · Controlled operator pilot</b><p>Approved data access, live adapters, engineering benchmarks, trace review, reliability and inference-cost assessment.</p></div>
<div class="vs-step"><b>03 · Governed operational rollout</b><p>Security, auditability, operator approval, resilience, integration and safe change-control verification.</p></div>
</div>
<div class="vs-caution"><b>Scope and limitations:</b> The public Streamlit application replays completed synthetic investigations; it does not run live agents or network actions. Inference economics, cost savings, MTTR improvement, formal operator RCA approval, and autonomous remediation have not been established.</div>
</section>'''


def render_page(st, cases):
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(page_html(cases), unsafe_allow_html=True)
    st.markdown('#### Explore the evidence behind these opportunities')
    st.caption('The demonstrations and technical pages remain available unchanged. The buttons navigate within the existing recorded-replay application.')
    cols=st.columns(3)
    for col,label,target in zip(cols,('Watch the investigation','Explore the network','Inspect RCA evidence'),('Guided Operations Demo','Network Overview','Root Cause Analysis')):
        with col:
            if st.button(label,key='vs_nav_'+target.replace(' ','_'),use_container_width=True):
                st.session_state['requested_page']=target
                st.rerun()
