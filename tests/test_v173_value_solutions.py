"""V1.7.3: dedicated additive Value Proposition & Solutions page."""
from pathlib import Path
import gzip
import json
import runpy
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from value_solutions import BENEFITS, SOLUTIONS, STYLE, page_html
from test_ui_smoke_without_streamlit import MockStreamlit

MANIFEST=json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))

def cases():
    found=[]
    for sid in MANIFEST['scenario_order']:
        with gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt',encoding='utf-8') as f:found.append(json.load(f))
    return found


def test_value_page_appears_directly_in_sidebar_without_removing_previous_pages():
    from ast import parse, Assign, literal_eval
    tree=parse((ROOT/'app.py').read_text(encoding='utf-8'))
    pages=next(literal_eval(n.value) for n in tree.body if isinstance(n, Assign) and any(getattr(t,'id',None)=='PAGES' for t in n.targets))
    assert pages==['Platform Overview','Value Proposition & Solutions','Guided Operations Demo','Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis','Engineering Evidence','Evaluation & Performance']


def test_new_page_renders_with_all_actual_source_scenarios(monkeypatch):
    stub=MockStreamlit('Value Proposition & Solutions','M05I0003')
    rendered=[]
    stub.markdown=lambda value,*a,**k:rendered.append(str(value))
    stub.subheader=lambda value,*a,**k:rendered.append(str(value))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
    txt='\n'.join(rendered)
    assert 'Value Proposition' in txt
    assert 'Demonstrated engineering outcomes' in txt
    assert 'Potential operational benefits' in txt
    assert 'Solutions enabled by the TEAD AI architecture' in txt
    assert 'Path from demonstration to operator adoption' in txt
    assert '&lt; 25 sec' in txt
    assert '&lt; 5 min' in txt
    assert 'Cross-domain' in txt
    assert '98.7%' in txt


def test_six_solutions_have_distinct_maturity_not_false_production_claims():
    txt=page_html(cases())
    assert len(SOLUTIONS)==6
    assert txt.count('class="vs-solution"')==6
    assert txt.count('Demonstrated experimentally')==3
    assert txt.count('Proposed extension')==2
    assert txt.count('Long-term research')==1
    assert 'Production MTTR reduced' not in txt
    assert 'have not been established' in txt


def test_value_proposition_prominent_without_expanders():
    txt=page_html(cases())
    assert '<details' not in txt and 'expander' not in txt.lower()
    assert len(BENEFITS)==4
    assert txt.count('class="vs-benefit"')==4
    assert txt.index('Potential operational benefits') < txt.index('Solutions enabled by the TEAD AI architecture')
    assert '@media(max-width:620px)' in STYLE


def test_recorded_stage_results_are_not_equated_with_cost_or_mttr_savings():
    txt=page_html(cases())
    assert 'synthetic-network experiments' in txt
    assert 'representation size, not token cost' in txt
    assert 'production MTTR or financial benefits have not been measured' in txt
    assert 'It does not run live agents' not in txt  # wording states the limitation with a different subject
    assert 'it does not run live agents' in txt


def test_navigation_buttons_target_existing_unmodified_pages(monkeypatch):
    stub=MockStreamlit('Value Proposition & Solutions','M05I0003')
    actual=[]
    def record_button(label,**kw):
        actual.append((label,kw.get('key')))
        return False
    stub.button=record_button
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
    assert [a[0] for a in actual]==['Watch the investigation','Explore the network','Inspect RCA evidence']
    assert all(a[1].startswith('vs_nav_') for a in actual)
