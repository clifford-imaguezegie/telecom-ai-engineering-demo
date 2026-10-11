"""Data-only replay checks. No Streamlit needed, no network or model calls."""
import gzip
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
MANIFEST=json.loads((DATA/'manifest.json').read_text())


def get_case(sid):
 with gzip.open(DATA/'cases'/f'{sid}.json.gz','rt',encoding='utf-8') as f:return json.load(f)


def read_evidence(ref):
 with gzip.open(ROOT/ref['file'],'rt',encoding='utf-8') as f:return json.load(f)


def test_exactly_nine_scenarios_and_corrected_priorities():
 ids=MANIFEST['scenario_order'];assert len(ids)==len(set(ids))==9
 assert {x['scenario_id'] for x in MANIFEST['cases']}==set(ids)
 sources={v['scenario_id']:v['source_filename'] for v in MANIFEST['cases']}
 assert '20261011T000245' in sources['M05I0004']
 assert '20261010T235443' in sources['M05I0005']
 assert '20261010T234923' in sources['M05I0008']
 assert '20261010T233337' in sources['M05I0016']


@pytest.mark.parametrize('sid',MANIFEST['scenario_order'])
def test_each_selected_trace_integrity(sid):
 c=get_case(sid)
 assert c['scenario_id']==sid
 assert c['stage_data']['supervisor_output']['scenario_id']==sid
 assert c['source_filename'].startswith(sid+'_')
 assert len(c['source_sha256'])==64
 assert c['trace_duration_seconds']>0
 assert c['recorded_execution_mode']=='LIVE_VALIDATION'
 assert c['derived_display']['incident_present']==(sid!='M05I0017')
 assert 'SP01' in c['route_nodes'] and 'SUPERVISOR' in c['route_nodes']
 assert len(c['observed_nodes'])>=30
 assert all(a.get('name') for a in c['observed_nodes'])
 assert all(x['key'] in c['stage_data'] for x in c['stages'])
 assert c['stages'][-1]['key']=='supervisor_output'
 assert c['stage_data']['sp01_localization_1']['terminal_materiality_decision'] is False


@pytest.mark.parametrize('sid',MANIFEST['scenario_order'])
def test_recorded_kpi_granularity_and_evidence_paths(sid):
 c=get_case(sid)
 all_ids=set()
 for ev in c['evidence_index']:
  assert ev['evidence_id'] not in all_ids
  all_ids.add(ev['evidence_id'])
  d=read_evidence(ev)
  assert d['evidence_id']==ev['evidence_id'] and d['tool']==ev['tool']
  assert d['stage']==ev['stage']
  assert (ROOT/ev['file']).resolve().is_relative_to((DATA/'evidence').resolve())
  assert isinstance(d['result'],(list,dict))
 ev=next(x for x in c['evidence_index'] if x['tool']=='telemetry_network_overview')
 data=read_evidence(ev)['result']
 rows=data['subnetwork_kpis']
 assert len(rows)==48
 assert {x['five_qi'] for x in rows}=={'1','5','9'}
 assert len({x['interval_start_utc'] for x in rows})==16
 cell=data['cell_kpis']
 assert cell['representation']=='LOSSLESS_COLUMNAR_TIME_SERIES'
 assert cell['source_row_count']==1440
 assert sum(len(x['timestamps']) for x in cell['groups'])==1440
 assert c['scenario_window']['pm_interval_minutes']==15


def test_routes_match_recorded_specialist_branches():
 for sid in MANIFEST['scenario_order']:
  c=get_case(sid);xs=set(c['route_nodes'])
  if sid=='M05I0017':assert 'DIRECT_JOIN' in xs and not ({'SP02','SP08'}&xs)
  elif c['route_family']=='LOCAL_SPECIALISTS':
   assert set(f'SP{i:02d}' for i in range(2,8)) <= xs and 'LOCAL_JOIN' in xs
   assert 'SP08' not in xs
  else:assert 'SP08' in xs and 'CU_JOIN' in xs and 'LOCAL_JOIN' not in xs


def test_postrun_scores_never_in_operational_stage_data():
 for sid in MANIFEST['scenario_order']:
  c=get_case(sid)
  text=json.dumps(c['stage_data'])
  assert 'judge_score_out_of_5' not in text
  assert 'structured_exact_match_rate' not in text
  assert c['saved_postrun_evaluation']['matches_selected_trace_filename'] is True


def test_curated_knowledge_base_passages_are_not_distributed():
 for sid in MANIFEST['scenario_order']:
  c=get_case(sid)
  for ev in c['evidence_index']:
   if ev['tool']!='supervisor_private_knowledge_search':continue
   assert ev['kind']=='restricted_provenance_only'
   r=read_evidence(ev)['result']
   assert isinstance(r.get('results'),str) and 'WITHHELD' in r['results']
   assert isinstance(r.get('results_count'),int)


def test_global_manifest_counts():
 assert sum(x['evidence_artifacts'] for x in MANIFEST['cases'])==126
 assert sum(x['observed_trace_nodes'] for x in MANIFEST['cases'])==799
 assert sum(bool(x['incident_present']) for x in MANIFEST['cases'])==8


@pytest.mark.parametrize('sid',MANIFEST['scenario_order'])
def test_supervisor_rag_impact_is_retained_separately_from_raw_passages(sid):
 c=get_case(sid)
 kb=c['stage_data']['supervisor_output']['knowledge_base_contribution']
 assert isinstance(kb,dict)
 for field in ['used','queries','supported_hypotheses','competing_hypotheses_discussed',
               'mechanism_summary','discriminating_observations_expected',
               'incident_observations_confirming_mechanism','incident_observations_missing',
               'contribution_type','evidence_weight','limitations']:
  assert field in kb, f'Missing {field} in {sid}'
 if sid=='M05I0017':
  assert kb['used'] is False
  assert kb['queries']==[]
  assert kb['contribution_type']=='NONE'
 else:
  assert kb['used'] is True
  assert kb['queries'] and kb['mechanism_summary']
  assert kb['evidence_weight']=='SUPPORTING'
  assert kb['contribution_type'] in {'MECHANISM_DISCRIMINATION','MECHANISM_PLAUSIBILITY'}
