"""V1.4 release tests: truthful agent execution, immutable evidence, director cut."""
from pathlib import Path
import gzip
import json
import runpy
import sys
from datetime import datetime
import pytest
from storyboard import build_story,workflow_svg
from operational_demo import executive_sequence,guided_sequence
from test_ui_smoke_without_streamlit import MockStreamlit,APP

ROOT=Path(__file__).resolve().parents[1]
IDS=json.loads((ROOT/'data/manifest.json').read_text())['scenario_order']

def case(sid):return json.load(gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt'))
def beats(c):
 def evidence(eid):
  record=next(e for e in c['evidence_index'] if e['evidence_id']==eid)
  return json.load(gzip.open(ROOT/record['file'],'rt'))
 return build_story(c,evidence)

@pytest.mark.parametrize('sid',['M05I0002','M05I0003','M05I0006','M05I0019'])
def test_sequential_recorded_specialist_spans(sid):
 c=case(sid)
 spans=[next(n for n in c['observed_nodes'] if n.get('name')==f'SP{i:02d}' and n.get('depth')==1 and n.get('run_type')=='chain') for i in range(2,8)]
 for a,b in zip(spans,spans[1:]):
  assert datetime.fromisoformat(a['end_time']) <= datetime.fromisoformat(b['start_time'])
 svg=workflow_svg(c['route_family'],beats(c),len(beats(c))-1)
 # The visual now represents each successive specialist handover, not fan-out from SP01.
 assert '<svg' in svg and 'IN FOCUS' in svg
 overview=workflow_svg(c['route_family'],beats(c),len(beats(c))-1,mode='overview')
 assert 'Specialist Evidence Consolidation' in overview
 assert 'Parallel branches' not in svg and 'Sequential specialist investigation' in svg

@pytest.mark.parametrize('sid',IDS)
def test_exec_uses_original_beats_only_and_keeps_last_report(sid):
 h=case('M05I0017');c=case(sid)
 full=guided_sequence(h,beats(h),c if sid!='M05I0017' else None,beats(c) if sid!='M05I0017' else [],True)
 cut=executive_sequence(full)
 assert cut and all(any(x is original for original in full) for x in cut)
 assert cut[-1]['beat']['agent']=='FINAL'
 if sid!='M05I0017':
  assert any(x['beat']['agent']=='SUPERVISOR' for x in cut)
  tools=[x['beat'].get('source','') for x in cut]
  for needed in ['ml_specialist_summary','ml_scope_probabilities','telemetry_network_overview','telemetry_events']:
   assert any(z.endswith(' · '+needed) for z in tools), needed
 assert len(cut)<=16

@pytest.mark.parametrize('page',['Guided Operations Demo','Root Cause Analysis','Engineering Evidence'])
def test_v14_pages_render_without_exception(monkeypatch,page):
 stub=MockStreamlit(page,'M05I0003')
 monkeypatch.setitem(sys.modules,'streamlit',stub)
 runpy.run_path(str(APP),run_name='__main__')


def test_public_app_has_external_brand_and_no_module_banner():
 src=APP.read_text('utf-8')
 assert "st.sidebar.markdown('### ◈ TEAD AI')" in src
 assert 'TEAD AI · TELECOM ENGINEERING INTELLIGENCE' in src
 assert 'Telecom AI Engineering / Module 5' not in src
 assert 'TELECOM AI ENGINEERING • MODULE 5' not in src
 assert 'Agentic Investigation Replay' in src
