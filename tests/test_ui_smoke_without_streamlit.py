"""Offline page render smoke tests using a recorder stub, not a browser test.
This verifies all six page branches with actual bundled data without installing
Streamlit or contacting the Internet. Real browser QA remains necessary.
"""
import runpy
import sys
from types import ModuleType, SimpleNamespace
from pathlib import Path
import pytest

APP=Path(__file__).resolve().parents[1]/'app.py'
PAGES=['Platform Overview','Guided Operations Demo','Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis','Engineering Evidence','Evaluation & Performance']

class _Context:
 def metric(self,*args,**kwargs):pass
 def __enter__(self):return self
 def __exit__(self,*args):return False

class MockStreamlit(ModuleType):
 def __init__(self,page,scenario):
  super().__init__('streamlit')
  self.session_state={'nav_page':page,'selected_scenario':scenario}
  self.sidebar=self
  self.components=SimpleNamespace(v1=SimpleNamespace(html=lambda *a,**k:None))
 def cache_data(self,**kwargs):return lambda fn:fn
 def fragment(self,**kwargs):return lambda fn:fn
 def set_page_config(self,**kwargs):pass
 def markdown(self,*args,**kwargs):pass
 def html(self,*args,**kwargs):pass
 def subheader(self,*args,**kwargs):pass
 def caption(self,*args,**kwargs):pass
 def divider(self,*args,**kwargs):pass
 def header(self,*args,**kwargs):pass
 def write(self,*args,**kwargs):pass
 def info(self,*args,**kwargs):pass
 def warning(self,*args,**kwargs):pass
 def success(self,*args,**kwargs):pass
 def error(self,*args,**kwargs):pass
 def json(self,*args,**kwargs):pass
 def code(self,*args,**kwargs):pass
 def dataframe(self,*args,**kwargs):pass
 def plotly_chart(self,*args,**kwargs):pass
 def progress(self,*args,**kwargs):pass
 def metric(self,*args,**kwargs):pass
 def button(self,*args,**kwargs):return False
 def rerun(self):raise RuntimeError('Unexpected rerun')
 def columns(self,spec,**kwargs):return [_Context() for _ in range(spec if isinstance(spec,int) else len(spec))]
 def tabs(self,spec,**kwargs):return [_Context() for _ in spec]
 def expander(self,*args,**kwargs):return _Context()
 def radio(self,label,options,**kwargs):
  if label=='Workspace':return self.session_state['nav_page']
  if label=='Replay mode' and getattr(self,'inspect_legacy',False):return options[1]
  if label=='Visitor experience' and getattr(self,'full_engineering',False):return options[1]
  return options[0]
 def selectbox(self,label,options,**kwargs):
  key=kwargs.get('key')
  if key in self.session_state:
   return self.session_state[key]
  return options[kwargs.get('index',0)]
 def select_slider(self,label,options,**kwargs):return kwargs.get('value',options[0])
 def slider(self,label,**kwargs):return self.session_state.get(kwargs.get('key'),kwargs.get('value',0))

@pytest.mark.parametrize('sid',['M05I0017','M05I0002','M05I0005','M05I0016'])
@pytest.mark.parametrize('page',PAGES)
def test_renders_every_page_branch(monkeypatch,sid,page):
 stub=MockStreamlit(page,sid)
 monkeypatch.setitem(sys.modules,'streamlit',stub)
 runpy.run_path(str(APP),run_name='__main__')


@pytest.mark.parametrize('page',['Root Cause Analysis','Agentic Replay'])
def test_original_rag_question_and_mechanism_are_visible_in_ui(monkeypatch,page):
 """The structured Supervisor RAG record is visible, not hidden in raw JSON."""
 import gzip,json
 sid='M05I0005'
 with gzip.open(APP.parent/'data'/'cases'/f'{sid}.json.gz','rt') as f:
  c=json.load(f)
 kb=c['stage_data']['supervisor_output']['knowledge_base_contribution']
 stub=MockStreamlit(page,sid)
 # Navigate to final Supervisor replay output instead of initial SP01 orientation.
 if page=='Agentic Replay':
  stub.session_state['replay_'+sid]=len(c['stages'])-1
  stub.inspect_legacy=True
 displayed=[]
 stub.info=lambda val,*a,**kw:displayed.append(str(val))
 stub.write=lambda val,*a,**kw:displayed.append(str(val))
 stub.markdown=lambda val,*a,**kw:displayed.append(str(val))
 monkeypatch.setitem(sys.modules,'streamlit',stub)
 runpy.run_path(str(APP),run_name='__main__')
 text='\n'.join(displayed)
 assert kb['queries'][0] in text
 assert kb['mechanism_summary'][0] in text
 assert kb['incident_observations_confirming_mechanism'][0] in text
 assert kb['incident_observations_missing'][0] in text


def test_healthy_control_explicitly_displays_no_rag_use(monkeypatch):
 sid='M05I0017'
 stub=MockStreamlit('Root Cause Analysis',sid)
 messages=[]
 stub.info=lambda v,*a,**kw:messages.append(str(v))
 monkeypatch.setitem(sys.modules,'streamlit',stub)
 runpy.run_path(str(APP),run_name='__main__')
 assert any('not used' in m.lower() for m in messages)


def test_guided_demo_progressively_reveals_sp01_model_and_telemetry(monkeypatch):
 """Live-looking console must not leak future ML outputs before SP01 calls tools."""
 import gzip,json,time
 from storyboard import build_story
 from operational_demo import guided_sequence
 root=APP.parent
 def case(sid):
  return json.load(gzip.open(root/'data/cases'/f'{sid}.json.gz','rt'))
 def beats(c):
  def evidence(eid):
   ev=next(e for e in c['evidence_index'] if e['evidence_id']==eid)
   return json.load(gzip.open(root/ev['file'],'rt'))
  return build_story(c,evidence)
 healthy=case('M05I0017');incident=case('M05I0005')
 seq=guided_sequence(healthy,beats(healthy),incident,beats(incident),False)
 ml_idx=next(i for i,item in enumerate(seq) if item['scenario_id']=='M05I0005' and
             item['beat']['source'].endswith(' · ml_specialist_summary'))
 scope_idx=next(i for i,item in enumerate(seq) if item['scenario_id']=='M05I0005' and
             item['beat']['source'].endswith(' · ml_scope_probabilities'))
 network_idx=next(i for i,item in enumerate(seq) if item['scenario_id']=='M05I0005' and
             item['beat']['source'].endswith(' · telemetry_network_overview'))
 def page_at(index):
  stub=MockStreamlit('Guided Operations Demo','M05I0005')
  stub.full_engineering=True
  stub.session_state['ops_player_M05I0005_False']={
   'index':index,'playing':False,'seconds':3,'last_tick':time.monotonic(),
   'carry':0.,'presentation_elapsed':0.,'started':True
  }
  messages=[]
  stub.markdown=lambda value,*a,**kw:messages.append(str(value))
  stub.info=lambda value,*a,**kw:messages.append(str(value))
  stub.write=lambda value,*a,**kw:messages.append(str(value))
  monkeypatch.setitem(sys.modules,'streamlit',stub)
  runpy.run_path(str(APP),run_name='__main__')
  return '\n'.join(messages)
 first=page_at(0)
 assert 'Waiting for this recorded tool result' in first
 assert '85.2%' not in first
 at_ml=page_at(ml_idx)
 assert '85.2%' in at_ml
 assert 'Waiting for this recorded tool result' in at_ml
 at_scope=page_at(scope_idx)
 assert '91.4%' in at_scope
 at_telemetry=page_at(network_idx)
 assert '48 recorded subnetwork KPI observations' in at_telemetry
