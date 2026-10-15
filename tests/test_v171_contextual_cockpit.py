"""V1.7.1 trace-grounded phase boards, duration, non-leakage and messaging."""
import gzip,json,runpy,sys
from pathlib import Path
from guided_story_ui import board_html,evidence_html,supervisor_html,specialist_html,_scope,_node_clock
from operational_demo import executive_sequence,guided_sequence,event_trace_offset
from storyboard import build_story
from test_ui_smoke_without_streamlit import APP,MockStreamlit

ROOT=APP.parent

def load(sid):
    with gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt',encoding='utf8') as f:return json.load(f)

def series(sid,executive=True):
    c=load(sid)
    def evidence(eid):
        e=next(x for x in c['evidence_index'] if x['evidence_id']==eid)
        with gzip.open(ROOT/e['file'],'rt',encoding='utf8') as f:return json.load(f)
    beats=build_story(c,evidence)
    all_=guided_sequence(None,[],c,beats,False)
    return executive_sequence(all_) if executive else all_,c

def render(seq,c,index,ready=False):
    return board_html(dict(seq[index],case=c),seq,index,ready)

def test_sp01_what_and_where_are_without_ml_prefix_and_show_original_clock():
    seq,c=series('M05I0003')
    pos={b['beat']['source'].split(' · ')[-1]:i for i,b in enumerate(seq) if b['beat']['kind']=='tool'}
    a=render(seq,c,0,True)
    assert a.count('AWAITING')==4
    assert 'SITE_008' not in a
    what=render(seq,c,pos['ml_specialist_summary'])
    assert 'WHAT' in what and '52.5%' in what and '00:02.6' in what
    assert 'SITE_008' not in what
    where=render(seq,c,pos['ml_scope_probabilities'])
    assert 'WHERE' in where and '65.5%' in where and '00:02.7' in where
    assert 'SITE_008' not in where
    assert 'Exact entities pending SP01 confirmation' in where
    handover=next(i for i,v in enumerate(seq) if v['beat']['kind']=='handover' and v['beat']['agent']=='SP01')
    confirmed=render(seq,c,handover)
    assert 'SITE_008' in confirmed and '3 affected cells' in confirmed
    assert '00:15.0' in confirmed and 'SP01 confirmed scope' in confirmed

def test_cell_and_cu_scope_use_actual_saved_identifiers():
    for sid,key in [('M05I0003','SITE_008'),('M05I0004','CU_DOMAIN_02')]:
        seq,c=series(sid)
        index=next(i for i,v in enumerate(seq) if v['beat']['kind']=='handover' and v['beat']['agent']=='SP01')
        panel=render(seq,c,index)
        assert key in panel
        assert 'SP01 confirmed scope' in panel
    assert '15 cells' in render(*((lambda sc:(sc[0],sc[1],next(i for i,v in enumerate(sc[0]) if v['beat']['kind']=='handover' and v['beat']['agent']=='SP01')))(series('M05I0004'))))

def test_specialist_timeline_retains_prior_agents_and_chooses_decisive_sp04():
    seq,c=series('M05I0003')
    specialists=[(i,x['beat']['agent']) for i,x in enumerate(seq) if x['beat']['kind']=='feedback']
    assert [agent for _,agent in specialists]==['SP02','SP04','SP07']
    t1=render(seq,c,specialists[0][0])
    assert 'COMPLETED AGENTS' in t1 and 'SP02' in t1 and 'SP04 ·' not in t1
    t2=render(seq,c,specialists[1][0])
    assert 'SP02 ·' in t2 and 'SP04 ·' in t2 and 'SP07 ·' not in t2
    assert 'RECORDED' in t2 and '00:00' not in t2

def test_supervisor_does_not_leak_final_conclusion_before_decision():
    seq,c=series('M05I0003')
    rag=next(i for i,x in enumerate(seq) if x['beat']['kind']=='rag' and x['beat']['agent']=='SUPERVISOR')
    decision=next(i for i,x in enumerate(seq) if x['beat']['kind']=='decision' and x['beat']['agent']=='SUPERVISOR')
    root=c['stage_data']['supervisor_output']['root_cause_assessment']['root_cause']
    before=render(seq,c,rag)
    assert root not in before and 'Awaiting final Supervisor decision' in before
    after=render(seq,c,decision)
    assert root in after and 'Supervisor complete at' in after
    assert 'SITE_008' in after and 'CONFIDENCE &amp; GAPS' in after
    end=render(seq,c,len(seq)-1)
    assert root in end and 'Recorded decision available' in end
    assert 'gs-rca-primary' in end

def test_healthy_control_has_no_fabricated_rca():
    seq,c=series('M05I0017')
    panel=render(seq,c,len(seq)-1)
    assert 'HEALTH CONCLUSION' in panel
    assert 'No material network incident supported' in panel
    assert 'No affected network scope' in panel
    assert 'RCA conclusion not recorded' not in panel

def test_recorded_supervisor_time_is_node_end_and_not_presentation_time():
    seq,c=series('M05I0003')
    d=next(x['beat'] for x in seq if x['beat']['agent']=='SUPERVISOR' and x['beat']['kind']=='decision')
    assert round(event_trace_offset(c,d),1)==203.4
    assert _node_clock(c,'SUPERVISOR')=='03:23.4'

def test_guided_player_includes_distinct_clocks_progress_hero_value(monkeypatch):
    mock=MockStreamlit('Guided Operations Demo','M05I0003')
    html=[]; mock.markdown=lambda value,*a,**k:html.append(str(value))
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    runpy.run_path(str(APP),run_name='__main__')
    src='\n'.join(html)
    assert 'gs-timeline-track' in src and 'role="progressbar"' in src
    assert 'SCENE PROGRESS' in src and 'WATCH TIME' in src and 'ORIGINAL TRACE' in src
    assert 'READY · SCENE 0' in src
    assert 'TEAD AI · AGENTIC NETWORK INVESTIGATION' in src
    assert src.count('Waiting for this recorded tool result')==4
    overview=MockStreamlit('Platform Overview','M05I0003')
    other=[];overview.markdown=lambda value,*a,**k:other.append(str(value))
    monkeypatch.setitem(sys.modules,'streamlit',overview)
    runpy.run_path(str(APP),run_name='__main__')
    other=' '.join(other)
    assert 'Agentic Telecom Network Investigation' in other
    assert 'governed autonomous-network operations' in other

def test_all_case_final_rca_board_uses_own_record_no_cross_case_data():
    for sid in ['M05I0002','M05I0003','M05I0004','M05I0005','M05I0006','M05I0008','M05I0016','M05I0019']:
        seq,c=series(sid)
        expected=c['stage_data']['supervisor_output']['root_cause_assessment']['root_cause']
        assert expected in render(seq,c,len(seq)-1)
        assert render(seq,c,len(seq)-1).count('gs-evidence')>=4

def test_final_scene_player_is_held_until_explicit_restart(monkeypatch):
    mock=MockStreamlit('Guided Operations Demo','M05I0003')
    key='ops_player_M05I0003_False_executive'
    sequence,c=series('M05I0003')
    mock.session_state[key]={'index':len(sequence)-1,'playing':True,'seconds':6,
        'last_tick':0.,'carry':0.,'presentation_elapsed':76.,'started':True}
    seen=[]
    original=mock.button
    def log_button(label,*args,**kwargs):
        seen.append((label,kwargs.get('disabled')))
        return original(label,*args,**kwargs)
    mock.button=log_button
    monkeypatch.setitem(sys.modules,'streamlit',mock)
    runpy.run_path(str(APP),run_name='__main__')
    assert mock.session_state[key]['index']==len(sequence)-1
    assert mock.session_state[key]['playing'] is False
    assert ('✓ Completed · Restart to replay',True) in seen
    assert mock.session_state[key]['presentation_elapsed']==76.
