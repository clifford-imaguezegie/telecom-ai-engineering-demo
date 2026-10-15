"""V1.6.0 executive overview and engineering-learning contracts.

Executed using the bundled frozen data and the same offline Streamlit stub as
prior releases. Browser acceptance for the deployed app is a separate gate.
"""
import gzip
import hashlib
import json
import runpy
import sys
from pathlib import Path
import pytest
from test_ui_smoke_without_streamlit import APP, MockStreamlit
from presentation import phase_execution_ranges

ROOT=APP.parent

def all_cases():
    with open(ROOT/'data/manifest.json', encoding='utf8') as f:
        ids=json.load(f)['scenario_order']
    with_cases=[]
    for case_id in ids:
        with gzip.open(ROOT/'data/cases'/f'{case_id}.json.gz','rt',encoding='utf8') as f:
            with_cases.append(json.load(f))
    return with_cases


def source_render(monkeypatch,page='Platform Overview'):
    mock=MockStreamlit(page,'M05I0003')
    html=[]
    captions=[]
    mock.markdown=lambda x,*args,**kw:html.append(str(x))
    mock.caption=lambda x,*args,**kw:captions.append(str(x))
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    app=runpy.run_path(str(APP),run_name='__main__')
    return app,' '.join(html),' '.join(captions)


def test_phase_windows_exact_against_nine_recorded_cases():
    m=phase_execution_ranges(all_cases())
    assert m['sp01']['count']==9
    assert m['specialists']['count']==8
    assert m['supervisor']['count']==8
    assert m['incident']['count']==8
    assert m['healthy']['count']==1
    assert m['sp01']['min']==pytest.approx(15.024)
    assert m['sp01']['max']==pytest.approx(24.271)
    assert m['specialists']['min']==pytest.approx(42.096)
    assert m['specialists']['max']==pytest.approx(111.587)
    assert m['supervisor']['min']==pytest.approx(98.806)
    assert m['supervisor']['max']==pytest.approx(173.416)
    # Prior informal summary omitted the fastest incident (CU M05I0005).
    assert m['incident']['min']==pytest.approx(168.248)
    assert m['incident']['max']==pytest.approx(272.936)
    assert m['healthy']['min']==pytest.approx(17.195)


def test_cell_specialist_chain_and_healthy_bypass():
    rows={x['scenario_id']:x for x in phase_execution_ranges(all_cases())['rows']}
    assert rows['M05I0003']['specialist_agents']==('SP02','SP03','SP04','SP05','SP06','SP07')
    assert rows['M05I0005']['specialist_agents']==('SP08',)
    assert rows['M05I0017']['specialist_agents']==()
    assert rows['M05I0017']['specialist_seconds'] is None


def test_overview_retains_existing_visitor_copy_and_adds_flow(monkeypatch):
    _, html, caption=source_render(monkeypatch)
    assert 'TEAD AI' in html
    assert 'TREAD AI' not in html
    assert 'Network Assessment &amp; Localisation' in html and 'Recorded Root Cause Analysis' in html
    assert 'SP02' in html and 'SP03' in html and 'SP07' in html
    assert 'directly to Supervisor' in html
    assert 'SP08' in html and 'CU-Domain &amp; Boundary Analysis' in html
    assert 'alternative recorded routes converging on one Supervisor' in html
    assert 'Detailed Architecture — original technical explanation' in (APP.read_text('utf8'))
    assert 'From network data to actionable engineering intelligence' in html
    assert 'Watch the investigation' in APP.read_text('utf8')
    assert 'not live inference' in html


def test_performance_headline_and_min_max_published_correctly(monkeypatch):
    _, html, captions=source_render(monkeypatch)
    for headline in ['&lt; 00:25','&lt; 01:52','&lt; 02:54','&lt; 04:33']:
        assert headline in html
    assert '00:15.0' in html and '00:24.3' in html
    assert '00:42.1' in html and '01:51.6' in html
    assert '01:38.8' in html and '02:53.4' in html
    assert '02:48.2' in html and '04:32.9' in html
    assert '00:17.2' in captions
    assert 'must not be summed' in captions


def test_engineering_optimizations_are_bounded_claims(monkeypatch):
    _, html, captions=source_render(monkeypatch)
    for phrase in ['17.29 MB to 227 KB','195,500-token','NOT proven token/cost savings',
                   'Technical resilience matters','Right-size the model']:
        assert phrase in html
    assert 'development' in captions.lower()
    assert 'production' in captions.lower()


def test_pages_except_overview_remain_working(monkeypatch):
    for page in ['Guided Operations Demo','Scenario Library','Evaluation & Performance','Root Cause Analysis']:
        app,html,_=source_render(monkeypatch,page)
        assert app


def test_no_mutation_of_evidence_under_brand_change():
    # Case hashes are checked against the packaged frozen data in separate
    # packaging validation; do not rewrite case JSON to change the public name.
    assert len(list((ROOT/'data').rglob('*.gz')))==135
    assert (ROOT/'data/manifest.json').is_file()
