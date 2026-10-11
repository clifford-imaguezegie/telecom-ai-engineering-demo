"""V1.3 visitor onboarding, trace-backed timing, agent naming, and safe UI review."""
import gzip
import json
import runpy
import sys
from pathlib import Path
import pytest

from presentation import agent_label, agent_execution_rows, benchmark_summary, format_duration
from storyboard import build_story, workflow_svg
from test_ui_smoke_without_streamlit import APP, MockStreamlit

ROOT=Path(__file__).resolve().parents[1]
IDS=json.loads((ROOT/'data/manifest.json').read_text())['scenario_order']


def load(sid):
    return json.load(gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt'))


def test_three_public_benchmarks_are_true_of_saved_executions():
    stats=benchmark_summary(load(x) for x in IDS)
    assert (stats['health_assessment_under_1min'],stats['health_assessment_total'])==(9,9)
    assert (stats['localisation_under_2min'],stats['localisation_total'])==(8,8)
    assert (stats['incident_rca_under_5min'],stats['incident_total'])==(8,8)
    assert 20 < stats['sp01_max_seconds'] < 60
    assert 270 < stats['incident_max_seconds'] < 300


@pytest.mark.parametrize('sid',IDS)
def test_each_agent_timing_and_tool_list_is_trace_backed(sid):
    case=load(sid)
    rows=agent_execution_rows(case)
    saved_agents={n['name'] for n in case['observed_nodes']
                  if n.get('depth')==1 and n.get('run_type')=='chain'}
    assert {r['ID'] for r in rows}==saved_agents&{'SP01','SP02','SP03','SP04','SP05','SP06','SP07','SP08','SUPERVISOR'}
    assert rows[0]['Agent']=='Network Health & Localisation Agent'
    for r in rows:
        node=next(n for n in case['observed_nodes'] if n.get('name')==r['ID'] and n.get('depth')==1)
        assert r['Agent runtime']==format_duration(node['duration_seconds'])
        assert r['Purpose']
        assert r['LLM calls']>=0
        if r['ID']=='SP01':
            assert r['Recorded tool outputs']>=4
            assert 'ML Fault-Family Prediction' in r['Tools used']
            assert 'Network Overview Telemetry' in r['Tools used']


def test_duration_units_are_legible():
    assert format_duration(17.195)=='17s'
    assert format_duration(168.2)=='2m 48s'
    assert format_duration(272.936)=='4m 33s'
    assert format_duration(None)=='—'


@pytest.mark.parametrize('agent', ['SP01','SP02','SP03','SP04','SP05','SP06','SP07','SP08','SUPERVISOR'])
def test_descriptive_agent_name_retains_trace_identifier(agent):
    name=agent_label(agent)
    assert 'Agent' in name or 'Supervisor' in name
    assert agent not in name
    assert agent in agent_label(agent,include_id=True)


def test_workflow_uses_readable_roles_and_keeps_ids():
    case=load('M05I0003')
    def evidence(eid):
        ref=next(e for e in case['evidence_index'] if e['evidence_id']==eid)
        return json.load(gzip.open(ROOT/ref['file'],'rt'))
    story=build_story(case,evidence)
    svg=workflow_svg(case['route_family'],story,4)
    for text in ['Network Health','Accessibility KPI','Cell &amp; Peer','Radio Analysis',
                 'Processing','Transport','Configuration','RCA Supervisor','ML + telemetry','Config evidence']:
        assert text in svg


def test_intro_and_close_show_on_landing_page(monkeypatch):
    stub=MockStreamlit('Guided Operations Demo','M05I0003')
    displayed=[]
    stub.markdown=lambda val,*a,**k:displayed.append(str(val))
    stub.caption=lambda val,*a,**k:displayed.append(str(val))
    stub.subheader=lambda val,*a,**k:displayed.append(str(val))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    text='\n'.join(displayed)
    for phrase in ['What is this?', 'Demonstrated investigation milestones',
                   '9/9 recorded scenarios','8/8 incident scenarios',
                   'The full solution architecture and design explanation are on **Platform Overview**',
                   'From network data to actionable engineering intelligence',
                   'not production SLAs']:
        assert phrase in text


def test_library_selector_is_visible_with_nonempty_default(monkeypatch):
    sid='M05I0003'
    stub=MockStreamlit('Scenario Library',sid)
    seen=[]
    old=stub.selectbox
    def capture(label, options, **kwargs):
        seen.append((label,options,kwargs))
        return old(label,options,**kwargs)
    stub.selectbox=capture
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    matching=[(label,opts,kwargs) for label,opts,kwargs in seen if label=='Choose a recorded investigation']
    assert matching and len(matching[0][1])==9
    assert stub.session_state['library_case_selection']==sid
    assert stub.session_state['selected_scenario']==sid


def test_rca_page_shows_agent_execution_and_inference(monkeypatch):
    stub=MockStreamlit('Root Cause Analysis','M05I0005')
    sections=[]
    stub.subheader=lambda v,*a,**k:sections.append(str(v))
    stub.dataframe=lambda frame,*a,**k:sections.append(frame)
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    assert any('execution time & tools' in s for s in sections if isinstance(s,str))
    frames=[x for x in sections if not isinstance(x,str) and hasattr(x,'columns')]
    assert any('LLM inference (spans)' in list(f.columns) and 'Tools used' in list(f.columns) for f in frames)


def test_platform_overview_is_a_real_start_page(monkeypatch):
    stub=MockStreamlit('Platform Overview','M05I0003')
    messages=[]
    stub.markdown=lambda val,*a,**kw:messages.append(str(val))
    stub.subheader=lambda val,*a,**kw:messages.append(str(val))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    page='\n'.join(messages)
    assert 'Solution Architecture — How the Investigation Works' in page
    for required in ['Network Health &amp; Localisation Agent',
                     'ML prediction: Fault family','ML prediction: Fault scope',
                     'Network Overview Telemetry','Network Event Telemetry',
                     'RCA Supervisor &amp; Evidence Synthesis',
                     'Curated Telecom Knowledge Base',
                     'Evidence-Grounded Root Cause Analysis']:
        assert required in page


def test_guided_playback_has_one_agent_drilldown_call():
    import ast
    tree=ast.parse(APP.read_text('utf-8'))
    player=next(node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name=='guided_operations_player')
    calls=[n for n in ast.walk(player) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='guided_agent_drilldown']
    assert len(calls)==1, 'Duplicate drill-down widgets can crash Streamlit with repeated keys'


def test_scenario_dropdown_is_high_contrast_and_preselected():
    source=APP.read_text('utf-8')
    assert '[data-testid="stSidebar"] *{color:#eef4fa}' not in source
    assert '[data-baseweb="select"] > div' in source
    assert 'border:2px solid #80cbd0' in source
    assert "'Select scenario ▾'" in source
    assert "st.session_state['selected_scenario']='M05I0003'" in source
