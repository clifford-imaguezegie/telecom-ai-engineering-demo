"""RC2: callback-first recovery, stale-event immunity, navigation context and chart safety.

These are local simulations, not certification of actual Streamlit Cloud UX.
"""
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from test_v143_seek_regression import InteractiveStreamlit, FragmentRerun, render
from measurement_series import partition_measurements
from release_identity import RELEASE_VERSION


def test_new_release_version_and_navigation_hooks():
    text = (ROOT/'app.py').read_text('utf-8')
    assert RELEASE_VERSION == 'V1.7.5 RC2.2'
    assert "on_click=_restart_guided_player,args=(key,)" in text
    assert "st.rerun()" in text
    assert "on_change=_workspace_changed" in text
    assert "_restore_destination_context()" in text


@pytest.mark.parametrize('scenario', ['M05I0017','M05I0003','M05I0005'])
@pytest.mark.parametrize('engineering', [False,True])
def test_completed_restart_ignores_retired_seek_event(monkeypatch, scenario, engineering):
    mock=InteractiveStreamlit('Guided Operations Demo',scenario,engineering=engineering,
                              incident_only=(scenario!='M05I0017'))
    functions=render(mock,monkeypatch)
    key=next(k for k in mock.session_state if k.startswith('ops_player_'))
    old_seek=key+'_seek'
    last=mock.seek_max[old_seek]
    old_callback=mock.seek_callbacks[old_seek]
    mock.session_state[key].update({'index':last,'started':True,'playing':False,
                                    'presentation_elapsed':31.})
    mock.session_state[old_seek]=last
    mock.click(key+'_restart')
    with pytest.raises(FragmentRerun):
        render(mock,monkeypatch)
    state=mock.session_state[key]
    assert (state['index'],state['started'],state['presentation_elapsed'])==(0,False,0.)
    assert mock.session_state[old_seek]==0
    # Simulate a late old slider event delivered after Restart committed.
    mock.session_state[old_seek]=last
    old_callback[0](*old_callback[1])
    assert mock.session_state[key]['index']==0
    render(mock,monkeypatch)
    latest=key+'_seek_1'
    assert mock.seek_values[latest]==0
    assert not mock.session_state[key]['started']


def test_sidebar_navigation_and_programmatic_routing_signal_top_reset(monkeypatch):
    mock=InteractiveStreamlit('Guided Operations Demo','M05I0003',incident_only=True)
    calls=[]
    mock.components.v1.html=lambda html,**kwargs:calls.append((html,kwargs))
    functions=render(mock,monkeypatch)
    assert not calls
    functions['_workspace_changed']()
    mock.session_state['nav_page']='Network Overview'
    render(mock,monkeypatch)
    assert len(calls)==1
    assert 'scrollTop = 0' in calls[0][0]
    assert calls[0][1]['height']==0
    assert not mock.session_state.get('page_navigation_pending', False)
    render(mock,monkeypatch)
    assert len(calls)==1
    mock.session_state['requested_page']='Platform Overview'
    render(mock,monkeypatch)
    assert len(calls)==2
    assert mock.session_state['nav_page']=='The Challenge'


def test_same_timestamp_missing_dimension_never_plotted():
    group={'static':{'entity_id':'CU_01','metric_name':'DRB.EstabAtt.5QI'},
           'timestamps':['2026-06-13T00:00:00Z']*3,
           'series':{'value_int':[767,123,187],'dimension_5qi':[None,None,None]}}
    frame,parts=partition_measurements(group)
    assert len(frame)==3 and len(parts)==1
    assert not parts[0]['safe_to_plot']
    assert len(parts[0]['frame'])==3


def test_conflicting_recorded_dimensions_rejected():
    group={'static':{'metric_name':'DRB.EstabAtt.5QI'},
           'timestamps':['2026-06-13T00:00:00Z'],
           'series':{'value_int':[7], 'dimension_5qi':['1'], 'dimensions_json':['{"5qi":"9"}']}}
    with pytest.raises(ValueError,match='Conflicting'):
        partition_measurements(group)
