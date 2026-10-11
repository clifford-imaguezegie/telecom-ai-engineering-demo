"""Offline page render smoke tests using a recorder stub, not a browser test.
This verifies all six page branches with actual bundled data without installing
Streamlit or contacting the Internet. Real browser QA remains necessary.
"""
import runpy
import sys
from types import ModuleType
from pathlib import Path
import pytest

APP=Path(__file__).resolve().parents[1]/'app.py'
PAGES=['Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis','Engineering Evidence','Evaluation & Performance']

class _Context:
 def metric(self,*args,**kwargs):pass
 def __enter__(self):return self
 def __exit__(self,*args):return False

class MockStreamlit(ModuleType):
 def __init__(self,page,scenario):
  super().__init__('streamlit')
  self.session_state={'nav_page':page,'selected_scenario':scenario}
  self.sidebar=self
 def cache_data(self,**kwargs):return lambda fn:fn
 def set_page_config(self,**kwargs):pass
 def markdown(self,*args,**kwargs):pass
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
  return options[0]
 def selectbox(self,label,options,**kwargs):
  if label=='Scenario':return self.session_state['selected_scenario']
  return options[kwargs.get('index',0)]
 def select_slider(self,label,options,**kwargs):return kwargs.get('value',options[0])

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
 if page=='Agentic Replay':stub.session_state['replay_'+sid]=len(c['stages'])-1
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
