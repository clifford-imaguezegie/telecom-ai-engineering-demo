"""Offline storyboard and workflow contract tests; no UI/framework or model dependency."""
import gzip
import json
from pathlib import Path
import pytest
from storyboard import AGENT_ROLES, build_story, workflow_svg

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'data/manifest.json').read_text())


def load_case(sid):
 with gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt',encoding='utf-8') as f:
  return json.load(f)


def build(c):
 def loader(eid):
  record=next(e for e in c['evidence_index'] if e['evidence_id']==eid)
  with gzip.open(ROOT/record['file'],'rt',encoding='utf-8') as f:
   return json.load(f)
 return build_story(c,loader)


@pytest.mark.parametrize('sid',MANIFEST['scenario_order'])
def test_each_storyboard_binds_to_original_evidence_and_route(sid):
 c=load_case(sid)
 beats=build(c)
 assert len(beats)>=12
 assert beats[0]['title']=='Network scan initiated'
 assert beats[-1]['agent']=='FINAL'
 assert 'Investigation report' in beats[-1]['title']
 assert beats[-1]['output']
 assert [b['sequence'] for b in beats]==list(range(1,len(beats)+1))
 assert all(b['source'] and b['stage_index']<len(c['stages']) for b in beats)
 references={e['evidence_id'] for e in c['evidence_index']}
 assert {b['evidence_id'] for b in beats if b['evidence_id']} <= references
 assert {b['evidence_id'] for b in beats if b['kind']=='tool'}==references
 assert any(b['title'].startswith('Issue identified') or b['title'].startswith('No material issue') for b in beats)
 assert any(b['kind']=='scan' for b in beats)
 assert any(b['kind']=='tool' for b in beats)
 assert any(b['kind']=='join' for b in beats)
 svg=workflow_svg(c['route_family'],beats,5)
 assert '<svg' in svg and 'IN FOCUS' in svg
 assert 'recorded LangGraph' in svg
 assert 'RCA Supervisor' in svg
 assert 'SP01' not in svg
 for b in beats:
  assert b['agent'] in AGENT_ROLES
  assert b['action']
  assert b['output']
  if b['evidence_id']:
   assert b['source'].startswith('LangSmith recorded tool output')


@pytest.mark.parametrize('sid',MANIFEST['scenario_order'])
def test_branch_routing_and_rag_are_not_fabricated(sid):
 c=load_case(sid);beats=build(c)
 agents={b['agent'] for b in beats}
 kb=c['stage_data']['supervisor_output']['knowledge_base_contribution']
 rag=[b for b in beats if b['kind']=='rag']
 if c['route_family']=='LOCAL_SPECIALISTS':
  assert {f'SP{i:02}' for i in range(2,8)} <= agents
  assert 'LOCAL_JOIN' in agents and 'SP08' not in agents
  assert sum(b['kind']=='feedback' for b in beats)==6
 elif c['route_family']=='CU_SPECIALIST':
  assert 'SP08' in agents and 'CU_JOIN' in agents
  assert 'SP02' not in agents
  assert sum(b['kind']=='feedback' for b in beats)==1
 else:
  assert sid=='M05I0017'
  assert 'DIRECT_JOIN' in agents and 'SP08' not in agents and 'SP04' not in agents
 assert len(rag)==(2 if kb['used'] else 0)
 if rag:
  assert kb['queries'][0] in rag[0]['input']
  assert kb['mechanism_summary'][0] in rag[0]['output']
  assert 'SUPPORTING' in rag[0]['action']
  assert kb['discriminating_observations_expected'][0] in rag[1]['action']


def test_radio_analysis_has_recorded_calls_and_feedback():
 c=load_case('M05I0002');beats=build(c)
 radio=[b for b in beats if b['agent']=='SP04']
 assert len(radio)>=4
 assert radio[0]['kind']=='dispatch'
 assert radio[-1]['kind']=='feedback'
 assert 'SINR' in radio[-1]['output']
 assert {b['source'].split(' · ')[0] for b in radio if b['kind']=='tool'}=={'LangSmith recorded tool output'}
 assert {e['tool'] for e in c['evidence_index'] if e['stage']=='SP04'}=={'telemetry_radio_state','telemetry_resource_state'}


def test_curated_private_passages_never_enter_storyboard():
 c=load_case('M05I0005');beats=build(c)
 text=json.dumps(beats).lower()
 assert 'curated knowledge' in text
 assert 'raw passage' not in text
 assert 'private book' not in text
 assert 'full retrieved passage' not in text
