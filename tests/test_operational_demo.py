"""Guided replay invariants: no fabricated polling, execution, or source outputs."""
import gzip
import json
from pathlib import Path
import pytest
from operational_demo import (director_cut, guided_sequence, get_run_durations,
                              event_trace_offset, format_clock, sp01_tools_unlocked,
                              available_agents)
from storyboard import build_story

ROOT=Path(__file__).resolve().parents[1]
IDS=['M05I0017','M05I0002','M05I0003','M05I0004','M05I0005','M05I0006','M05I0008','M05I0016','M05I0019']

def load(sid):
    return json.load(gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt',encoding='utf-8'))

def story(c):
    def loader(eid):
        e=next(e for e in c['evidence_index'] if e['evidence_id']==eid)
        return json.load(gzip.open(ROOT/e['file'],'rt',encoding='utf-8'))
    return build_story(c,loader)

@pytest.mark.parametrize('sid',IDS)
def test_directors_cut_preserves_sp01_four_inputs_agent_reports_and_report(sid):
    c=load(sid)
    beats=director_cut(c,story(c))
    all_evidence={e['evidence_id'] for e in c['evidence_index']}
    assert all(b['evidence_id'] in all_evidence for b in beats if b.get('evidence_id'))
    assert beats[0]['agent']=='SP01' and beats[-1]['agent']=='FINAL'
    assert [b['kind'] for b in beats if b['agent']=='SP01'].count('handover')==1
    tools={b['source'].rsplit(' · ',1)[-1] for b in beats if b['agent']=='SP01' and b['kind']=='tool'}
    assert {'ml_specialist_summary','ml_scope_probabilities','telemetry_network_overview','telemetry_events'} <= tools
    assert not any(b['agent']=='SUPERVISOR' and b['kind']=='rag' for b in beats) if sid=='M05I0017' else any(b['agent']=='SUPERVISOR' and b['kind']=='rag' for b in beats)
    for specialist in available_agents(c):
        if specialist.startswith('SP') and specialist!='SP01':
            assert any(b['agent']==specialist and b['kind']=='dispatch' for b in beats)
            assert any(b['agent']==specialist and b['kind']=='feedback' for b in beats)
    assert 'private book' not in json.dumps(beats).lower()

@pytest.mark.parametrize('sid',IDS[1:])
def test_healthy_to_incident_replay_is_two_distinct_runs(sid):
    healthy,incident=load('M05I0017'),load(sid)
    sequence=guided_sequence(healthy,story(healthy),incident,story(incident),True)
    ids=[e['scenario_id'] for e in sequence]
    assert ids.count('M05I0017')>0 and ids.count(sid)>0
    assert ids==['M05I0017']*ids.count('M05I0017')+[sid]*ids.count(sid)
    assert ids[0]=='M05I0017' and ids[-1]==sid
    assert sequence[-1]['beat']['agent']=='FINAL'
    # Two original scenarios, not a synthetic continuous 15-minute network timeline.
    assert len({healthy['trace_id'],incident['trace_id']})==2
    first=next(i for i,e in enumerate(sequence) if e['scenario_id']==sid)
    assert 'ml_specialist_summary' not in sp01_tools_unlocked(sequence,first)
    ml_i=next(i for i,e in enumerate(sequence) if e['scenario_id']==sid and e['beat']['source'].endswith(' · ml_specialist_summary'))
    assert 'ml_specialist_summary' in sp01_tools_unlocked(sequence,ml_i)
    assert 'ml_scope_probabilities' not in sp01_tools_unlocked(sequence,ml_i)

@pytest.mark.parametrize('sid',IDS)
def test_exact_timers_come_from_actual_trace(sid):
    c=load(sid)
    metrics=get_run_durations(c)
    assert metrics['total']==c['trace_duration_seconds']
    assert metrics['sp01']>0 and metrics['sp01']<=metrics['total']
    beats=story(c)
    handover=next(b for b in beats if b['agent']=='SP01' and b['kind']=='handover')
    offset=event_trace_offset(c,handover)
    assert offset is not None and offset>=metrics['sp01']-.2
    assert event_trace_offset(c,beats[0]) is None
    assert abs(event_trace_offset(c,beats[-1])-metrics['total'])<.2
    assert format_clock(metrics['total']).count(':')==1


def test_healthy_only_route_no_rag_or_specialists():
    c=load('M05I0017')
    beats=guided_sequence(c,story(c),None,[],True)
    assert {b['scenario_id'] for b in beats}=={'M05I0017'}
    assert not any(e['beat']['kind']=='rag' for e in beats)
    assert not any(e['beat']['agent']=='SP08' for e in beats)
