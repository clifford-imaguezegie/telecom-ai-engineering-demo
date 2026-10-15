"""V1.5.0 unified cockpit contracts. No browser claims; Streamlit rendered QA is separate."""
import gzip
import json
import runpy
import sys
from pathlib import Path
from html import unescape
import pytest
from test_ui_smoke_without_streamlit import APP, MockStreamlit
from storyboard import build_story
from operational_demo import guided_sequence

ROOT=APP.parent

def helpers(monkeypatch, scenario='M05I0003'):
    mock=MockStreamlit('Guided Operations Demo',scenario)
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    return runpy.run_path(str(APP),run_name='__main__')


def recorded_case(sid):
    with gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt') as f:
        return json.load(f)


def storyboard(sid):
    case=recorded_case(sid)
    def evidence(eid):
        item=next(x for x in case['evidence_index'] if x['evidence_id']==eid)
        with gzip.open(ROOT/item['file'],'rt') as f:
            return json.load(f)
    return build_story(case,evidence)


def test_same_screen_stage_evidence_uses_exact_authored_fields(monkeypatch):
    app=helpers(monkeypatch)
    beat=next(x for x in storyboard('M05I0005') if x.get('output') and x.get('action'))
    html=app['cockpit_activity_html'](beat,3,24)
    for section in ['INCOMING / HANDOVER','AGENT ACTION / TOOL','RECORDED RESULT']:
        assert section in html
    assert 'Step 3/24' in html
    assert 'cockpit-activity-cards' in html
    assert '<script' not in html


def test_cockpit_escapes_original_strings_and_preserves_data(monkeypatch):
    app=helpers(monkeypatch)
    beat={'agent':'SP01','input':'<script>attack()</script>',
          'action':'network < 5 & telemetry','output':'<b>not markup</b>'}
    html=app['cockpit_activity_html'](beat,1,16)
    assert '<script>' not in html and '&lt;script&gt;' in html
    assert 'network &lt; 5 &amp; telemetry' in html
    assert '<b>not markup</b>' not in html and '&lt;b&gt;' in html
    assert 'title="' in html


def test_compact_guided_page_has_no_full_hero_and_retains_inspectors(monkeypatch):
    mock=MockStreamlit('Guided Operations Demo','M05I0005')
    shown=[]
    mock.markdown=lambda html,*a,**k:shown.append(str(html))
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    runpy.run_path(str(APP),run_name='__main__')
    joined='\n'.join(shown)
    assert 'tread-guided-marker' in joined
    assert 'V1.6.1 · UNIFIED INVESTIGATION COCKPIT' in joined
    assert 'cockpit-status' in joined and 'cockpit-activity' in joined
    assert '<div class="hero">' not in joined
    assert 'Awaiting Localisation Agent' in joined


def test_cockpit_no_future_tool_data_leaks(monkeypatch):
    mock=MockStreamlit('Guided Operations Demo','M05I0005')
    seen=[]
    mock.markdown=lambda x,*a,**k:seen.append(str(x))
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    runpy.run_path(str(APP),run_name='__main__')
    output=' '.join(seen)
    assert 'Awaiting Localisation Agent' in output
    assert '91.4%' not in output


def test_n03_evaluation_language_specific_to_selected_scenario(monkeypatch):
    for scenario in ['M05I0003','M05I0005']:
        mock=MockStreamlit('Evaluation & Performance',scenario)
        captions=[]
        mock.caption=lambda value,*a,**kw:captions.append(str(value))
        monkeypatch.setitem(sys.modules,'streamlit',mock)
        runpy.run_path(str(APP),run_name='__main__')
        expected='100.0%' if scenario=='M05I0003' else '75.0%'
        specific=[x for x in captions if 'field-level breakdown' in x]
        assert specific and expected in specific[0] and scenario in specific[0]
        assert '75% exact match cannot' not in specific[0]


def test_no_cockpit_impact_on_other_pages(monkeypatch):
    mock=MockStreamlit('Platform Overview','M05I0003')
    shown=[]
    mock.markdown=lambda x,*a,**k:shown.append(str(x))
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    runpy.run_path(str(APP),run_name='__main__')
    joined=' '.join(shown)
    assert '<div class="hero">' in joined
    assert '<span class="tread-guided-marker"' not in joined


def test_source_preserves_state_persistence_contracts():
    source=APP.read_text('utf-8')
    assert 'on_change=_seek_from_widget,args=(key,seek_key,last)' in source
    assert '_set_playhead(play,seek_key,0,last)' in source
    assert 'View complete recorded agent route' in source
    assert 'Full current-stage messages and localisation evidence' in source
    assert 'guided_agent_drilldown(case,beat[\'agent\'],beat)' in source
    assert 'height=250,scrolling=False' in source


def test_long_message_is_compact_without_affecting_source(monkeypatch):
    app=helpers(monkeypatch)
    giant='IMPORTANT EVIDENCE '*1000
    original={'agent':'SP08','input':giant,'action':'Review saved telemetry','output':giant}
    html=app['cockpit_activity_html'](original,12,22)
    assert len(html)<4000
    assert original['input']==giant and original['output']==giant
    assert 'Full messages and tool evidence below' in html
