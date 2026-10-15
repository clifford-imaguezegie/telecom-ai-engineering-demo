"""V1.6.2: compact first-view diagram and preserved full investigation detail."""
import re
import runpy
import sys
from test_ui_smoke_without_streamlit import APP, MockStreamlit


def markup(monkeypatch, page='Platform Overview'):
    mock=MockStreamlit(page,'M05I0003')
    pieces=[]
    mock.markdown=lambda v,*a,**k:pieces.append(str(v))
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    runpy.run_path(str(APP),run_name='__main__')
    return '\n'.join(pieces)


def test_compact_routes_and_full_diagram_preserved(monkeypatch):
    doc=markup(monkeypatch)
    assert doc.count('<section class="tead-oneframe"')==1
    assert doc.count('<section class="tead-flow"')==1
    assert doc.index('<section class="tead-oneframe"')<doc.index('<section class="tead-flow"')
    section=doc.split('<section class="tead-oneframe"',1)[1].split('</section>',1)[0]
    assert len(re.findall('class="of-lane (healthy|site|cu)"',section))==3
    assert re.findall('class="of-agent"><b>(SP\d+)</b>',section)==['SP02','SP03','SP04','SP05','SP06','SP07']
    assert section.count('class="of-connector"')==5
    assert section.count('class="of-card of-supervisor"')==1
    assert 'No specialist escalation' in doc or 'no specialist escalation' in doc
    assert 'SP08' in section and 'RAG support when recorded' in section
    assert 'not represent live network analysis' in section
    assert 'Detailed investigation flow — full agents, tools, and provenance' in APP.read_text('utf8')
    assert 'Detailed Architecture — original technical explanation (preserved)' in APP.read_text('utf8')


def test_all_other_pages_exclude_compact_overview(monkeypatch):
    for page in ['Guided Operations Demo','Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis','Engineering Evidence','Evaluation & Performance']:
        doc=markup(monkeypatch,page)
        assert '<section class="tead-oneframe"' not in doc
        assert '<section class="tead-flow"' not in doc
