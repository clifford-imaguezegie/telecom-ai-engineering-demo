"""Recorded, read-only guided operations demo (no network inference or polling).

A healthy control and an incident are *separate* completed LangGraph runs.
The sequence is a presentation cut of trace-backed storyboard beats, never a
continuous historical series, fresh monitor scan, or new autonomous action.
"""
from datetime import datetime
from storyboard import AGENT_ROLES

ESSENTIAL_SP01 = {
    'telemetry_topology', 'ml_model_metadata',
    'ml_specialist_summary', 'ml_scope_probabilities',
    'telemetry_network_overview', 'telemetry_events',
}


def _tool(beat):
    src = beat.get('source', '')
    if beat.get('kind') == 'tool' and ' · ' in src:
        return src.rsplit(' · ', 1)[-1]
    return None


def director_cut(case, beats, healthy=False):
    """Keep every substantive SP01 input and each routed agent's handover/feedback.

    Representative specialist calls are selected for pacing; the full tool list
    remains in the animated replay, and all original outputs in the drill-down.
    """
    selected = []
    seen_agent_tools = set()
    for beat in beats:
        agent, kind = beat['agent'], beat['kind']
        keep = False
        if agent == 'SP01':
            keep = kind in {'scan', 'decision', 'handover'} or (
                kind == 'tool' and _tool(beat) in ESSENTIAL_SP01
            )
        elif agent.startswith('SP'):
            if kind in {'dispatch', 'feedback'}:
                keep = True
            elif kind == 'tool' and agent not in seen_agent_tools:
                keep = True
                seen_agent_tools.add(agent)
        elif agent in {'LOCAL_JOIN', 'CU_JOIN', 'DIRECT_JOIN'}:
            keep = True
        elif agent == 'SUPERVISOR':
            keep = kind in {'review', 'plan', 'rag', 'decision'} or (
                kind == 'tool' and _tool(beat) == 'supervisor_private_knowledge_search'
            )
        elif agent == 'FINAL':
            keep = True
        if keep:
            selected.append(beat)
    assert selected and selected[0]['title'] == 'Network scan initiated'
    assert selected[-1]['agent'] == 'FINAL'
    return selected


def guided_sequence(healthy_case, healthy_beats, incident_case, incident_beats, include_healthy=True):
    """Build an ordered playlist, with a truthful boundary between independent traces."""
    segments = []
    if include_healthy:
        segments.append((healthy_case, healthy_beats, 'HEALTH ASSESSMENT'))
    if incident_case is not None:
        segments.append((incident_case, incident_beats, 'INCIDENT INVESTIGATION'))
    timeline = []
    for case, beats, act in segments:
        for beat in director_cut(case, beats, healthy=(not case['derived_display']['incident_present'])):
            timeline.append({'scenario_id': case['scenario_id'], 'act': act,
                             'beat': beat, 'case_title': case['title']})
    return timeline


def get_run_durations(case):
    """Use *recorded* top-level LangSmith run durations; no guessed stage clocks."""
    nodes = case.get('observed_nodes', [])
    def find(name):
        for n in nodes:
            if n.get('name') == name and n.get('run_type') == 'chain' and n.get('depth') == 1:
                return n.get('duration_seconds')
        return None
    return {'sp01': find('SP01'), 'supervisor': find('SUPERVISOR'),
            'total': case.get('trace_duration_seconds')}


def event_trace_offset(case, beat):
    """Exact elapsed offset only where a saved event timestamp/end marker exists."""
    value = beat.get('timestamp') if beat.get('kind') == 'tool' else None
    if not value and beat.get('kind') == 'handover' and beat.get('agent') == 'SP01':
        value = next((n.get('end_time') for n in case['observed_nodes']
                      if n.get('name') == 'SP01' and n.get('depth') == 1), None)
    if not value and beat.get('kind') == 'feedback' and beat.get('agent','').startswith('SP'):
        value = next((n.get('end_time') for n in case['observed_nodes']
                      if n.get('name') == beat['agent'] and n.get('depth') == 1), None)
    if not value and beat.get('kind') == 'decision' and beat.get('agent') == 'SUPERVISOR':
        value = next((n.get('end_time') for n in case['observed_nodes']
                      if n.get('name') == 'SUPERVISOR' and n.get('depth') == 1), None)
    if not value and beat.get('kind') == 'report' and beat.get('agent') == 'FINAL':
        value = case.get('trace_end_utc')
    if not value:
        return None
    start = case.get('trace_start_utc')
    if not start:
        return None
    try:
        a = datetime.fromisoformat(str(start).replace('Z', '+00:00'))
        b = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        offset = (b-a).total_seconds()
        if 0 <= offset <= case['trace_duration_seconds'] + 0.1:
            return offset
    except (TypeError, ValueError):
        pass
    return None


def format_clock(seconds):
    if seconds is None:
        return '—'
    seconds = int(round(seconds))
    return f'{seconds//60:02}:{seconds%60:02}'


def sp01_tools_unlocked(timeline, index):
    """Only expose SP01 tool results after their beat was actually presented."""
    current = timeline[index]['scenario_id']
    visible = set()
    for item in timeline[:index + 1]:
        beat = item['beat']
        if item['scenario_id'] == current and beat['agent'] == 'SP01':
            tool = _tool(beat)
            if tool: visible.add(tool)
    return visible


def available_agents(case):
    present = {s['agent'] for s in case.get('stages', [])}
    return [a for a in AGENT_ROLES if a in present]


def executive_sequence(timeline):
    """A ~90-second, 15-scene director's cut using only original recorded beats.

    The full engineering sequence remains available without data duplication.
    """
    if not timeline:
        return []
    def choose(items, predicate):
        return next((x for x in items if predicate(x['beat'])),None)
    healthy=[x for x in timeline if x['act']=='HEALTH ASSESSMENT']
    incidents=[x for x in timeline if x['act']=='INCIDENT INVESTIGATION']
    chosen=[]
    if healthy:
        # Executive healthy-control path must reveal the four recorded SP01
        # results before asserting that the network had no material incident.
        for kind,arg in [('scan','SP01'),('tool','ml_specialist_summary'),
                         ('tool','ml_scope_probabilities'),
                         ('tool','telemetry_network_overview'),
                         ('tool','telemetry_events'),
                         ('decision','SP01'),('report','FINAL')]:
            if kind=='tool':
                pick=choose(healthy,lambda b:b['kind']=='tool' and _tool(b)==arg)
            else:
                pick=choose(healthy,lambda b:b['kind']==kind and b['agent']==arg)
            if pick and pick not in chosen:chosen.append(pick)
    if incidents:
        # All SP01 ML + overview/event outputs are preserved in the short story.
        order=[('scan','SP01'),('tool','ml_specialist_summary'),('tool','ml_scope_probabilities'),
               ('tool','telemetry_network_overview'),('tool','telemetry_events'),
               ('decision','SP01'),('handover','SP01')]
        for kind,arg in order:
            if kind=='tool':
                pick=choose(incidents,lambda b:b['kind']=='tool' and _tool(b)==arg)
            else:pick=choose(incidents,lambda b:b['kind']==kind and b['agent']==arg)
            if pick and pick not in chosen:chosen.append(pick)
        specialists=[x for x in incidents if x['beat']['kind']=='feedback' and x['beat']['agent'].startswith('SP') and x['beat']['agent']!='SP01']
        # Keep chronological specialist feedback as recorded, rather than imply concurrency.
        if specialists:
            indexes=([0,2,len(specialists)-1] if len(specialists)>2 else list(range(len(specialists))))
            for i in sorted(set(indexes)):
                if specialists[i] not in chosen:chosen.append(specialists[i])
        for kind,agent in [('rag','SUPERVISOR'),('decision','SUPERVISOR'),('report','FINAL')]:
            pick=choose(incidents,lambda b:b['kind']==kind and b['agent']==agent)
            if pick and pick not in chosen:chosen.append(pick)
    return chosen
