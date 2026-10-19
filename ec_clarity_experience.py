"""TEAD AI clarity-first public presentation (read-only, trace-grounded).

No agents, inference, external data calls, or remediation are performed here.
E/C inspired information hierarchy; TEAD original routes and colours are retained.
"""
from __future__ import annotations

import json
from collections import OrderedDict
from html import escape

WORKSPACES = [
    "The Challenge", "Network Overview", "Architecture", "Case Stories",
    "Agent Flow", "Evidence Room", "Results",
]
LEGACY_TO_WORKSPACE = {
    "Platform Overview": "The Challenge",
    "Value Proposition & Solutions": "The Challenge",
    "Guided Operations Demo": "Case Stories",
    "Scenario Library": "Case Stories",
    "Agentic Replay": "Agent Flow",
    "Root Cause Analysis": "Evidence Room",
    "Engineering Evidence": "Evidence Room",
    "Evaluation & Performance": "Results",
}

STYLE = """<style>
/* Distinct TEAD palette, not the Exception / Control brand. */
:root{--tc-ink:#0c1630;--tc-blue:#3557e9;--tc-lime:#c9f271;--tc-ice:#8ddcf0;--tc-muted:#586981}
.tc-hero{background:linear-gradient(115deg,#0c1630,#183465);border-radius:19px;color:#f5f8ff;padding:30px 34px;margin:12px 0 20px}
.tc-kicker{color:#c9f271;font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;font-weight:800}
.tc-hero h1{color:#fff;font-size:clamp(1.6rem,3vw,2.4rem);line-height:1.12;margin:9px 0}
.tc-hero p{font-size:1.02rem;color:#d7e3f7;max-width:760px;line-height:1.6;margin-bottom:0}
.tc-section{font-size:.73rem;color:#425b8b;letter-spacing:.12em;text-transform:uppercase;font-weight:800;margin:20px 0 7px}
.tc-value-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:15px 0}
.tc-value{border:1px solid #d7e2ef;border-radius:13px;padding:16px;background:#f8fbff;min-width:0}
.tc-value b{display:block;color:#173056;font-size:.97rem;margin-bottom:7px}
.tc-value span{font-size:.88rem;color:#42556c;line-height:1.48}
.tc-journey{display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:10px 0}
.tc-journey .node{background:#eff3ff;border:1px solid #cbd7fc;border-radius:9px;padding:9px 11px;font-weight:700;color:#18305a;font-size:.82rem}
.tc-journey .arr{color:#3557e9;font-weight:800}
.tc-summary{background:#f6f9fd;border:1px solid #d7e4f0;border-radius:15px;padding:16px 20px;margin:12px 0}
.tc-case-eyebrow{font-weight:800;color:#3557e9;font-size:.75rem;text-transform:uppercase;letter-spacing:.1em}
.tc-case-title{color:#12284b;font-weight:800;font-size:1.32rem;margin:4px 0 8px}
.tc-evidence{border-left:3px solid #3557e9;padding:10px 13px;background:#f7f9ff;border-radius:4px;color:#253653;margin-top:13px;white-space:pre-wrap;overflow-wrap:anywhere}
.tc-note{font-size:.81rem;color:#64748b;line-height:1.6}
.tc-arch{border:1px solid #dce4f3;border-radius:17px;background:#f8fbff;padding:20px 23px;margin:16px 0}
.tc-arch-row{display:flex;justify-content:center;gap:11px;align-items:stretch;flex-wrap:wrap}
.tc-arch-box{border:1px solid #c8d5e8;background:#fff;border-radius:11px;padding:13px 18px;text-align:center;flex:1;min-width:150px;color:#11264b}
.tc-arch-box span{display:block;color:#53647a;font-size:.76rem;margin-top:4px;line-height:1.4}
.tc-arch-box.primary{background:#e7eeff;border-color:#a8baff}
.tc-arch-box.final{background:#edf9df;border-color:#bcdd8b}
.tc-arch-arrow{color:#3557e9;text-align:center;font-weight:900;padding:7px}
.tc-route{flex:1;background:#fff;border:1px solid #cddced;padding:12px;border-radius:11px;text-align:center;min-width:150px}
.tc-route b{color:#173056;display:block}.tc-route span{font-size:.78rem;display:block;color:#52647b;margin-top:5px}
@media(max-width:680px){.tc-hero{padding:21px}.tc-value-grid{grid-template-columns:1fr}.tc-arch{padding:12px}.tc-route{min-width:120px}}
</style>"""

AGENT_NAMES = {
    "SP01":"Network Health & Localisation",
    "SP02":"KPI Analysis", "SP03":"Cell & Peer Comparison",
    "SP04":"Radio Analysis", "SP05":"Processing Analysis",
    "SP06":"Transport Analysis", "SP07":"Configuration Analysis",
    "SP08":"CU-Domain & Boundary Analysis",
    "LOCAL_JOIN":"Specialist Findings Join", "CU_JOIN":"CU Findings Join",
    "DIRECT_JOIN":"Healthy Direct Join", "SUPERVISOR":"RCA Supervisor",
    "FINAL":"Recorded RCA Report",
}
JOIN_IDS = {"LOCAL_JOIN", "CU_JOIN", "DIRECT_JOIN"}
ROUTE_NAMES = {"DIRECT_SUPERVISOR":"Healthy — direct Supervisor review",
               "LOCAL_SPECIALISTS":"Cell/site — sequential specialists SP02–SP07",
               "CU_SPECIALIST":"CU-domain — specialist SP08"}


def _s(value, max_length=1500):
    if value is None: return ""
    if isinstance(value,(list,tuple)):
        value = "; ".join(_s(part, 340) for part in value[:5])
    elif isinstance(value,dict):
        value = "; ".join(f"{k}: {_s(v,170)}" for k,v in list(value.items())[:6])
    txt = " ".join(str(value).split())
    return txt[:max_length-1].rstrip()+"…" if len(txt)>max_length else txt


def _html(value):
    return escape(str(value), quote=True)


def route_from_beats(beats):
    """Return ONLY actual sequential stage transitions from saved beat order."""
    stages=[]
    for beat in beats:
        agent=beat.get("agent")
        if agent and agent not in stages:
            stages.append(agent)
    return stages


def agent_stages(beats):
    """One readable step per recorded stage, with its constituent source events preserved."""
    groups=OrderedDict()
    for beat in beats:
        agent=beat.get('agent')
        if not agent:
            continue
        groups.setdefault(agent,[]).append(beat)
    result=[]
    for agent,records in groups.items():
        # Prefer the last substantive output from the stage rather than a generic tool-field list.
        preferred = ('report','feedback','decision','review','handover','dispatch','join','scan')
        summary_beat=None
        for kind in preferred:
            matching=[b for b in records if b.get('kind')==kind and b.get('output')]
            if matching:
                summary_beat=matching[-1];break
        summary_beat=summary_beat or next((b for b in reversed(records) if b.get('output')),records[-1])
        starting=next((b for b in records if b.get('input')),records[0])
        tools=[b for b in records if b.get('kind')=='tool']
        result.append({
            'id':agent,'name':AGENT_NAMES.get(agent,agent),
            'role': 'consolidation' if agent in JOIN_IDS else 'report' if agent=='FINAL' else 'agent',
            'question':_s(starting.get('input'),500),
            'activity':_s(summary_beat.get('action'),480),
            'finding':_s(summary_beat.get('output'),830),
            'tool_count':len(tools),
            'tools':[{'name':_s(b.get('title'),180),'result':_s(b.get('output'),460),'evidence_id':b.get('evidence_id') or ''} for b in tools],
            'events':[{'kind':_s(b.get('kind'),45),'title':_s(b.get('title'),180),
                       'input':_s(b.get('input'),1000),'action':_s(b.get('action'),1000),
                       'output':_s(b.get('output'),1800),'source':_s(b.get('source'),240),
                       'evidence_id':b.get('evidence_id') or '', 'timestamp':b.get('timestamp') or ''}
                      for b in records],
        })
    return result


def case_story_steps(case,beats):
    """Trace-grounded editorial chapters: not extra agents or recorded execution spans."""
    stages=agent_stages(beats)
    find=lambda x: next((s for s in stages if s['id']==x),None)
    sp01=find('SP01')
    specialists=[x for x in stages if x['id'].startswith('SP') and x['id']!='SP01']
    sup=find('SUPERVISOR')
    final=find('FINAL')
    scenario=case.get('scenario_id','Recorded investigation')
    route=case.get('route_family')
    ret=[{
        'label':'THE SIGNAL','title':'What network investigation was recorded?',
        'summary':f"{scenario}: {case.get('title','Recorded synthetic-network scenario')}. This is one saved experimental investigation, not a live network incident.",
        'evidence':_s(next((b.get('input') for b in beats if b.get('agent')=='SP01' and b.get('input')),''),750),
        'agent':'SP01'},
        {'label':'NETWORK ASSESSMENT','title':'What did the localisation agent establish?',
         'summary':_s(sp01['finding'] if sp01 else 'SP01 evidence was not supplied.',960),
         'evidence':f"Recorded route: {ROUTE_NAMES.get(route,route or 'Not recorded')}. SP01 uses supporting ML predictions and network telemetry; ML tools are not additional agents.",
         'agent':'SP01'},
    ]
    if specialists:
        summary=' | '.join(f"{s['id']} {s['name']}: {_s(s['finding'] or s['activity'],140)}" for s in specialists)
        ret.append({'label':'SPECIALIST INVESTIGATION',
                    'title':'What did the specialist investigation establish?',
                    'summary':_s(summary,1200),
                    'evidence':('The recorded sequence contains '+str(len(specialists))+
                                ' specialist agent(s). Their individual handovers, source events and tools '
                                'are shown separately in Agent Flow.'),
                    'agent':specialists[0]['id']})
    else:
        ret.append({'label':'ROUTING DECISION','title':'Why were specialist agents not called?',
                    'summary':'The recorded healthy route went directly towards Supervisor assessment; no specialist investigation is represented.',
                    'evidence':'This is the direct Supervisor path, not a hidden parallel specialist execution.',
                    'agent':'DIRECT_JOIN'})
    ret.append({'label':'SUPERVISOR','title':'How were the findings brought together?',
                'summary':_s(sup['finding'] if sup else 'No Supervisor stage in the supplied recorded sequence.',1000),
                'evidence':'The Supervisor reviews the recorded evidence, hypotheses and uncertainty. Knowledge retrieval is supporting evidence where recorded.',
                'agent':'SUPERVISOR'})
    out=(case.get('stage_data') or {}).get('supervisor_output') or {}
    ret.append({'label':'OUTCOME','title':'What did the recorded investigation conclude?',
                'summary':_s(out.get('diagnosis') or (final or {}).get('finding') or 'See the preserved RCA source.',1100),
                'evidence':'This conclusion and any uncertainty are the original recorded Supervisor output. No live diagnosis, remediation or network change occurs here.',
                'agent':'FINAL'})
    return ret


def _case_header(case,stage_title):
    return ('<section class="tc-summary"><div class="tc-case-eyebrow">'+_html(stage_title)+' · RECORDED EXPERIMENT</div>'
            '<div class="tc-case-title">'+_html(case.get('title','Recorded case'))+'</div>'
            '<span><b>Scenario:</b> '+_html(case.get('scenario_id','—'))+'</span> &nbsp; · &nbsp; '
            '<span><b>Route:</b> '+_html(ROUTE_NAMES.get(case.get('route_family'),case.get('route_family','—')))+'</span>'
            '</section>')


def render_challenge(st, scenario_id='M05I0003'):
    st.markdown('''<section class="tc-hero"><div class="tc-kicker">TEAD AI · AGENTIC TELECOM ENGINEERING</div>
      <h1>Understand the network problem.<br>See how the agents diagnosed it.</h1>
      <p>From fragmented network measurements to an evidence-backed root-cause assessment. Explore actual recorded synthetic-network investigations, one clear step at a time.</p></section>''',unsafe_allow_html=True)
    st.markdown('<div class="tc-section">The operational challenge</div>',unsafe_allow_html=True)
    st.markdown('''<div class="tc-value-grid">
    <div class="tc-value"><b>Fragmented evidence</b><span>Radio, accessibility, processing, transport and configuration data must be correlated across sites and cells.</span></div>
    <div class="tc-value"><b>Multiple possible causes</b><span>Similar symptoms can arise from different network domains. The diagnosis needs discrimination, not just classification.</span></div>
    <div class="tc-value"><b>Defensible conclusions</b><span>Operators need a clear root-cause explanation, affected scope, supporting evidence and explicit uncertainties.</span></div>
    </div>''',unsafe_allow_html=True)
    st.markdown('<div class="tc-section">How to explore TEAD AI</div>',unsafe_allow_html=True)
    st.markdown('''<div class="tc-journey"><span class="node">Explore 10 sites / 30 cells</span><span class="arr">→</span>
      <span class="node">Understand the agent architecture</span><span class="arr">→</span>
      <span class="node">Read a case story</span><span class="arr">→</span>
      <span class="node">Watch the agent flow</span><span class="arr">→</span><span class="node">Inspect the evidence</span></div>''',unsafe_allow_html=True)
    st.caption('The public demonstration is offline: it replays saved synthetic-network experiments only. Recorded investigation times are not measured field MTTR savings.')
    a,b,c=st.columns(3,gap='small')
    with a:
        if st.button('▶ Start with a case story',type='primary',key='tc_challenge_story',use_container_width=True):
            st.session_state['selected_scenario']=scenario_id
            st.session_state['requested_page']='Case Stories'; st.rerun()
    with b:
        if st.button('Understand the architecture →',key='tc_challenge_arch',use_container_width=True):
            st.session_state['requested_page']='Architecture'; st.rerun()
    with c:
        if st.button('Watch the agent flow →',key='tc_challenge_flow',use_container_width=True):
            st.session_state['selected_scenario']=scenario_id
            st.session_state['requested_page']='Agent Flow';st.rerun()


def render_architecture(st):
    st.markdown('''<section class="tc-hero"><div class="tc-kicker">02 / HOW THE SYSTEM WORKS</div>
      <h1>One network assessment. Three possible routes.</h1><p>Understand the implemented AI investigation before watching it run. Only one conditional route is taken in a recorded case.</p></section>''',unsafe_allow_html=True)
    st.markdown('''<section class="tc-arch" aria-label="TEAD AI source-grounded conditional architecture">
      <div class="tc-arch-row"><div class="tc-arch-box"><b>Saved network observations</b><span>15-minute PM, events, topology, radio, processing, transport and configuration evidence</span></div></div>
      <div class="tc-arch-arrow">↓</div>
      <div class="tc-arch-row"><div class="tc-arch-box primary"><b>SP01 · Network Health &amp; Localisation</b><span>Two ML prediction <em>tools</em> (fault family and scope) + telemetry. Assesses degradation and selects investigation route.</span></div></div>
      <div class="tc-arch-arrow">↓ Conditional route selected from saved evidence ↓</div>
      <div class="tc-arch-row">
        <div class="tc-route"><b>Healthy network</b><span>Direct Supervisor review · no specialist escalation</span></div>
        <div class="tc-route"><b>Cell / site incident</b><span>SP02 → SP03 → SP04 → SP05 → SP06 → SP07, sequentially</span></div>
        <div class="tc-route"><b>CU-domain incident</b><span>SP08 · CU-Domain &amp; Boundary specialist</span></div>
      </div>
      <div class="tc-arch-arrow">↓ Recorded findings consolidated through the applicable join ↓</div>
      <div class="tc-arch-row"><div class="tc-arch-box"><b>RCA Supervisor</b><span>Cross-domain synthesis, alternative hypotheses, uncertainty and curated knowledge support where recorded</span></div></div>
      <div class="tc-arch-arrow">↓</div>
      <div class="tc-arch-row"><div class="tc-arch-box final"><b>Recorded RCA</b><span>Diagnosis · affected scope · supporting evidence · outstanding uncertainty</span></div></div>
      </section>''',unsafe_allow_html=True)
    st.info('The flow above represents the experimental implementation, not a live control loop. ML tools are not agents; join and report nodes are workflow stages. No network execution or remediation is enabled.')
    st.markdown('**Meet the specialists**')
    cols=st.columns(3)
    for i,agent in enumerate([f'SP{j:02d}' for j in range(2,9)]):
        with cols[i%3]:
            st.markdown(f'**{agent} · {AGENT_NAMES[agent]}**')
    st.caption('SP02–SP07 are the sequential cell/site route. SP08 is an alternative CU-domain route, not a seventh sequential cell/site specialist.')


def render_case_stories(st,case,beats):
    steps=case_story_steps(case,beats)
    sid=case['scenario_id']
    key=f'tc_story_{sid}'
    ix=max(0,min(len(steps)-1,int(st.session_state.get(key,0))))
    st.markdown('<section class="tc-hero"><div class="tc-kicker">04 / CASE STORIES</div><h1>What happened in this investigation?</h1><p>A simple, evidence-grounded narrative. Read the diagnosis first; open Agent Flow only when you want to see the recorded handovers.</p></section>',unsafe_allow_html=True)
    st.markdown(_case_header(case,'CASE STORY'),unsafe_allow_html=True)
    st.caption('Use the sidebar to select another case. Each case is a separate recorded experiment.')
    st.progress((ix+1)/len(steps),text=f'Chapter {ix+1} of {len(steps)} · {steps[ix]["label"]}')
    step=steps[ix]
    st.markdown(f'<section class="tc-summary"><div class="tc-case-eyebrow">{_html(step["label"])}</div><div class="tc-case-title">{_html(step["title"])}</div><p>{_html(step["summary"])}</p><div class="tc-evidence">{_html(step["evidence"])}</div></section>',unsafe_allow_html=True)
    a,b,c=st.columns([1,1,1.5])
    with a:
        if st.button('← Previous chapter',disabled=ix==0,key='tc_story_back',use_container_width=True):
            st.session_state[key]=ix-1;st.rerun()
    with b:
        if st.button('Next chapter →',disabled=ix>=len(steps)-1,key='tc_story_next',use_container_width=True):
            st.session_state[key]=ix+1;st.rerun()
    with c:
        if st.button('See this case in Agent Flow →',type='primary',key='tc_story_flow',use_container_width=True):
            st.session_state['requested_page']='Agent Flow';st.rerun()
    with st.expander('All chapters at a glance',expanded=False):
        for j,s in enumerate(steps):
            st.markdown(f'{j+1}. **{s["title"]}** — {s["label"]}')
    st.caption('Chapters are editorial summaries derived from saved evidence, not additional agents or real-time events. The precise recorded event order is available inside Agent Flow.')


def build_agent_flow_html(case,beats):
    """Self-contained, read-only, interactive E/C-style visual flow of actual agent route."""
    stages=agent_stages(beats)
    if not stages:
        return '<p>No recorded stages available for this scenario.</p>'
    payload={'scenario':case.get('scenario_id'), 'title':case.get('title'),
             'route':ROUTE_NAMES.get(case.get('route_family'),case.get('route_family')),
             'stages':stages}
    data=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return _FLOW_HTML.replace('__PAYLOAD__',data)


def render_agent_flow(st,case,beats,embed_html):
    st.markdown('<section class="tc-hero"><div class="tc-kicker">05 / CONNECTED AGENT FLOW</div><h1>Follow the agents. See what each one contributed.</h1><p>One route, one playback, with the current stage and saved findings always together. Every output comes from the recorded investigation.</p></section>',unsafe_allow_html=True)
    st.markdown(_case_header(case,'AGENT FLOW'),unsafe_allow_html=True)
    st.caption('Press Next to move one agent/stage at a time, or Play for automatic reading. Start in Manual mode; individual raw events are in the expandable inspector.')
    embed_html(build_agent_flow_html(case,beats),height=720,scrolling=False)
    if st.button('Open this case in Evidence Room →',type='primary',key='tc_flow_evidence'):
        st.session_state['requested_page']='Evidence Room';st.rerun()
    st.caption('Playback pace is for reading, not the original recorded execution duration. Saved performance measurements and original evidence remain separate.')


_FLOW_HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
:root{--ink:#0c1630;--blue:#3557e9;--lime:#c9f271;--ice:#8ddcf0;--muted:#586981;--line:#d6dfef}
*{box-sizing:border-box}body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;color:var(--ink);margin:0;background:#fff;font-size:14px}
.shell{border:1px solid var(--line);border-radius:17px;overflow:hidden;background:#f9fbff}
.toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:13px 16px;background:#0c1630;color:#fff;position:sticky;top:0;z-index:2}
.toolbar .label{font-weight:800;flex:1;min-width:145px;color:#e7f1ff}.toolbar button,.toolbar select{border:1px solid #7089b4;padding:9px 12px;border-radius:8px;color:#f9fcff;background:#1c3356;font-size:13px;cursor:pointer}
.toolbar button:disabled{opacity:.45;cursor:not-allowed}.toolbar button.primary{background:#c9f271;border-color:#c9f271;color:#0c1630;font-weight:800}
.toolbar select{max-width:180px}.route-meta{padding:13px 17px 6px;font-size:13px;color:#47566e}.route-meta strong{color:#0c1630}
.flow{padding:14px 18px 19px;background:linear-gradient(135deg,#f8fbff,#eff4ff)}
.flowline{display:flex;align-items:center;justify-content:flex-start;gap:6px;flex-wrap:nowrap;overflow-x:auto;padding:8px 2px;scrollbar-color:#b9c9e4 transparent}
.flowline[hidden]{display:none}#upstream,#downstream{justify-content:center}
.node{flex:0 0 auto;text-align:center;width:128px;min-height:67px;display:flex;flex-direction:column;justify-content:center;background:#fff;border:2px solid #cdd6e8;color:#31435f;border-radius:10px;padding:9px 7px;transition:border-color .25s,box-shadow .25s,background .25s}
.node .id{font-weight:850;font-size:12px;color:#274784}.node .name{font-size:11px;line-height:1.2;font-weight:670;margin-top:5px}
.node.done{border-color:#9ab4d8;background:#e7f0ff}.node.active{background:#e6f0ff;border-color:var(--blue);box-shadow:0 0 0 4px #3557e921}
.node.active .id{color:#1a2bb4}.node.report.active{background:#f0f9dc;border-color:#7aa42a}.node.consolidation{width:114px;border-style:dashed}
.arrow{color:#3557e9;font-weight:950;flex:0 0 auto;text-align:center}.flow-down{text-align:center;color:#3557e9;font-weight:900;font-size:19px;line-height:1;padding:2px}.statusline{display:flex;gap:10px;flex-wrap:wrap;justify-content:space-between;margin-top:9px;border-top:1px solid #dce7f5;padding-top:10px;font-size:12px;color:#34496c}
.details{display:grid;grid-template-columns:1.06fr .94fr;border-top:1px solid #d6dfef;min-height:245px}
.panel{padding:20px 21px;background:#fff}.panel+ .panel{border-left:1px solid #d6dfef;background:#fcfdff}
.eyebrow{color:#3557e9;letter-spacing:.10em;font-size:11px;text-transform:uppercase;font-weight:800}
.title{font-size:19px;font-weight:830;margin:7px 0 14px;line-height:1.25}
.line{margin:10px 0;line-height:1.46}.line b{color:#28436c}.finding{padding:12px 14px;border-left:4px solid #3557e9;background:#f2f6ff;border-radius:5px;margin-top:15px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere}
.tools{font-size:12px;color:#42556a;padding:8px 10px;background:#f2f6fb;border-radius:8px;margin:12px 0}
.finding{max-height:170px;overflow-y:auto}#events{max-height:220px;overflow-y:auto}.reading{padding:11px 18px;background:#ebf0fa;border-top:1px solid #d7dfed;font-size:12px;color:#455672}
summary{cursor:pointer;font-weight:740;color:#224ca1}details{margin-top:11px;border-top:1px solid #e0e7f4;padding-top:11px}details .event{margin:10px 0;background:#f2f5fa;padding:8px;border-radius:6px;font-size:12px;line-height:1.5;overflow-wrap:anywhere}
.labeltiny{font-weight:800;text-transform:uppercase;color:#536d94;font-size:10px;margin:8px 0 3px}
@media(max-width:760px){.details{grid-template-columns:1fr}.panel+.panel{border-left:0;border-top:1px solid #d6dfef}.node{width:118px}.toolbar{position:static}.flowline{justify-content:flex-start}}
@media(prefers-reduced-motion:reduce){.node{transition:none}}
</style></head><body><div class="shell">
<div class="toolbar"><div class="label">RECORDED AGENT JOURNEY</div>
<button id="prev" aria-label="Previous stage">← Back</button><button id="play" class="primary" aria-label="Play or pause playback">▶ Play</button><button id="next" aria-label="Next stage">Next →</button><button id="reset" aria-label="Restart">↺ Restart</button>
<label for="pace" style="font-size:12px">Reading pace</label><select id="pace" aria-label="Reading pace"><option value="manual">Manual (recommended)</option><option value="15">Overview · 15 s</option><option value="30">Comfortable · 30 s</option><option value="60">Detailed · 60 s</option></select></div>
<div class="route-meta"><strong id="scenario"></strong> &nbsp; · &nbsp; <span id="route"></span></div>
<div class="flow" role="group" aria-label="Recorded selected agent route">
 <div id="upstream" class="flowline"></div><div class="flow-down" aria-hidden="true">↓</div><div id="specialists" class="flowline"></div><div class="flow-down" aria-hidden="true">↓</div><div id="downstream" class="flowline"></div>
 <div class="statusline"><b id="stepmeta"></b><span id="duration">Manual reading · no live execution</span></div>
</div>
<div class="details"><div class="panel"><div class="eyebrow" id="role"></div><div class="title" id="title"></div>
<div class="line"><b>Received / investigated:</b> <span id="input"></span></div><div class="line"><b>Action:</b> <span id="activity"></span></div>
<div class="finding"><strong>What this stage established</strong><div id="finding"></div></div>
<div class="tools" id="toolcount"></div></div>
<div class="panel"><div class="eyebrow">FOLLOW THE HANDOVER</div><div class="title" id="handover"></div>
<div id="handover-text" class="line"></div>
<details><summary>Inspect original recorded events for this stage</summary><div id="events"></div></details>
<div class="line" style="font-size:12px;color:#667992">This panel uses source-backed presentation summaries, not a new agent decision. Read the original events above for exact recorded words and evidence IDs.</div></div></div>
<div class="reading">One highlighted stage at a time. Arrows reflect recorded sequential order only. Consolidation and report nodes are not AI agents. The public replay does not invoke live agents, tools or network actions.</div>
</div><script>
const data=__PAYLOAD__;
const $=(id)=>document.getElementById(id);let index=0,timer=null,playing=false;
const stages=data.stages;
function addText(parent,text){const n=document.createElement('div');n.className='event';n.textContent=text||'Not recorded';parent.appendChild(n);}
function drawRow(id,nodes){const row=$(id);row.replaceChildren();row.hidden=nodes.length===0;
  nodes.forEach((n,i)=>{if(i){const arrow=document.createElement('span');arrow.className='arrow';arrow.textContent='→';row.appendChild(arrow)}
  const cell=document.createElement('div');cell.className='node '+n.role;if(n.idx<index)cell.classList.add('done');if(n.idx===index)cell.classList.add('active');
  const label=document.createElement('div');label.className='id';label.textContent=n.id==='FINAL'?'RCA':n.id.endsWith('_JOIN')?'JOIN':n.id;
  const sub=document.createElement('div');sub.className='name';sub.textContent=n.name;cell.append(label,sub);row.appendChild(cell);if(n.idx===index){requestAnimationFrame(()=>{row.scrollLeft=Math.max(0,cell.offsetLeft-row.offsetLeft-row.clientWidth/2+cell.clientWidth/2)})}});
}
function show(){const s=stages[index];$('scenario').textContent=data.scenario+' · '+data.title;$('route').textContent=data.route||'';
  const head=stages.findIndex(x=>x.id==='SUPERVISOR');const tail=stages.findIndex(x=>x.id==='FINAL');
  drawRow('upstream',stages.map((x,idx)=>({...x,idx})).filter(x=>x.id==='SP01'));
  drawRow('specialists',stages.map((x,idx)=>({...x,idx})).filter(x=>x.id!=='SP01'&&x.id!=='SUPERVISOR'&&x.id!=='FINAL'));
  drawRow('downstream',stages.map((x,idx)=>({...x,idx})).filter(x=>x.id==='SUPERVISOR'||x.id==='FINAL'));
  $('stepmeta').textContent=`STAGE ${index+1} OF ${stages.length} · ${s.role==='agent'?'AGENT':s.role==='consolidation'?'CONSOLIDATION':'RECORDED REPORT'}`;
  $('role').textContent=s.role==='agent'?'ACTIVE AGENT':s.role==='consolidation'?'RECORDING HANDOVER':'RECORDED OUTPUT';
  $('title').textContent=s.id+' · '+s.name;
  $('input').textContent=s.question||'No separate input summary recorded';$('activity').textContent=s.activity||'Source event available in inspector';
  $('finding').textContent=s.finding||'No summary in the saved stage';
  $('toolcount').textContent=s.tool_count?`${s.tool_count} recorded tool event(s) in this stage — expand the event inspector to view evidence IDs.`:'No separate tool call recorded for this stage.';
  $('handover').textContent=index===stages.length-1?'Investigation complete':`Next: ${stages[index+1].id} · ${stages[index+1].name}`;
  $('handover-text').textContent=index===stages.length-1?'Open Evidence Room in the main application for original RCA and measurements.':'Follow the recorded route to the next stage. This does not represent a new live handover.';
  const host=$('events');host.replaceChildren();s.events.forEach((e,i)=>{addText(host,`${i+1}. ${e.title} [${e.kind}]\nINPUT: ${e.input||'Not separately recorded'}\nACTION: ${e.action||'Not separately recorded'}\nOUTPUT: ${e.output||'Not separately recorded'}\nSOURCE: ${e.source||'Not recorded'}${e.evidence_id?'\nEVIDENCE ID: '+e.evidence_id:''}${e.timestamp?'\nRECORDED START: '+e.timestamp:''}`)});
  $('prev').disabled=index===0;$('next').disabled=index===stages.length-1;$('play').textContent=playing?'⏸ Pause':'▶ Play';
  if(index===stages.length-1&&playing)stop();
}
function stop(){playing=false;if(timer!==null)clearTimeout(timer);timer=null;$('play').textContent='▶ Play'}
function advance(n){index=Math.max(0,Math.min(stages.length-1,n));show()}
function schedule(){if(!playing)return;const t=Number($('pace').value);if(!t){stop();return}
 timer=setTimeout(()=>{if(index>=stages.length-1){stop();return}advance(index+1);schedule()},t*1000)}
$('prev').addEventListener('click',()=>{stop();advance(index-1)});
$('next').addEventListener('click',()=>{stop();advance(index+1)});
$('reset').addEventListener('click',()=>{stop();advance(0)});
$('play').addEventListener('click',()=>{if(playing){stop();return}if($('pace').value==='manual')$('pace').value='30';if(index===stages.length-1)index=0;playing=true;show();schedule()});
$('pace').addEventListener('change',()=>{if(playing){clearTimeout(timer);if($('pace').value==='manual'){stop();return}schedule()}});
show();
</script></body></html>'''
