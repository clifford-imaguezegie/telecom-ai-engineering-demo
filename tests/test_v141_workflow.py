"""V1.4.1 laptop-readable stage focus; no fabricated routes or new execution."""
import gzip
import json
from pathlib import Path
from html import escape
import pytest
from storyboard import build_story,workflow_svg,_recorded_route,AGENT_ROLES

ROOT=Path(__file__).resolve().parents[1]
IDS=json.loads((ROOT/'data/manifest.json').read_text('utf-8'))['scenario_order']

def story_for(sid):
    case=json.load(gzip.open(ROOT/'data'/'cases'/f'{sid}.json.gz','rt'))
    def evidence(eid):
        record=next(e for e in case['evidence_index'] if e['evidence_id']==eid)
        return json.load(gzip.open(ROOT/record['file'],'rt'))
    return case,build_story(case,evidence)

@pytest.mark.parametrize('sid',IDS)
def test_readable_three_card_focus_and_full_route(sid):
    case,beats=story_for(sid)
    route=_recorded_route(beats)
    assert route[0]=='SP01' and route[-1]=='FINAL'
    for idx in (0,len(beats)//2,len(beats)-1):
        html=workflow_svg(case['route_family'],beats,idx)
        overview=workflow_svg(case['route_family'],beats,idx,mode='overview')
        assert html.count('class="agent ') == 3
        assert 'IN FOCUS' in html
        assert 'RECORDED AGENT WORKFLOW' in html
        assert 'font-size:16px' in html
        assert 'viewBox="0 0 1345 395"' not in html
        assert 'grid-template-columns:minmax(0,1fr)' in html
        assert 'Original recorded LangGraph' in html
        assert 'FULL RECORDED ROUTE' in overview
        assert overview.count('class="route-chip ') == len(route)
        assert escape(AGENT_ROLES['SUPERVISOR']) in overview
        assert 'SP01' not in html
        assert 'Parallel branches' not in html
        assert 'Sequential specialist investigation' in html if case['route_family']=='LOCAL_SPECIALISTS' else True

@pytest.mark.parametrize('sid',IDS)
def test_prev_next_follows_first_occurrence_in_recorded_story(sid):
    case,beats=story_for(sid)
    route=_recorded_route(beats)
    for idx,beat in enumerate(beats):
        html=workflow_svg(case['route_family'],beats,idx)
        location=route.index(beat['agent'])
        assert escape(AGENT_ROLES[beat['agent']]) in html or beat['agent'] in ('LOCAL_JOIN','CU_JOIN','DIRECT_JOIN')
        if location == 0:
            assert 'Investigation start' in html
        if location == len(route)-1:
            assert 'Investigation complete' in html


def test_invalid_mode_and_index_rejected():
    case,beats=story_for('M05I0003')
    with pytest.raises(ValueError):
        workflow_svg(case['route_family'],beats,0,mode='animated_live')
    with pytest.raises(ValueError):
        workflow_svg(case['route_family'],beats,len(beats))
