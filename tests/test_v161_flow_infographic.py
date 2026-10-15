"""V1.6.1 conditional infographic contracts; no additional test dependencies."""
import re
import runpy
import sys
from test_ui_smoke_without_streamlit import APP, MockStreamlit


def render(monkeypatch, page='Platform Overview'):
    mock=MockStreamlit(page,'M05I0003')
    output=[]
    mock.markdown=lambda content,*a,**kw:output.append(str(content))
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    runpy.run_path(str(APP),run_name='__main__')
    return '\n'.join(output)


def flow_only(text):
    return text.split('<section class="tead-flow"',1)[1].split('</section>',1)[0]


def test_three_alternative_paths_and_real_sp_route(monkeypatch):
    f=flow_only(render(monkeypatch))
    assert re.findall(r'<div class="flow-lane (healthy|cell|cu)"',f)==['healthy','cell','cu']
    assert 'SP01' in f and 'ML 01' in f and 'ML 02' in f
    assert 'Event telemetry' in f
    assert 'No specialist escalation' in f
    assert re.findall(r'<div class="flow-agent"><b>(SP\d+)</b>',f)==['SP02','SP03','SP04','SP05','SP06','SP07']
    assert len(re.findall('class="flow-step-arrow"',f))==5
    assert 'SP08' in f and 'CU-Domain &amp; Boundary Analysis' in f
    assert f.count('class="flow-convergence"')==1
    assert 'Supervisor · Evidence Synthesis' in f
    assert 'Recorded Root Cause Analysis' in f
    assert f.count('class="flow-into-supervisor ') ==3
    assert f.count('class="flow-support-item"')==4


def test_flow_is_presentational_not_live(monkeypatch):
    f=flow_only(render(monkeypatch))
    assert 'not live inference' in f
    assert 'Nothing on this page invokes a live agent' in f
    assert '15-minute observation window' in f
    assert 'RAG support' in f
    assert 'post-run evaluation' in f
    assert 'not extra execution stages' in f
    assert 'Detailed Architecture — original technical explanation (preserved)' in APP.read_text('utf8')


def test_other_pages_do_not_embed_overview_infographic(monkeypatch):
    for page in ['Guided Operations Demo','Network Overview','Engineering Evidence','Evaluation & Performance']:
        txt=render(monkeypatch,page)
        assert '<section class="tead-flow"' not in txt
