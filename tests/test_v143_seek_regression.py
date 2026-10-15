"""V1.4.3 slider persistence tests — post-Restart bug N02.

These tests simulate Streamlit's frontend-value-then-on_change callback order.
They do not replace an actual browser acceptance test on Streamlit Cloud.
"""
import runpy
import sys
import time

import pytest
from test_ui_smoke_without_streamlit import APP, MockStreamlit


class FragmentRerun(Exception):
    pass


class InteractiveStreamlit(MockStreamlit):
    def __init__(self, page, scenario, *, engineering=True, incident_only=False):
        super().__init__(page, scenario)
        self.full_engineering = engineering
        self.incident_only = incident_only
        self.click_next = set()
        self.seek_callbacks = {}
        self.seek_max = {}
        self.seek_values = {}

    def radio(self, label, options, **kwargs):
        if label == 'Presentation' and self.incident_only and len(options) > 1:
            return options[1]
        return super().radio(label, options, **kwargs)

    def button(self, label, **kwargs):
        key=kwargs.get('key')
        if key in self.click_next:
            self.click_next.remove(key)
            return True
        return False

    def slider(self, label, **kwargs):
        key=kwargs['key']
        self.seek_max[key]=kwargs['max_value']
        self.seek_callbacks[key]=(kwargs['on_change'],kwargs['args'])
        self.seek_values[key]=self.session_state.get(key)
        return self.session_state.get(key)

    def rerun(self, **kwargs):
        raise FragmentRerun(kwargs)

    def drag(self, seek_key, new_value):
        """Browser sends widget update; callback executes *before* rerun."""
        self.session_state[seek_key] = new_value
        callback, args = self.seek_callbacks[seek_key]
        callback(*args)

    def click(self, key):
        self.click_next.add(key)


def render(mock, monkeypatch):
    monkeypatch.setitem(sys.modules, 'streamlit', mock)
    return runpy.run_path(str(APP), run_name='__main__')


@pytest.mark.parametrize('scenario', ['M05I0003', 'M05I0005', 'M05I0017'])
@pytest.mark.parametrize('engineering', [False, True])
@pytest.mark.parametrize('incident_only', [False, True])
def test_guided_post_restart_slider_persists_after_fragment_refresh(monkeypatch, scenario, engineering, incident_only):
    mock=InteractiveStreamlit('Guided Operations Demo',scenario,engineering=engineering,incident_only=incident_only)
    render(mock,monkeypatch)
    key=next(k for k in mock.session_state if k.startswith('ops_player_'))
    seek=key+'_seek'
    last=mock.seek_max[seek]
    assert last>=2
    # Previously completed journey; restart must reset player AND widget state.
    mock.session_state[key]['index']=last
    mock.session_state[key]['started']=True
    mock.session_state[seek]=last
    mock.click(key+'_restart')
    with pytest.raises(FragmentRerun):render(mock,monkeypatch)
    assert mock.session_state[key]['index']==0
    assert mock.session_state[seek]==0
    # Restart remounts the slider under a fresh key, preventing the old
    # browser widget's terminal value from replaying onto the new Ready state.
    seek=seek+'_'+str(mock.session_state[key]['seek_generation'])
    render(mock,monkeypatch)
    assert mock.seek_values[seek]==0
    # Browser user interaction: the saved slider value is authoritative.
    destination=max(1,last//2)
    mock.drag(seek,destination)
    assert mock.session_state[key]['index']==destination
    assert mock.session_state[key]['playing'] is False
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==destination
    assert mock.seek_values[seek]==destination
    # Auto fragment refresh / unrelated widget rerun must not stomp the chosen beat.
    render(mock,monkeypatch)
    assert mock.session_state[seek]==destination
    assert mock.session_state[key]['index']==destination
    # Keyboard equivalent: a one-position arrow-key change must also persist.
    mock.drag(seek,destination+1)
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==destination+1
    assert mock.seek_values[seek]==destination+1
    # Next/Back continue synchronising both the displayed thumb and actual beat.
    if destination+1<last:
        mock.click(key+'_next')
        with pytest.raises(FragmentRerun):render(mock,monkeypatch)
        assert mock.session_state[key]['index']==destination+2
        assert mock.session_state[seek]==destination+2
        mock.click(key+'_back')
        with pytest.raises(FragmentRerun):render(mock,monkeypatch)
        assert mock.session_state[key]['index']==destination+1
        assert mock.session_state[seek]==destination+1


@pytest.mark.parametrize('scenario', ['M05I0003', 'M05I0005', 'M05I0017'])
def test_standalone_post_restart_timeline_persists(monkeypatch,scenario):
    mock=InteractiveStreamlit('Agentic Replay',scenario)
    render(mock,monkeypatch)
    key='cinema_'+scenario
    seek='cinema_seek_'+scenario
    last=mock.seek_max[seek]
    assert last>=3
    mock.session_state[key]['index']=last
    mock.session_state[key]['started']=True
    mock.session_state[seek]=last
    mock.click('cinema_restart_'+scenario)
    with pytest.raises(FragmentRerun):render(mock,monkeypatch)
    assert mock.session_state[key]['index']==0
    assert mock.session_state[seek]==0
    render(mock,monkeypatch)
    destination=max(1,last//2)
    mock.drag(seek,destination)
    for _ in range(2):
        render(mock,monkeypatch)
        assert mock.session_state[key]['index']==destination
        assert mock.seek_values[seek]==destination
    mock.drag(seek,destination+1)
    render(mock,monkeypatch)
    assert mock.session_state[key]['index']==destination+1


@pytest.mark.parametrize('page,scenario', [('Guided Operations Demo','M05I0005'),('Agentic Replay','M05I0005')])
def test_autoplay_advances_slider_and_playhead_together(monkeypatch,page,scenario):
    mock=InteractiveStreamlit(page,scenario,engineering=True,incident_only=True)
    render(mock,monkeypatch)
    key=next(k for k in mock.session_state if k.startswith(('cinema_','ops_player_')) and isinstance(mock.session_state[k],dict))
    seek='cinema_seek_'+scenario if page=='Agentic Replay' else key+'_seek'
    player=mock.session_state[key]
    player['playing']=True
    player['seconds']=2 if page=='Agentic Replay' else 3
    player['last_tick']=time.monotonic()-3.0
    render(mock,monkeypatch)
    assert player['index']>0
    assert mock.seek_values[seek]==player['index']

@pytest.mark.parametrize('scenario,expected', [
    ('M05I0003', '0.525 is modest and uncalibrated'),
    ('M05I0005', 'RRC NoReply/MaxRetrans'),
])
def test_rca_interpretation_notes_qualify_recorded_claims(monkeypatch, scenario, expected):
    mock=InteractiveStreamlit('Root Cause Analysis', scenario)
    notes=[]
    mock.caption=lambda value,*a,**k:notes.append(str(value))
    render(mock,monkeypatch)
    assert any(expected in n for n in notes)


def test_both_focus_replays_keep_compact_frames():
    source=APP.read_text('utf-8')
    assert source.count('height=250,scrolling=False') == 1
    assert 'gs-route' in source and 'guided_operations_player' in source
    assert 'st.session_state[seek_key]=player[\'index\']\n seek=st.slider' not in source
    assert 'st.session_state[seek_key]=play[\'index\']\n    changed=st.slider' not in source


def test_mobile_focus_labels_are_compact_and_accessible():
    from storyboard import workflow_svg, build_story
    import gzip, json
    root=APP.parent
    c=json.load(gzip.open(root/'data/cases/M05I0005.json.gz','rt'))
    def evidence(eid):
        ref=next(x for x in c['evidence_index'] if x['evidence_id']==eid)
        return json.load(gzip.open(root/ref['file'],'rt'))
    story=build_story(c,evidence)
    i=next(j for j,beat in enumerate(story) if beat['agent']=='SUPERVISOR')
    html=workflow_svg(c['route_family'],story,i)
    assert 'role-compact' in html and 'role-full' in html
    assert 'CU Evidence Join' in html and 'RCA Supervisor' in html
    assert 'aria-label="IN FOCUS: RCA Supervisor &amp; Evidence Synthesis"' in html
    assert '.role-full{display:none}.role-compact{display:inline}' in html
