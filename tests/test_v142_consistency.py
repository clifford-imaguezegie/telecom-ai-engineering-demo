"""V1.4.2 regression cases for externally reproduced live browser issues.

These tests validate logic and saved presentation content. Browser acceptance
at exact viewport dimensions remains a separate release check.
"""
import gzip
import json
import runpy
import sys
from pathlib import Path
import pytest
from test_ui_smoke_without_streamlit import APP, MockStreamlit
from storyboard import build_story, workflow_overview_html, _recorded_route

DATA=APP.parent/'data'

def load_case(sid):
    return json.load(gzip.open(DATA/'cases'/f'{sid}.json.gz','rt'))

def story(sid):
    case=load_case(sid)
    def evidence(eid):
        item=next(x for x in case['evidence_index'] if x['evidence_id']==eid)
        return json.load(gzip.open(APP.parent/item['file'],'rt'))
    return build_story(case,evidence)

@pytest.mark.parametrize('sid',['M05I0003','M05I0005','M05I0017'])
def test_library_to_evidence_to_rca_retains_same_scenario(monkeypatch,sid):
    """Streamlit discards conditional widget keys between pages; never canonical ID."""
    mock=MockStreamlit('Scenario Library','M05I0003')
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    ns=runpy.run_path(str(APP),run_name='__main__')
    # Browser: visitor changes inline scenario dropdown, firing on_change.
    mock.session_state['library_case_selection']=sid
    ns['sync_scenario_from']('library_case_selection')
    assert mock.session_state['selected_scenario']==sid
    # Browser: user navigates away and Streamlit deletes library widget state.
    mock.session_state.pop('library_case_selection',None)
    mock.session_state['nav_page']='Engineering Evidence'
    page=runpy.run_path(str(APP),run_name='__main__')
    assert page['sid']==sid and page['c']['scenario_id']==sid
    assert mock.session_state['sidebar_scenario_picker']==sid
    mock.session_state['nav_page']='Root Cause Analysis'
    page=runpy.run_path(str(APP),run_name='__main__')
    assert page['sid']==sid and page['c']['scenario_id']==sid
    # Return to Library: inline selector must initialise from canonical state.
    mock.session_state['nav_page']='Scenario Library'
    runpy.run_path(str(APP),run_name='__main__')
    assert mock.session_state['library_case_selection']==sid

@pytest.mark.parametrize('sid',['M05I0017','M05I0003','M05I0005'])
def test_sidebar_selection_stays_canonical_across_navigation(monkeypatch,sid):
    mock=MockStreamlit('Scenario Library','M05I0003')
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    ns=runpy.run_path(str(APP),run_name='__main__')
    mock.session_state['sidebar_scenario_picker']=sid
    ns['sync_scenario_from']('sidebar_scenario_picker')
    page=runpy.run_path(str(APP),run_name='__main__')
    assert page['sid']==sid and page['c']['scenario_id']==sid
    assert mock.session_state['library_case_selection']==sid

@pytest.mark.parametrize('sid',['M05I0017','M05I0003','M05I0005'])
def test_full_route_native_auto_height_and_all_stages(sid):
    beats=story(sid)
    route=_recorded_route(beats)
    html=workflow_overview_html(beats,len(beats)-1)
    assert html.count('class="tread-route-item ') == len(route)
    assert 'tread-route-foot' in html
    assert 'Recorded LangGraph order' in html
    assert 'height:405px' not in html
    assert 'minmax(min(100%,195px),1fr)' in html
    assert 'role="list"' in html
    assert 'recorded stages' in html
    assert all(str(i).zfill(2) in html for i in range(1,len(route)+1))


def test_full_route_uses_native_st_html_in_both_modes():
    src=APP.read_text('utf-8')
    assert src.count('st.html(workflow_overview_html(')==2
    assert "height=405" not in src
    assert "Stage {selected+1}" in (APP.parent/'storyboard.py').read_text('utf-8')


def test_empty_competitor_heading_suppressed_and_original_supervisor_preserved(monkeypatch):
    sid='M05I0005'
    assert not (load_case(sid)['stage_data']['supervisor_output'].get('contradictory_evidence') or [])
    stub=MockStreamlit('Root Cause Analysis',sid)
    rendered=[]
    stub.markdown=lambda content,*a,**kw:rendered.append(str(content))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    assert not any('Weakened competing explanations' in x for x in rendered)
    assert any('Recorded likely fault mechanism' in x for x in rendered)
    assert any('Uncertainty and evidence gaps' in x for x in rendered)


def test_valid_competitor_heading_retained(monkeypatch):
    sid='M05I0003'
    assert load_case(sid)['stage_data']['supervisor_output'].get('contradictory_evidence')
    stub=MockStreamlit('Root Cause Analysis',sid)
    rendered=[]
    stub.markdown=lambda content,*a,**kw:rendered.append(str(content))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    assert any('Weakened competing explanations' in x for x in rendered)
