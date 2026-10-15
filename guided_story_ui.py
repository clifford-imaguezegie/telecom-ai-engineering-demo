"""Presentation-only direction for TEAD AI's recorded Guided Operations Demo.

No model, network, or data calls. All statements about recorded outcomes come
from existing storyboard beats and original saved case records supplied by app.py.
"""
from html import escape

EVIDENCE_TOOLS = (
    ('ml_specialist_summary', 'ML · WHAT', 'Fault-family prediction'),
    ('ml_scope_probabilities', 'ML · WHERE', 'Affected-scope prediction'),
    ('telemetry_network_overview', 'NETWORK', 'Performance counters'),
    ('telemetry_events', 'EVENTS', 'Event telemetry'),
)
ROUTES = {'DIRECT_SUPERVISOR':'healthy','LOCAL_SPECIALISTS':'site','CU_SPECIALIST':'cu'}
SPECIALISTS = ['SP02','SP03','SP04','SP05','SP06','SP07']
SPECIALIST_NAMES = ['KPI','Cell / peer','Radio','Processing','Transport','Configuration']


def tool_for(beat):
    src = beat.get('source','')
    return src.rsplit(' · ',1)[-1] if beat.get('kind') == 'tool' and ' · ' in src else None


def phase_for(item):
    beat=item['beat']; agent=beat['agent']; kind=beat['kind']
    if not item['case']['derived_display']['incident_present']:
        if agent=='FINAL':
            return (3,'Healthy outcome','Supervisor confirms that available evidence does not support a material incident.')
        if kind in ('decision','handover') or agent=='SUPERVISOR':
            return (2,'Health decision','Assess whether the recorded observations justify specialist escalation.')
        return (1,'Health and evidence review','Inspect the network, ML predictions and telemetry before making a decision.')
    if agent=='FINAL':
        return (6,'Investigation outcome','Read the recorded RCA or healthy outcome and verify its supporting evidence.')
    if agent=='SUPERVISOR' or agent.endswith('_JOIN'):
        return (5,'Supervisor synthesis','Reconcile domain evidence, technical knowledge, alternatives and uncertainty.')
    if agent.startswith('SP') and agent!='SP01':
        return (4,'Specialist investigation','Inspect the selected engineering domain and record supporting or weakening evidence.')
    if kind in {'decision','handover'}:
        return (3,'Assessment and routing','Determine if the evidence supports degradation and choose the investigation route.')
    if kind=='tool':
        return (2,'ML and telemetry arrive','Collect supporting ML predictions and deterministic network observations.')
    return (1,'Start network assessment','Understand the selected observation window before drawing conclusions.')


def _state(label, done, active):
    return f'{label}'+(' · NOW' if active else ' · REVIEWED' if done else '')


def flow_html(item, past, ready=False):
    """Four-node connected architecture with mutually exclusive paths; never preselect a path."""
    case=item['case']; beat=item['beat']; phase=phase_for(item)[0] if not ready else 0
    selected=ROUTES.get(case['route_family']) if (not ready and any(
        x['scenario_id']==item['scenario_id'] and x['beat']['agent']=='SP01' and
        x['beat']['kind'] in ('decision','handover') for x in past)) else None
    current=beat['agent'] if not ready else ''
    done_agents={x['beat']['agent'] for x in past if x['scenario_id']==item['scenario_id'] and x['beat']['kind']=='feedback'}
    def path(route,title,content):
        chosen=route==selected
        cls=' chosen' if chosen else ' waiting' if selected is None else ' muted'
        if route=='site':
            chips=[]
            for id_,short in zip(SPECIALISTS,SPECIALIST_NAMES):
                active=(current==id_ and not ready)
                done=(id_ in done_agents)
                cc=' active' if active else ' done' if done else ''
                chips.append(f'<span class="gs-specialist{cc}" title="{escape(id_+" "+short)}">{escape(id_)}</span>')
            content='<div class="gs-specialists">'+''.join(chips)+'</div><small>Sequential KPI → Cell → Radio → Processing → Transport → Config</small>'
        return f'<div class="gs-path{cls}"><b>{escape(title)}</b>{content}</div>'
    sp01_cls=' active' if current=='SP01' else ' done' if current else ''
    supervisor_cls=' active' if current=='SUPERVISOR' or current.endswith('_JOIN') else ' done' if current=='FINAL' else ''
    final_cls=' active' if current=='FINAL' else ''
    html=(f'<section class="gs-route" aria-label="Connected recorded investigation flow">'
          f'<div class="gs-flow-heading"><b>INVESTIGATION ROUTE</b><span>'
          f'{"Potential routes · awaiting evidence" if selected is None else "Selected path · "+{"healthy":"Healthy direct review","site":"Cell/site specialists","cu":"CU specialist"}[selected]}</span></div>'
          f'<div class="gs-flow-grid">'
          f'<div class="gs-node{sp01_cls}"><span class="gs-eyebrow">01 · ASSESS</span><b>Network health &amp; localisation</b><small>SP01 · ML + telemetry</small></div>'
          '<div class="gs-arrow" aria-hidden="true">→</div>'
          '<div class="gs-branches">'
          +path('healthy','HEALTHY · Direct Supervisor','<small>No specialists</small>')
          +path('site','CELL / SITE · SP02–SP07','')
          +path('cu','CU DOMAIN · SP08','<small>CU &amp; boundary investigation</small>')
          +'</div><div class="gs-arrow" aria-hidden="true">→</div>'
          +f'<div class="gs-node gs-supervisor{supervisor_cls}"><span class="gs-eyebrow">03 · CORRELATE</span><b>RCA Supervisor</b><small>Evidence + RAG where used</small></div>'
          +'<div class="gs-arrow" aria-hidden="true">→</div>'
          +f'<div class="gs-node gs-final{final_cls}"><span class="gs-eyebrow">04 · OUTCOME</span><b>Recorded RCA</b><small>Source-backed conclusion</small></div>'
          +'</div><div class="gs-flow-note">Routes are alternatives, not parallel paths. Cell/site specialists ran sequentially in the recorded experiments.</div></section>')
    return html


def evidence_html(timeline, index, ready=False):
    """Progressive four-source evidence board, scoped to the current source trace."""
    sid=timeline[index]['scenario_id']; beat=timeline[index]['beat']
    revealed={}
    if not ready:
        for x in timeline[:index+1]:
            if x['scenario_id']!=sid: continue
            b=x['beat']
            tool=tool_for(b)
            if b['agent']=='SP01' and tool in dict((t[0],1) for t in EVIDENCE_TOOLS):
                revealed[tool]=b
    current_tool=tool_for(beat) if not ready else None
    blocks=[]
    for tool,short,title in EVIDENCE_TOOLS:
        b=revealed.get(tool)
        if b:
            msg=' '.join(str(b.get('output') or 'Recorded output available').split())
            msg=msg if len(msg)<180 else msg[:177].rsplit(' ',1)[0]+'…'
            now=tool==current_tool
            cls=' new' if now else ' revealed'
            marker='<strong class="gs-new">JUST REVEALED</strong>' if now else '<strong class="gs-received">RECEIVED</strong>'
        else:
            msg='Waiting for this recorded tool result';cls=' pending';marker='<strong class="gs-await">AWAITING</strong>'
        blocks.append(f'<div class="gs-evidence{cls}"><div class="gs-evidence-head"><span>{escape(short)}</span>{marker}</div><b>{escape(title)}</b><p>{escape(msg)}</p></div>')
    return '<section class="gs-evidence-wrap" aria-label="Evidence is revealed in recorded order"><div class="gs-board-head"><b>WHAT EVIDENCE HAS ARRIVED?</b><span>Outputs appear only after their source beat</span></div><div class="gs-evidence-grid">'+''.join(blocks)+'</div></section>'


def focus_html(item, position, count, ready=False):
    """One focal observation at a time, rather than three competing scrolling panes."""
    b=item['beat'];num,title,why=phase_for(item)
    if ready:
        return ('<section class="gs-focus" aria-label="Ready to watch">'
                '<span class="gs-scene">READY · SCENE 0</span><h3>Start with the network evidence</h3>'
                '<p>The recorded run is paused before its first investigation scene. Select <b>Play</b> or <b>Next</b> to reveal what the localisation agent reviews.</p>'
                '<div class="gs-why">Follow the highlighted route and the four evidence tiles as each saved result appears.</div></section>')
    output=' '.join(str(b.get('output') or 'No separate recorded result saved for this scene.').split())
    if len(output)>310:output=output[:307].rsplit(' ',1)[0]+'…'
    return (f'<section class="gs-focus" aria-label="Current recorded investigation scene">'
            f'<div class="gs-focus-top"><span class="gs-scene">CHAPTER {num} / {3 if not item["case"]["derived_display"]["incident_present"] else 6} · SCENE {position}/{count}</span><span class="gs-scene-agent">{escape(b["agent"])} · {escape(b["kind"].upper())}</span></div>'
            f'<h3>{escape(b["title"])}</h3>'
            f'<div class="gs-why"><b>WHY THIS STEP?</b> {escape(why)}</div>'
            f'<div class="gs-result"><b>RECORDED OBSERVATION</b><p>{escape(output)}</p></div>'
            '<p class="gs-source-note">Result from the original saved experiment; full messages and tool evidence are below.</p>'
            '</section>')


def boundary_html(healthy_id, incident_id):
    return (f'<section class="gs-boundary"><b>FIRST RECORDING COMPLETE · {escape(healthy_id)}</b>'
            '<h3>This healthy network did not become the next incident.</h3>'
            f'<p>The next demonstration opens an <b>independent recorded synthetic-network case ({escape(incident_id)})</b>. '
            'It is not a fault that developed during the healthy recording.</p>'
            '<p>Playback stops here until you explicitly continue.</p></section>')
