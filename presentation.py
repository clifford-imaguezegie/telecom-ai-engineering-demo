"""Read-only public presentation utilities for the LangSmith-derived replay.

All timing claims are computed from the bundled completed executions. The
application never creates agent calls or makes new network observations.
"""
from storyboard import AGENT_ROLES, label_tool

DISPLAY_NAMES = {
    'SP01': 'Network Health & Localisation Agent',
    'SP02': 'Accessibility KPI Analysis Agent',
    'SP03': 'Cell & Peer Comparison Agent',
    'SP04': 'Radio Analysis Agent',
    'SP05': 'Processing Analysis Agent',
    'SP06': 'Transport Analysis Agent',
    'SP07': 'Configuration Analysis Agent',
    'SP08': 'CU-Domain & Boundary Analysis Agent',
    'SUPERVISOR': 'RCA Supervisor & Evidence Synthesis',
    'LOCAL_JOIN': 'Specialist Evidence Consolidation',
    'CU_JOIN': 'CU-Domain Evidence Consolidation',
    'DIRECT_JOIN': 'Direct Supervisor Review',
    'FINAL': 'Root Cause Analysis Report',
}

AGENT_MISSIONS = {
    'SP01': 'Assess network health, invoke two ML predictions and network telemetry, localise and route',
    'SP02': 'Analyse accessibility KPIs and degradation signatures',
    'SP03': 'Compare affected cells and peer-cell behaviour',
    'SP04': 'Investigate radio conditions and resource state',
    'SP05': 'Assess processing pressure and compute-related signals',
    'SP06': 'Investigate transport state and connectivity evidence',
    'SP07': 'Investigate network configuration and change-related evidence',
    'SP08': 'Investigate CU-domain and boundary-layer fault mechanisms',
    'SUPERVISOR': 'Correlate evidence, assess competing hypotheses, and deliver RCA',
}


def agent_label(identifier, include_id=False):
    """Present the role first; retain raw graph ID only when requested."""
    name = DISPLAY_NAMES.get(identifier, AGENT_ROLES.get(identifier, identifier))
    return f'{name} ({identifier})' if include_id and identifier in DISPLAY_NAMES else name


def format_duration(seconds):
    """Human-readable minutes and seconds, not a large unlabelled seconds total."""
    if seconds is None:
        return '—'
    whole = int(round(float(seconds)))
    if whole < 60:
        return f'{whole}s'
    minutes, secs = divmod(whole, 60)
    return f'{minutes}m {secs:02d}s'


def agent_execution_rows(case):
    """Agent wall-clock duration vs LLM-only spans; never sum overlapping agents."""
    nodes = case.get('observed_nodes', [])
    outputs = case.get('evidence_index', [])
    rows = []
    for agent in ['SP01', 'SP02', 'SP03', 'SP04', 'SP05', 'SP06', 'SP07', 'SP08', 'SUPERVISOR']:
        chain = next((n for n in nodes if n.get('name') == agent and n.get('run_type') == 'chain' and n.get('depth') == 1), None)
        if not chain:
            continue
        llm_nodes = [n for n in nodes if n.get('run_type') == 'llm' and str(n.get('name', '')).startswith('LLM | '+agent+' | ')]
        llm_sum = sum(float(n['duration_seconds']) for n in llm_nodes if isinstance(n.get('duration_seconds'), (int, float)))
        tools = sorted({e['tool'] for e in outputs if e.get('stage') == agent})
        rows.append({
            'Agent': agent_label(agent),
            'Purpose': AGENT_MISSIONS.get(agent, ''),
            'Agent runtime': format_duration(chain.get('duration_seconds')),
            'LLM inference (spans)': format_duration(llm_sum) if llm_nodes else '—',
            'LLM calls': len(llm_nodes),
            'Tools used': ', '.join(label_tool(t) for t in tools) if tools else 'None recorded',
            'Recorded tool outputs': sum(e.get('stage') == agent for e in outputs),
            'ID': agent,
        })
    return rows


def benchmark_summary(cases):
    """Return audit-ready timing ranges and pass counts from saved top-level runs."""
    cases = list(cases)
    sp01 = []
    complete = []
    localised = []
    for case in cases:
        root = float(case['trace_duration_seconds'])
        chain = next((n for n in case['observed_nodes'] if n.get('name') == 'SP01' and n.get('run_type') == 'chain' and n.get('depth') == 1), None)
        if chain is not None and isinstance(chain.get('duration_seconds'), (int,float)):
            sp01.append(float(chain['duration_seconds']))
        if case['derived_display']['incident_present']:
            complete.append(root)
            if chain is not None and isinstance(chain.get('duration_seconds'), (int,float)):
                localised.append(float(chain['duration_seconds']))
    return {
        'health_assessment_under_1min': sum(t < 60 for t in sp01),
        'health_assessment_total': len(sp01),
        'localisation_under_2min': sum(t <= 120 for t in localised),
        'localisation_total': len(localised),
        'incident_rca_under_5min': sum(t < 300 for t in complete),
        'incident_total': len(complete),
        'sp01_max_seconds': max(sp01) if sp01 else None,
        'incident_max_seconds': max(complete) if complete else None,
    }


PHASE_AGENTS = ('SP01', 'SP02', 'SP03', 'SP04', 'SP05', 'SP06', 'SP07', 'SP08', 'SUPERVISOR')

def phase_execution_rows(cases):
    """Recorded phase wall times; agent chain spans are not token/price metrics.

    Phases derive from the depth-one chain records for each frozen scenario. The
    specialist phase sums only recorded, sequential specialist spans; the
    healthy route has no specialist phase. Root time includes orchestration.
    """
    rows = []
    for case in cases:
        chains = {n.get('name'): float(n['duration_seconds'])
                  for n in case.get('observed_nodes', [])
                  if n.get('run_type') == 'chain' and n.get('depth') == 1
                  and n.get('name') in PHASE_AGENTS
                  and isinstance(n.get('duration_seconds'), (int, float))}
        incident = bool(case['derived_display']['incident_present'])
        specialists = ['SP02','SP03','SP04','SP05','SP06','SP07'] if case.get('route_family') == 'cell_site' else ['SP08']
        # Derive from actual child chains; do not invent a specialist for healthy.
        active = [x for x in specialists if x in chains] if incident else []
        # Fallback to observed agent IDs if the frozen export uses a different route label.
        if incident and not active:
            active = [x for x in ('SP02','SP03','SP04','SP05','SP06','SP07','SP08') if x in chains]
        rows.append({
            'scenario_id': case['scenario_id'], 'title': case['title'],
            'incident': incident, 'route': case.get('route_family'),
            'sp01_seconds': chains.get('SP01'),
            'specialist_seconds': sum(chains[x] for x in active) if active else None,
            'supervisor_seconds': chains.get('SUPERVISOR'),
            'end_to_end_seconds': float(case['trace_duration_seconds']),
            'specialist_agents': tuple(active),
        })
    return rows


def phase_execution_ranges(cases):
    """Return min/max independently for each phase across the appropriate cases."""
    rows = phase_execution_rows(cases)
    incidents = [r for r in rows if r['incident']]
    def window(items, key):
        nums = [float(r[key]) for r in items if r[key] is not None]
        return {'min': min(nums), 'max': max(nums), 'count': len(nums)} if nums else None
    return {
        'sp01': window(rows, 'sp01_seconds'),
        'specialists': window(incidents, 'specialist_seconds'),
        'supervisor': window(incidents, 'supervisor_seconds'),
        'incident': window(incidents, 'end_to_end_seconds'),
        'healthy': window([r for r in rows if not r['incident']], 'end_to_end_seconds'),
        'rows': rows,
    }
