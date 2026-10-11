"""Offline, evidence-preserving extractor for the nine M05_06D LangSmith exports.

Execution: python build_replay.py
No network, inference, LangSmith, telemetry MCP, graph, or notebook execution.
Each tool response is stored verbatim as a compressed JSON payload, separate from
stage summaries and evaluation-only notebook records.
"""
import gzip
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
DATA = HERE / 'data'
EVID = DATA / 'evidence'
CASES = DATA / 'cases'
SIDS = ['M05I0017','M05I0002','M05I0006','M05I0003','M05I0019','M05I0004','M05I0005','M05I0008','M05I0016']
TITLES = {
 'M05I0017':'Healthy network control',
 'M05I0002':'Single-cell radio interference',
 'M05I0006':'Single-cell 5QI / QoS configuration',
 'M05I0003':'Single-site radio resource congestion (A)',
 'M05I0019':'Single-site radio resource congestion (B)',
 'M05I0004':'CU-domain N2 impairment',
 'M05I0005':'CU-domain processing pressure',
 'M05I0008':'CU-domain AMF-facing boundary',
 'M05I0016':'CU-domain boundary / alternate CU',
}
SOURCES = {
 'M05I0017':'M05I0017_langsmith_full_trace_20261010T204551Z(1).json',
 'M05I0002':'M05I0002_langsmith_full_trace_20261010T221400Z(1).json',
 'M05I0006':'M05I0006_langsmith_full_trace_20261010T222908Z(1).json',
 'M05I0003':'M05I0003_langsmith_full_trace_20261010T223629Z(1).json',
 'M05I0019':'M05I0019_langsmith_full_trace_20261010T224541Z(1).json',
 'M05I0004':'M05I0004_langsmith_full_trace_20261011T000245Z(1).json',
 'M05I0005':'M05I0005_langsmith_full_trace_20261010T235443Z(1).json',
 'M05I0008':'M05I0008_langsmith_full_trace_20261010T234923Z(1).json',
 'M05I0016':'M05I0016_langsmith_full_trace_20261010T233337Z(1).json',
}
NOTEBOOK = 'M05_06D_GPT_Luna_10102026_1912 (2).ipynb'
AUDIT = 'M05_06D_Replay_Source_Audit.json'

def sha256_file(path):
 h = hashlib.sha256()
 with open(path,'rb') as fp:
  for part in iter(lambda:fp.read(4*1024*1024),b''):h.update(part)
 return h.hexdigest()

def gzip_json(path, obj):
 with gzip.open(path,'wt',encoding='utf-8',compresslevel=6) as w:
  json.dump(obj,w,ensure_ascii=False,separators=(',',':'),default=str)

def iso_dt(s):
 if not s:return None
 try:return datetime.fromisoformat(str(s).replace('Z','+00:00'))
 except (ValueError,TypeError):return None

def duration(start, end):
 s,e=iso_dt(start),iso_dt(end)
 return round((e-s).total_seconds(),3) if s and e else None

def slim_node(a):
 return {k:a.get(k) for k in ['id','parent_run_id','name','run_type','start_time','end_time','status','error','prompt_tokens','completion_tokens','total_tokens','total_cost','prompt_cost','completion_cost']} | {'duration_seconds': duration(a.get('start_time'),a.get('end_time'))}

def walk(r):
 stack=[(r,0)]
 while stack:
  node,depth=stack.pop()
  yield node,depth
  stack.extend((c,depth+1) for c in reversed(node.get('child_runs') or []))

def clean_path(s):
 return re.sub(r'[^a-zA-Z0-9_\-]','_',s)[:105]

def main():
 CASES.mkdir(parents=True,exist_ok=True);EVID.mkdir(parents=True,exist_ok=True)
 oldaudit=json.load(open(SRC/AUDIT,encoding='utf-8'))
 hist={c['scenario_id']:c for c in oldaudit['cases']}
 # Refresh post-run evaluation from the UPDATED supplied notebook (2).
 # Four corrected runs do have new saved evaluation and matching export receipts.
 notebook=json.load(open(SRC/NOTEBOOK,encoding='utf-8'))
 refreshed={}
 for sid in SIDS:
  evalcase=hist[sid].copy()
  cell=notebook['cells'][evalcase['notebook_cell_index_zero_based']]
  outputs='\n'.join(''.join(o.get('text',[])) for o in cell.get('outputs',[]) if o.get('output_type')=='stream')
  ix=outputs.rfind('POST-RUN EVALUATION')
  if ix<0:raise ValueError(f'{sid}: new notebook saved evaluation missing')
  evaluation=outputs[ix:]
  for field,pat in {
    'run_status':r'^Status\s*:\s*(\w+)',
    'deterministic_status':r'^Deterministic status\s*:\s*(\w+)',
    'path_check':r'^Path check\s*:\s*(\w+)',
    'supervisor_schema':r'^Supervisor schema\s*:\s*(\w+)',
    'judge_status':r'^Judge status\s*:\s*(\w+)',
    'structured_exact_match_rate':r'^Exact match rate\s*:\s*([0-9.]+)',
    'overall_judge_score_out_of_5':r'^Overall score\s*:\s*([0-9.]+)'
   }.items():
   m=re.search(pat,evaluation,re.M)
   if not m:raise ValueError(f'{sid}: missing {field} in updated evaluation')
   evalcase[field]=float(m.group(1)) if field in ['structured_exact_match_rate','overall_judge_score_out_of_5'] else m.group(1)
  pathmatch=re.search(r'/content/langsmith_traces/(M05I\d+_langsmith_full_trace_\d+T\d+Z\.json)',outputs)
  if not pathmatch:raise ValueError(f'{sid}: saved export receipt not found')
  evalcase['langsmith_trace_path_reported_in_notebook']='/content/langsmith_traces/'+pathmatch.group(1)
  refreshed[sid]=evalcase
 hist=refreshed
 manifest={'schema_version':'v1.0','source':'Recorded LangSmith full-trace exports from completed synthetic-network experiments','notebook_filename':NOTEBOOK,'notebook_sha256':sha256_file(SRC/NOTEBOOK),'source_selection_policy':'Latest explicitly corrected user upload for same scenario ID; never automatically select superseded exports', 'scenario_order':SIDS,'cases':[], 'evaluation_policy':'Saved evaluations from updated notebook (2), matched to all nine selected JSON export timestamps, are post-run results only and never available to replayed agentic reasoning.', 'hosting_safety':'Static local replay. No API keys, live LangSmith, external telemetry, agents, LLM, or network calls.'}
 for order,sid in enumerate(SIDS,1):
  p=SRC/SOURCES[sid]
  if not p.is_file():raise FileNotFoundError(p)
  print(f'[{order}/9] {sid}: {p.name}',flush=True)
  source_sha=sha256_file(p)
  raw=json.load(open(p,encoding='utf-8'))
  if raw.get('scenario_id')!=sid or raw.get('trace_count')!=1:raise ValueError(f'{sid} identifier/trace count mismatch')
  r=raw['traces'][0]['run']; o=r['outputs']; inp=r['inputs']
  if o.get('scenario_id')!=sid or inp.get('scenario_id')!=sid:raise ValueError(f'{sid}: run input/output scenario mismatch')
  en={}; evfiles=[]; stages=[]; nodes=[]; seen=set()
  def register(stage,tool,obj,why=None):
   if not isinstance(obj,dict):return
   ev=obj.get('evidence') or obj
   eid=ev.get('evidence_id') or obj.get('evidence_id')
   result=ev.get('result')
   if result is None or not isinstance(result,(list,dict)) or not eid:return
   if eid in seen:return
   seen.add(eid)
   restricted = (tool == 'supervisor_private_knowledge_search')
   if restricted and isinstance(result,dict):
    # Curated telecom knowledge base retrieval may contain restricted third-party excerpts.
    # Preserve provenance, corpus/query/method and original-result count without
    # redistributing that source content in the deployable demo package.
    result={k:v for k,v in result.items() if k!='results'} | {
      'results_count':len(result.get('results') or []),
      'results':'WITHHELD: curated telecom knowledge base retrieval passages excluded from distributable V1',
    }
   j={'stage':stage,'tool':tool,'evidence_id':eid,'reason':why or obj.get('reason'), 'result':result}
   filename=clean_path(eid)+'.json.gz'
   ep=EVID/sid;ep.mkdir(exist_ok=True)
   target=ep/filename
   gzip_json(target,j)
   en[eid]={'stage':stage,'tool':tool,'evidence_id':eid,'reason':j['reason'],'file':str(target.relative_to(HERE)),'compressed_bytes':target.stat().st_size,'result_keys':list(result) if isinstance(result,dict) else [],'kind':'restricted_provenance_only' if restricted else 'recorded_tool_output'}
  for k,v in (o.get('sp01_prerun_evidence') or {}).items():register('SP01',k,v)
  for k,v in (o.get('sp01_evidence_cycle_1') or {}).items():register('SP01',k,v)
  for v in o.get('supervisor_evidence_history') or []:register('SUPERVISOR',v.get('tool'),v,why=v.get('analytical_use') or v.get('reason'))
  for a,depth in walk(r):
   n=slim_node(a);n['depth']=depth;nodes.append(n)
   name=a.get('name') or ''
   if re.fullmatch(r'SP\d\d_EVIDENCE_\d+',name):
    st=name.split('_')[0]
    out=a.get('outputs') or {}
    for v in (out.get(st.lower()+'_evidence_history') or []):
     register(st,v.get('tool'),v)
  nodes=sorted(nodes,key=lambda x: (x.get('start_time') or '',x['depth']))
  # Determine path from the current selected trace, not a historic notebook.
  canonical=['SP01','SP02','SP03','SP04','SP05','SP06','SP07','SP08','DIRECT_JOIN','LOCAL_JOIN','CU_JOIN','SUPERVISOR']
  executed={n['name'] for n in nodes}
  observed_path=[name for name in canonical if name in executed]
  if 'SP01' not in observed_path or 'SUPERVISOR' not in observed_path:
   raise ValueError(f'{sid}: SP01 or Supervisor absent in selected trace')
  expected_path=hist[sid].get('observed_path',[])
  if set(observed_path)!=set(expected_path):
   raise ValueError(f'{sid}: selected trace route differs from notebook route {observed_path} vs {expected_path}')
  # Operational stage display is entirely recorded; supervisor and specialist state
  # come from the same root trace, not from post-run ground truth.
  for key,label in [('sp01_localization_1','SP01 orientation'),('sp01_evidence_cycle_1','SP01 evidence cycle'),('sp01_localization_2','SP01 localization'),('sp01_output','SP01 handover')]:
   if key in o:stages.append({'key':key,'label':label,'agent':'SP01','kind':'localization' if 'localization' in key else 'evidence' if 'cycle' in key else 'handover'})
  for k in [f'sp{i:02d}_output' for i in range(2,9)]:
   if k in o:stages.append({'key':k,'label':f'{k[:4].upper()} specialist review','agent':k[:4].upper(),'kind':'specialist'})
  for key,label in [('supervisor_observe_1','Supervisor orientation'),('supervisor_evidence_plan','Supervisor evidence plan'),('supervisor_evidence_analysis','Supervisor correlation'),('supervisor_output','Supervisor final finding')]:
   if key in o:stages.append({'key':key,'label':label,'agent':'SUPERVISOR','kind':'supervisor'})
  # Do not include sp01 evidence-cycle raw telemetry in stage (is kept on disk)
  # to prevent duplicate payload and reserve loaded stage for narrative evidence.
  stage_data={k:o.get(k) for k in ['sp01_localization_1','sp01_localization_2','sp01_output','supervisor_observe_1','supervisor_evidence_plan','supervisor_evidence_analysis','supervisor_output']}
  stage_data['sp01_evidence_cycle_1']={key:{'reason':v.get('reason'),'evidence_id':(v.get('evidence') or {}).get('evidence_id'),'tool':(v.get('evidence') or {}).get('tool')} for key,v in (o.get('sp01_evidence_cycle_1') or {}).items()}
  for i in range(2,9):
   k=f'sp{i:02d}_output'
   if k in o:stage_data[k]=o[k]
  su=o['supervisor_output']
  # Keep the original Supervisor's structured knowledge-grounding analysis in
  # stage_data['supervisor_output']. It is separate from withheld retrieved
  # document passages, and must never be synthesized or re-authored.
  kb=su.get('knowledge_base_contribution')
  if not isinstance(kb,dict) or 'used' not in kb:
   raise ValueError(f'{sid}: missing recorded Supervisor RAG contribution contract')
  # Compare timestamp stem against latest saved notebook export receipt.
  original_ref=(hist[sid].get('langsmith_trace_path_reported_in_notebook') or '')
  matching_export=(SOURCES[sid].split('_full_trace_')[-1].replace('(1).json','') in original_ref)
  if not matching_export:raise ValueError(f'{sid}: selected export does not match UPDATED notebook receipt')
  record={
   'scenario_id':sid,'order':order,'title':TITLES[sid], 'exported_at_utc':raw.get('exported_at_utc'),'source_filename':p.name,'source_sha256':source_sha,'root_run_id':r.get('id'),'trace_id':raw['traces'][0].get('trace_id'),
   'source_bytes':p.stat().st_size,'root_status':r.get('status'),'run_status':o.get('run_status'), 'recorded_execution_mode':o.get('execution_mode'),
   'trace_start_utc':r.get('start_time'),'trace_end_utc':r.get('end_time'),'trace_duration_seconds':duration(r.get('start_time'),r.get('end_time')),
   'scenario_window':o.get('public_case',{}), 'data_inventory':o.get('frozen_data_inventory',{}),
   'route_family':o.get('route_family'),'route_nodes':observed_path,'observed_nodes':nodes,'stages':stages,'stage_data':stage_data,
   'ml_evidence_id':next((v['evidence_id'] for v in en.values() if v['tool']=='ml_specialist_summary'),None),
   'network_evidence_id':next((v['evidence_id'] for v in en.values() if v['tool']=='telemetry_network_overview'),None),
   'topology_evidence_id':next((v['evidence_id'] for v in en.values() if v['tool']=='telemetry_topology'),None),
   'evidence_index':list(en.values()), 'recorded_warnings':{k:o.get(k,[]) for k in ['runtime_warnings','parent_runtime_warnings','supervisor_runtime_warnings']},
   'saved_postrun_evaluation':{'run_status':hist[sid].get('run_status'),'deterministic_status':hist[sid].get('deterministic_status'),'path_check':hist[sid].get('path_check'),'supervisor_schema':hist[sid].get('supervisor_schema'),'judge_status':hist[sid].get('judge_status'),'judge_score_out_of_5':hist[sid].get('overall_judge_score_out_of_5'),'structured_exact_match_rate':hist[sid].get('structured_exact_match_rate'),'notebook_source_cell':hist[sid].get('notebook_cell_index_zero_based'),'reported_trace_basename':Path(original_ref).name,'matches_selected_trace_filename':matching_export},
   'derived_display':{'incident_present':su.get('incident_present'), 'fault_family':su.get('root_cause_family'),'scope_class':su.get('scope_class'),'max_severity':su.get('max_severity'),'target_site_id':su.get('target_site_id'),'target_cu_domain_id':su.get('target_cu_domain_id'),'incident_start_utc':su.get('incident_start_utc'),'incident_end_utc':su.get('incident_end_utc'),'diagnosis':su.get('diagnosis'),'target_5qi':su.get('target_5qi'),'root_cause_assessment':su.get('root_cause_assessment')}
  }
  gzip_json(CASES/(sid+'.json.gz'),record)
  manifest['cases'].append({'scenario_id':sid,'title':TITLES[sid], 'source_filename':p.name,'source_sha256':source_sha,'source_bytes':p.stat().st_size,'selected_export_utc':raw.get('exported_at_utc'),'root_run_id':r.get('id'),'trace_duration_seconds':record['trace_duration_seconds'],'case_file':f'data/cases/{sid}.json.gz','evidence_artifacts':len(en),'observed_trace_nodes':len(nodes),'route_family':record['route_family'],'incident_present':su.get('incident_present'),'scope_class':su.get('scope_class'),'fault_family':su.get('root_cause_family'),'notebook_evaluation_matches_selected_trace':matching_export})
  print('  ',len(nodes),'nodes,',len(en),'distinct evidence records,', len(stages),'replay stages; exported=',raw.get('exported_at_utc'),'eval same-export:',matching_export,flush=True)
  del raw
 with open(DATA/'manifest.json','w',encoding='utf-8') as w:json.dump(manifest,w,indent=2)
 print('COMPLETE. Evidence records:',sum(c['evidence_artifacts'] for c in manifest['cases']))

if __name__=='__main__':main()
