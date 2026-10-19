"""TEAD AI visitor experience — Candidate 4.2; evidence-grounded replay.

Preserves the accepted seven-page presentation, recorded investigation routes,
and frozen experimental evidence without executing network actions or models.
"""
from __future__ import annotations

from html import escape
import re
from pathlib import Path
import json

from presentation import format_duration, phase_execution_ranges

from ec_clarity_experience import (AGENT_NAMES, ROUTE_NAMES, JOIN_IDS,
                                   agent_stages, case_story_steps)

STYLE_PATH=Path(__file__).with_name('ec_reference_style.css')
REFERENCE_CSS=STYLE_PATH.read_text(encoding='utf-8')
EXTRAS='''<style>
/* Only the seven new visitor workspaces receive the reference treatment. */
.ec-ref-header{max-width:100%;}
.ec-ref-footer{margin-top:28px;}
.ec-ref-insight{background:#fff;border:1px solid #eadbd3;padding:16px 19px;border-radius:13px;margin:13px 0;color:#493848;line-height:1.6}
.ec-ref-insight b{color:#38243f}
.ec-ref-route{font-size:.82rem;color:#7a556e;margin:9px 0 14px}
.ec-ref-badge{display:inline-block;padding:4px 9px;border-radius:7px;background:#f9e7dd;color:#703e4f;font-size:.72rem;font-weight:750}
.ec-ref-map-note{color:#735f6e;font-size:.81rem;margin:10px 0 18px}
/* Navigation as in E/C, placed after brand and before page hero. */
[data-testid="stHorizontalBlock"] .stRadio [role="radiogroup"]{flex-wrap:wrap}
/* Override original TEAD/Network Observatory title and sidebar theme. */
[data-testid="stAppViewContainer"],.stApp{background:#FFF9F2!important;color:#291D2D!important}
[data-testid="stSidebar"]{background:#FFF9F2!important}
[data-testid="stSidebar"] :is(h1,h2,h3,p,label){color:#463449!important}
[data-testid="stSidebar"] [data-baseweb="select"] > div{background:#fff!important;border-color:#EBDDD3!important}
[data-testid="stSidebar"] [data-baseweb="select"] :is(div,span,input){color:#291D2D!important;-webkit-text-fill-color:#291D2D!important}
[data-testid="stSidebar"] [data-baseweb="select"] svg{fill:#291D2D!important;color:#291D2D!important}
.ec-ref-flow .shell{border:1px solid #e9d8cb;border-radius:19px;background:#fffbf6;overflow:hidden;color:#291d2d;font-family:Segoe UI,system-ui,sans-serif}
.ec-ref-flow .toolbar{padding:15px 17px;display:flex;align-items:center;justify-content:space-between;gap:12px;background:#321e3d;color:#fef7f3;flex-wrap:wrap}
.ec-ref-flow .toolbar .name{font-weight:800;font-size:14px}
.ec-ref-flow .buttons{display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.ec-ref-flow button,.ec-ref-flow select{border:1px solid #cdb8c9;border-radius:9px;background:#fff;padding:8px 10px;color:#422b47;font-size:12px;font-weight:700;cursor:pointer}
.ec-ref-flow button.primary{background:#ed6848;border-color:#ed6848;color:#fff}
.ec-ref-flow button:disabled{opacity:.45;cursor:default}
.ec-ref-flow .graphwrap{overflow-x:auto;padding:18px 15px 10px;background:linear-gradient(135deg,#fffcf9,#fff6ef)}
.ec-ref-flow .graph{position:relative;width:100%;min-width:580px;height:265px;margin:auto}
.ec-ref-flow .edges{position:absolute;width:100%;height:100%;inset:0;overflow:visible}
.ec-ref-flow .edge{fill:none;stroke:#c9b5c3;stroke-width:2.5;stroke-dasharray:5 5;opacity:.95}
.ec-ref-flow .travel{fill:none;stroke:#ef6d4b;stroke-width:4}
.ec-ref-flow .orb{fill:#ef6d4b;stroke:#fff;stroke-width:3;filter:drop-shadow(0 1px 5px #ef6d4b77)}
.ec-ref-flow .node{position:absolute;transform:translate(-50%,-50%);width:17%;max-width:166px;min-width:96px;min-height:74px;padding:10px 7px;border:2px solid #dfd1df;border-radius:12px;background:#fff;text-align:center;display:flex;flex-direction:column;justify-content:center;box-sizing:border-box}
.ec-ref-flow .node .id{font-size:13px;font-weight:850;color:#34203c}
.ec-ref-flow .node .nm{font-size:10px;line-height:1.25;color:#6e5b70;margin-top:5px}
.ec-ref-flow .node.active{border-color:#ed6848;background:#fff0e6;box-shadow:0 0 20px #ed684844}
.ec-ref-flow .node.done{border-color:#91ad93;background:#f5fbf3}
.ec-ref-flow .node.pending{opacity:.65}
.ec-ref-flow .progress{height:5px;background:#e6d7dc}.ec-ref-flow .fill{height:100%;background:#ed6848;width:0%}
.ec-ref-flow .bottom{display:grid;grid-template-columns:1.1fr .9fr;min-height:215px}
.ec-ref-flow .panel{padding:19px 23px;min-width:0;overflow-wrap:anywhere}
.ec-ref-flow .panel + .panel{border-left:1px solid #e9d8cb;background:#fff}
.ec-ref-flow .kicker{color:#a4554b;font-size:10px;letter-spacing:.15em;font-weight:850;margin-bottom:8px}
.ec-ref-flow .out-title{font-size:17px;font-weight:800;margin-bottom:7px;color:#38223f}
.ec-ref-flow .stage-time{font-size:12px;font-weight:750;color:#A4554B;margin:0 0 10px}
.ec-ref-flow .out-line{font-size:13px;color:#4f4052;line-height:1.55;max-height:106px;overflow-y:auto}
.ec-ref-flow .evidence-note{font-size:12px;line-height:1.5;background:#fff1e7;border-left:3px solid #df795b;padding:8px 10px;margin-top:11px;max-height:135px;overflow-y:auto}
.ec-ref-flow .history{max-height:178px;overflow-y:auto;font-size:12px;line-height:1.5;color:#655568}
.ec-ref-flow .history div{padding:4px 0;border-bottom:1px solid #f1e9ee}
.ec-ref-flow .status{display:flex;flex-wrap:wrap;gap:7px 18px;padding:11px 21px;background:#fff0e2;border-top:1px solid #e9d8cb;font-size:12px;color:#594653}
.ec-ref-flow .disclaimer{font-size:11px;line-height:1.55;color:#88748a;padding:12px 20px;background:#fffbf7;border-top:1px solid #ede0df}
.ec-ref-flow .inspector{margin:0 15px 15px;padding:12px 16px;background:#fff;border:1px solid #e9d8cb;border-radius:12px}
.ec-ref-flow .inspector summary{font-size:12px;font-weight:800;cursor:pointer;color:#422b47}
.ec-ref-flow .inspector-item{border-top:1px solid #f0e7ec;padding:10px 0;color:#463749;font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere}
/* Preserve the same E/C colours inside the original telecom topology widget. */
.net-inventory .net-domain,.net-inventory .net-site,.net-inventory .net-summary{background:#FFFBF6!important;border-color:#EBDDD3!important;color:#291D2D!important}
.net-inventory .net-domain-head,.net-inventory .net-path,.net-inventory .net-domain-nodes span{background:#FFF0E5!important;border-color:#EBDDD3!important;color:#4D2C4B!important}
.net-inventory :is(h2,h3,strong,b){color:#34203C!important}
.net-inventory .net-summary b{color:#AD4C39!important}
.net-inventory .net-domain-connector{color:#A05245!important}
@media(max-width:700px){.ec-ref-flow .bottom{display:block}.ec-ref-flow .panel+.panel{border-left:0;border-top:1px solid #e9d8cb}.ec-ref-flow .toolbar{padding:11px}.ec-ref-flow .node{min-width:85px}.ec-ref-flow .panel{padding:13px 16px}}
@media(prefers-reduced-motion: reduce){.ec-ref-flow .node,.ec-ref-flow .orb{transition:none}}
</style>'''


def h(v):return escape(str(v), quote=True)

def brand(st):
    st.markdown('''<div class="brand ec-ref-header"><div class="brandmark"><span class="brandicon">T</span><span>TEAD AI<br><span style="font-size:.67rem;color:#897581;font-weight:500;letter-spacing:.05em">AGENTIC TELECOM NETWORK INVESTIGATION &amp; RCA</span></span></div><div class="brandright">PROOF OF CONCEPT &nbsp; / &nbsp; RECORDED REPLAY &nbsp; / &nbsp; 2026</div></div>''',unsafe_allow_html=True)


def hero(st,kicker,title,subtitle):
    st.markdown(f'<section class="hero"><div class="eyebrow">{h(kicker)}</div><h1>{h(title)}</h1><p class="lead">{h(subtitle)}</p></section>',unsafe_allow_html=True)


def heading(st,kicker,title):
    st.markdown(f'<div class="section-eyebrow">{h(kicker)}</div><div class="section-title">{h(title)}</div>',unsafe_allow_html=True)


def card(st,num,title,description):
    st.markdown(f'<div class="card"><div class="number">{h(num)}</div><h3>{h(title)}</h3><p>{h(description)}</p></div>',unsafe_allow_html=True)


def boundary(st):
    """One transparent description of provenance, without repeated disclaimer panels."""
    st.markdown('<div class="feature"><strong>Behind this demonstration:</strong> The AI agents completed nine investigations using synthetic 5G Radio Access Network (RAN) data. Their LangSmith execution traces, engineering measurements and RCA findings were captured at the time. This interactive experience brings those real recorded analyses to life for inspection; the public viewer does not rerun them.</div>',unsafe_allow_html=True)


def recorded_times(case):
    """Two distinct source times: SP01 agent duration and whole completed RCA trace.

    These are not additive. The RCA clock is intentionally labelled as
    end-to-end investigation time rather than claiming it is an isolated
    Supervisor inference span or a measured production fault-resolution time.
    """
    nodes=case.get('observed_nodes') or []
    node=next((n for n in nodes if n.get('name')=='SP01'
               and n.get('run_type')=='chain' and n.get('depth')==1
               and isinstance(n.get('duration_seconds'),(int,float))),None)
    sp01_seconds=float(node['duration_seconds']) if node is not None else None
    total=case.get('trace_duration_seconds')
    total_seconds=float(total) if isinstance(total,(int,float)) else None
    incident=bool((case.get('derived_display') or {}).get('incident_present',
                  case.get('incident_present',False)))
    return {
      'incident':incident,
      'localisation_seconds':sp01_seconds,
      'localisation_text':format_duration(sp01_seconds),
      'localisation_label':'Fault localisation (SP01)' if incident else 'Network health assessment (SP01)',
      'rca_seconds':total_seconds,
      'rca_text':format_duration(total_seconds),
      'rca_label':'Root-cause assessment (end-to-end)' if incident else 'Completed healthy review (end-to-end)',
    }


def challenge(st,cases):
    hero(st,'The challenge / 5G RAN network investigation',
         'From network degradation to an evidence-grounded root cause.',
         'Across a 5G Radio Access Network (RAN), accessibility symptoms can originate in radio, processing, transport or configuration. TEAD AI shows how machine learning and coordinated specialist AI agents investigate the network, localise the problem and build a defensible Root Cause Analysis (RCA).')
    heading(st,'01 / THE OPERATIONAL FRICTION','Why network incidents take time to investigate')
    cols=st.columns(3,gap='medium')
    problems=[
      ('01 — SIGNAL','Find the affected scope','Across 10 sites and 30 cells, performance observations and events may point to different affected objects. Not every anomaly warrants a specialist investigation.'),
      ('02 — CAUSE','Distinguish symptoms from causes','Congestion, radio impairments, processing pressure, transport disruption and configuration can produce overlapping network symptoms.'),
      ('03 — TRUST','Defend the conclusion','An operator needs more than a fault label: supporting measurements, competing hypotheses, scope, uncertainty and a traceable diagnosis.')
    ]
    for col,detail in zip(cols,problems):
        with col:card(st,*detail)
    heading(st,'02 / THE SOLUTION','A coordinated network investigation—not an AI dashboard')
    a,b=st.columns([1.06,.94],gap='large')
    with a:
        st.markdown('The implemented 5G RAN workflow brings together **network performance measurements, event telemetry, machine-learning predictions and domain-specific AI investigations**. It establishes affected network scope, follows the relevant engineering evidence and synthesises a traceable RCA.')
        st.markdown('For a network operations team, this means an opportunity for **faster diagnosis, more consistent cross-domain investigations, less manual evidence correlation and better-supported engineering decisions**. Production efficiency benefits can be quantified in a future operator pilot.')
    with b:
        st.markdown('''<div class="card" style="background:#FFF0E5;border-color:#EDCEBD;min-height:200px"><div class="number">THE OPERATING PRINCIPLE</div><h3 style="font-size:1.3rem">Establish the signal.<br>Follow the evidence.<br>Explain the cause.</h3><p>The investigation localises the network issue, directs specialist review to the relevant domain, and ends with an evidence-grounded assessment that engineers can inspect.</p></div>''',unsafe_allow_html=True)
    heading(st,'03 / OPERATIONAL VALUE','From fragmented observations to a reviewable RCA')
    st.markdown('''<div class="value-lead"><div class="value-lead-copy"><span class="value-eyebrow">WHAT NETWORK OPERATIONS COULD GAIN</span><p>Without a connected diagnostic workflow, evidence must be assembled and reinterpreted across functions. TEAD AI demonstrates an integrated approach to that preparation while keeping engineering judgement and action authority separate.</p></div><div class="value-bridge"><div><small>FROM</small><strong>Scattered KPIs, alarms and domain handovers</strong></div><span class="value-bridge-arrow">→</span><div><small>TO</small><strong>One evidence-backed investigation record</strong></div></div></div>''',unsafe_allow_html=True)
    cards=[
      ('01','DIAGNOSIS SPEED','Faster fault localisation','Network measurements, events and ML-supported scope assessment are correlated before deeper investigation.','Opportunity: reduce manual first-pass correlation.'),
      ('02','ENGINEERING CONSISTENCY','Repeatable investigation','Conditional routes sequence specialists for the relevant network domain.','Opportunity: reduce variation in incident assessment.'),
      ('03','DECISION TRUST','Traceable root cause','The Supervisor combines agent findings, alternative causes and missing evidence.','Opportunity: make diagnoses easier to review and challenge.'),
      ('04','KNOWLEDGE REUSE','Retain expertise','Where recorded, knowledge retrieval supports mechanism discrimination rather than replacing telemetry.','Opportunity: reuse engineering knowledge in a governed manner.'),
      ('05','OPERATIONAL GOVERNANCE','Human-controlled action','The replay documents possible assessments without controlling a real network.','Opportunity: validate recommendations before any approved action interface.')
    ]
    markup=[]
    for n,cat,title,mechanism,value in cards:
        markup.append(f'<article class="value-card"><div class="value-card-top"><span class="value-num">{h(n)}</span><span class="value-category">{h(cat)}</span></div><h3>{h(title)}</h3><p class="value-mechanism">{h(mechanism)}</p><div class="value-impact"><span>OPERATIONAL OPPORTUNITY</span><p>{h(value)}</p></div></article>')
    st.markdown('<div class="value-grid">'+''.join(markup)+'</div>',unsafe_allow_html=True)
    heading(st,'04 / RECORDED RESULTS','Completed 5G RAN investigations — measured execution')
    spans=phase_execution_ranges(list(cases))
    incident_rows=[r for r in spans['rows'] if r['incident']]
    loc_samples=[r['sp01_seconds'] for r in incident_rows if r['sp01_seconds'] is not None]
    rca_samples=[r['end_to_end_seconds'] for r in incident_rows]
    loc_label='< 25 sec' if len(loc_samples)==len(incident_rows) and loc_samples and max(loc_samples)<25 else (format_duration(max(loc_samples)) if loc_samples else '—')
    rca_label='< 5 min' if rca_samples and max(rca_samples)<300 else (format_duration(max(rca_samples)) if rca_samples else '—')
    metrics=[(loc_label,'Fault localisation','SP01 · '+str(len(loc_samples))+'/'+str(len(incident_rows))+' incident runs'),
             (rca_label,'Root-cause assessment completed','Completed end-to-end RCA · '+str(len(rca_samples))+' incidents'),
             (str(len(cases)),'Completed investigations','Eight incident cases + one healthy control'),
             ('10 / 30','5G RAN sites / cells','Two recorded CU domains')]
    cols=st.columns(4,gap='small')
    for col,(val,label,note) in zip(cols,metrics):
        with col:st.markdown(f'<div class="kpi"><div class="label">{h(label)}</div><div class="value">{h(val)}</div><div class="desc">{h(note)}</div></div>',unsafe_allow_html=True)
    st.caption('Times come from the saved LangSmith executions: localisation uses the SP01 chain duration; RCA time is the full elapsed investigation through its recorded outcome. The values are experimental measurements, not production MTTR.')
    st.markdown('<div class="feature"><strong>Start with the SITE_008 investigation:</strong> Accessibility deteriorates across three radio cells. Is this radio-resource congestion, a different radio impairment or a problem elsewhere in the network? Follow the recorded sequence from localisation to specialist assessment and the final evidence-grounded RCA. Then compare with the CU-processing case to see how the agent route changes.</div>',unsafe_allow_html=True)
    boundary(st)
    with st.expander('Where the investigation approach could add operator value',expanded=False):
        st.markdown('**Demonstrated today:** ML-assisted localisation, conditional 5G RAN investigation, recorded specialist evidence and Supervisor RCA across the nine saved experiments.')
        st.markdown('**Operator applications requiring adaptation:** historical incident investigation on operator PM/events/topology, assisted NOC ticket handover, and configuration/change assurance. Each requires approved evidence connections, vendor-specific counter mapping, private inference and independent evaluation.')
        st.markdown('**Further roadmap:** proactive triggering, wider Core correlation and controlled automation require separately evaluated models, integrations and safety controls. These are opportunities for operator discovery, not capabilities exercised by this replay.')
    a,b=st.columns(2)
    with a:
        if st.button('▶ Follow the congestion case',key='ref_challenge_story',type='primary',use_container_width=True):
            st.session_state['selected_scenario']='M05I0003';st.session_state['requested_page']='Case Stories';st.rerun()
    with b:
        if st.button('See the implemented architecture →',key='ref_challenge_arch',use_container_width=True):
            st.session_state['requested_page']='Architecture';st.rerun()


def architecture(st):
    hero(st,'Inside the system / Recorded experimental implementation',
         'One assessment. Three possible investigation routes. One accountable RCA.',
         'Follow the implemented sequence from network observations to ML-supported localisation, conditional specialist investigation and Supervisor synthesis. No invented parallel agents or revision loops.')
    heading(st,'01 / END-TO-END ARCHITECTURE','From network signals to evidence-grounded RCA')
    def row(entries):
        return '<div class="arch-row">'+''.join(f'<div class="arch-node {h(kind)}">{h(t)}<small>{h(desc)}</small></div>' for t,desc,kind in entries)+'</div>'
    parts=['<div class="arch">','<div class="layer">Network observation and engineering context</div>',row([('Radio PM and events','15-minute recorded KPI series',''),('Network topology','10 sites · 30 cells · 2 CU domains',''),('Domain evidence','Radio · processing · transport · configuration','gold')]),'<div class="arch-down">↓</div>','<div class="layer">Assessment tools and routing</div>',row([('ML tool 1','Fault-family prediction · not an agent','orange'),('SP01 Network Health & Localisation','Selects conditional recorded route','plum'),('ML tool 2','Affected-scope prediction · not an agent','orange')]),'<div class="arch-down">↓</div>','<div class="layer">Choose one conditional branch per recorded scenario</div>',row([('Healthy direct path','No specialist escalation','gold'),('Cell/site specialists','SP02 → SP03 → SP04 → SP05 → SP06 → SP07','orange'),('CU domain','SP08 only','soft')]),'<div class="arch-callout"><strong>Conditional routing:</strong> These are alternatives, not concurrent chains. SP02–SP07 execute sequentially in recorded cell/site investigations. A saved join stage consolidates the selected route before Supervisor review.</div>','<div class="arch-down">↓</div>','<div class="layer">Synthesis, knowledge and conclusions</div>',row([('Recorded findings join','Workflow consolidation · not an AI agent','gold'),('RCA Supervisor','Evidence, alternatives, RAG if recorded','plum')]),'<div class="arch-down">↓</div>',row([('Recorded RCA','Diagnosis · scope · evidence · uncertainty','orange')]),'<div class="arch-callout"><strong>Source boundary:</strong> Each event and result shown in this public experience comes from original captured synthetic-network investigations. Models and network interfaces are not running in this app.</div>','</div>']
    st.markdown(''.join(parts),unsafe_allow_html=True)
    heading(st,'02 / AGENT RESPONSIBILITIES','Why each agent exists')
    tasks=[('SP01 — Network Health & Localisation','Checks 5G RAN performance and events, calls two ML prediction tools plus network-overview and event telemetry, confirms the affected cells, sites and CU domain where supported, and selects the investigation route.'),('SP02 — KPI','Investigates accessibility KPIs and their performance components.'),('SP03 — Cell and Peer','Compares affected cells with neighbouring network observations.'),('SP04 — Radio','Checks radio state and resource pressure against the suspected incident.'),('SP05 — Processing','Examines processing utilisation and internal resource state.'),('SP06 — Transport','Reviews transport interfaces, connectivity and relevant events.'),('SP07 — Configuration','Checks recorded parameters and configuration state.'),('SP08 — CU and Boundary','Investigates CU-domain control-plane, user-plane and boundary conditions.'),('Supervisor — RCA','Integrates specialist reports, competing evidence, knowledge support and uncertainty.')]
    cols=st.columns(3,gap='medium')
    for i,(name,description) in enumerate(tasks):
        with cols[i%3]:card(st,f'{i+1:02d}',name,description)
    st.caption('ML predictors are tools invoked by SP01, not separate AI agents. The routes are conditional, not simultaneous. In the healthy control, the direct Supervisor chain closes the assessment without a separate recorded Supervisor LLM span.')


def network(st,inventory,topology_fn):
    hero(st,'The network / Recorded synthetic topology','Thirty cells. Ten sites. Two connected CU domains.',
         'Understand the network investigated by every saved case before following a diagnosis. This is a logical topology, not a live monitoring dashboard or geographic map.')
    heading(st,'01 / THE NETWORK UNDER INVESTIGATION','Recorded sites, cells and CU relationships')
    st.caption('CU-side and DU-side cell identifiers are two recorded views of the same 30 NR cells; they are not 60 separate cells.')
    st.markdown(topology_fn(inventory),unsafe_allow_html=True)
    st.markdown('<div class="ec-ref-map-note">Topology objects originate from the recorded telemetry-topology evidence. The scenarios are independent experiments sharing this inventory; no geographic position or live state is inferred.</div>',unsafe_allow_html=True)
    st.caption('One physical cell may appear through both CU-side and DU-side managed-object views. This page shows the actual recorded inventory; the agent-routing architecture is explained separately under Architecture.')


def _outcome(case):
    su=(case.get('stage_data') or {}).get('supervisor_output') or {}
    diagnosis=su.get('diagnosis') or 'No material incident supported by the recorded evidence.'
    return su,diagnosis


def _case_banner(case):
    su,diag=_outcome(case)
    status='NO MATERIAL INCIDENT' if not su.get('incident_present') else str(su.get('root_cause_family') or 'RECORDED INCIDENT').replace('_',' ')
    scope=su.get('scope_class') or case.get('route_family') or 'Not recorded'
    times=recorded_times(case)
    return (f'<div class="case-banner"><strong>{h(case.get("scenario_id","—"))} / {h(case.get("title","Recorded network investigation"))}</strong><br>'
            f'<span style="font-size:.85rem">{h(status)} &nbsp; · &nbsp; {h(scope)}</span>'
            f'<div class="ec-ref-route"><strong>{h(times["localisation_label"])}:</strong> {h(times["localisation_text"])}'
            f' &nbsp; · &nbsp; <strong>{h(times["rca_label"])}:</strong> {h(times["rca_text"])}</div></div>')


def complete_diagnosis_excerpt(value, target=335):
    """Never cut a saved diagnosis mid-sentence or silently edit its meaning."""
    text=str(value or '').strip()
    if len(text)<=target:return text
    sentences=re.split(r'(?<=[.!?])\s+',text)
    chosen=[]
    for sentence in sentences:
        candidate=' '.join(chosen+[sentence])
        if len(candidate)>target and chosen:break
        if len(candidate)>target and not chosen:
            # A single long statement is shown whole rather than misleadingly clipped.
            return sentence
        chosen.append(sentence)
    return ' '.join(chosen) if chosen else text


def investigation_opening(case, original_scene):
    """Source-backed editorial overview, not a newly inferred diagnostic event."""
    sid=case.get('scenario_id')
    reviewed={
      'M05I0003':('Accessibility deteriorated over successive recorded intervals across the three SITE_008 cells. The investigation needed to distinguish radio resource pressure from other radio, processing, transport and configuration explanations.',
                   'Recorded 5G RAN accessibility measurements for SITE_008 and its three cells; inspect the original series in Evidence Room.'),
      'M05I0005':('Several sites sharing CU_DOMAIN_01 showed a related accessibility degradation. The investigation examined whether shared CU processing or a boundary mechanism better explained the cross-site pattern.',
                   'Recorded cross-site accessibility and CU-domain observations for SITE_001–SITE_005 / CU_DOMAIN_01.'),
      'M05I0017':('The supplied 5G RAN observation window required a network health assessment. The recorded review did not establish a coherent material fault, so the direct review route was used.',
                   'Recorded health-assessment inputs and network observations; no affected fault scope was established.'),
    }
    if sid in reviewed:return reviewed[sid]
    # For other cases rely only on the saved scenario title; do not invent alarms,
    # counters, threshold breaches, affected identities or onset timing.
    name=str(case.get('title') or '5G RAN network condition')
    return (f'The completed investigation examined the recorded 5G RAN observations associated with {name.lower()}. Follow how SP01 established the supported scope, selected a specialist route and contributed to the final evidence-grounded assessment.',
            original_scene.get('evidence') or 'Original SP01 observations are available in the recorded source events.')


def causal_interpretation(case):
    """Keep original RCA intact; make confidence boundaries understandable."""
    sid=case.get('scenario_id')
    if sid=='M05I0003':
        return ('Engineering interpretation: the saved measurements support increased radio resource pressure associated with the accessibility decline. Without explicit capacity/admission limits and detailed DRB failure causes, a claim of fully exhausted resources is not independently established by those measurements.')
    if sid=='M05I0005':
        return ('Engineering interpretation: the saved CU-CP observations support a processing-pressure association across the CU domain. The initiating trigger, applicable capacity limit and granular RRC failure mechanism remain unresolved in the visible evidence.')
    return ''


def evidence_focus(case):
    """A case-specific chart target taken only from saved Supervisor object identity."""
    su=(case.get('stage_data') or {}).get('supervisor_output') or {}
    raw=su.get('target_cells') or []
    target=next((t.get('nr_cell_cu_id') for t in raw if isinstance(t,dict) and t.get('nr_cell_cu_id')),None)
    return {'scenario_id':case.get('scenario_id'),
            'entity_id':target,
            'metric':'partial_drb_accessibility_pct'}


def story(st,case,beats):
    hero(st,'The case stories / Nine recorded investigations','Follow the diagnosis. Understand why the agents were needed.',
         'Five clear chapters explain the completed 5G RAN investigation, from observed symptoms to the saved RCA. Agent Flow provides the original handovers and technical records.')
    heading(st,'01 / CHOOSE YOUR NETWORK CASE','Different incidents. Different investigative routes.')
    st.markdown(_case_banner(case),unsafe_allow_html=True)
    su,diag=_outcome(case)
    e=(su.get('supporting_evidence') or [])[:2]
    uncertainty=(su.get('residual_uncertainty') or [])[:1]
    a,b,c=st.columns(3,gap='small')
    with a:card(st,'01 / DIAGNOSIS','Recorded finding',complete_diagnosis_excerpt(diag))
    with b:card(st,'02 / SCOPE','Network impact',str(su.get('scope_class') or 'Not recorded')+' · '+', '.join((su.get('final_scope') or {}).get('affected_sites') or [])[:190])
    with c:card(st,'03 / EVIDENCE GAP','What remains uncertain',complete_diagnosis_excerpt(uncertainty[0]) if uncertainty else 'No residual uncertainty listed in the recorded final output.')
    with st.expander('Full original Supervisor diagnosis and evidence interpretation',expanded=False):
        st.write(diag)
        interpretation=causal_interpretation(case)
        if interpretation:st.info(interpretation)
        st.caption('The recorded RCA and agent decisions remain unchanged; interpretation clarifies what the displayed measurements establish.')
    scenes=case_story_steps(case,beats)
    # Editorial titles retain each scene's source-backed findings, but put them
    # into a recognisable incident-investigation story arc.
    if len(scenes)==5:
        route=case.get('route_family')
        titles=[
          'The first signal: what did the network show?' if route!='DIRECT_SUPERVISOR' else 'The first signal: is the network actually healthy?',
          'SP01 establishes the scope and chooses a route',
          ('Six specialists challenge competing explanations' if route=='LOCAL_SPECIALISTS'
            else 'A CU-domain specialist investigates the shared fault' if route=='CU_SPECIALIST'
            else 'Healthy evidence avoids an unnecessary escalation'),
          'The Supervisor weighs the evidence and alternatives',
          'The diagnosis—and what remains uncertain',
        ]
        scenes=[{**scene,'title':title} for scene,title in zip(scenes,titles)]
        # Describe the historical 5G RAN analysis positively and precisely;
        # do not repeatedly contrast every chapter with real-network operations.
        scenes[0]['summary'],scenes[0]['evidence']=investigation_opening(case,scenes[0])
    sid=case.get('scenario_id')
    key='ref_story_'+sid
    ix=max(0,min(int(st.session_state.get(key,0)),len(scenes)-1))
    current=scenes[ix]
    l,r=st.columns([1.6,1],gap='large')
    with l:
        heading(st,'02 / GUIDED STORY','Read the investigation as five decisions')
        st.markdown(f'<div class="scene"><div class="chapter">{h(current["label"])} &nbsp; · &nbsp; CHAPTER {ix+1} OF {len(scenes)}</div><h2>{h(current["title"])}</h2><p>{h(current["summary"])}</p><div class="scenefoot">EDITED FROM SAVED RECORDS · ORIGINAL AGENT OUTPUTS IN AGENT FLOW</div></div>',unsafe_allow_html=True)
        a,b,c=st.columns(3)
        with a:
            if st.button('↺ First chapter',key='ref_story_first',disabled=ix==0,use_container_width=True):st.session_state[key]=0;st.rerun()
        with b:
            if st.button('← Back',key='ref_story_back',disabled=ix==0,use_container_width=True):st.session_state[key]=ix-1;st.rerun()
        with c:
            if st.button('Next chapter →',key='ref_story_next',disabled=ix>=len(scenes)-1,use_container_width=True,type='primary'):st.session_state[key]=ix+1;st.rerun()
        st.progress((ix+1)/len(scenes),text=f'Guided story: chapter {ix+1} of {len(scenes)}')
    with r:
        st.markdown('#### Evidence behind this chapter')
        st.markdown('<div class="event-card">'+h(current.get('evidence') or 'See original recorded trace')+'</div>',unsafe_allow_html=True)
        if ix==len(scenes)-1:
            if e:
                for obs in e:st.markdown('<div class="event-card">'+h(obs)+'</div>',unsafe_allow_html=True)
            if uncertainty:st.caption('Uncertainty retained: '+str(uncertainty[0]))
        times=recorded_times(case)
        st.metric(times['localisation_label'],times['localisation_text'])
        st.metric(times['rca_label'],times['rca_text'])
        st.caption('Localisation is the SP01 agent span; RCA is the full recorded investigation time. These clocks are not additive.')
    st.markdown('**Want to watch the real recorded agent handovers?** Open **Agent Flow**. The story chapters are interpretive, while Agent Flow presents the saved sequence and source events.')
    focus=evidence_focus(case)
    label=('Inspect the affected-cell accessibility evidence →' if focus['entity_id']
           else 'Inspect recorded network measurements →')
    if st.button(label,key='ref_story_measurements',use_container_width=True):
        st.session_state['tead_evidence_focus']=focus
        st.session_state['tc_evidence_view']='Network measurements & provenance'
        st.session_state['requested_page']='Evidence Room'
        st.rerun()


def flow_steps(case,beats):
    stages=agent_stages(beats)
    expected={'DIRECT_SUPERVISOR':['SP01','DIRECT_JOIN','SUPERVISOR','FINAL'],
              'LOCAL_SPECIALISTS':['SP01','SP02','SP03','SP04','SP05','SP06','SP07','LOCAL_JOIN','SUPERVISOR','FINAL'],
              'CU_SPECIALIST':['SP01','SP08','CU_JOIN','SUPERVISOR','FINAL']}
    ids=[s['id'] for s in stages]
    target=expected.get(case.get('route_family'))
    if target and ids!=target:
        # Never construct a narrative from an assumed branch if source order differs.
        raise ValueError(f'Saved stage sequence does not match {case.get("route_family")}: {ids}')
    return stages


def _coord(index,count):
    # E/C's two-row agent map. Order is left-to-right across the upper row,
    # then right-to-left along the lower row; shorter cases use one row.
    if count<=5:return 16+(68*index/(max(1,count-1))),38
    if index<5:return 10+20*index,30
    return 90-20*(index-5),72


def build_reference_flow_html(case,beats):
    """One E/C-like connected storyboard; only source-recorded agents and joins."""
    stages=flow_steps(case,beats)
    chain_times={n.get('name'):n.get('duration_seconds') for n in case.get('observed_nodes',[])
                 if n.get('run_type')=='chain' and n.get('depth')==1
                 and isinstance(n.get('duration_seconds'),(int,float))}
    for stage in stages:
        duration=chain_times.get(stage['id'])
        stage['recorded_duration']=format_duration(duration) if duration is not None else None
    nodes=[];edges=[]
    for i,s in enumerate(stages):
        x,y=_coord(i,len(stages))
        symbol='RCA' if s['id']=='FINAL' else 'JOIN' if s['id'] in JOIN_IDS else s['id']
        nodes.append(f'<div class="node pending" id="node-{h(s["id"])}" style="left:{x}%;top:{y}%"><div class="id">{h(symbol)}</div><div class="nm">{h(s["name"])}</div></div>')
        if i:
            x0,y0=_coord(i-1,len(stages))
            edges.append(f'<path class="edge" marker-end="url(#arrow)" d="M {x0*10} {y0*2.65} L {x*10} {y*2.65}"/>')
    window=case.get('scenario_window') or {}
    window_from=window.get('window_start_utc') or window.get('start_utc') or ''
    window_to=window.get('window_end_utc') or window.get('end_utc') or ''
    window_text=' · '.join(str(v) for v in (window_from,window_to) if v)
    intake={'title':'Investigation intake — 5G RAN evidence',
            'activity':'A completed experiment begins with performance measurements, network events and the recorded topology context for a 10-site, 30-cell 5G RAN. SP01 will determine whether a material issue exists.',
            'finding':'Affected cells, sites, CU domain and fault family are not established at intake. Advance to SP01 to see the recorded localisation findings.',
            'observation_window':window_text,
            'role':'context'}
    payload={'id':case.get('scenario_id'),'title':case.get('title'),'route':ROUTE_NAMES.get(case.get('route_family'),case.get('route_family')),
             'duration':case.get('trace_duration_seconds'),'timings':recorded_times(case),
             'intake':intake,'stages':stages,
             'points':{x['id']:list(_coord(i,len(stages))) for i,x in enumerate(stages)}}
    # Use textContent when displaying source strings; prevent literal HTML/script injection.
    data=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;background:#fff9f2"><div class="ec-ref-flow">''' + EXTRAS + '''
<script id="replay-source" type="application/json">'''+data+'''</script>
<div class="shell"><div class="toolbar"><div class="name" id="scenario">RECORDED NETWORK CASE</div><div class="buttons"><button id="prev">← Back</button><button id="play" class="primary">▶ Play</button><button id="next">Next →</button><button id="reset">↺ Reset</button><label for="speed" style="font-size:12px">Reading pace</label><select id="speed"><option value="quick" selected>Quick overview · 5s</option><option value="reading">Read · 15s</option><option value="manual">Manual · no timer</option></select></div></div>
<div class="graphwrap"><div class="graph"><svg class="edges" viewBox="0 0 1000 265" preserveAspectRatio="none"><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="#c9b5c3"/></marker></defs>'''+''.join(edges)+'''<path id="travel" class="travel" d=""/><circle id="orb" class="orb" r="10" cx="0" cy="0"/></svg>'''+''.join(nodes)+'''</div></div><div class="progress"><div class="fill" id="fill"></div></div>
<div class="bottom"><div class="panel"><div class="kicker" id="stepcount">RECORDED STAGE</div><div class="out-title" id="out-title"></div><div class="stage-time" id="stage-runtime"></div><div class="out-line" id="out-line"></div><div class="evidence-note" id="evidence-note"></div></div><div class="panel"><div class="kicker">RECORDED HANDOVER HISTORY</div><div class="history" id="activity"></div></div></div>
<div class="status"><span><b id="stepmeta"></b></span><span id="time-localisation"></span><span id="duration"></span><span>Current step: <b id="progress-meta"></b></span><span>Reader: <b id="playback-info"></b></span></div>
<details class="inspector"><summary>Original recorded inputs, agent/tool events and evidence identifiers for current stage</summary><div id="source-events"></div></details>
<div class="disclaimer">Recorded investigation playback · the speed selector controls reading time, not the original execution time. Source events and engineering details remain available above.</div></div></div>
<script>
(()=>{'use strict';const data=JSON.parse(document.getElementById('replay-source').textContent);const $=id=>document.getElementById(id);const stages=data.stages,points=data.points;let i=-1,playing=false,timer=null,frame=null,last=stages[0].id;
const pace={quick:5000,reading:15000,manual:0};
function point(id){const p=points[id];return [p[0]*10,p[1]*2.65]}
function stop(){playing=false;clearTimeout(timer);timer=null;cancelAnimationFrame(frame);$('play').textContent='▶ Play'}
function animate(from,to){const [x0,y0]=point(from),[x1,y1]=point(to);const path=$('travel'),orb=$('orb');const d=`M ${x0} ${y0} L ${x1} ${y1}`;path.setAttribute('d',d);if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){orb.setAttribute('cx',x1);orb.setAttribute('cy',y1);path.setAttribute('d','');return}const length=path.getTotalLength(),begin=performance.now();function tick(now){const f=Math.min(1,(now-begin)/500);const pt=path.getPointAtLength(f*length);orb.setAttribute('cx',pt.x);orb.setAttribute('cy',pt.y);if(f<1)frame=requestAnimationFrame(tick);else path.setAttribute('d','')}frame=requestAnimationFrame(tick)}
function render(){
const intake=i<0;
const s=intake?{id:'INTAKE',name:data.intake.title,role:'context',activity:data.intake.activity,finding:data.intake.finding,events:[]}:stages[i];
stages.forEach((x,j)=>{$('node-'+x.id).className='node '+(intake?'pending':(j===i?'active':j<i?'done':'pending'))});
$('orb').style.opacity=intake?'0':'1';
$('scenario').textContent=data.id+' · '+data.title;
$('stepcount').textContent=intake?'START / RECORDED NETWORK CONTEXT':'RECORDED STAGE '+(i+1)+' / '+stages.length;
$('out-title').textContent=intake?'Before SP01 · '+data.intake.title:s.id+' · '+s.name;
$('stage-runtime').textContent=intake?'Context only · no agent runtime':(s.recorded_duration?'Recorded '+s.id+' agent runtime: '+s.recorded_duration:'No separate agent runtime recorded for this join/report stage');
$('out-line').textContent=s.activity||'Recorded activity; original events are available below.';
$('evidence-note').textContent=s.finding||'No saved finding in this stage.';
$('stepmeta').textContent=intake?'Before network localisation':'Stage '+(i+1)+' of '+stages.length;
$('time-localisation').textContent=data.timings.localisation_label+': '+data.timings.localisation_text;
$('duration').textContent=data.timings.rca_label+': '+data.timings.rca_text;
$('progress-meta').textContent=intake?'Context (not an agent)':s.role==='agent'?'Agent':s.role==='consolidation'?'Join (not an agent)':'Report (not an agent)';
$('fill').style.width=(intake?0:(i+1)/stages.length*100)+'%';
$('prev').disabled=i===-1;$('next').disabled=i===stages.length-1;
$('playback-info').textContent=$('speed').value==='manual'?'Manual stepping':(playing?'Playing':'Ready')+' · '+pace[$('speed').value]/1000+'s/step';
const recent=intake?[{id:'START',name:'Investigation intake',finding:'Network context presented before localisation'}]:stages.slice(Math.max(0,i-3),i+1);
$('activity').replaceChildren(...recent.map(x=>{const d=document.createElement('div');d.textContent=x.id+' · '+x.name+' — '+(x.finding||'source event recorded').slice(0,155);return d}));
const host=$('source-events');host.replaceChildren(...s.events.map((e,n)=>{const d=document.createElement('div');d.className='inspector-item';d.textContent=(n+1)+'. '+e.title+'\\nINPUT: '+e.input+'\\nACTION: '+e.action+'\\nOUTPUT: '+e.output+'\\nSOURCE: '+e.source+(e.evidence_id?'\\nEVIDENCE ID: '+e.evidence_id:'')+(e.timestamp?'\\nRECORDED START: '+e.timestamp:'');return d}));
if(intake){const d=document.createElement('div');d.className='inspector-item';d.textContent='Opening context is a presentation stage, not an additional agent or recorded execution span.'+(data.intake.observation_window?'\\nRecorded observation window: '+data.intake.observation_window:'');host.replaceChildren(d)}
if(!intake){animate(last,s.id);last=s.id}
}
function advance(k){i=Math.min(stages.length-1,Math.max(-1,k));render()}
function queue(){clearTimeout(timer);if(!playing)return;let ms=pace[$('speed').value];if(!ms){stop();return}timer=setTimeout(()=>{if(i>=stages.length-1){stop();render();return}advance(i+1);queue()},ms)}
$('play').onclick=()=>{if(playing){stop();render();return}if($('speed').value==='manual')return;if(i===stages.length-1)advance(0);playing=true;$('play').textContent='⏸ Pause';queue();render()};$('prev').onclick=()=>{stop();advance(i-1)};$('next').onclick=()=>{stop();advance(i+1)};$('reset').onclick=()=>{stop();advance(-1)};$('speed').onchange=()=>{if(playing)queue();render()};document.addEventListener('visibilitychange',()=>{if(document.hidden){stop();render()}});const [x,y]=point(last);$('orb').setAttribute('cx',x);$('orb').setAttribute('cy',y);render();
})();
</script></body></html>'''


def agent_flow(st,case,beats,embed):
    hero(st,'Agent flow / Original recorded stages','Follow the agents. See what each contributed.',
         'Begin with network evidence intake, then follow the actual agent route from SP01 localisation to the final RCA. Quick overview advances every five seconds; Manual gives you complete control.')
    heading(st,'01 / CHOOSE YOUR CASE','Watch the recorded route—not all possible branches')
    st.markdown(_case_banner(case),unsafe_allow_html=True)
    heading(st,'02 / AGENT-TO-AGENT REPLAY','The original stage order and saved findings')
    embed(build_reference_flow_html(case,beats),height=800,scrolling=False)
    st.caption('The opening intake is a viewing aid, not an extra agent. The animation follows original recorded handover order; original evidence IDs and tool events are available in the stage inspector and Evidence Room.')


def evidence_intro(st):
    hero(st,'Evidence room / Saved diagnosis and telemetry','The conclusion is visible. The measurements remain inspectable.',
         'Review what the Supervisor actually concluded, its competing hypotheses and uncertainty, and the exact recorded network measurements used to support the assessment.')


def results_intro(st,cases=None):
    hero(st,'Results / Completed 5G RAN investigations','Measured fault localisation and root-cause assessment.',
         'Compare per-case SP01 localisation, complete end-to-end investigation times, post-run evaluations and source provenance from nine recorded experimental executions.')
    if cases:
        heading(st,'01 / CASE-BY-CASE EXECUTION','How long each recorded investigation took')
        rows=[]
        for case in cases:
            times=recorded_times(case)
            rows.append({
                'Scenario':case.get('scenario_id','—'),
                'Investigation':case.get('title','Recorded investigation'),
                'SP01 — health/localisation':times['localisation_text'],
                'RCA / review completed (end-to-end)':times['rca_text'],
            })
        st.dataframe(rows,use_container_width=True,hide_index=True)
        st.caption('SP01 is its recorded depth-one chain duration. RCA/review is the complete root trace elapsed time to the saved outcome; these durations overlap and must not be added together. Healthy controls do not have a fault localisation claim.')
        with st.expander('Separate engineering experiment · CU evidence payload optimisation',expanded=False):
            st.markdown('**Reported development result:** approximately **98.7% reduction in evidence-payload byte size** in a separate CU-domain packaging experiment. This is a data-representation result, not a measured token, inference-cost or latency reduction, and is not part of the nine-case timing comparison.')
            st.caption('Review the original engineering evidence and measurement basis before using this result in an operator proposal.')


def ui_build_id():
    """Presentation-aware fingerprint; leaves RC2.2 source identity unchanged."""
    from hashlib import sha256
    root=Path(__file__).resolve().parent
    paths=('app.py','ec_clarity_experience.py','ec_reference_experience.py',
           'ec_reference_style.css','terminology.py')
    digest=sha256()
    for name in paths:
        p=root/name
        if not p.is_file():return 'source unavailable'
        digest.update(name.encode('utf8')+b'\x00')
        digest.update(p.read_bytes())
    return digest.hexdigest()[:12]


def footer(st):
    st.markdown(f'''<div class="footer-note"><div class="footer-description"><div class="footer-heading">TEAD AI · AGENTIC 5G RAN INVESTIGATION</div><p>Inspect completed multi-agent investigations, recorded telemetry and evidence-grounded RCA.</p></div><div class="release-tag"><div class="release-main"><span>TEAD AI DEMONSTRATION</span><strong>Interface Candidate 4.2</strong></div><div class="release-trace">UI build {h(ui_build_id())} · recorded investigation replay</div></div></div>''',unsafe_allow_html=True)
