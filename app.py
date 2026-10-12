"""Telecom AI Engineering — Evidence-Grounded Investigation Replay (offline V1).

The Streamlit interface never calls original notebook, LangGraph, LangSmith,
RAG/LLMs, MCP telemetry, or any external service. It reads only bundled gzip.
"""
import gzip
import json
import re
import time
from storyboard import AGENT_ROLES, build_story, workflow_svg, workflow_overview_html, evidence_preview
from operational_demo import (guided_sequence, executive_sequence, get_run_durations, event_trace_offset,
                              format_clock, sp01_tools_unlocked, available_agents)
from html import escape
from presentation import agent_label, format_duration, agent_execution_rows, benchmark_summary
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
try:
 from streamlit.components.v1 import html as embed_workflow_html
except ImportError:
 # Lightweight local test stub has no Streamlit package hierarchy.
 embed_workflow_html = st.components.v1.html

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
PAGES = ['Platform Overview','Guided Operations Demo','Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis','Engineering Evidence','Evaluation & Performance']

st.set_page_config(page_title='TREAD AI | Telecom Investigation & RCA',page_icon='📡',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container {padding-top:1.5rem;padding-bottom:3rem;max-width:1500px}
[data-testid="stSidebar"]{background:#101e30}
/* Sidebar labels are light, but SELECT BOX text/icons must contrast with its background. */
[data-testid="stSidebar"]{color:#edf7fb}
[data-testid="stSidebar"] :is(h1,h2,h3,p,label){color:#edf7fb}
[data-testid="stSidebar"] [data-baseweb="select"] > div{
  background:#173c51!important;border:2px solid #80cbd0!important;box-shadow:0 0 0 1px rgba(128,203,208,.15)!important
}
[data-testid="stSidebar"] [data-baseweb="select"] :is(div,span,input){color:#ffffff!important;-webkit-text-fill-color:#ffffff!important}
[data-testid="stSidebar"] [data-baseweb="select"] svg{fill:#ffffff!important;color:#ffffff!important}
[data-testid="stSidebar"] [data-baseweb="select"] [role="button"]{color:#ffffff!important}
[data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div{outline:2px solid #73cdd1;outline-offset:1px}
h1,h2,h3{letter-spacing:-.025em}
.hero{padding:1.4rem 1.7rem;border-radius:14px;border:1px solid #28435e;background:linear-gradient(118deg,#10283d 10%,#153d51 100%);color:#f6f9fc;margin-bottom:1.1rem}
.hero .eyebrow{font-size:.77rem;letter-spacing:.17em;color:#96bed0;text-transform:uppercase;font-weight:700}
.hero h1{margin:.18rem 0 .35rem 0;font-size:1.9rem;font-weight:740;color:#fff}
.hero .sub{color:#c3d7e4;font-size:.91rem}
.note{font-size:.86rem;color:#6b7b8b}
.ops-hero{padding:1.3rem 1.5rem;border-radius:15px;background:linear-gradient(110deg,#102b42,#123e48);color:#edf8fb;border:1px solid #29536a;margin:.7rem 0 1rem 0;box-shadow:0 8px 28px rgba(12,30,48,.12)}
.ops-eyebrow{font-size:.73rem;font-weight:750;letter-spacing:.13em;color:#a6cbd4}
.ops-head{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
.ops-headline{font-size:1.46rem;font-weight:760;letter-spacing:-.025em;margin:.22rem 0}
.ops-sub{color:#c4dce3;font-size:.9rem;line-height:1.6}
.ops-pill{display:inline-block;border:1px solid #6597a7;background:#1c4d5b;padding:7px 11px;border-radius:22px;color:#e3fbf4;font-size:.76rem;font-weight:700;letter-spacing:.045em}
.ops-pill.alert{background:#793c35;border-color:#d88772;color:#fff2ee}
.ops-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#74efd1;margin-right:6px;box-shadow:0 0 0 4px rgba(116,239,209,.1);animation:opsblink 1.5s infinite}
@keyframes opsblink{50%{opacity:.35;transform:scale(.85)}}
.ops-stage{border-radius:13px;border:1px solid #34586b;background:#10263b;color:#e9f4fb;padding:1rem 1.2rem;margin:.6rem 0}
.ops-stage .role{letter-spacing:.13em;color:#8cc9db;font-size:.69rem;font-weight:750}
.ops-stage .act{font-size:1.17rem;font-weight:750;margin:.4rem 0}
.ops-stage .message{color:#b8d2e1;font-size:.9rem;line-height:1.6}
/* Main theatre: workflow and rolling messages remain together in the viewport. */
.ops-theatre-note{font-size:.78rem;color:#96bed0;margin-top:-.15rem}
.ops-compact{background:#10263b;border:1px solid #34586b;color:#eef7fb;border-radius:12px;padding:.8rem .95rem;margin-bottom:.5rem}
.ops-compact .tag{color:#9dd2df;text-transform:uppercase;font-size:.69rem;letter-spacing:.09em;font-weight:750;margin-bottom:.3rem}
.ops-compact .title{font-size:1.02rem;font-weight:760;line-height:1.3;margin:.2rem 0 .6rem}
.ops-compact .desc{font-size:.81rem;line-height:1.43;color:#d5e8ef;overflow-wrap:anywhere;max-height:88px;overflow-y:auto}
.ops-compact.output{border-color:#287d70;background:#113533}
.ops-compact.input{background:#152e43}
.ops-milestone{border:1px solid #294860;border-radius:10px;padding:.75rem;background:#f3f8fb;height:100%}
.ops-milestone .number{font-weight:790;font-size:1.55rem;color:#123c58;line-height:1.2}
.ops-milestone .label{font-size:.8rem;font-weight:720;color:#1e465c;margin:.25rem 0}
.ops-milestone .detail{font-size:.73rem;color:#46637a;line-height:1.35}
.ops-architecture{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:10px 0}
.ops-architecture .step{padding:10px 9px;background:#edf5f8;border-radius:9px;border:1px solid #cce0e8;color:#19445b}
.ops-architecture .step strong{display:block;font-size:.81rem}
.ops-architecture .step span{font-size:.72rem;display:block;margin-top:4px;color:#456578;line-height:1.4}
.ops-value{border:1px solid #cee3df;background:#f4faf8;border-radius:12px;padding:1.1rem 1.3rem;color:#1b4f49}
.ops-value strong{font-size:1.1rem}
.ops-value p{font-size:.84rem;color:#41645f;line-height:1.55}
@media(max-width:760px){.ops-architecture{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.ops-milestone .number{font-size:1.2rem}}
.ops-kpi{border:1px solid #365e6c;background:#173244;border-radius:12px;padding:.9rem;height:100%;color:#f0fbff;min-height:112px}
.ops-kpi .name{font-size:.72rem;letter-spacing:.06em;color:#a6c9d5;text-transform:uppercase}
.ops-kpi .value{font-size:1.12rem;font-weight:800;margin:.5rem 0 .2rem;overflow-wrap:anywhere}
.ops-kpi .desc{font-size:.75rem;color:#c0d8e0}
.route-box{background:#f6f9fc;border:1px solid #dce8f1;padding:.8rem 1rem;border-radius:10px;font-size:.88rem;line-height:2.15}
@media (prefers-color-scheme:dark){.route-box{background:#1a2631;border:1px solid #405261}}
.wrap-value{border:1px solid #cbdbe5;background:#f3f8fa;border-radius:10px;padding:12px 14px;min-height:90px}
.wrap-value span{display:block;color:#496778;font-size:.78rem;margin-bottom:8px}
.wrap-value strong{display:block;color:#14384c;font-size:1.12rem;line-height:1.28;overflow-wrap:anywhere;white-space:normal}
[data-testid="stVerticalBlock"]{scroll-margin-top:1rem}
</style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_manifest():
 return json.loads((DATA/'manifest.json').read_text('utf-8'))

@st.cache_data(show_spinner=False,max_entries=20)
def load_case(sid):
 if sid not in load_manifest()['scenario_order']:raise ValueError('Unknown scenario identifier')
 with gzip.open(DATA/'cases'/f'{sid}.json.gz','rt',encoding='utf-8') as f:return json.load(f)

@st.cache_data(show_spinner=False,max_entries=35)
def load_evidence(sid,eid):
 case=load_case(sid)
 item=next((e for e in case['evidence_index'] if e['evidence_id']==eid),None)
 if item is None:raise ValueError('Unknown evidence identifier')
 path=BASE/item['file']
 if not path.resolve().is_relative_to((DATA/'evidence').resolve()):raise ValueError('Invalid evidence path')
 with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)

def pretty(v,none='Not identified'):
 if v is None or v=='' or v==[]:return none
 if isinstance(v,bool):return 'Yes' if v else 'No'
 if isinstance(v,(int,float)):return f'{v:,.2f}'
 if isinstance(v,dict):return str(v.get('label') or v.get('fault_family') or v.get('scope_class') or v.get('root_cause') or v)
 return str(v).replace('_',' ')

def display_tool_name(tool):
 # Preserve exact LangSmith tool identifiers for trace lookup and provenance.
 # Only the user-facing description adopts the curated knowledge-base name.
 if tool == 'supervisor_private_knowledge_search':
  return 'Curated Telecom Knowledge Base Search'
 return tool

def nice_time(val):
 if not val:return '—'
 try:return datetime.fromisoformat(str(val).replace('Z','+00:00')).strftime('%d %b %Y  %H:%M UTC')
 except ValueError:return str(val)

def heading(title,desc=None):
 st.subheader(title)
 if desc:st.caption(desc)

def route_text(c):
 """Public-facing route summary while trace identifiers remain in engineer view."""
 if c['route_family']=='LOCAL_SPECIALISTS':
  return 'Network Localisation → KPI → Cell & Peer → Radio → Processing → Transport → Configuration → RCA Supervisor (recorded sequential route)'
 if c['route_family']=='CU_SPECIALIST':
  return 'Network Localisation → CU-Domain & Boundary Analysis → Evidence Consolidation → RCA Supervisor'
 return 'Network Health Assessment → RCA Supervisor (healthy control)'

def run_badge(c):
 return 'HEALTHY / NO INCIDENT' if not c['derived_display']['incident_present'] else 'INCIDENT DETECTED'

def count_caps(c):
 x=c.get('data_inventory',{})
 return x.get('telemetry_rows',0),x.get('cell_kpi_rows',0),x.get('subnetwork_kpi_rows',0)

def evidence_by_tool(c,tool):
 return next((e for e in c['evidence_index'] if e['tool']==tool),None)

def query_network(c):
 a=evidence_by_tool(c,'telemetry_network_overview')
 return load_evidence(c['scenario_id'],a['evidence_id'])['result'] if a else {}

def network_chart(c,metric='partial_drb_accessibility_pct',by='five_qi'):
 rows=query_network(c).get('subnetwork_kpis',[])
 if not rows:return st.info('Recorded subnetwork KPI rows unavailable for this case.')
 frame=pd.DataFrame(rows).sort_values('interval_start_utc')
 frame['time']=pd.to_datetime(frame['interval_start_utc'],utc=True)
 fig=go.Figure()
 for key,group in frame.groupby(by,sort=True):
  fig.add_trace(go.Scatter(x=group.time,y=group[metric],mode='lines+markers',name=f'5QI {key}',line={'width':2},marker={'size':5}))
 fig.update_layout(height=325,margin={'l':10,'r':10,'t':18,'b':15},yaxis={'title':metric.replace('_',' ').title(),'ticksuffix':'%'},xaxis={'title':'Recorded observation time (UTC)'},legend={'orientation':'h','y':1.15},hovermode='x unified',template='plotly_white')
 st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
 st.caption('Source: recorded telemetry_network_overview • subnetwork KPIs • 15-minute PM intervals. This is replay data, not live telemetry.')

def data_field_sections(data,show_json=False):
 if not isinstance(data,dict):st.write(data);return
 # Avoid repeating huge bulky objects in front-end narrative views.
 for field in ['rationale','analysis_summary','diagnosis','selection_rationale']:
  if data.get(field) and isinstance(data[field],str):st.markdown(f'**{field.replace("_"," ").title()}** — {data[field]}')
 for field in ['observations','supported_observations','positive_metrics','candidate_fault_families','supported_hypotheses','weakened_hypotheses','contradictions','uncertainties','uncertainty','limitations','remaining_uncertainty','remaining_questions','supporting_evidence','recommendations']:
  v=data.get(field)
  if v:
   with st.expander(field.replace('_',' ').title(),expanded=field in ['observations','supported_hypotheses']):
    if isinstance(v,list):
     for entry in v:
      if isinstance(entry,str):st.markdown('• '+entry)
      else:st.json(entry,expanded=False)
    else:st.json(v,expanded=False) if isinstance(v,dict) else st.write(v)
 if 'domain_analysis' in data and data['domain_analysis']:
  with st.expander('Specialist domain analysis — original structured record'):
   st.json(data['domain_analysis'],expanded=False)
 if show_json:
  with st.expander('Full recorded stage output (JSON)'):
   st.json(data,expanded=False)

def state_summary(c):
 d=c['derived_display']
 a,b,cc=st.columns(3)
 for col,title,val in [(a,'Observed condition',run_badge(c)),(b,'Final scope',pretty(d['scope_class'])),(cc,'Trace execution',format_duration(c['trace_duration_seconds']))]:
  with col:
   st.markdown(f'<div class="wrap-value"><span>{escape(title)}</span><strong>{escape(val)}</strong></div>',unsafe_allow_html=True)
 st.caption('Full recorded Supervisor diagnosis is available under Original detailed Supervisor diagnosis.')



def render_rca_outcome(case):
    """Source-backed executive reading layer; saved Supervisor outputs remain intact."""
    su=case['stage_data']['supervisor_output']
    scope=su.get('final_scope') or {}
    sites=scope.get('affected_sites') or []
    domains=scope.get('affected_cu_domains') or []
    cells=scope.get('affected_cells') or []
    st.subheader('Investigation outcome at a glance')
    if not su.get('incident_present'):
        st.success('No material incident supported by this recorded assessment. No specialist escalation was required.')
        st.caption('The healthy control was reviewed by the RCA Supervisor without knowledge-base retrieval.')
        return
    st.markdown('**Recorded likely fault mechanism:** '+str((su.get('root_cause_assessment') or {}).get('root_cause') or su.get('root_cause_family') or 'Not established'))
    st.markdown('**Affected scope:** '+str(len(sites))+' site(s), '+str(len(cells))+' cell(s), '+str(len(domains))+' CU domain(s)')
    if sites:st.caption('Sites: '+', '.join(map(str,sites)))
    st.markdown('**Recorded execution time:** '+format_duration(case.get('trace_duration_seconds'))+' · **Agent confidence class:** '+str((su.get('root_cause_assessment') or {}).get('confidence') or 'Unreported'))
    x,y=st.columns(2)
    with x:
        st.markdown('**Key supporting observations**')
        for v in (su.get('supporting_evidence') or [])[:3]:st.markdown('• '+str(v))
        alternatives=su.get('contradictory_evidence') or []
        if alternatives:
            st.markdown('**Weakened competing explanations**')
            for v in alternatives[:2]:st.markdown('• '+str(v))
    with y:
        st.markdown('**Uncertainty and evidence gaps**')
        for v in (su.get('residual_uncertainty') or ['No further limitation recorded in the Supervisor final output.'])[:3]:st.markdown('• '+str(v))
        st.markdown('**Recommended engineering follow-up**')
        for v in (su.get('recommendations') or ['See original Supervisor report.'])[:2]:st.markdown('• '+str(v))
    st.caption('This summary is extracted from the recorded Supervisor output and is not a new RCA. A HIGH class is the agent’s recorded judgement, not independently calibrated probability or validation of the exact physical failure mechanism.')

def kb_list(label, values, empty='Not recorded in this Supervisor output'):
 """Show Supervisor-recorded knowledge grounding text without raw retrieved passages."""
 st.markdown(f'**{label}**')
 if not values:
  st.caption(empty)
 elif isinstance(values,list):
  for text in values:st.write('• '+str(text))
 else:
  st.write(str(values))

def render_kb_contribution(supervisor):
 """Recorded RAG contribution, not a live search, direct source quotation or causal claim."""
 k=supervisor.get('knowledge_base_contribution')
 heading('Curated Telecom Knowledge Base | RAG reasoning contribution',
         'The original Supervisor recorded how external telecom-domain knowledge informed mechanism assessment and discrimination between competing explanations.')
 if not isinstance(k,dict):
  st.info('No structured knowledge-base contribution was recorded in this investigation.')
  return
 if not k.get('used'):
  st.info('Knowledge-base retrieval was not used for this healthy-network investigation. The Supervisor concluded directly from available network evidence.')
  st.caption('Recorded knowledge-base contribution: NONE / NOT_USED. No retrieval is simulated in this replay.')
  return
 a,b,d=st.columns(3)
 with a:st.metric('RAG contribution','Used')
 with b:st.markdown(f'<div class="wrap-value"><span>Contribution type</span><strong>{escape(pretty(k.get("contribution_type")))}</strong></div>',unsafe_allow_html=True)
 with d:st.markdown(f'<div class="wrap-value"><span>Evidence weight</span><strong>{escape(pretty(k.get("evidence_weight")))}</strong></div>',unsafe_allow_html=True)
 st.markdown('**1. Question asked by the Supervisor**')
 for q in k.get('queries') or []:st.info(str(q))
 st.markdown('**2. Knowledge-informed fault mechanism**')
 kb_list('Mechanism interpretation',k.get('mechanism_summary'))
 left,right=st.columns(2)
 with left:kb_list('Hypotheses supported by domain knowledge',k.get('supported_hypotheses'))
 with right:kb_list('Competing hypotheses assessed',k.get('competing_hypotheses_discussed'))
 st.markdown('**3. Discriminating network observations**')
 expected,observed,missing=st.columns(3)
 with expected:kb_list('What the mechanism predicts',k.get('discriminating_observations_expected'))
 with observed:kb_list('Incident observations cited by Supervisor',k.get('incident_observations_confirming_mechanism'))
 with missing:kb_list('Evidence not available / not observed',k.get('incident_observations_missing'),empty='No missing observations listed')
 st.markdown('**4. Limits of the contribution**')
 kb_list('Recorded limitations',k.get('limitations'),empty='No additional limitations recorded in this field')
 st.caption('Provenance: Supervisor final knowledge_base_contribution field from the selected LangSmith trace. These are the Supervisor’s recorded interpretations, not redistributed retrieval passages, formal document citations or a measured causal RAG performance gain. Deterministic network observations carry primary weight; knowledge is SUPPORTING evidence.')

@st.cache_data(show_spinner=False,max_entries=12)
def load_storyboard(sid):
 c = load_case(sid)
 return build_story(c,lambda eid:load_evidence(sid,eid))

def friendly_replay_text(value):
 """Translate source-only trace IDs in the public theatre, not the saved evidence."""
 text=str(value or '')
 aliases={'SP01':'Localisation Agent','SP02':'KPI Agent','SP03':'Cell & Peer Agent',
          'SP04':'Radio Agent','SP05':'Processing Agent','SP06':'Transport Agent',
          'SP07':'Configuration Agent','SP08':'CU-Domain Agent'}
 return re.sub(r'\bSP0[1-8]\b',lambda match:aliases[match.group(0)],text)


def compact_beat_content(beat):
 """Short, synchronised theatre messages; complete raw text remains in detail expander."""
 def card(kind,label,text,limit=320):
  value=' '.join(friendly_replay_text(text or 'No separate field recorded for this stage.').split())
  short=value if len(value)<=limit else value[:limit-1].rstrip()+'…'
  return f'<div class="ops-compact {kind}"><div class="tag">{escape(label)}</div><div class="desc">{escape(short)}</div></div>'
 return (card('input','Incoming evidence / handover',beat.get('input')),
         card('action','Agent action / tool call',beat.get('action')),
         card('output','Recorded output / feedback',beat.get('output'),450))


def architecture_diagram():
    """Reader-friendly architecture, with SP01 as initiator of BOTH ML calls and telemetry.

    Trace identifiers deliberately stay in technical drill-down and provenance only.
    """
    st.subheader('Solution Architecture — How the Investigation Works')
    st.caption('A conceptual overview. The animated graph in the demo follows each real recorded execution route.')
    st.markdown("""<div style="border:1px solid #d1e1e9;border-radius:14px;padding:18px;background:#f3f8fb;color:#163449">
<div style="max-width:710px;margin:auto;text-align:center;padding:12px;border-radius:11px;background:#13344a;color:#f8ffff"><strong>1. Network Health &amp; Localisation Agent</strong><div style="color:#c7dfe8;font-size:.84rem;margin-top:5px">Initiates assessment · invokes intelligence tools · interprets evidence · determines routing</div></div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ requests ↓</div>
<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;max-width:850px;margin:auto">
<div style="padding:11px;background:#e0effb;border:1px solid #a9cee1;border-radius:9px"><strong>ML prediction: Fault family</strong><div style="font-size:.82rem">What could be wrong?</div></div>
<div style="padding:11px;background:#e0effb;border:1px solid #a9cee1;border-radius:9px"><strong>ML prediction: Fault scope</strong><div style="font-size:.82rem">Where is the fault likely located?</div></div>
<div style="padding:11px;background:#e4f4f0;border:1px solid #b8dbd2;border-radius:9px"><strong>Network Overview Telemetry</strong><div style="font-size:.82rem">Measured KPIs and network performance</div></div>
<div style="padding:11px;background:#e4f4f0;border:1px solid #b8dbd2;border-radius:9px"><strong>Network Event Telemetry</strong><div style="font-size:.82rem">Recorded events and operational context</div></div>
</div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ evidence returns to the localisation agent ↓</div>
<div style="max-width:710px;margin:auto;text-align:center;padding:11px;border-radius:10px;background:#174b62;color:#fff"><strong>2. Assessment, Fault Localisation &amp; Routing</strong><div style="font-size:.82rem;color:#ddf4fa">Evaluate incident materiality and affected site, cell or CU domain</div></div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ conditional investigation route ↓</div>
<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;max-width:850px;margin:auto">
<div style="padding:11px;border-radius:9px;background:#e4f4ed;border:1px solid #9ccab4"><strong>Healthy network</strong><div style="font-size:.82rem">Direct Supervisor review; no specialist escalation</div></div>
<div style="padding:11px;border-radius:9px;background:#fef2df;border:1px solid #e8c68d"><strong>Material incident</strong><div style="font-size:.82rem">Sequential specialist analysis (cell/site recordings) or CU-domain analysis; investigate tools, measurements and competing causes</div></div>
</div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ investigation evidence ↓</div>
<div style="max-width:710px;margin:auto;text-align:center;padding:11px;border-radius:10px;background:#173d53;color:#f4fcff"><strong>3. RCA Supervisor &amp; Evidence Synthesis</strong><div style="font-size:.82rem;color:#d3eaf0">Correlates agent results; uses Curated Telecom Knowledge Base when needed to assess fault mechanisms and hypotheses</div></div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓</div>
<div style="max-width:710px;margin:auto;text-align:center;padding:12px;border-radius:10px;background:#0f6159;color:#fff"><strong>4. Evidence-Grounded Root Cause Analysis</strong><div style="font-size:.82rem;color:#e1f8f4">Supported diagnosis · affected network scope · causal reasoning · uncertainties · recorded execution time</div></div>
</div>""",unsafe_allow_html=True)
    st.caption('The two ML models are tools called by the Localisation Agent, not independent agents. In V1 this is replayed from recorded synthetic-network investigations, not a live network scan.')


def render_solution_intro(cases, include_architecture=True):
 """Concise visitor onboarding; performance derived from recorded LangSmith runs."""
 b=benchmark_summary(cases)
 st.markdown("""<div style="font-size:1.04rem;line-height:1.55;margin:.15rem 0 .65rem">
 <strong>What is this?</strong> An AI-enabled 5G network investigation system that combines
 <strong>ML-assisted fault identification</strong>, recorded network telemetry,
 specialist AI agents and a <strong>Curated Telecom Knowledge Base</strong> to produce
 evidence-grounded root cause analysis. Watch a real recorded execution from the synthetic experimental network.
 </div>""",unsafe_allow_html=True)
 st.markdown('**Demonstrated investigation milestones**')
 x,y,z=st.columns(3)
 facts=[(x,'< 1 min','Assess network health',f"Localisation agent assessment • {b['health_assessment_under_1min']}/{b['health_assessment_total']} recorded scenarios"),
        (y,'≤ 2 min','Localise affected scope',f"Localisation agent handover • {b['localisation_under_2min']}/{b['localisation_total']} recorded scenarios"),
        (z,'< 5 min','Evidence-grounded RCA',f"Full incident investigation • {b['incident_rca_under_5min']}/{b['incident_total']} incident scenarios")]
 for col,num,title,detail in facts:
  with col:
   st.markdown(f'<div class="ops-milestone"><div class="number">{escape(num)}</div><div class="label">{escape(title)}</div><div class="detail">{escape(detail)}</div></div>',unsafe_allow_html=True)
 st.caption('Benchmarks are from completed synthetic-network LangSmith traces, not production SLAs or validated MTTR savings. Health assessment and initial fault-scope localisation share the same recorded SP01 completion timestamp; they are not two independently timed milestones. No specialist-localisation latency is claimed.')
 if include_architecture:
  architecture_diagram()



def render_value_proposition():
 st.markdown("""<div class="ops-value"><strong>From network data to actionable engineering intelligence</strong>
 <p><b>Detect faster. Localise intelligently. Diagnose with evidence.</b> The demonstration illustrates how
 agent-led ML and telemetry assessment, coordinated specialist investigations and knowledge-grounded
 Supervisor reasoning could reduce manual evidence correlation, improve diagnostic consistency and
 make specialist expertise more accessible.</p>
 <p>Production MTTR, OPEX reduction, remediation and sustained monitoring outcomes require validation in an operating network;
 this is a recorded, inspectable investigation demonstration, not an operational SLA.</p></div>""",unsafe_allow_html=True)

@st.fragment(run_every='1s')
def cinematic_replay(sid):
 """Autoplay of saved evidence only. A refresh advances one authored beat, not a live run."""
 c=load_case(sid)
 beats=load_storyboard(sid)
 key='cinema_'+sid
 if key not in st.session_state:
  st.session_state[key]={'index':0,'playing':False,'seconds':3,'last_tick':time.monotonic()}
 player=st.session_state[key]
 last=len(beats)-1
 now=time.monotonic()
 if player['playing'] and now-player['last_tick']>=player['seconds']:
  player['index']=min(last,player['index']+1)
  player['last_tick']=now
  if player['index']==last:player['playing']=False

 ctrl=st.columns([1.25,.9,.85,.85,1.6])
 with ctrl[0]:
  if st.button('⏸ Pause' if player['playing'] else '▶ Play',type='primary',use_container_width=True,key='cinema_play_'+sid):
   if not player['playing'] and player['index']==last:player['index']=0
   player['playing']=not player['playing']; player['last_tick']=time.monotonic()
   st.rerun(scope='fragment')
 with ctrl[1]:
  if st.button('◀ Back',disabled=player['index']==0,use_container_width=True,key='cinema_back_'+sid):
   player['playing']=False; player['index']-=1;player['last_tick']=time.monotonic();st.rerun(scope='fragment')
 with ctrl[2]:
  if st.button('Next ▶',disabled=player['index']==last,use_container_width=True,key='cinema_next_'+sid):
   player['playing']=False;player['index']+=1;player['last_tick']=time.monotonic();st.rerun(scope='fragment')
 with ctrl[3]:
  if st.button('↺ Restart',use_container_width=True,key='cinema_restart_'+sid):
   player['index']=0;player['playing']=False;player['last_tick']=time.monotonic();st.rerun(scope='fragment')
 with ctrl[4]:
  speed=st.selectbox('Pacing per beat',[2,3,5,8],index=[2,3,5,8].index(player['seconds']),format_func=lambda v:f'{v} seconds',label_visibility='collapsed',key='cinema_speed_'+sid)
  if speed!=player['seconds']:
   player['seconds']=speed;player['last_tick']=time.monotonic()

 seek_key='cinema_seek_'+sid
 st.session_state[seek_key]=player['index']
 seek=st.slider('Presentation timeline',min_value=0,max_value=last,format='%d',key=seek_key)
 if seek!=player['index']:
  player['index']=seek;player['playing']=False;player['last_tick']=time.monotonic();st.rerun(scope='fragment')
 idx=player['index']
 beat=beats[idx]
 st.progress((idx+1)/len(beats),text=f'PLAYBACK {idx+1} / {len(beats)}  •  {"PLAYING" if player["playing"] else "PAUSED"}  •  {agent_label(beat["agent"])}')
 embed_workflow_html(workflow_svg(c['route_family'],beats,idx),height=250,scrolling=False)
 with st.expander('View complete recorded agent route',expanded=False):
  st.html(workflow_overview_html(beats,idx))
 st.markdown(f'#### {idx+1:02d} — {beat["title"]}')
 panels=st.columns([1,1,1.12])
 with panels[0]:
  st.markdown('**📥 INPUT / HANDOVER**')
  st.info(beat['input'] or 'No separate input detail saved for this stage.')
 with panels[1]:
  st.markdown('**⚙️ AGENT ACTION / TOOL CALL**')
  st.write(beat['action'] or 'Recorded analysis stage.')
 with panels[2]:
  st.markdown('**📤 RECORDED OUTPUT / FEEDBACK**')
  st.success(beat['output'] or 'No separate output detail saved in this field.')
 if beat.get('timestamp'):
  st.caption('Original recorded tool start: '+nice_time(beat['timestamp']))
 st.caption('Provenance: '+beat['source']+(('  ·  Evidence ID: `'+beat['evidence_id']+'`') if beat['evidence_id'] else ''))
 if c['route_family']=='LOCAL_SPECIALISTS':
  st.caption('Recorded execution: the six cell/site specialists ran sequentially in this experiment. Parallel execution was deferred to avoid instability with large investigation inputs.')
 st.caption('Playback pacing is illustrative, not the original execution timing. Original node timestamps/durations are available under the technical stage inspector. No network scan, LLM, RAG, or tool call is executed here.')
 with st.expander('Original recorded source for the current beat'):
  stage=c['stages'][beat['stage_index']]
  st.markdown('**Saved stage:** '+stage['label']+' · `'+stage['key']+'`')
  if beat['evidence_id']:
   ev=load_evidence(sid,beat['evidence_id'])
   st.json({'tool':ev.get('tool'),'evidence_id':beat['evidence_id'],'result_keys':list((ev.get('result') or {}).keys()) if isinstance(ev.get('result'),dict) else [],'source_stage':ev.get('stage')},expanded=False)
   st.caption('Large recorded tool responses remain accessible on Engineering Evidence rather than rendered unfiltered here.')
  else:
   st.json(c['stage_data'][stage['key']],expanded=False)
 if beat['agent']=='FINAL':
  if st.button('Open Root Cause Analysis →',key='cinema_rca_'+sid):
   st.session_state['requested_page']='Root Cause Analysis';st.rerun()


# Guided operations presentation: all inputs and outputs are frozen trace records.
# This fragment is a media player, never a monitor, a model invocation or an agent run.
def guided_sp01_cards(sid, unlocked):
    cases = load_case(sid)
    labels = [
        ('ml_specialist_summary', 'ML 01 · Fault family', 'WHAT'),
        ('ml_scope_probabilities', 'ML 02 · Affected scope', 'WHERE'),
        ('telemetry_network_overview', 'Network Overview Telemetry', 'KPI evidence'),
        ('telemetry_events', 'Network Event Telemetry', 'Event evidence'),
    ]
    cols=st.columns(4)
    for col,(tool,title,hint) in zip(cols,labels):
        e=next((x for x in cases['evidence_index'] if x['stage']=='SP01' and x['tool']==tool), None)
        visible=tool in unlocked and e is not None
        value='Awaiting Localisation Agent'; desc='Recorded tool not yet presented'
        if visible:
            payload=load_evidence(sid,e['evidence_id'])['result']
            if tool=='ml_specialist_summary':
                hit=payload.get('top_fault_family') or {}
                value=pretty(hit.get('label'))
                desc=f"ML score {float(hit.get('probability',0)):.1%} · uncalibrated"
            elif tool=='ml_scope_probabilities':
                hits=payload.get('ranked_scopes') or []
                value=pretty(hits[0].get('label')) if hits else 'No scope predicted'
                desc=(f"ML score {float(hits[0].get('probability',0)):.1%} · uncalibrated" if hits else 'Not recorded')
            elif tool=='telemetry_network_overview':
                rows=payload.get('subnetwork_kpis') or []
                value=f'{len(rows)} KPI observations'
                desc='Recorded 15-minute PM measurements'
            else:
                events=payload if isinstance(payload,list) else payload.get('events',[])
                value=f'{len(events)} returned events'
                desc='Recorded event telemetry (zero is a valid result)'
        with col:
            st.markdown(f"""<div class="ops-kpi"><div class="name">{escape(title)}</div>
              <div class="value">{escape(value)}</div><div class="desc">{escape(desc)}</div> </div>""",unsafe_allow_html=True)
    st.caption('These are outputs called by the Network Health & Localisation Agent. The two ML prediction outputs do not independently initiate investigations; their probabilities are supporting, uncalibrated evidence.')


def guided_agent_drilldown(case, current_agent, current_beat):
    sid=case['scenario_id']
    agents=available_agents(case)
    if not agents:return
    with st.expander('🔎 Engineer drill-down — inspect any recorded agent, its tools and outputs',expanded=False):
        st.caption('All panels inspect stored execution records. Choosing an agent does not start a new investigation.')
        follow='↪ Follow highlighted agent'
        choice=st.selectbox('Agent to inspect',[follow]+agents,
                          format_func=lambda a:a if a==follow else agent_label(a,include_id=True),
                          key='ops_agent_pick_'+sid)
        pick=(current_agent if current_agent in agents else 'SUPERVISOR') if choice==follow else choice
        src_stages=[s for s in case['stages'] if s['agent']==pick]
        st.markdown('**Original analytical stages · '+agent_label(pick,include_id=True)+'**')
        current_index=current_beat['stage_index']
        matching_key=case['stages'][current_index]['key'] if current_index < len(case['stages']) else None
        default_stage=next((i for i,v in enumerate(src_stages) if v['key']==matching_key),0)
        stage=st.selectbox('Saved stage',src_stages,index=default_stage,
                           format_func=lambda x:x['label'],
                           key='ops_stage_pick_'+sid+'_'+pick+(('_follow_'+str(current_index)) if choice==follow else ''))
        data_field_sections(case['stage_data'][stage['key']],show_json=True)
        if pick=='SUPERVISOR' and stage['key']=='supervisor_output':
            render_kb_contribution(case['stage_data']['supervisor_output'])
        evs=[e for e in case['evidence_index'] if e['stage']==pick]
        if evs:
            st.markdown('**Agent-initiated tool calls and recorded replies**')
            e=st.selectbox('Evidence artifact',evs,
                format_func=lambda v:display_tool_name(v['tool'])+' · '+v['evidence_id'][-8:],
                key='ops_evidence_pick_'+sid+'_'+pick)
            payload=load_evidence(sid,e['evidence_id'])
            st.info(evidence_preview(e,payload))
            with st.expander('Evidence metadata and safe data preview'):
                st.json({'tool':display_tool_name(e['tool']),'source_tool_identifier':e['tool'],
                         'evidence_id':e['evidence_id'],'reason':e.get('reason'),
                         'result_keys':list(payload.get('result',{}).keys()) if isinstance(payload.get('result'),dict) else [],
                         'stored_data_type':type(payload.get('result')).__name__},expanded=False)
                st.caption('For complete KPI measurements, source series, and evidence IDs use Engineering Evidence. Third-party retrieved knowledge passages are not in this public dataset.')
        agent_nodes=[n for n in case['observed_nodes'] if n['name']==pick and n.get('depth')==1]
        if agent_nodes:
            n=agent_nodes[0]
            st.caption(f"Saved {agent_label(pick)} execution: {format_duration(n.get('duration_seconds'))} · {nice_time(n.get('start_time'))} to {nice_time(n.get('end_time'))}")


@st.fragment(run_every='1s')
def guided_operations_player(selected_sid, include_healthy, executive=False):
    healthy_sid='M05I0017'
    healthy=load_case(healthy_sid)
    incident=load_case(selected_sid)
    timeline=guided_sequence(healthy,load_storyboard(healthy_sid),
        incident if selected_sid != healthy_sid else None,
        load_storyboard(selected_sid) if selected_sid != healthy_sid else [],
        include_healthy=include_healthy or selected_sid==healthy_sid)
    if executive:
        timeline=executive_sequence(timeline)
    if not timeline:
        st.warning('No recorded investigation selected.')
        return
    key='ops_player_'+selected_sid+'_'+str(include_healthy)+('_executive' if executive else '')
    if key not in st.session_state:
        st.session_state[key]={'index':0,'playing':False,'seconds':6 if executive else 7,'last_tick':time.monotonic(),
                               'carry':0.,'presentation_elapsed':0.}
    play=st.session_state[key]
    last=len(timeline)-1
    now=time.monotonic()
    if play['playing']:
        dt=max(0.,min(now-play['last_tick'],3.))
        play['carry']+=dt
        play['presentation_elapsed']+=dt
        while play['index'] < last:
            current_kind=timeline[play['index']]['beat']['kind']
            hold=play['seconds'] * (1.0 if executive else (1.5 if current_kind in {'decision','rag','feedback','handover','report'} else 1.0))
            if play['carry'] < hold:break
            play['carry']-=hold
            play['index']+=1
        if play['index']>=last:
            play['playing']=False
            play['carry']=0.
    play['last_tick']=now

    controls=st.columns([1.1,.85,.85,.9,1.45])
    with controls[0]:
        if st.button('⏸ Pause' if play['playing'] else '▶ Play',type='primary',use_container_width=True,key=key+'_play'):
            if not play['playing'] and play['index']==last:play['index']=0;play['presentation_elapsed']=0.
            play['playing']=not play['playing'];play['carry']=0.;play['last_tick']=time.monotonic()
            st.rerun(scope='fragment')
    with controls[1]:
        if st.button('◀ Back',disabled=play['index']==0,use_container_width=True,key=key+'_back'):
            play['playing']=False;play['index']-=1;play['carry']=0.;st.rerun(scope='fragment')
    with controls[2]:
        if st.button('Next ▶',disabled=play['index']==last,use_container_width=True,key=key+'_next'):
            play['playing']=False;play['index']+=1;play['carry']=0.;st.rerun(scope='fragment')
    with controls[3]:
        if st.button('↺ Restart',use_container_width=True,key=key+'_restart'):
            play.update({'index':0,'playing':False,'carry':0.,'presentation_elapsed':0.,'last_tick':time.monotonic()})
            st.rerun(scope='fragment')
    with controls[4]:
        speeds=[4,5,6,7,8] if executive else [3,5,7,10,14]
        speed=st.selectbox('Playback pacing',speeds,
                           index=speeds.index(play['seconds']) if play['seconds'] in speeds else 2,
                           format_func=lambda x:f'{x}s per presentation beat',
                           label_visibility='collapsed',key=key+'_pace')
        if speed!=play['seconds']:play['seconds']=speed;play['carry']=0.
    seek_key=key+'_seek'
    st.session_state[seek_key]=play['index']
    changed=st.slider('Playback position',min_value=0,max_value=last,key=seek_key)
    if changed!=play['index']:
        play['index']=changed;play['playing']=False;play['carry']=0.;st.rerun(scope='fragment')
    idx=play['index'];item=timeline[idx];sid=item['scenario_id'];beat=item['beat'];case=healthy if sid==healthy_sid else incident
    durations=get_run_durations(case)
    scoped=timeline[:idx+1]
    at_end=beat['agent']=='FINAL'
    material=case['derived_display']['incident_present']
    assessed=any(x['scenario_id']==sid and x['beat']['kind']=='decision' and x['beat']['agent']=='SP01' for x in scoped)
    if not assessed:status='ASSESSMENT UNDERWAY'
    elif not material:status='NO MATERIAL INCIDENT'
    elif at_end:status='RCA AVAILABLE'
    else:status='DEGRADATION IDENTIFIED'
    alert=material and assessed
    title='Network Health Assessment' if not material else 'Incident Investigation & Root Cause Analysis'
    st.markdown(f"""<div class="ops-hero"><div class="ops-head"><div>
      <div class="ops-eyebrow"><span class="ops-dot"></span>{escape(item['act'])} · RECORDED LANGGRAPH REPLAY</div>
      <div class="ops-headline">{escape(title)}</div>
      <div class="ops-sub">{escape(case['title'])}</div></div>
      <div class="ops-pill{' alert' if alert else ''}">{escape(status)}</div></div> </div>""",unsafe_allow_html=True)
    a,b,d,e=st.columns(4)
    a.metric('Presentation timer',format_clock(play['presentation_elapsed']),help='Time spent watching playback, not original execution duration.')
    b.metric('Recorded localisation runtime',format_clock(durations['sp01']),help='Original Network Health & Localisation Agent chain duration from LangSmith.')
    d.metric('Recorded end-to-end RCA' if material else 'Recorded health-check duration',format_clock(durations['total']),help='Original completed LangGraph execution duration, independent of replay pacing.')
    exact=event_trace_offset(case,beat)
    e.metric('Recorded event offset',format_clock(exact),help='Shows an exact recorded timestamp offset only when an original tool start or agent completion timestamp is available.')
    st.progress((idx+1)/len(timeline),text=f'Guided journey {idx+1} / {len(timeline)} · {"PLAYING" if play["playing"] else "PAUSED"} · {agent_label(beat["agent"])}')
    # Theatre: current workflow and its changing messages sit side-by-side, so
    # viewers do not have to scroll between the graphic and the latest output.
    graph,live=st.columns([1.36,1],gap='small')
    with graph:
        st.caption('Recorded orchestration · selected agent highlighted · sequential specialist execution in cell/site cases')
        case_beats=load_storyboard(sid)
        active_index=next(i for i,b in enumerate(case_beats) if b['sequence']==beat['sequence'])
        embed_workflow_html(workflow_svg(case['route_family'],case_beats,active_index),height=250,scrolling=False)
        with st.expander('View complete recorded agent route',expanded=False):
            st.html(workflow_overview_html(case_beats,active_index))
    with live:
        st.markdown(f'**{escape(agent_label(beat["agent"]))}**')
        st.caption(f'{beat["title"]} · Stage {idx+1}/{len(timeline)}')
        panels=compact_beat_content(beat)
        # Brief, readable previews scroll *inside* their cards; complete content
        # is available below without losing the animation's current position.
        st.markdown(''.join(panels),unsafe_allow_html=True)
    st.caption('Recorded '+agent_label(beat['agent'])+' activity · '+('Executive cut: selected source-backed milestones.' if executive else 'Important findings have longer playback holds.')+' Pause or open the inspector to see the original record.')
    with st.expander('Full current-stage messages and localisation evidence (click to inspect)',expanded=False):
        st.caption('Original trace provenance: '+beat['source'] + (' · '+beat['evidence_id'] if beat.get('evidence_id') else ''))
        st.markdown('**Incoming context / handover**')
        st.write(beat['input'] or 'No separate input recorded.')
        st.markdown('**Agent action / tool request**')
        st.write(beat['action'] or 'No action detail recorded.')
        st.markdown('**Recorded output / feedback**')
        st.write(beat['output'] or 'No output detail recorded.')
        if beat['agent']=='SP01' or assessed:
            st.markdown('**Network Health & Localisation Agent · Two ML predictions + two telemetry services**')
            unlocked=sp01_tools_unlocked(timeline,idx)
            guided_sp01_cards(sid,unlocked)
            if 'telemetry_network_overview' in unlocked:
                with st.expander('📈 Inspect the recorded 15-minute accessibility trend (network telemetry)'):
                    network_chart(case)
    if include_healthy and selected_sid!=healthy_sid and sid==healthy_sid:
        st.info('First independent recording: healthy network. After its report, the presentation switches to a **different recorded incident**, not a new alert detected in the same continuous live network.')
    if case['route_family']=='LOCAL_SPECIALISTS':
        st.caption('Recorded execution: the six cell/site specialists ran sequentially. The graph and evidence progression reflect that experimental execution order.')
    guided_agent_drilldown(case,beat['agent'],beat)
    if beat['agent']=='FINAL':
        if not material:st.success('Recorded health check complete: no material degradation identified; no specialist escalation was needed.')
        else:
            st.success('Recorded investigation complete. Diagnosis: '+str(case['derived_display'].get('diagnosis') or 'See Supervisor final output.'))
        if st.button('View complete Root Cause Analysis →',key=key+'_rca'):
            st.session_state['selected_scenario']=sid
            st.session_state['requested_page']='Root Cause Analysis'
            st.rerun()
    st.caption('Two clocks: presentation timer = playback viewing time; SP01/end-to-end/event offset = measured original LangSmith times. No new ML inference, telemetry polling, agent execution or RAG search occurs. Each case is a separate synthetic-network snapshot.')


# Scenario selection is persistent business state, not ephemeral widget state.
# Streamlit may delete a widget key when it disappears from a page.
manifest=load_manifest()
_valid_scenarios=manifest['scenario_order']
_default_scenario='M05I0003'

def sync_scenario_from(widget_key):
    candidate=st.session_state.get(widget_key)
    if candidate in _valid_scenarios:
        st.session_state['selected_scenario']=candidate

def sync_scenario_picker(widget_key):
    # Set widget values before drawing them, using the persistent scenario ID.
    canonical=st.session_state['selected_scenario']
    if st.session_state.get(widget_key)!=canonical:
        st.session_state[widget_key]=canonical

st.sidebar.markdown('### ◈ TREAD AI')
st.sidebar.caption('Telecom AI Engineering Platform')
st.sidebar.divider()
if 'requested_page' in st.session_state:
    st.session_state['nav_page']=st.session_state.pop('requested_page')
if st.session_state.get('selected_scenario') not in _valid_scenarios:
    st.session_state['selected_scenario']=_default_scenario
if 'nav_page' not in st.session_state:
    st.session_state['nav_page']='Platform Overview'
page=st.sidebar.radio('Workspace',PAGES,key='nav_page')
opts={x:next(c['title'] for c in manifest['cases'] if c['scenario_id']==x) for x in _valid_scenarios}
sync_scenario_picker('sidebar_scenario_picker')
st.sidebar.selectbox('Select scenario ▾',options=_valid_scenarios,format_func=lambda x:opts[x],
                     key='sidebar_scenario_picker',on_change=sync_scenario_from,args=('sidebar_scenario_picker',))
sid=st.session_state['selected_scenario']
c=load_case(sid)
st.sidebar.divider()
st.sidebar.caption('RECORDED INVESTIGATION DEMO')
st.sidebar.caption('No live agent, telemetry, LLM, API key or paid inference calls.')
st.sidebar.caption('Synthetic experimental network • not production operations')

st.markdown(f'''<div class="hero"><div class="eyebrow">TREAD AI · TELECOM ENGINEERING INTELLIGENCE</div><h1>TREAD AI — Telecom AI Engineering Platform</h1><div class="sub">Intelligent network assessment · ML-assisted localisation · Specialist AI investigation · Knowledge-grounded root cause analysis</div></div>''',unsafe_allow_html=True)

if page=='Platform Overview':
 heading('Discover TREAD AI','Network fault investigation often requires engineers to correlate radio, processing, transport and configuration evidence. See how agent-led ML, telemetry, specialised analysis and telecom knowledge produce a traceable RCA.')
 render_solution_intro([load_case(x) for x in manifest['scenario_order']],include_architecture=False)
 st.markdown('### Choose your experience')
 st.write('Follow the Network Health & Localisation Agent through its two ML predictions, network telemetry, specialist analysis, knowledge-grounded reasoning and final RCA. Pause anywhere to inspect the original evidence.')
 if st.button('▶ Watch the investigation',type='primary',use_container_width=True):
  st.session_state['requested_page']='Guided Operations Demo';st.rerun()
 st.divider()
 architecture_diagram()
 st.divider()
 render_value_proposition()

elif page=='Guided Operations Demo':
 st.caption('Recorded synthetic-network investigations · Select the executive overview or full engineering replay. Architecture and benchmarks are on **Platform Overview**.')
 heading('Guided Operations Demo','An animated, engineer-inspectable journey from network health assessment to evidence-grounded root cause analysis. All data comes from completed, independent LangGraph runs.')
 main_sid=sid if sid!='M05I0017' else 'M05I0003'
 experience=st.radio('Visitor experience',['Executive overview (~90 seconds)','Full engineering replay'],horizontal=True)
 modes=['Healthy check → Separate incident','Incident investigation only'] if sid!='M05I0017' else ['Healthy check only']
 mode=st.radio('Presentation',modes,horizontal=True)
 if sid=='M05I0017':st.info('Healthy-control scenario selected. Choose an incident in the sidebar to show a complete health-to-incident demonstration.')
 elif mode==modes[0]:
  st.info('**Two independent saved scenarios:** M05I0017 (healthy control), then '+main_sid+' ('+c['title']+'). The scene change is editorial, not an assertion that the healthy network developed a fault. The original 15-minute telemetry interval is independent of playback speed.')
 else:
  st.caption('Single recorded incident investigation. The animated pace is for explanation, not a claim that the platform is running now.')
 guided_operations_player(main_sid if sid!='M05I0017' else sid,mode==modes[0],executive=experience.startswith('Executive'))
 st.divider()
 render_value_proposition()
 st.markdown('**Want more detail?** Open **Agentic Replay** for every recorded call and stage, **Engineering Evidence** for source KPI series, or **Evaluation & Performance** for the original trace measurements and post-run checks.')

elif page=='Network Overview':
 heading('Network Overview','Nine independent synthetic-network snapshots, each with its own recorded observation window. Not a single continuous live network timeline.')
 cases=manifest['cases']
 a,b,d,e=st.columns(4)
 a.metric('Recorded scenarios',len(cases)); b.metric('Incident cases',sum(bool(x['incident_present']) for x in cases));d.metric('Healthy controls',sum(not x['incident_present'] for x in cases));e.metric('Distinct evidence artifacts',sum(x['evidence_artifacts'] for x in cases))
 st.divider()
 l,r=st.columns([1.4,1])
 with l:
  heading('Selected scenario / accessibility trend',f"{c['scenario_id']} · {c['title']}")
  metric=st.radio('KPI', ['partial_drb_accessibility_pct','total_drb_accessibility_pct'],format_func=lambda v:v.replace('_',' ').title(),horizontal=True)
  network_chart(c,metric)
 with r:
  heading('Recorded network topology')
  top=evidence_by_tool(c,'telemetry_topology')
  ent=load_evidence(sid,top['evidence_id'])['result'].get('entities',[]) if top else []
  sites={a['site_id'] for a in ent if a.get('site_id')};cu={a['cu_domain_id'] for a in ent if a.get('cu_domain_id')};cells=[a for a in ent if a.get('entity_type')=='NR_CELL_CU']
  m1,m2,m3=st.columns(3)
  m1.metric('Sites',len(sites));m2.metric('CU domains',len(cu));m3.metric('NR CU cells',len(cells))
  st.markdown('**5G RAN accessibility investigation**')
  st.write('The Network Health & Localisation Agent invokes ML predictions and network telemetry, assesses the evidence, and routes material incidents to the appropriate specialist branch and RCA Supervisor.')
  st.markdown(f'<div class="route-box">{route_text(c)}</div>',unsafe_allow_html=True)
 st.divider()
 heading('Investigation portfolio')
 kb_map={x['scenario_id']:load_case(x['scenario_id'])['stage_data']['supervisor_output'].get('knowledge_base_contribution') or {} for x in cases}
 overview=pd.DataFrame([{'Case':x['scenario_id'],'Scenario':x['title'],'Incident':'Yes' if x['incident_present'] else 'No','Scope':x['scope_class'],'Fault family':x['fault_family'] or 'None','RAG contribution':pretty(kb_map[x['scenario_id']].get('contribution_type'),none='Not used'),'Recorded duration':format_duration(x['trace_duration_seconds'])} for x in cases])
 st.dataframe(overview,hide_index=True,use_container_width=True)
 st.caption(f"Recorded knowledge-base retrieval was used in {sum(bool(k.get('used')) for k in kb_map.values())} of {len(cases)} scenarios. This counts original reported usage, not a measured gain in root-cause accuracy.")
 st.divider()
 heading('Curated Telecom Knowledge Base | Investigation grounding')
 selected_kb=c['stage_data']['supervisor_output'].get('knowledge_base_contribution') or {}
 if selected_kb.get('used'):
  st.write('This selected case used recorded knowledge-base retrieval to assess a fault mechanism and distinguish plausible causes. The question and resulting reasoning are visible in **Root Cause Analysis** and the **Supervisor final finding** replay stage.')
  for q in selected_kb.get('queries') or []:st.info(q)
  st.caption(f"Recorded contribution: {pretty(selected_kb.get('contribution_type'))} · evidence weight: {pretty(selected_kb.get('evidence_weight'))}. This is an already completed RAG investigation, not a live query.")
 else:
  st.info('The selected healthy-control scenario was investigated without knowledge-base retrieval. No unnecessary RAG call is represented.')

elif page=='Scenario Library':
 heading('Scenario Library','Choose one of the nine completed LangSmith investigations. All incident classifications below come from recorded Supervisor outputs.')
 sync_scenario_picker('library_case_selection')
 st.selectbox('Choose a recorded investigation',options=_valid_scenarios,
     format_func=lambda x:opts[x],key='library_case_selection',
     on_change=sync_scenario_from,args=('library_case_selection',))
 st.caption('One scenario is selected by default. Use the dropdown above to explore any of the nine completed cases.')
 left,right=st.columns([1,1.6]);d=c['derived_display']
 with left:
  st.caption('SELECTED INVESTIGATION')
  st.header(c['title'])
  st.caption('Trace reference: '+sid)
  st.markdown('**Recorded status:** '+run_badge(c))
  st.markdown('**Fault family:** '+pretty(d['fault_family']))
  st.markdown('**Affected scope:** '+pretty(d['scope_class']))
  st.markdown('**Incident window:** '+nice_time(d['incident_start_utc'])+' — '+nice_time(d['incident_end_utc']))
  st.markdown('**Scenario window:** '+nice_time(c['scenario_window'].get('window_start_utc'))+' — '+nice_time(c['scenario_window'].get('window_end_utc')))
  if st.button('Open agentic replay',type='primary',use_container_width=True):
   st.session_state['requested_page']='Agentic Replay';st.session_state['replay_'+sid]=0;st.rerun()
 with right:
  heading('Supervisor outcome')
  st.write(d.get('diagnosis') or 'No incident diagnosed.')
  st.markdown('**Execution route**')
  st.code(route_text(c),language=None)
  st.caption(f"{len(c['observed_nodes'])} recorded LangSmith run nodes · {len(c['evidence_index'])} distinct recorded evidence outputs")
  with st.expander('Original public investigation task'):
   st.write(c['scenario_window'].get('task','—'))
  st.info('This replay shows the outcome of an already completed investigation. Selecting another scenario does not execute a new investigation.')

elif page=='Agentic Replay':
 heading('Agentic Investigation Replay','Interactive animated workflow with recorded network scan, specialist dispatch, tool calls, evidence feedback and Supervisor final assessment.')
 mode=st.radio('Replay mode',['▶ Animated workflow','Recorded-stage inspector'],horizontal=True,key='replay_mode')
 if mode=='▶ Animated workflow':
  st.caption('Play or scrub through the original recorded investigation. A highlighted agent indicates the point being *presented*, not an active live process.')
  cinematic_replay(sid)
 else:
  heading('Recorded-stage inspector','Reveal the actual saved localisation, specialist, and Supervisor reasoning stages in sequence. This is navigation through recorded outputs—not rerunning models.')
  stages=c['stages']; key='replay_'+sid
  if key not in st.session_state:st.session_state[key]=0
  step=st.session_state[key];step=min(step,len(stages)-1)
  col1,col2,col3,col4=st.columns([.8,.8,4,.8])
  with col1:
   if st.button('◀ Previous',disabled=step==0,use_container_width=True):st.session_state[key]=step-1;st.rerun()
  with col2:
   if st.button('Next ▶',disabled=step>=len(stages)-1,use_container_width=True):st.session_state[key]=step+1;st.rerun()
  with col3:
   new=st.select_slider('Recorded stage',options=list(range(len(stages))),value=step,format_func=lambda i:f'{i+1:02d} — {stages[i]["label"]}')
   if new!=step:st.session_state[key]=new;st.rerun()
  with col4:st.metric('Stage',f'{step+1}/{len(stages)}')
  st.progress((step+1)/len(stages))
  st.write('**Recorded routing:** '+route_text(c))
  if c['route_family']=='LOCAL_SPECIALISTS':st.caption('The recorded cell/site investigation ran six specialist chains sequentially; the stage navigator follows the saved order.')
  active=stages[step];item=c['stage_data'][active['key']]
  st.subheader(f"{agent_label(active['agent'],include_id=True)}  /  {active['label']}")
  if active['key']=='sp01_evidence_cycle_1':
   st.write('The Network Health & Localisation Agent requested the following evidence before localising the suspected incident:')
   for name,v in item.items():st.markdown(f"• **{name}** · `{v.get('evidence_id')}`")
  elif active['key']=='supervisor_output':
   st.markdown('**Final recorded decision**')
   st.write(item.get('diagnosis') or 'No issue')
   st.markdown('**Fault family:** '+pretty(item.get('root_cause_family')))
   st.markdown('**Scope:** '+pretty(item.get('scope_class')))
   data_field_sections(item,show_json=True)
   st.divider()
   render_kb_contribution(item)
  else:
   data_field_sections(item,show_json=True)
  with st.expander('All recorded LangSmith nodes and timestamps'):
   df=pd.DataFrame(c['observed_nodes'])[['name','run_type','depth','start_time','duration_seconds','status','total_tokens','total_cost']]
   st.dataframe(df,hide_index=True,use_container_width=True,height=350)

elif page=='Root Cause Analysis':
 heading('Root Cause Analysis','This is the recorded Supervisor conclusion, not an independently inferred or regenerated RCA.')
 su=c['stage_data']['supervisor_output'];d=c['derived_display']
 render_rca_outcome(c)
 st.divider()
 with st.expander('Original detailed Supervisor diagnosis',expanded=False):
  st.write(su.get('diagnosis') or 'No material incident supported.')
 state_summary(c)
 if su.get('incident_present'):
  cl,cr=st.columns([1,1]);
  with cl:
   heading('Fault assessment')
   st.markdown('**Fault family**');st.write(pretty(su.get('root_cause_family')))
   st.markdown('**Root cause statement**');st.write((su.get('root_cause_assessment') or {}).get('root_cause','Not established'))
   st.markdown('**Recorded confidence class**');st.write((su.get('root_cause_assessment') or {}).get('confidence','Not recorded'))
   st.markdown('**Target component**');st.write(pretty(su.get('target_component')))
   st.markdown('**Affected domain**');st.write(pretty(su.get('target_cu_domain_id')))
   st.markdown('**Affected site(s)**');st.write(', '.join((su.get('final_scope') or {}).get('affected_sites') or []) or pretty(su.get('target_site_id')))
   if su.get('target_component_justification'):st.caption(su['target_component_justification'])
  with cr:
   heading('Supporting evidence')
   for row in su.get('supporting_evidence') or []:st.markdown('• '+str(row))
  st.divider();left,right=st.columns(2)
  with left:
   heading('Contradictory or alternative evidence')
   alt=su.get('contradictory_evidence') or []
   if alt:
    for v in alt:st.markdown('• '+str(v))
   else:st.write('No contradictory evidence listed in the final Supervisor record. Check specialist analysis for weakened hypotheses.')
  with right:
   heading('Residual uncertainty')
   for v in su.get('residual_uncertainty') or ['No residual uncertainty recorded.']:st.markdown('• '+str(v))
  heading('Engineering recommendations')
  for i,v in enumerate(su.get('recommendations') or [],1):st.markdown(f'**{i}.** {v}')
 else:
  st.success('The original Supervisor concluded that no material accessibility incident was supported by available recorded measurements.')
  for v in su.get('supporting_evidence') or []:st.markdown('• '+str(v))
 st.divider()
 render_kb_contribution(su)
 st.divider()
 heading('Investigation agents · execution time & tools',
         'Per-agent wall-clock execution and separately summed LLM invocation spans. Recorded cell/site specialist runs were sequential. Agent runtime includes tool and LLM work; do not confuse individual LLM spans with full-chain wall time.')
 records=agent_execution_rows(c)
 if records:
  shown=[{k:v for k,v in row.items() if k in ['Agent','Purpose','Agent runtime','LLM inference (spans)','Tools used']} for row in records]
  st.dataframe(pd.DataFrame(shown),hide_index=True,use_container_width=True)
  with st.expander('Specialist timing and tool attribution details'):
   for row in records:
    st.markdown(f"**{row['Agent']} · {row['Agent runtime']}** (original `{row['ID']}`)")
    st.caption(row['Purpose'])
    st.write(f"LLM inference: {row['LLM inference (spans)']} across {row['LLM calls']} recorded invocation(s). Tools: {row['Tools used']}.")
  st.caption('Wall-clock runtime is measured from each agent’s saved LangSmith chain. LLM inference is the sum of its recorded LLM spans, not the complete agent runtime; tool names correspond to saved evidence. Neither is an independent production latency benchmark.')
 with st.expander('Recorded Supervisor specialist agreement and scope'):
  st.json({'specialist_agreement':su.get('specialist_agreement'), 'final_scope':su.get('final_scope'),'time_windows':su.get('time_windows')},expanded=False)

elif page=='Engineering Evidence':
 heading('Engineering Evidence Explorer','Review the source measurements that the completed investigation consulted. Values are preserved from the LangSmith tool outputs.')
 tab1,tab2,tab3=st.tabs(['Accessibility KPIs','Operational measurements','Evidence provenance'])
 with tab1:
  n=query_network(c)
  granularity=st.radio('Granularity',['Subnetwork (5QI)','NRCellDU/CU object (5QI)'],horizontal=True)
  metric=st.selectbox('Accessibility KPI',['partial_drb_accessibility_pct','total_drb_accessibility_pct'],format_func=lambda x:x.replace('_',' ').title())
  if granularity=='Subnetwork (5QI)':network_chart(c,metric)
  else:
   x=n.get('cell_kpis',{}); groups=x.get('groups',[]) if isinstance(x,dict) else []
   ids=sorted({g.get('static',{}).get('entity_id') for g in groups if g.get('static',{}).get('entity_id')})
   if ids:
    target=c['stage_data']['supervisor_output'].get('target_cells') or []
    preferred=target[0].get('nr_cell_cu_id') if target and isinstance(target[0],dict) else None
    sel=st.selectbox('NR CU cell',ids,index=ids.index(preferred) if preferred in ids else 0)
    qivals=sorted({g.get('static',{}).get('five_qi') for g in groups if g.get('static',{}).get('entity_id')==sel})
    qi=st.selectbox('5QI',qivals)
    g=next((a for a in groups if a.get('static',{}).get('entity_id')==sel and a.get('static',{}).get('five_qi')==qi),None)
    if g:
     df=pd.DataFrame({'interval_start_utc':g['timestamps'],metric:g['series'].get(metric,[])})
     df['interval_start_utc']=pd.to_datetime(df['interval_start_utc'],utc=True)
     f=go.Figure(go.Scatter(x=df['interval_start_utc'],y=df[metric],mode='lines+markers',name=metric))
     f.update_layout(height=300,template='plotly_white',margin={'l':8,'r':8,'b':10,'t':15},yaxis_title='Accessibility (%)',xaxis_title='UTC')
     st.plotly_chart(f,use_container_width=True)
     st.dataframe(df,hide_index=True,use_container_width=True)
    st.caption(f"Lossless columnar replay: {len(groups)} source groups, {x.get('source_row_count', '—')} original cell-KPI rows.")
  if n.get('events'):st.dataframe(pd.DataFrame(n['events']),hide_index=True,use_container_width=True)
 with tab2:
  available=[]
  for ev in c['evidence_index']:
   if ev['tool'].startswith('telemetry_') and ev['tool'] not in ['telemetry_network_overview','telemetry_topology','telemetry_events']:
    available.append(ev)
  if not available:st.info('No additional specialist telemetry requested in this healthy-control route.')
  else:
   selected=st.selectbox('Recorded telemetry tool',available,format_func=lambda e:agent_label(e['stage'])+' · '+display_tool_name(e['tool'])+' · '+str(e.get('reason') or 'recorded response')[:44]+' · '+e['evidence_id'][-7:])
   result=load_evidence(sid,selected['evidence_id'])['result']
   fields=[]
   if isinstance(result,dict):
    fields=[(k,v) for k,v in result.items() if isinstance(v,dict) and v.get('groups') is not None]
    if result.get('groups') is not None:fields=[('measurements',result)]+fields
   if fields:
    field_keys=[k for k,_ in fields]
    name=st.selectbox('Evidence dataset',field_keys)
    x=dict(fields)[name]
    groups=x.get('groups') or []
    if groups:
     allmetrics=sorted({(g.get('static') or {}).get('metric_name') for g in groups if (g.get('static') or {}).get('metric_name')})
     if allmetrics:
      metric=st.selectbox('Metric',allmetrics)
      gs=[g for g in groups if (g.get('static') or {}).get('metric_name')==metric]
     else:
      gs=groups
     names=[]
     for i,g in enumerate(gs):
      s=g.get('static') or {};names.append((f"{s.get('entity_id','object')} | 5QI {s.get('five_qi','—')} | {s.get('operational_category','')}",i))
     chosen=st.selectbox('Entity / recorded series',names,format_func=lambda z:z[0])
     g=gs[chosen[1]];static=g.get('static') or {};series=g.get('series') or {}
     nrows=len(g.get('timestamps') or []);df=pd.DataFrame({'interval_start_utc':g['timestamps']})
     for k,v in series.items():
      if isinstance(v,list) and len(v)==nrows and (k.startswith('value_') or k in ['partial_drb_accessibility_pct','total_drb_accessibility_pct']):df[k]=v
     for k in ['value_float','value_int','value_bool','value_text']:
      if k not in df and static.get(k) is not None:df[k]=[static[k]]*nrows
     quantitative=[k for k in ['value_float','value_int','value_bool','partial_drb_accessibility_pct','total_drb_accessibility_pct'] if k in df and pd.to_numeric(df[k],errors='coerce').notna().any()]
     if quantitative:
      metric_value=st.selectbox('Value column',quantitative)
      df[metric_value]=pd.to_numeric(df[metric_value],errors='coerce')
      fig=go.Figure(go.Scatter(x=pd.to_datetime(df['interval_start_utc'],utc=True),y=df[metric_value],mode='lines+markers'))
      fig.update_layout(height=310,template='plotly_white',margin={'l':10,'r':10,'b':10,'t':15},yaxis_title=static.get('unit') or metric_value,xaxis_title='UTC')
      st.plotly_chart(fig,use_container_width=True)
     else:st.info('State/categorical telemetry; source values shown in the table.')
     st.dataframe(df,hide_index=True,use_container_width=True)
     st.caption(f"Source: {selected['evidence_id']} · {x.get('representation','recorded data')} · {x.get('source_row_count','—')} source rows · {len(groups)} groups.")
     with st.expander('Recorded entity metadata'):st.json(static,expanded=False)
   else:
    st.caption('The selected tool returned structured recorded evidence rather than a columnar time series.')
    st.json(result,expanded=False)
 with tab3:
  st.write('**Data origin:** Frozen synthetic 5G RAN scenario processed in a completed LangGraph execution, exported from LangSmith.')
  st.dataframe(pd.DataFrame([{k:(display_tool_name(e.get(k)) if k=='tool' else e.get(k)) for k in ['stage','tool','evidence_id','compressed_bytes','reason']} for e in c['evidence_index']]),hide_index=True,use_container_width=True)
  v=st.selectbox('Inspect exact recorded tool response',c['evidence_index'],format_func=lambda e:e['stage']+' / '+display_tool_name(e['tool'])+' / '+e['evidence_id'][-9:])
  if v['tool']=='supervisor_private_knowledge_search':st.info('Only raw curated knowledge-base retrieval passages are withheld. The exact Supervisor query, mechanism reasoning, hypothesis comparison and observation checks are visible in Root Cause Analysis and the Supervisor final replay stage.')
  with st.expander('Raw recorded response (read-only)'):
   st.json(load_evidence(sid,v['evidence_id'])['result'],expanded=False)

elif page=='Evaluation & Performance':
 heading('Evaluation & Performance','Separate operational runtime measurements and trace integrity from post-run evaluations of the corresponding saved runs.')
 run=c['saved_postrun_evaluation'];a,b,d=st.columns(3)
 a.metric('Recorded trace duration',format_duration(c['trace_duration_seconds']))
 b.metric('LangSmith run nodes',len(c['observed_nodes']))
 d.metric('Recorded evidence artifacts',len(c['evidence_index']))
 st.divider();heading('Recorded execution profile')
 nodes=pd.DataFrame(c['observed_nodes'])
 x=nodes[(nodes['depth']==0) | (nodes['name'].isin(['SP01','SP02','SP03','SP04','SP05','SP06','SP07','SP08','SUPERVISOR']))]
 st.dataframe(x[['name','run_type','start_time','end_time','duration_seconds','total_tokens','total_cost']],hide_index=True,use_container_width=True)
 st.caption('Token and cost fields in the export are not reliable proof of original inference usage or zero cost. Treat missing/zero accounting as unavailable unless independently reconciled.')
 tokens=pd.to_numeric(nodes.loc[nodes['run_type']=='llm','total_tokens'],errors='coerce').dropna()
 if len(tokens):st.caption(f"Summed reported tokens across LLM node records (not a billing estimate): {int(tokens.sum()):,}.")
 else:st.caption('No complete per-LLM token counts were recorded in exported child nodes. No synthetic usage estimate is shown.')
 heading('Saved post-run notebook evaluation')
 if not run.get('matches_selected_trace_filename'):
  st.warning('The saved notebook export reference differs from the selected trace. Treat the evaluation as unmatched until reconciled.')
 else:st.info('The updated notebook references this same LangSmith export timestamp. This evaluation is a post-run assessment and was not available to agents during their investigation.')
 score1,score2,score3=st.columns(3)
 score1.metric('Post-run judge score',f"{run.get('judge_score_out_of_5'):.2f} / 5" if run.get('judge_score_out_of_5') is not None else '—')
 score2.metric('Post-run exact match',f"{run.get('structured_exact_match_rate')*100:.1f}%" if run.get('structured_exact_match_rate') is not None else '—')
 score3.metric('Post-run deterministic checks',pretty(run.get('deterministic_status')))
 st.caption('The saved evaluation provides a summary score without the field-level match breakdown or full judging rubric. These values are not independent RCA accuracy; 75% exact match cannot be attributed to particular fields from this dataset alone.')
 st.write('**Post-run path check:** '+str(run.get('path_check'))+'  ·  **Supervisor schema:** '+str(run.get('supervisor_schema'))+'  ·  **Post-run judge status:** '+str(run.get('judge_status')))
 st.caption(f"Source: saved notebook cell {run.get('notebook_source_cell')}, reported trace export {run.get('reported_trace_basename')}")
 st.divider();heading('Source provenance & verification')
 st.markdown(f"**Trace ID:** `{c['trace_id']}`")
 st.markdown(f"**Export selected:** {nice_time(c['exported_at_utc'])}")
 st.markdown(f"**Source filename:** `{c['source_filename']}`")
 st.markdown(f"**Original source SHA-256:** `{c['source_sha256']}`")
 st.markdown(f"**Reported execution mode (original run):** `{c['recorded_execution_mode']}` — the present application is offline static replay.")
 st.markdown('**Original run status:** '+str(c['run_status']))
 warn=c.get('recorded_warnings') or {};n=sum(len(v) if isinstance(v,list) else 0 for v in warn.values());st.caption(f'{n} exported runtime warnings across recorded warning lists (expand for details).')
 with st.expander('Raw trace runtime warnings'):st.json(warn,expanded=False)
 st.divider();heading('Scope and controls')
 st.write('V1 replays original operational results without model inference or live telemetry. The original ML outputs are supporting probabilistic evidence and are explicitly uncalibrated; they are not ground truth. Post-run grading is never supplied to the replayed agentic decision stages.')
 st.caption('V2 (deferred) would require live retrieval/authentication, LangGraph execution, MCP adapters, access policies, observability, and cost controls. None are enabled in V1.')

st.divider()
st.caption('TREAD AI • RECORDED INVESTIGATION REPLAY • SYNTHETIC TEST NETWORK • ALL TIMESTAMPS IN UTC')
