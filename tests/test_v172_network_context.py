"""V1.7.2: topology truth, agent/tool provenance and visitor navigation."""
from pathlib import Path
import gzip
import json
import re
import runpy
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from network_overview import derive_inventory, observed_tools, topology_html, tools_html, AGENT_ROLES
from test_ui_smoke_without_streamlit import MockStreamlit

MANIFEST=json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))


def get_case(sid):
    with gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt',encoding='utf-8') as f:return json.load(f)


def inventory(sid):
    c=get_case(sid)
    item=next(e for e in c['evidence_index'] if e['tool']=='telemetry_topology')
    with gzip.open(ROOT/item['file'],'rt',encoding='utf-8') as f:
        return derive_inventory(json.load(f)['result']['entities'])


def test_all_nine_record_same_ten_sites_thirty_cells_two_domains():
    reference=None
    for sid in MANIFEST['scenario_order']:
        inv=inventory(sid)
        assert len(inv['sites'])==10
        assert inv['cell_count']==30
        assert inv['du_cell_views']==30
        assert len(inv['domains'])==2
        assert set(inv['domains'])=={'CU_DOMAIN_01','CU_DOMAIN_02'}
        assert len([x for x in inv['sites'] if x['domain']=='CU_DOMAIN_01'])==5
        assert len([x for x in inv['sites'] if x['domain']=='CU_DOMAIN_02'])==5
        assert all(len(s['cu_cells'])==len(s['du_cells'])==3 for s in inv['sites'])
        assert all(s['du'] and s['f1'] for s in inv['sites'])
        assert all(z['cp'] and z['up'] and z['e1'] and z['n2'] and z['amf'] for z in inv['domains'].values())
        if reference is None:reference=inv
        else:assert inv==reference


def test_topology_graph_contains_recorded_object_ids_no_invented_gnb_id():
    inv=inventory('M05I0003')
    html=topology_html(inv)
    for s in inv['sites']:
        assert s['site'] in html and s['du'] in html and s['f1'] in html
        for cell in s['cu_cells']:assert cell in html
    for domain in inv['domains']:
        assert domain in html
    assert len(re.findall(r'class="net-site"',html))==10
    assert len(re.findall(r'title="NRCELL_CU_',html))==30
    assert 'not a separately reported gNB identifier' in html
    assert '15-minute' not in html


def test_agent_mapping_matches_observed_tool_outputs_not_invented():
    cases=[get_case(sid) for sid in MANIFEST['scenario_order']]
    tools=observed_tools(cases)
    assert set(tools)==set(AGENT_ROLES)
    assert tools['SP08']==['telemetry_cu_domain_state']
    assert 'telemetry_topology' in tools['SP01']
    assert 'telemetry_kpis' in tools['SP02']
    assert 'telemetry_radio_state' in tools['SP04']
    assert 'supervisor_private_knowledge_search' in tools['SUPERVISOR']
    text=tools_html(tools)
    assert 'Curated telecom knowledge search' in text
    assert 'supervisor_private_knowledge_search' in text  # hidden in title provenance
    assert len(re.findall('class="net-agent"',text))==9


def test_network_overview_topology_precedes_tools_and_selected_scenario_elsewhere(monkeypatch):
    stub=MockStreamlit('Network Overview','M05I0003')
    seen=[]
    stub.markdown=lambda txt,*a,**kw:seen.append(('markup',str(txt)))
    stub.subheader=lambda txt,*a,**kw:seen.append(('heading',str(txt)))
    stub.caption=lambda txt,*a,**kw:seen.append(('caption',str(txt)))
    stub.info=lambda txt,*a,**kw:seen.append(('info',str(txt)))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
    full='\n'.join(x[1] for x in seen)
    assert full.index('Recorded Network Topology') < full.index('Agent and Tool Capability Map')
    assert full.index('SITE_001') < full.index('Agent and Tool Capability Map')
    assert 'Open **Scenario Library**' in full or 'open **Scenario Library**' in full
    assert 'Selected scenario / accessibility trend' not in full


def test_guided_discovery_and_agentic_replay_context(monkeypatch):
    for page in ('Guided Operations Demo','Agentic Replay'):
        stub=MockStreamlit(page,'M05I0003')
        seen=[]
        stub.info=lambda txt,*a,**kw:seen.append(str(txt))
        stub.caption=lambda txt,*a,**kw:seen.append(str(txt))
        monkeypatch.setitem(sys.modules,'streamlit',stub)
        runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
        assert any('Select scenario ▾' in v for v in seen)
        assert any('M05I0003' in v for v in seen)
