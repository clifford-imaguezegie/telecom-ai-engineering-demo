"""Telecom AI Engineering — Evidence-Grounded Investigation Replay (offline V1).

The Streamlit interface never calls original notebook, LangGraph, LangSmith,
RAG/LLMs, MCP telemetry, or any external service. It reads only bundled gzip.
"""
import gzip
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
PAGES = ['Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis','Engineering Evidence','Evaluation & Performance']

st.set_page_config(page_title='Telecom AI | Investigation Replay',page_icon='📡',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container {padding-top:1.5rem;padding-bottom:3rem;max-width:1500px}
[data-testid="stSidebar"]{background:#101e30}
[data-testid="stSidebar"] *{color:#eef4fa}
h1,h2,h3{letter-spacing:-.025em}
.hero{padding:1.4rem 1.7rem;border-radius:14px;border:1px solid #28435e;background:linear-gradient(118deg,#10283d 10%,#153d51 100%);color:#f6f9fc;margin-bottom:1.1rem}
.hero .eyebrow{font-size:.77rem;letter-spacing:.17em;color:#96bed0;text-transform:uppercase;font-weight:700}
.hero h1{margin:.18rem 0 .35rem 0;font-size:1.9rem;font-weight:740;color:#fff}
.hero .sub{color:#c3d7e4;font-size:.91rem}
.note{font-size:.86rem;color:#6b7b8b}
.route-box{background:#f6f9fc;border:1px solid #dce8f1;padding:.8rem 1rem;border-radius:10px;font-size:.88rem;line-height:2.15}
@media (prefers-color-scheme:dark){.route-box{background:#1a2631;border:1px solid #405261}}
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
 names=c['route_nodes']
 if 'LOCAL_JOIN' in names:
  members=[n for n in names if n in {'SP02','SP03','SP04','SP05','SP06','SP07'}]
  return 'SP01 → ['+' ∥ '.join(members)+'] → LOCAL_JOIN → SUPERVISOR'
 return ' → '.join(names)

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
 with a:st.metric('Observed condition',run_badge(c))
 with b:st.metric('Final scope',pretty(d['scope_class']))
 with cc:st.metric('Trace execution',f"{c['trace_duration_seconds']:.1f} s")
 st.markdown(f"**Supervisor diagnosis:** {d.get('diagnosis') or 'No diagnosis recorded.'}")


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
 with b:st.metric('Contribution type',pretty(k.get('contribution_type')))
 with d:st.metric('Evidence weight',pretty(k.get('evidence_weight')))
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

# Sidebar state
manifest=load_manifest()
st.sidebar.markdown('### ◈ TELECOM AI ENGINEERING')
st.sidebar.caption('M05_06D • Recorded Investigation Replay')
st.sidebar.divider()
if 'requested_page' in st.session_state:
 st.session_state['nav_page']=st.session_state.pop('requested_page')
if 'selected_scenario' not in st.session_state:st.session_state['selected_scenario']='M05I0002'
if 'nav_page' not in st.session_state:st.session_state['nav_page']='Network Overview'
page=st.sidebar.radio('Workspace',PAGES,key='nav_page')
opts={x:x+'   ·   '+next(c['title'] for c in manifest['cases'] if c['scenario_id']==x) for x in manifest['scenario_order']}
sid=st.sidebar.selectbox('Scenario',options=manifest['scenario_order'],format_func=lambda x:opts[x],key='selected_scenario')
c=load_case(sid)
st.sidebar.divider()
st.sidebar.caption('MODE  01 — STATIC / OFFLINE REPLAY')
st.sidebar.caption('No live agent, telemetry, LLM, API key or paid inference calls.')
st.sidebar.caption('Synthetic experimental network • not production operations')

st.markdown(f'''<div class="hero"><div class="eyebrow">Telecom AI Engineering / Module 5</div><h1>Evidence-Grounded Investigation Replay</h1><div class="sub">Recorded LangGraph execution • 9 selected scenarios • 15-minute 5G RAN accessibility measurements • V1 static demonstration</div></div>''',unsafe_allow_html=True)

if page=='Network Overview':
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
  st.write('The SP01 localization agent inspects deterministic PM evidence, then routes a material case to the appropriate specialist branch and Supervisor.')
  st.markdown(f'<div class="route-box">{route_text(c)}</div>',unsafe_allow_html=True)
 st.divider()
 heading('Investigation portfolio')
 kb_map={x['scenario_id']:load_case(x['scenario_id'])['stage_data']['supervisor_output'].get('knowledge_base_contribution') or {} for x in cases}
 overview=pd.DataFrame([{'Case':x['scenario_id'],'Scenario':x['title'],'Incident':'Yes' if x['incident_present'] else 'No','Scope':x['scope_class'],'Fault family':x['fault_family'] or 'None','RAG contribution':pretty(kb_map[x['scenario_id']].get('contribution_type'),none='Not used'),'Trace duration (s)':x['trace_duration_seconds']} for x in cases])
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
 left,right=st.columns([1,1.6]);d=c['derived_display']
 with left:
  st.caption('SELECTED CASE')
  st.header(sid)
  st.write(c['title'])
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
 heading('Agentic Investigation Replay','Reveal the actual saved SP01, specialist, and Supervisor reasoning stages in sequence. This is navigation through recorded outputs—not rerunning models.')
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
 if c['route_family']=='LOCAL_SPECIALISTS':st.caption('SP02–SP07 form parallel analytical branches; the stage navigator presents their saved outputs sequentially for inspection.')
 active=stages[step];item=c['stage_data'][active['key']]
 st.subheader(f"{active['agent']}  /  {active['label']}")
 if active['key']=='sp01_evidence_cycle_1':
  st.write('SP01 retrieved the following source records before localizing the suspected incident:')
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
   st.markdown('**Affected site**');st.write(pretty(su.get('target_site_id')))
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
   selected=st.selectbox('Recorded telemetry tool',available,format_func=lambda e:e['stage']+' · '+e['tool'])
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
 a.metric('Recorded trace duration',f"{c['trace_duration_seconds']:.2f} s")
 b.metric('LangSmith run nodes',len(c['observed_nodes']))
 d.metric('Recorded evidence artifacts',len(c['evidence_index']))
 st.divider();heading('Recorded execution profile')
 nodes=pd.DataFrame(c['observed_nodes'])
 x=nodes[(nodes['depth']==0) | (nodes['name'].isin(['SP01','SP02','SP03','SP04','SP05','SP06','SP07','SP08','SUPERVISOR']))]
 st.dataframe(x[['name','run_type','start_time','end_time','duration_seconds','total_tokens','total_cost']],hide_index=True,use_container_width=True)
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
st.caption('TELECOM AI ENGINEERING • MODULE 5 / M05_06D • STATIC EVIDENCE REPLAY • SYNTHETIC TEST NETWORK • ALL TIMESTAMPS IN UTC')
