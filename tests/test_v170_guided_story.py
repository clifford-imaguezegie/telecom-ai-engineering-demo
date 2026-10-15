"""V1.7.0 visitor comprehension, evidence order and truthful trace-boundary QA."""
import gzip,json,runpy,sys,time
from html import unescape
from pathlib import Path
from operational_demo import guided_sequence,executive_sequence
from storyboard import build_story
from guided_story_ui import evidence_html,flow_html,focus_html,phase_for,tool_for
from test_ui_smoke_without_streamlit import APP,MockStreamlit

ROOT=APP.parent

def case(sid):
    with gzip.open(ROOT/'data/cases'/f'{sid}.json.gz','rt',encoding='utf-8') as f:
        return json.load(f)

def timeline(sid,healthy=False,executive=True):
    c=case(sid);h=case('M05I0017')
    def beats(x):
        def ev(eid):
            ref=next(e for e in x['evidence_index'] if e['evidence_id']==eid)
            with gzip.open(ROOT/ref['file'],'rt',encoding='utf-8') as f:return json.load(f)
        return build_story(x,ev)
    full=guided_sequence(h,beats(h),c if sid!='M05I0017' else None,
                         beats(c) if sid!='M05I0017' else [],healthy or sid=='M05I0017')
    return (executive_sequence(full) if executive else full),c

def test_default_opens_single_incident_with_blank_evidence(monkeypatch):
    stub=MockStreamlit('Guided Operations Demo','M05I0003')
    rendered=[]
    captions=[]
    stub.caption=lambda x,*a,**k:captions.append(str(x))
    stub.markdown=lambda x,*args,**kwargs:rendered.append(str(x))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    html='\n'.join(rendered)
    assert 'Selected synthetic incident: M05I0003' in ' '.join(captions)
    assert 'READY · SCENE 0' in html
    assert html.count('Waiting for this recorded tool result')==4
    assert 'RECORDING B' not in html
    assert 'SITE_008 cells show pronounced' not in html
    assert 'gs-route' in html and 'gs-evidence-grid' in html and 'gs-focus' in html


def test_progressive_evidence_reveal_never_leaks_future_outputs():
    seq,c=timeline('M05I0003',healthy=False,executive=True)
    tools=[tool_for(x['beat']) for x in seq]
    ml=tools.index('ml_specialist_summary')
    scope=tools.index('ml_scope_probabilities')
    telemetry=tools.index('telemetry_network_overview')
    before=evidence_html(seq,0,ready=True)
    assert before.count('AWAITING')==4 and '52.5%' not in before
    a=evidence_html(seq,ml)
    assert '52.5%' in a and '65.5%' not in a and '48 recorded' not in a
    assert a.count('JUST REVEALED')==1
    b=evidence_html(seq,scope)
    assert '52.5%' in b and '65.5%' in b and '48 recorded' not in b
    assert b.count('JUST REVEALED')==1
    d=evidence_html(seq,telemetry)
    assert '48 recorded' in d and '65.5%' in d
    assert 'Selected path' not in flow_html(dict(seq[0],case=c),seq[:1])


def test_conditional_branch_only_highlights_after_actual_sp01_decision():
    seq,c=timeline('M05I0003',healthy=False,executive=True)
    before=next(i for i,x in enumerate(seq) if x['beat']['kind']=='decision')-1
    branch=next(i for i,x in enumerate(seq) if x['beat']['kind']=='decision')
    x=dict(seq[before],case=c);y=dict(seq[branch],case=c)
    assert 'Potential routes' in flow_html(x,seq[:before+1])
    assert 'Selected path' not in flow_html(x,seq[:before+1])
    assert 'Selected path · Cell/site specialists' in flow_html(y,seq[:branch+1])
    assert 'SP02' in flow_html(y,seq[:branch+1]) and 'SP07' in flow_html(y,seq[:branch+1])


def test_cu_route_is_alternative_not_a_cell_specialist_continuation():
    seq,c=timeline('M05I0004',healthy=False,executive=True)
    i=next(i for i,x in enumerate(seq) if x['beat']['kind']=='decision')
    v=flow_html(dict(seq[i],case=c),seq[:i+1])
    assert 'Selected path · CU specialist' in v
    assert 'CU DOMAIN · SP08' in v
    assert 'Routes are alternatives' in v


def test_healthy_exec_presents_real_tools_before_healthy_conclusion():
    seq,c=timeline('M05I0017',healthy=True,executive=True)
    kinds=[tool_for(e['beat']) for e in seq]
    for name in ['ml_specialist_summary','ml_scope_probabilities','telemetry_network_overview','telemetry_events']:
        assert name in kinds
    d=next(i for i,x in enumerate(seq) if x['beat']['kind']=='decision')
    assert all(kinds.index(x)<d for x in kinds if x)
    assert seq[-1]['beat']['agent']=='FINAL'
    label=phase_for(dict(seq[-1],case=c))
    assert label[0]==3 and 'Healthy' in label[1]
    html=evidence_html(seq,d)
    assert html.count('RECORDED')==4


def test_comparison_pauses_at_explicit_case_boundary(monkeypatch):
    seq,c=timeline('M05I0003',healthy=True,executive=True)
    switch=next(i for i in range(len(seq)-1) if seq[i]['scenario_id']!=seq[i+1]['scenario_id'])
    stub=MockStreamlit('Guided Operations Demo','M05I0003')
    radio=stub.radio
    stub.radio=lambda label,opts,**k:opts[-1] if label=='Presentation' else radio(label,opts,**k)
    key='ops_player_M05I0003_True_executive'
    stub.session_state[key]={'index':switch,'playing':True,'seconds':4,
                             'last_tick':time.monotonic()-9,'carry':0.,'presentation_elapsed':0.,'started':True}
    rendered=[]
    stub.markdown=lambda x,*a,**k:rendered.append(str(x))
    monkeypatch.setitem(sys.modules,'streamlit',stub)
    runpy.run_path(str(APP),run_name='__main__')
    assert stub.session_state[key]['playing'] is False
    assert stub.session_state[key]['index']==switch
    result='\n'.join(rendered)
    assert 'This healthy network did not become the next incident' in result
    assert 'independent recorded synthetic-network case' in result


def test_user_supplied_text_is_html_escaped():
    seq,c=timeline('M05I0003',healthy=False,executive=True)
    item=dict(seq[0],case=c)
    beat=dict(item['beat'],title='<img src=x onerror=alert(1)>',output='<script>bad()</script>')
    item['beat']=beat
    v=focus_html(item,1,len(seq))
    assert '<script>' not in v and '&lt;script&gt;' in v
    assert '<img' not in v and '&lt;img' in v
