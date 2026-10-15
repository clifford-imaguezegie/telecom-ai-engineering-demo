"""Presentation-only direction for TEAD AI's recorded Guided Operations Demo.

No model, network, or data calls. All statements about recorded outcomes come
from existing storyboard beats and original saved case records supplied by app.py.
"""
from html import escape
import re
from operational_demo import event_trace_offset, format_clock

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


def _compact(value, limit=210):
    value=' '.join(str(value or '').split())
    return value if len(value)<=limit else value[:limit-1].rsplit(' ',1)[0]+'…'


def _clock(case, beat):
    if case is None:
        return None
    elapsed=event_trace_offset(case,beat)
    if elapsed is None:
        return None
    return f'{int(elapsed)//60:02}:{elapsed%60:04.1f}'


def _node_clock(case, agent):
    for n in case.get('observed_nodes',[]):
        if n.get('name')==agent and n.get('depth')==1 and n.get('run_type')=='chain':
            from datetime import datetime
            try:
                start=datetime.fromisoformat(case['trace_start_utc'].replace('Z','+00:00'))
                end=datetime.fromisoformat(n['end_time'].replace('Z','+00:00'))
                seconds=(end-start).total_seconds()
                if 0 <= seconds <= case['trace_duration_seconds']+0.1:
                    return f'{int(seconds)//60:02}:{seconds%60:04.1f}'
            except (ValueError,TypeError,KeyError):
                pass
    return None


def _scope(case):
    scope=case.get('stage_data',{}).get('supervisor_output',{}).get('final_scope') or {}
    kind=scope.get('scope_class') or case.get('derived_display',{}).get('scope_class') or 'UNKNOWN'
    sites=scope.get('affected_sites') or []
    domains=scope.get('affected_cu_domains') or []
    cells=[x.get('nr_cell_cu_id') for x in scope.get('affected_cells',[]) if isinstance(x,dict) and x.get('nr_cell_cu_id')]
    if kind=='NO_ISSUE':
        return 'No affected network scope', 'Healthy assessment · no material incident'
    if kind in ('CU_DOMAIN','CU_DOMAIN_BOUNDARY'):
        return ', '.join(domains) or case.get('derived_display',{}).get('target_cu_domain_id') or kind, f'{len(sites)} sites · {len(cells)} cells affected' if sites or cells else 'CU-domain investigation'
    if kind=='SITE':
        return ', '.join(sites) or case.get('derived_display',{}).get('target_site_id') or kind, f'{len(cells)} affected cells' if cells else 'Recorded site scope'
    if kind in ('CELL','CELL_5QI'):
        return ', '.join(cells[:2]) + (f' +{len(cells)-2}' if len(cells)>2 else '') if cells else kind, f'{len(cells)} recorded affected cell(s)'
    return kind, f'{len(sites)} sites · {len(cells)} cells' if sites or cells else 'Recorded investigation scope'


def _card(label, title, desc, status, current=False, large=False):
    cls=' new' if current else ' revealed' if status!='AWAITING' else ' pending'
    cls+=' gs-rca-primary' if large else ''
    tag=('<strong class="gs-new">JUST REVEALED</strong>' if current else
         '<strong class="gs-received">RECORDED</strong>' if status!='AWAITING' else
         '<strong class="gs-await">AWAITING</strong>')
    return (f'<div class="gs-evidence{cls}"><div class="gs-evidence-head"><span>{escape(label)}</span>{tag}</div>'
            f'<b>{escape(_compact(title,460 if large else 150))}</b><p>{escape(_compact(desc,360 if large else 215))}</p></div>')


def evidence_html(timeline, index, ready=False, case=None):
    """Progressive recorded WHAT/WHERE evidence; no confirmed scope until SP01 handover."""
    sid=timeline[index]['scenario_id'];beat=timeline[index]['beat']
    shown=[] if ready else [x['beat'] for x in timeline[:index+1] if x['scenario_id']==sid]
    revealed={}
    for b in shown:
        tool=tool_for(b)
        if b['agent']=='SP01' and tool in ('ml_specialist_summary','ml_scope_probabilities',
                                            'telemetry_network_overview','telemetry_events'):
            revealed[tool]=b
    confirmed=next((b for b in shown if b['agent']=='SP01' and b['kind']=='handover'),None)
    current=tool_for(beat) if not ready else None
    what=revealed.get('ml_specialist_summary');where=revealed.get('ml_scope_probabilities')
    if what:
        value=re.search(r'Model output:\s*([A-Z0-9_]+)',what.get('output',''))
        family=value.group(1).replace('_',' ').title() if value else _compact(what.get('output'),80)
        title=family
        probability=re.search(r'\(([0-9.]+%)\)',what.get('output',''))
        description='Recorded model prediction'+(f' · score {probability.group(1)}' if probability else '')+' · uncalibrated'+(f' · elapsed {_clock(case,what)}' if _clock(case,what) else '')
    else:
        title='Fault-family prediction'; description='Waiting for this recorded tool result'
    cards=[_card('WHAT',title,description,'RECORDED' if what else 'AWAITING',current=='ml_specialist_summary')]
    if confirmed and case:
        title, detail=_scope(case)
        t=_clock(case,confirmed)
        description='SP01 confirmed scope'+(f' · elapsed {t}' if t else '')+' · '+detail
        now=beat is confirmed
        status='RECORDED'
    elif where:
        hit=re.search(r'Top ML scope:\s*([A-Z0-9_]+)',where.get('output',''))
        title=hit.group(1).replace('_',' ').title() if hit else _compact(where.get('output'),80)
        probability=re.search(r'\(([0-9.]+%)\)',where.get('output',''))
        description='Predicted scope class'+(f' · score {probability.group(1)}' if probability else '')+' · uncalibrated'+(f' · elapsed {_clock(case,where)}' if _clock(case,where) else '')+' · Exact entities pending SP01 confirmation'
        now=current=='ml_scope_probabilities';status='RECORDED'
    else:
        title='Affected scope and network entities';description='Waiting for this recorded tool result';now=False;status='AWAITING'
    cards.append(_card('WHERE',title,description,status,now))
    for tool,label,title in [('telemetry_network_overview','NETWORK','Performance counters'),('telemetry_events','EVENTS','Event telemetry')]:
        b=revealed.get(tool)
        desc=(_compact(b.get('output'),140)+(f' · {_clock(case,b)} recorded elapsed' if _clock(case,b) else '')) if b else 'Waiting for this recorded tool result'
        cards.append(_card(label,title,desc,'RECORDED' if b else 'AWAITING',current==tool))
    return ('<section class="gs-evidence-wrap" aria-label="SP01 evidence arrives in recorded order">'
            '<div class="gs-board-head"><b>NETWORK ASSESSMENT · SP01</b><span>Recorded predictions are not confirmed network truth</span></div>'
            '<div class="gs-evidence-grid">'+''.join(cards)+'</div></section>')


def specialist_html(item, timeline, index):
    """Four reusable specialist cards; completed results remain available by recorded agent."""
    case=item['case'];sid=item['scenario_id'];b=item['beat']
    feedback=[x['beat'] for x in timeline[:index+1] if x['scenario_id']==sid and
              x['beat']['agent'].startswith('SP') and x['beat']['agent']!='SP01' and
              x['beat']['kind']=='feedback']
    latest=feedback[-1] if feedback else None
    current_agent=b['agent'] if b['agent'].startswith('SP') and b['agent']!='SP01' else (latest['agent'] if latest else None)
    detail=case.get('stage_data',{}).get((latest or {}).get('agent','').lower()+'_output',{}) if latest else {}
    assessment=detail.get('assessment_outcome') or {}
    latest_time=_clock(case,latest) if latest else None
    cards=[
        _card('AGENT',current_agent or 'Awaiting specialist',
              'Current investigation domain'+(f' · recorded completion {latest_time}' if latest_time else ''),
              'RECORDED' if current_agent else 'AWAITING',bool(current_agent)),
        _card('EVIDENCE',_compact(assessment.get('brief_update') or (latest or {}).get('output') or 'Awaiting specialist evidence',145),
              'Saved specialist observation'+(f' · elapsed {latest_time}' if latest_time else ''),
              'RECORDED' if latest else 'AWAITING',bool(latest and b is latest)),
        _card('FINDING',assessment.get('conclusion') or 'Awaiting specialist finding',
              _compact(detail.get('current_assessment') or 'Original engineering details available below',160),
              'RECORDED' if latest else 'AWAITING',bool(latest and b is latest)),
        _card('HANDOVER',('Available to Supervisor' if latest else 'Awaiting engineering handover'),
              ('Completed specialist findings contribute to final evidence synthesis.' if latest else
               'The next recorded specialist result has not arrived yet.'),
              'RECORDED' if latest else 'AWAITING',False),
    ]
    history=''.join(f'<span class="gs-history-chip">{escape(v["agent"])} · {escape(_clock(case,v) or "time unavailable")}</span>' for v in feedback)
    return ('<section class="gs-evidence-wrap" aria-label="Recorded specialist results">'
            '<div class="gs-board-head"><b>SPECIALIST INVESTIGATION</b><span>Results appear on recorded feedback; prior agents remain visible</span></div>'
            '<div class="gs-evidence-grid">'+''.join(cards)+'</div>'
            +('<div class="gs-history"><b>COMPLETED AGENTS</b>'+history+'</div>' if history else '')+'</section>')


def supervisor_html(item, timeline, index):
    """Show the final RCA only after recorded Supervisor decision, then hold it at report."""
    case=item['case'];b=item['beat'];sid=item['scenario_id']
    past=[x['beat'] for x in timeline[:index+1] if x['scenario_id']==sid]
    issued=any(x['agent']=='SUPERVISOR' and x['kind']=='decision' for x in past)
    final=b['agent']=='FINAL'
    published=issued or final
    output=case.get('stage_data',{}).get('supervisor_output') or {}
    assessment=output.get('root_cause_assessment') or {}
    incident=case.get('derived_display',{}).get('incident_present',False)
    duration=_node_clock(case,'SUPERVISOR')
    rc=assessment.get('root_cause') or ('No material network incident supported by recorded evidence.' if not incident else 'RCA conclusion not recorded')
    support=output.get('supporting_evidence') or []
    scope_title,scope_detail=_scope(case)
    confidence=assessment.get('confidence') or 'Not recorded'
    gaps=output.get('residual_uncertainty') or []
    prefix=(f'Supervisor complete at {duration} recorded elapsed' if duration else 'Supervisor completion marker not separately available')
    if not published:
        # RAG messages can be shown without leaking the final diagnosis prematurely.
        waiting='Awaiting final Supervisor decision'
        rag=next((x for x in reversed(past) if x['agent']=='SUPERVISOR' and x['kind']=='rag'),None)
        cards=[_card('ROOT CAUSE',waiting,'Not yet issued in this recorded scene','AWAITING'),
               _card('KNOWLEDGE', 'Telecom knowledge reviewed' if rag else 'Awaiting evidence synthesis',
                     _compact(rag.get('output'),170) if rag else 'Specialist findings being correlated',
                     'RECORDED' if rag else 'AWAITING',bool(rag and rag is b)),
               _card('IMPACT & SCOPE','Pending final Supervisor review','No final RCA result yet','AWAITING'),
               _card('CONFIDENCE & GAPS','Pending final assessment','Uncertainty assessed at conclusion','AWAITING')]
    else:
        cards=[_card('ROOT CAUSE' if incident else 'HEALTH OUTCOME',rc,prefix,'RECORDED',b['kind']=='decision' or final,large=True),
               _card('DECISIVE EVIDENCE',_compact(support[0],160) if support else ('No material degradation identified' if not incident else 'No evidence summary recorded'),
                     _compact(support[1],150) if len(support)>1 else 'Full source observations available in RCA detail',
                     'RECORDED'),
               _card('IMPACT & SCOPE',scope_title,scope_detail,'RECORDED'),
               _card('CONFIDENCE & GAPS',f'Recorded judgement: {confidence}',
                     _compact(gaps[0],175) if gaps else 'No residual uncertainty recorded; judgement is not calibrated',
                     'RECORDED')]
    return ('<section class="gs-evidence-wrap gs-rca-board" aria-label="Supervisor evidence and recorded RCA conclusion">'
            '<div class="gs-board-head"><b>SUPERVISOR · '+('FINAL RCA' if incident else 'HEALTH CONCLUSION')+'</b>'
            '<span>'+('Recorded decision available · held at conclusion' if published else 'Awaiting recorded RCA decision')+'</span></div>'
            '<div class="gs-evidence-grid">'+''.join(cards)+'</div></section>')


def board_html(item,timeline,index,ready=False):
    if ready or item['beat']['agent']=='SP01':
        return evidence_html(timeline,index,ready,case=item['case'])
    b=item['beat'];sid=item['scenario_id']
    if b['agent']=='FINAL' or b['agent']=='SUPERVISOR' or b['agent'].endswith('_JOIN'):
        return supervisor_html(item,timeline,index)
    if b['agent'].startswith('SP'):
        return specialist_html(item,timeline,index)
    return evidence_html(timeline,index,ready,case=item['case'])


def focus_html(item, position, count, ready=False):
    """One current finding; at final report, show the full RCA, not a disappearing snippet."""
    b=item['beat'];num,title,why=phase_for(item)
    if ready:
        return ('<section class="gs-focus" aria-label="Ready to watch">'
                '<span class="gs-scene">READY · SCENE 0</span><h3>Start with the network evidence</h3>'
                '<p>The recorded run is paused before its first investigation scene. Select <b>Play</b> or <b>Next</b> to reveal what the localisation agent reviews.</p>'
                '<div class="gs-why">Watch the same four result cards change as the investigation moves from SP01 through specialists to RCA.</div></section>')
    output=' '.join(str(b.get('output') or 'No separate recorded result saved for this scene.').split())
    if b['agent']=='FINAL':
        assessment=item['case'].get('stage_data',{}).get('supervisor_output',{}).get('root_cause_assessment') or {}
        root=assessment.get('root_cause')
        if root:output=root
    if len(output)>550:output=_compact(output,550)
    completed=b['agent']=='FINAL'
    return (f'<section class="gs-focus{" gs-focus-final" if completed else ""}" aria-label="Current recorded investigation scene">'
            f'<div class="gs-focus-top"><span class="gs-scene">CHAPTER {num} / {3 if not item["case"]["derived_display"]["incident_present"] else 6} · SCENE {position}/{count}</span><span class="gs-scene-agent">{escape(b["agent"])} · {escape(b["kind"].upper())}</span></div>'
            f'<h3>{escape("Final recorded RCA — investigation complete" if completed and item["case"]["derived_display"]["incident_present"] else b["title"])}</h3>'
            f'<div class="gs-why"><b>WHY THIS STEP?</b> {escape(why)}</div>'
            f'<div class="gs-result"><b>{"RECORDED FINAL CONCLUSION" if completed else "RECORDED OBSERVATION"}</b><p>{escape(output)}</p></div>'
            '<p class="gs-source-note">Result from the original saved experiment; full messages, evidence and report available below.</p>'
            '</section>')


def boundary_html(healthy_id, incident_id):
    return (f'<section class="gs-boundary"><b>FIRST RECORDING COMPLETE · {escape(healthy_id)}</b>'
            '<h3>This healthy network did not become the next incident.</h3>'
            f'<p>The next demonstration opens an <b>independent recorded synthetic-network case ({escape(incident_id)})</b>. '
            'It is not a fault that developed during the healthy recording.</p>'
            '<p>Playback stops here until you explicitly continue.</p></section>')
