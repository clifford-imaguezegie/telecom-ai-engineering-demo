"""R09: a selected Guided scenario/presentation begins at Ready, not cached scene 1.

These tests model Streamlit's persistent session-state across full app reruns.
They do not substitute for browser acceptance on deployed Streamlit Cloud.
"""
import time
import pytest
from test_v143_seek_regression import InteractiveStreamlit, render


def _player(mock, prefix):
    matches=[k for k in mock.session_state if k.startswith(prefix) and isinstance(mock.session_state[k],dict)]
    assert matches, (prefix, list(mock.session_state))
    return matches[0]


@pytest.mark.parametrize('source,target', [
    ('M05I0003','M05I0017'),
    ('M05I0017','M05I0003'),
    ('M05I0003','M05I0005'),
    ('M05I0005','M05I0003'),
])
@pytest.mark.parametrize('engineering', [False,True])
def test_switching_to_previously_visited_scenario_must_reset_cached_scene(monkeypatch,source,target,engineering):
    mock=InteractiveStreamlit('Guided Operations Demo',source,engineering=engineering,
                              incident_only=False)
    ns=render(mock,monkeypatch)
    suffix='' if engineering else '_executive'
    target_key=f'ops_player_{target}_{target=="M05I0017"}{suffix}'
    # An earlier visit left this target paused on its first visible recorded beat.
    # This is the observed RC2 browser anomaly (1/7 or 1/13 instead of Ready).
    mock.session_state[target_key]={
        'index':1,'playing':False,'started':True,'seconds':3,
        'last_tick':time.monotonic(),'carry':0.,'presentation_elapsed':5.,
    }
    mock.session_state[target_key+'_seek']=1
    mock.session_state['sidebar_scenario_picker']=target
    ns['sync_scenario_from']('sidebar_scenario_picker')
    render(mock,monkeypatch)
    player=mock.session_state[target_key]
    assert player['index']==0 and player['started'] is False
    assert player['playing'] is False and player['presentation_elapsed']==0
    assert player['seek_generation']==1
    assert mock.seek_values[target_key+'_seek_1']==0


@pytest.mark.parametrize('engineering', [False, True])
def test_returning_to_same_scenario_after_other_case_must_reset(monkeypatch,engineering):
    mock=InteractiveStreamlit('Guided Operations Demo','M05I0003',engineering=engineering,
                              incident_only=False)
    ns=render(mock,monkeypatch)
    key=_player(mock,'ops_player_M05I0003_False')
    player=mock.session_state[key]
    player.update(index=1,started=True,playing=False)
    mock.session_state[key+'_seek']=1
    mock.session_state['sidebar_scenario_picker']='M05I0005'
    ns['sync_scenario_from']('sidebar_scenario_picker')
    ns=render(mock,monkeypatch)
    mock.session_state['sidebar_scenario_picker']='M05I0003'
    ns['sync_scenario_from']('sidebar_scenario_picker')
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==0
    assert not mock.session_state[key]['started']


def test_switching_executive_to_previously_used_engineering_resets(monkeypatch):
    mock=InteractiveStreamlit('Guided Operations Demo','M05I0005',engineering=False,
                              incident_only=False)
    render(mock,monkeypatch)
    engineering_key='ops_player_M05I0005_False'
    mock.session_state[engineering_key]={
        'index':1,'playing':False,'started':True,'seconds':3,
        'last_tick':time.monotonic(),'carry':0.,'presentation_elapsed':12.,
    }
    mock.session_state[engineering_key+'_seek']=1
    mock.full_engineering=True
    render(mock,monkeypatch)
    assert mock.session_state[engineering_key]['index']==0
    assert not mock.session_state[engineering_key]['started']
    assert mock.seek_values[engineering_key+'_seek_1']==0


def test_same_scenario_mode_and_page_refresh_does_not_erase_manual_seek(monkeypatch):
    mock=InteractiveStreamlit('Guided Operations Demo','M05I0003',engineering=False,
                              incident_only=False)
    render(mock,monkeypatch)
    key='ops_player_M05I0003_False_executive'
    mock.session_state[key].update(index=4,started=True,playing=False)
    mock.session_state[key+'_seek']=4
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==4
    assert mock.session_state[key]['started']
    mock.session_state['nav_page']='Root Cause Analysis'
    render(mock,monkeypatch)
    mock.session_state['nav_page']='Guided Operations Demo'
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==4
    assert mock.session_state[key]['started']


@pytest.mark.parametrize('target', [
    'M05I0017','M05I0002','M05I0003','M05I0004','M05I0005',
    'M05I0006','M05I0008','M05I0016','M05I0019',
])
@pytest.mark.parametrize('engineering',[False,True])
def test_all_nine_scenarios_initialize_at_ready_after_selection(monkeypatch,target,engineering):
    source='M05I0005' if target!='M05I0005' else 'M05I0003'
    mock=InteractiveStreamlit('Guided Operations Demo',source,engineering=engineering,
                              incident_only=False)
    ns=render(mock,monkeypatch)
    suffix='' if engineering else '_executive'
    key=f'ops_player_{target}_{target=="M05I0017"}{suffix}'
    mock.session_state[key]={
        'index':1,'playing':False,'started':True,'seconds':5,
        'last_tick':time.monotonic(),'carry':0.,'presentation_elapsed':9.,
    }
    mock.session_state[key+'_seek']=1
    mock.session_state['sidebar_scenario_picker']=target
    ns['sync_scenario_from']('sidebar_scenario_picker')
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==0
    assert mock.session_state[key]['started'] is False
    assert mock.session_state[key]['playing'] is False
    assert mock.session_state[key]['presentation_elapsed']==0
    assert mock.seek_values[key+'_seek_1']==0


def test_delayed_slider_event_from_retired_scenario_cannot_undo_initialisation(monkeypatch):
    mock=InteractiveStreamlit('Guided Operations Demo','M05I0003',engineering=False,
                              incident_only=False)
    ns=render(mock,monkeypatch)
    mock.session_state['sidebar_scenario_picker']='M05I0017'
    ns['sync_scenario_from']('sidebar_scenario_picker')
    ns=render(mock,monkeypatch)
    key='ops_player_M05I0017_True_executive'
    old_seek=key+'_seek'
    callback=mock.seek_callbacks[old_seek]
    mock.session_state[key].update(index=1,started=True,playing=False)
    mock.session_state[old_seek]=1
    mock.session_state['sidebar_scenario_picker']='M05I0003'
    ns['sync_scenario_from']('sidebar_scenario_picker')
    ns=render(mock,monkeypatch)
    mock.session_state['sidebar_scenario_picker']='M05I0017'
    ns['sync_scenario_from']('sidebar_scenario_picker')
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==0
    mock.session_state[old_seek]=1
    callback[0](*callback[1])
    assert mock.session_state[key]['index']==0
    assert mock.session_state[key]['started'] is False
