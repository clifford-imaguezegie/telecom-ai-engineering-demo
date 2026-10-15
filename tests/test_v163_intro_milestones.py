"""V1.6.3 onboarding claims derive from exactly the bundled SP01/incident traces."""
import gzip
import json
import runpy
import sys
from pathlib import Path

from presentation import benchmark_summary
from test_ui_smoke_without_streamlit import APP, MockStreamlit

ROOT=Path(__file__).resolve().parents[1]


def _cases():
    manifest=json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
    return [json.load(gzip.open(ROOT/'data'/'cases'/f'{sid}.json.gz','rt',encoding='utf-8'))
            for sid in manifest['scenario_order']]


def test_sp01_under_25_seconds_for_all_nine_recordings():
    stats=benchmark_summary(_cases())
    assert (stats['health_assessment_under_25sec'],stats['health_assessment_total']) == (9,9)
    assert (stats['localisation_under_25sec'],stats['localisation_total']) == (8,8)
    assert stats['sp01_max_seconds'] < 25
    assert 24.2 < stats['sp01_max_seconds'] < 24.4


def test_incident_rca_count_remains_eight_under_five_minutes():
    stats=benchmark_summary(_cases())
    assert (stats['incident_rca_under_5min'],stats['incident_total']) == (8,8)
    assert stats['incident_max_seconds'] < 273


def test_platform_intro_has_correct_single_clock_milestones(monkeypatch):
    stub=MockStreamlit('Platform Overview','M05I0003')
    displayed=[]
    stub.markdown=lambda val,*a,**kw:displayed.append(str(val))
    stub.caption=lambda val,*a,**kw:displayed.append(str(val))
    stub.subheader=lambda val,*a,**kw:displayed.append(str(val))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    text='\n'.join(displayed)
    for phrase in ('Discover TEAD AI','From complex network investigations',
                   '&lt; 25 sec','9/9 recorded scenarios','8/8',
                   'same SP01 execution','share the same SP01 completion timestamp',
                   '&lt; 5 min','not production SLAs'):
        assert phrase in text
    assert '≤ 2 min' not in text
    assert 'Assess network health' in text
