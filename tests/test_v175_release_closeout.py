"""V1.7.5 RC1 — P1 evidence identity and P2 release-closure regressions."""
from pathlib import Path
import gzip
import json
import re
import sys
import pytest
from test_v143_seek_regression import InteractiveStreamlit, FragmentRerun, render

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from measurement_series import partition_measurements
from release_identity import release_build_id, RELEASE_VERSION


def _read(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)


def test_m05i0005_cu_counter_preserves_three_5qi_series():
    c=_read(ROOT/'data/cases/M05I0005.json.gz')
    e=next(x for x in c['evidence_index'] if x['tool']=='telemetry_cu_domain_state')
    response=_read(ROOT/e['file'])['result']['measurements']
    group=next(x for x in response['groups'] if x['static']['metric_name']=='DRB.EstabAtt.5QI'
               and x['static']['entity_id']=='NRCELL_CU_001_1')
    raw, parts=partition_measurements(group)
    assert len(raw)==48
    assert {p['label'] for p in parts}=={'5QI 1','5QI 5','5QI 9'}
    assert all(p['safe_to_plot'] and len(p['frame'])==16 for p in parts)
    expected={'5QI 9':767,'5QI 5':123,'5QI 1':187}
    for p in parts:
        assert p['frame'].iloc[0]['value_int']==expected[p['label']]
        assert p['frame']['interval_start_utc'].is_unique
    # Original source order and original per-observation data are never altered.
    assert raw['value_int'].iloc[:3].tolist()==[767,123,187]
    assert raw['observation_id'].is_unique


def test_all_nine_records_preserve_source_dimensions_for_all_duplicate_groups():
    total_groups=total_observations=total_series=0
    for case_path in sorted((ROOT/'data/cases').glob('*.json.gz')):
        case=_read(case_path)
        for evidence in case['evidence_index']:
            if not evidence['tool'].startswith('telemetry_'):continue
            result=_read(ROOT/evidence['file'])['result']
            if not isinstance(result,dict):continue
            datasets=[v for v in result.values() if isinstance(v,dict) and v.get('groups') is not None]
            if result.get('groups') is not None:datasets=[result]+datasets
            for dataset in datasets:
                for group in dataset['groups']:
                    source_times=group.get('timestamps') or []
                    if len(source_times)==len(set(source_times)):continue
                    raw,parts=partition_measurements(group)
                    total_groups+=1;total_observations+=len(raw);total_series+=len(parts)
                    assert sum(len(p['frame']) for p in parts)==len(raw)
                    assert all(p['safe_to_plot'] for p in parts), (case['scenario_id'],evidence['tool'])
                    assert all(p['frame']['interval_start_utc'].is_unique for p in parts)
    assert (total_groups,total_observations,total_series)==(1120,53760,3360)


def test_ambiguous_identity_fails_closed_without_silent_aggregation():
    group={'static':{'entity_id':'CELL_X','metric_name':'COUNTER'},
           'timestamps':['2026-06-13T00:00:00Z']*2,
           'series':{'observation_id':['A','B'],'value_int':[10,20]}}
    raw,parts=partition_measurements(group)
    assert len(raw)==2 and len(parts)==1
    assert not parts[0]['safe_to_plot']
    assert parts[0]['duplicate_timestamps']=={'2026-06-13T00:00:00Z':2}


def test_dynamic_cause_dimension_is_not_merged():
    group={'static':{'entity_id':'CELL_Y'},
           'timestamps':['2026-06-13T00:00:00Z']*2,
           'series':{'dimension_cause':['causeA','causeB'],
                     'dimensions_json':['{"CAUSE":"causeA"}','{"CAUSE":"causeB"}'],
                     'value_int':[4,7]}}
    raw,parts=partition_measurements(group)
    assert len(raw)==2 and len(parts)==2
    assert {p['label'] for p in parts}=={'Cause causeA','Cause causeB'}
    assert all(p['safe_to_plot'] for p in parts)


def test_release_source_exposes_traceable_identity_and_correct_pm_scope():
    app=(ROOT/'app.py').read_text('utf-8')
    assert '15-minute observation window' not in app
    assert '15-minute network observation window' not in app
    assert 'PM and event telemetry across the scenario observation window' in app
    assert 'partition_measurements(g)' in app
    assert "if not part['safe_to_plot']" in app
    assert 'No rows or dimensions were discarded or silently aggregated.' in app
    assert '.gs-rca-board .gs-evidence{max-height:none' in app
    assert 'COMPLETED · Select Restart' in app
    assert "opts={x:f\"{x}" in app
    assert 'release_build_id()' in app
    assert RELEASE_VERSION=='V1.7.5 RC2'
    assert re.fullmatch(r'[0-9a-f]{12}',release_build_id())
    assert 'field-level comparison records and full judging rubric are not in this public replay' in app


@pytest.mark.parametrize('scenario', ['M05I0003','M05I0005','M05I0017'])
@pytest.mark.parametrize('engineering', [False,True])
def test_five_consecutive_guided_restarts_with_seek_visible(monkeypatch,scenario,engineering):
    # React-like mounted seek values must not overwrite the reset Ready scene.
    mock=InteractiveStreamlit('Guided Operations Demo',scenario,
                              engineering=engineering,incident_only=(scenario!='M05I0017'))
    render(mock,monkeypatch)
    player_key=next(k for k in mock.session_state if k.startswith('ops_player_'))
    original_seek=player_key+'_seek'
    last=mock.seek_max[original_seek]
    seek=original_seek
    for generation in range(1,6):
        mock.session_state[player_key]['index']=last
        mock.session_state[player_key]['started']=True
        mock.session_state[player_key]['presentation_elapsed']=65.
        mock.session_state[seek]=last
        mock.click(player_key+'_restart')
        with pytest.raises(FragmentRerun):render(mock,monkeypatch)
        state=mock.session_state[player_key]
        assert state['index']==0 and not state['started']
        assert state['presentation_elapsed']==0 and not state['playing']
        assert state['seek_generation']==generation
        seek=original_seek+'_'+str(generation)
        render(mock,monkeypatch)
        assert mock.seek_values[seek]==0
        # The old mounted widget remains in session state, but is never read as
        # the next generation's position.
        assert mock.session_state[player_key]['index']==0
