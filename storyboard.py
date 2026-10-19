"""Pure, deterministic presentation adapter for saved LangSmith investigation records.

No telemetry queries, LLM calls, invented measurements, source-passage distribution,
or wall-clock simulation. Playback is a guided presentation of saved evidence, NOT a
re-execution or a claim that sequential agents ran concurrently.
"""
from html import escape

AGENT_ROLES = {
    'SP01': 'Network Health & Localisation',
    'SP02': 'Accessibility KPI Analysis',
    'SP03': 'Cell & Peer Comparison',
    'SP04': 'Radio Analysis',
    'SP05': 'Processing Analysis',
    'SP06': 'Transport Analysis',
    'SP07': 'Configuration Analysis',
    'SP08': 'CU-Domain & Boundary Analysis',
    'SUPERVISOR': 'RCA Supervisor & Evidence Synthesis',
    'LOCAL_JOIN': 'Specialist Findings Join',
    'CU_JOIN': 'CU Findings Join',
    'DIRECT_JOIN': 'Healthy-Case Direct Join',
    'FINAL': 'Final Investigation Report',
}


def label_tool(name):
    """Readable public tool names; source names are retained for exact trace links."""
    labels = {
        'supervisor_private_knowledge_search': 'Curated Telecom Knowledge Base Search',
        'ml_model_metadata': 'ML Model Metadata',
        'ml_specialist_summary': 'ML Fault-Family Prediction',
        'ml_scope_probabilities': 'ML Affected-Scope Prediction',
        'ml_fault_family_probabilities': 'ML Fault-Family Probabilities',
        'ml_feature_drivers': 'ML Feature Drivers',
        'telemetry_topology': 'Network Topology Telemetry',
        'telemetry_network_overview': 'Network Overview Telemetry',
        'telemetry_events': 'Network Event Telemetry',
        'telemetry_kpi_components': 'Accessibility KPI Components',
        'telemetry_kpis': 'Accessibility KPIs',
        'telemetry_peer_cells': 'Peer-Cell Telemetry',
        'telemetry_measurements': 'Cell Measurements',
        'telemetry_radio_state': 'Radio-State Telemetry',
        'telemetry_resource_state': 'Radio-Resource Telemetry',
        'telemetry_processing_state': 'Processing-State Telemetry',
        'telemetry_transport_state': 'Transport-State Telemetry',
        'telemetry_configuration': 'Configuration Telemetry',
        'telemetry_cu_domain_state': 'CU-Domain State Telemetry',
    }
    return labels.get(name, name.replace('_', ' ').title())


def summary_text(v, limit=460):
    if isinstance(v, dict):
        v = v.get('summary') or v.get('brief_update') or v.get('conclusion') or ''
    if isinstance(v, list):
        v = '; '.join(str(x) for x in v[:2])
    if v is None:
        return ''
    s = ' '.join(str(v).split())
    return s[:limit-1].rstrip()+'…' if len(s)>limit else s


def evidence_preview(e, payload):
    """Read only public recorded evidence data; never return knowledge-base excerpts."""
    result = payload.get('result', {}) if isinstance(payload, dict) else {}
    tool = e['tool']
    if tool == 'telemetry_topology':
        return f"Topology returned {len(result.get('entities', []))} recorded managed / operational objects."
    if tool == 'ml_model_metadata':
        return f"ML model: {result.get('model_family', 'not recorded')}; calibration: {result.get('calibration_status', 'not recorded')}."
    if tool == 'ml_specialist_summary':
        f = result.get('top_fault_family') or {}
        s = result.get('top_scope') or {}
        return f"Model output: {f.get('label', '—')} ({float(f.get('probability', 0)):.1%}); suggested scope: {s.get('label', '—')}. These model probabilities are uncalibrated supporting evidence."
    if tool == 'ml_scope_probabilities':
        r = result.get('ranked_scopes') or []
        return 'Top ML scope: '+(f"{r[0].get('label')} ({float(r[0].get('probability',0)):.1%}); uncalibrated supporting evidence." if r else 'no ranked scope recorded.')
    if tool == 'telemetry_network_overview':
        sub = result.get('subnetwork_kpis') or []
        cell = result.get('cell_kpis') or {}
        num = cell.get('source_row_count') if isinstance(cell,dict) else len(cell) if isinstance(cell,list) else None
        return f"Returned {len(sub)} recorded subnetwork KPI observations" + (f" and {num:,} cell KPI records" if isinstance(num,int) else '') + ' at the scenario observation intervals.'
    if tool == 'telemetry_events':
        count = len(result) if isinstance(result,list) else len(result.get('events',[])) if isinstance(result,dict) else 0
        return f"Returned {count} recorded event entries."
    if tool == 'supervisor_private_knowledge_search':
        count = result.get('results_count') if isinstance(result,dict) else None
        return 'Knowledge-base tool completed; retrieved passages are intentionally withheld from the public demo.' + (f' Returned results: {count}.' if count is not None else '')
    if isinstance(result, dict):
        collected=[]
        for value in result.values():
            if isinstance(value,dict) and isinstance(value.get('groups'),list):
                collected.append(value)
        if isinstance(result.get('groups'),list): collected.insert(0,result)
        if collected:
            groups=[g for v in collected for g in v.get('groups',[])]
            metrics=sorted({str((g.get('static') or {}).get('metric_name')) for g in groups if (g.get('static') or {}).get('metric_name')})
            return f"Retrieved {len(groups)} recorded telemetry series." + (f" Metrics include: {', '.join(metrics[:3])}." if metrics else ' See Engineering Evidence for measurements.')
        keys=[k for k in result if k not in {'results','passages','documents','chunks','text','content'}]
        return 'Returned recorded result fields: '+', '.join(keys[:5]) if keys else 'Recorded tool execution completed; see evidence explorer.'
    return 'Recorded tool response preserved in the evidence index.'


def find_tool_start(c, agent, tool):
    for node in c['observed_nodes']:
        if node.get('run_type') != 'tool':
            continue
        name = str(node.get('name',''))
        if name == f'TOOL | {agent} | {tool}' or (agent == 'SP01' and name == f'TOOL | {tool}') or (agent == 'SUPERVISOR' and name == f'TOOL | {tool}'):
            return node.get('start_time')
    return None


def build_story(c, evidence_loader):
    """Create evidence-backed visual beats, each associated with an original stage."""
    beats=[]
    entries=c.get('evidence_index') or []
    su=c['stage_data']['supervisor_output']
    pos=0

    def add(agent, kind, title, input_text, action, output, stage_index, source, timestamp=None, evidence_id=None):
        beats.append({'sequence':len(beats)+1,'agent':agent,'kind':kind,'title':title,
            'input':summary_text(input_text,2000 if kind=='rag' else 360),'action':summary_text(action,1300 if kind=='rag' else 500),
            'output':summary_text(output,2000 if kind=='rag' else 720),'stage_index':stage_index,
            'source':source,'timestamp':timestamp,'evidence_id':evidence_id})

    def tools_for(agent, stage_index, include_pre_run=False):
        pre={'telemetry_topology','ml_model_metadata'}
        selected=[e for e in entries if e.get('stage')==agent and ((e['tool'] in pre)==include_pre_run if agent=='SP01' else True)]
        for e in selected:
            p=evidence_loader(e['evidence_id'])
            add(agent,'tool',f'{AGENT_ROLES[agent]} calls {label_tool(e["tool"])}',
                e.get('reason') or 'Recorded evidence request',
                'Calling recorded tool: '+label_tool(e['tool']),
                evidence_preview(e,p),stage_index,
                f"LangSmith recorded tool output · {e['tool']}",
                find_tool_start(c,agent,e['tool']),e['evidence_id'])

    for i,s in enumerate(c['stages']):
        key=s['key'];d=c['stage_data'][key];agent=s['agent']
        if key=='sp01_localization_1':
            window=c.get('scenario_window') or {}
            add('SP01','scan','Network scan initiated',
                f"Investigation: {window.get('task','5G RAN accessibility')} | Observation window: {window.get('window_start_utc','—')} to {window.get('window_end_utc','—')}",
                'Network Health & Localisation Agent reviews topology and scope before interpreting KPI evidence.',
                summary_text(d.get('rationale') or d.get('observations') or 'No affected scope established yet.'),i,'SP01 localization 1 (recorded)')
            tools_for('SP01',i,include_pre_run=True)
        elif key=='sp01_evidence_cycle_1':
            add('SP01','scan','Network Health Agent scans recorded measurements',
                '15-minute PM KPIs, event observations and supporting ML outputs',
                'Gather the recorded deterministic network evidence and supporting probabilistic features.',
                f"The selected scenario has {c.get('data_inventory',{}).get('telemetry_rows',0):,} recorded telemetry rows in its frozen source inventory.",i,'SP01 evidence cycle 1 (recorded)')
            tools_for('SP01',i)
        elif key=='sp01_localization_2':
            material=bool(d.get('material_degradation_identified'))
            scope=d.get('candidate_scope') or {}
            observations=d.get('observations') or []
            add('SP01','decision','Issue identified and localized' if material else 'No material issue found',
                'Network Health & Localisation Agent has assessed the ML predictions, network overview and event evidence',
                f"Localisation assessment — material degradation: {'YES' if material else 'NO'}; candidate scope: {scope.get('supported_scope_class') or 'not identified'}.",
                summary_text(observations or d.get('rationale') or 'No sustained material degradation established.',700),i,'SP01 localization 2 (recorded)')
        elif key=='sp01_output':
            outcome=d.get('assessment_outcome') or {}
            scope=d.get('scope') or {}
            branch=c['route_family']
            target=('sequential specialist investigation (KPI, cell/peer, radio, processing, transport, configuration)' if branch=='LOCAL_SPECIALISTS' else 'CU-Domain & Boundary Analysis Agent' if branch=='CU_SPECIALIST' else 'direct RCA Supervisor review')
            add('SP01','handover','Localisation Agent dispatches investigation',
                f"Localisation assessment: {outcome.get('conclusion','—')} | Scope class: {scope.get('supported_scope_class','—')}",
                f"Recorded routing decision: {target}.",
                summary_text((d.get('assessment_feedback') or {}).get('supporting_observations') or d.get('observations'),700),i,'SP01 final output (recorded)')
        elif s['kind']=='specialist':
            role=AGENT_ROLES[agent]
            assess=d.get('assessment_feedback') or {}
            outcome=d.get('assessment_outcome') or {}
            focus=d.get('investigated_scope') or {}
            add(agent,'dispatch',f'Investigation handed to {role} Agent',
                f"Handover from SP01: {summary_text(focus,200) if not isinstance(focus,dict) else str(focus.get('supported_scope_class') or focus.get('scope_class') or 'Recorded scoped investigation')}",
                f'{role} Agent begins its recorded evidence review.',
                summary_text(outcome.get('brief_update') or 'Reviewing the relevant tool evidence.',700),i,f'{agent} specialist output (recorded)')
            tools_for(agent,i)
            add(agent,'feedback',f'{role} Agent reports analytical findings',
                'Recorded telemetry and investigation scope reviewed by this specialist',
                f"Specialist assessment: {outcome.get('conclusion','—')} | Status: {d.get('status','—')}",
                summary_text(assess.get('summary') or outcome.get('brief_update') or assess.get('supporting_observations') or d.get('positive_metrics'),700),i,f'{agent} assessment_feedback / assessment_outcome (recorded)')
        elif key=='supervisor_observe_1':
            join={'LOCAL_SPECIALISTS':'LOCAL_JOIN','CU_SPECIALIST':'CU_JOIN','DIRECT_SUPERVISOR':'DIRECT_JOIN'}.get(c['route_family'],'DIRECT_JOIN')
            join_note={
                'LOCAL_JOIN':'SP02–SP07 specialist chains ran sequentially and were consolidated for Supervisor review.',
                'CU_JOIN':'SP08 CU-domain findings were consolidated for Supervisor review; the cell/site specialist path did not execute.',
                'DIRECT_JOIN':'SP01 network-health assessment passed directly to Supervisor completion; no domain specialists executed.',
            }[join]
            add(join,'join','Recorded branch reaches findings consolidation',
                'Recorded SP01 and applicable specialist findings',
                'Collect the recorded branch results for Supervisor review.',
                f'Recorded graph route uses {join}. {join_note}',i,'Recorded LangGraph route')
            add('SUPERVISOR','review','Supervisor reviews incident and hypotheses',
                'SP01 findings, domain-specialist reports and contradictions',
                'Review affected scope, competing fault hypotheses, and gaps in the existing evidence.',
                summary_text(d.get('supported_observations') or d.get('route_interpretation') or d.get('materiality_assessment'),700),i,'Supervisor orientation (recorded)')
        elif key=='supervisor_evidence_plan':
            requests=d.get('tool_requests') or []
            add('SUPERVISOR','plan','Supervisor selects additional investigations',
                'Outstanding fault-family questions and specialist findings',
                f"Supervisor plan status: {d.get('status','—')}; {len(requests)} recorded tool request(s).",
                summary_text(d.get('selection_rationale') or 'No further tools needed for the healthy control.',700),i,'Supervisor evidence plan (recorded)')
            tools_for('SUPERVISOR',i)
        elif key=='supervisor_evidence_analysis':
            add('SUPERVISOR','review','Supervisor correlates engineering evidence',
                'Deterministic measurements, specialist assessments, model probabilities and any curated telecom knowledge lookup',
                'Reconcile supporting and competing explanations in the saved Supervisor reasoning.',
                summary_text(d.get('analysis_summary') or d.get('supported_hypotheses') or d.get('deterministic_evidence'),700),i,'Supervisor evidence analysis (recorded)')
            kb=su.get('knowledge_base_contribution') or {}
            if kb.get('used'):
                q=(kb.get('queries') or [''])[0]
                statement=(kb.get('mechanism_summary') or [''])[0]
                observations=(kb.get('incident_observations_confirming_mechanism') or [])
                add('SUPERVISOR','rag','Curated knowledge informs fault-mechanism assessment',
                    q,'Compare domain-mechanism expectations against this incident’s recorded observations. Knowledge is SUPPORTING, not network truth.',
                    statement,i,'Supervisor final knowledge_base_contribution: query and mechanism (recorded)')
                supported='; '.join(kb.get('supported_hypotheses') or [])
                competing='; '.join(kb.get('competing_hypotheses_discussed') or [])
                predicted='; '.join(kb.get('discriminating_observations_expected') or [])
                confirming='; '.join(observations)
                missing='; '.join(kb.get('incident_observations_missing') or [])
                limitations='; '.join(kb.get('limitations') or [])
                add('SUPERVISOR','rag','Knowledge-grounded hypothesis discrimination',
                    ('Supported hypothesis: '+supported+' | Competing explanation: '+competing),
                    ('Expected distinguishing observations: '+predicted),
                    ('Incident evidence cited: '+confirming+' | Missing: '+missing+' | Limitation: '+limitations),i,
                    'Supervisor final knowledge_base_contribution: discrimination and limitations (recorded)')
        elif key=='supervisor_output':
            diagnose=su.get('diagnosis') or 'No material incident established in this recorded investigation.'
            root=su.get('root_cause_assessment') or {}
            add('SUPERVISOR','decision','Supervisor issues final root-cause assessment' if su.get('incident_present') else 'Supervisor confirms healthy network',
                'Correlated evidence, hypotheses, discriminating observations and uncertainty',
                f"Recorded decision: incident {'present' if su.get('incident_present') else 'not present'}. Fault family: {su.get('root_cause_family') or 'not applicable'}; scope: {su.get('scope_class') or 'no incident'}.",
                summary_text(diagnose,710),i,'Supervisor final output (recorded)')
            add('FINAL','report','Investigation report available',
                f"Scenario {c['scenario_id']} | Recorded Supervisor final decision",
                'Present the recorded report with links to engineering evidence, RAG contribution and recorded trace.',
                summary_text(root.get('root_cause') or diagnose,700),i,'Recorded Supervisor final output (not newly generated)')
    return beats


def _recorded_route(story):
    """Actual saved stage order, including recorded joins; never infer parallelism."""
    route = []
    for event in story:
        agent = event['agent']
        if agent not in route:
            route.append(agent)
    return route


def workflow_svg(route_family, story, active_index, mode='focus'):
    """Responsive HTML workflow with source-backed focus and optional full-route view.

    Historical name retained for compatibility with previous replay modules. It
    returns self-contained HTML containing SVG arrow glyphs, NOT a huge SVG
    canvas compressed to half a laptop screen. Does not change any trace data.
    """
    if mode not in {'focus', 'overview'}:
        raise ValueError('mode must be focus or overview')
    if not story or not 0 <= active_index < len(story):
        raise ValueError('A valid recorded presentation beat is required')
    route = _recorded_route(story)
    current = story[active_index]['agent']
    selected = route.index(current)
    visited = {event['agent'] for event in story[:active_index]}
    role_detail = {
        'SP01':'ML predictions and network telemetry',
        'SP02':'Accessibility KPI evidence',
        'SP03':'Affected cells and peer comparisons',
        'SP04':'Radio signal and resource evidence',
        'SP05':'Processing and compute evidence',
        'SP06':'Transport diagnostic evidence',
        'SP07':'Configuration diagnostic evidence',
        'SP08':'CU-domain and boundary evidence',
        'LOCAL_JOIN':'Specialist evidence consolidated',
        'CU_JOIN':'CU evidence consolidated',
        'DIRECT_JOIN':'Healthy network direct review',
        'SUPERVISOR':'Correlation and root cause reasoning',
        'FINAL':'Recorded investigation conclusion',
    }
    def arrow():
        return ('<svg class="arrow" viewBox="0 0 32 24" aria-hidden="true">'
                '<path d="M2 12h25m-9-8 9 8-9 8" fill="none" stroke="#8fbbce" '
                'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    public_roles={'DIRECT_JOIN':'Direct Supervisor Review',
                  'LOCAL_JOIN':'Specialist Evidence Consolidation',
                  'CU_JOIN':'CU Evidence Consolidation'}
    # Compact names are visual-only for narrow mobile cards. The complete
    # recorded role remains in the desktop label and accessible aria-label.
    compact_roles={'SP01':'Network Health', 'SP02':'KPI Analysis',
                   'SP03':'Cell & Peer', 'SP04':'Radio Analysis',
                   'SP05':'Processing', 'SP06':'Transport',
                   'SP07':'Configuration', 'SP08':'CU Analysis',
                   'SUPERVISOR':'RCA Supervisor', 'LOCAL_JOIN':'Evidence Join',
                   'CU_JOIN':'CU Evidence Join', 'DIRECT_JOIN':'Direct Review',
                   'FINAL':'Final RCA Report'}
    def public_role(agent):
        return public_roles.get(agent,AGENT_ROLES[agent])
    def tile(agent, kind):
        if agent is None:
            label='Investigation start' if kind=='previous' else 'Investigation complete'
            detail='No preceding agent' if kind=='previous' else 'No further agent'
            css='endpoint'
        else:
            label=public_role(agent)
            detail=role_detail.get(agent, '')
            css='active' if kind=='current' else ('done' if agent in visited else 'queued')
        status={'previous':'PREVIOUS','current':'IN FOCUS','next':'NEXT'}[kind]
        return (f'<div class="agent {css}" role="group" aria-label="{escape(status+": "+label)}">'
                f'<div class="step-label">{status}</div>'
                f'<div class="agent-name"><span class="role-full">{escape(label)}</span>'
                f'<span class="role-compact">{escape(compact_roles.get(agent,label))}</span></div>'
                f'<div class="agent-detail">{escape(detail)}</div>'
                '</div>')
    route_kind = ('Sequential specialist investigation' if route_family=='LOCAL_SPECIALISTS'
                  else 'CU-domain investigation' if route_family=='CU_SPECIALIST'
                  else 'Healthy network direct review')
    common="""<style>
      *{box-sizing:border-box} html,body{margin:0;padding:0;background:transparent;color:#f0fbff;
        font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif}
      .frame{border:1px solid #416378;border-radius:14px;background:linear-gradient(122deg,#0c2135,#133149);
        padding:13px 14px;min-height:100%}
      .top{display:flex;justify-content:space-between;gap:10px;align-items:baseline;margin-bottom:12px}
      .overline{color:#95c7d6;font-weight:800;letter-spacing:.08em;font-size:12px}
      .step-count{color:#cae7ef;font-weight:650;font-size:12px;white-space:nowrap}
      .focus-flow{display:grid;grid-template-columns:minmax(0,1fr) 24px minmax(0,1.32fr) 24px minmax(0,1fr);
        gap:7px;align-items:stretch;width:100%}
      .arrow{height:25px;width:24px;align-self:center}
      .agent{min-width:0;min-height:140px;border-radius:10px;border:1px solid #5c7c90;
        background:#19354a;padding:13px 11px;display:flex;flex-direction:column;justify-content:center;gap:6px}
      .agent.active{background:#175264;border:2px solid #61e9c9;box-shadow:0 0 0 2px rgba(97,233,201,.13);
        padding:12px 10px}
      .agent.done{border-color:#3b9f91;background:#1b444c}
      .agent.endpoint{opacity:.7;border-style:dashed}
      .step-label{color:#a4d5e2;font-size:11px;letter-spacing:.075em;font-weight:800}
      .active .step-label{color:#91ffdf}
      .agent-name{color:#f6ffff;font-size:14px;line-height:1.24;font-weight:760;overflow-wrap:anywhere}
      .role-compact{display:none}
      .active .agent-name{font-size:16px;line-height:1.2}
      .agent-detail{color:#b4d2df;font-size:11px;line-height:1.3;overflow-wrap:anywhere}
      .bottom{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:5px;
        margin-top:10px;color:#b6d5e2;font-size:11px;line-height:1.3}
      .route-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:8px}
      .route-chip{border:1px solid #587d8e;border-radius:9px;padding:10px 11px;color:#ddecf5;background:#1a374a;
        font-size:13px;min-height:65px;display:flex;gap:9px;align-items:center}
      .route-chip.active{border:2px solid #61e9c9;background:#175264;font-weight:700}
      .route-chip.done{border-color:#3b9f91}
      .ordinal{font-weight:800;color:#a9d6e4;font-size:12px}
      @media(max-width:460px){.frame{padding:9px}.focus-flow{grid-template-columns:minmax(0,1fr) 17px minmax(0,1.3fr) 17px minmax(0,1fr);gap:4px}
        .arrow{width:17px}.agent{padding:8px 6px}.active .agent-name{font-size:14px}.agent-name{font-size:12px}
        .agent-detail{font-size:10px}.role-full{display:none}.role-compact{display:inline}}
    </style>"""
    if mode=='overview':
        chips=[]
        for i,agent in enumerate(route):
            state='active' if agent==current else 'done' if agent in visited else 'queued'
            chips.append(f'<div class="route-chip {state}"><span class="ordinal">{i+1:02d}</span>'
                         f'<span>{escape(public_role(agent))}</span></div>')
        body=(f'<div class="top"><span class="overline">FULL RECORDED ROUTE</span>'
              f'<span class="step-count">{len(route)} recorded stages</span></div>'
              f'<div class="route-grid">{"".join(chips)}</div>'
              '<div class="bottom">Recorded LangGraph order · sequential specialist execution where applicable · not a live run</div>')
    else:
        prev_agent=route[selected-1] if selected>0 else None
        next_agent=route[selected+1] if selected+1<len(route) else None
        body=(f'<div class="top"><span class="overline">RECORDED AGENT WORKFLOW</span>'
              f'<span class="step-count">Stage {selected+1} of {len(route)}</span></div>'
              f'<div class="focus-flow">{tile(prev_agent,"previous")}{arrow()}'
              f'{tile(current,"current")}{arrow()}{tile(next_agent,"next")}</div>'
              f'<div class="bottom"><span>{escape(route_kind)}</span>'
              '<span>Original recorded LangGraph · not live execution</span></div>')
    return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+common+'</head><body><div class="frame">'+body+'</div></body></html>'

def workflow_overview_html(story, active_index):
    """Full recorded route for Streamlit st.html; auto height, no clipping iframe.

    The HTML/CSS is scoped to the route container, and every label is escaped.
    Both playback modes use the same saved story events and route order.
    """
    if not story or not 0 <= active_index < len(story):
        raise ValueError('A valid recorded presentation beat is required')
    route = _recorded_route(story)
    active = story[active_index]['agent']
    visited = {event['agent'] for event in story[:active_index]}
    labels = {'DIRECT_JOIN': 'Direct Supervisor Review',
              'LOCAL_JOIN': 'Specialist Evidence Consolidation',
              'CU_JOIN': 'CU Evidence Consolidation'}
    items = []
    for i, agent in enumerate(route):
        state = 'active' if agent == active else ('done' if agent in visited else 'queued')
        role = escape(labels.get(agent, AGENT_ROLES[agent]))
        items.append(f'<div class="tread-route-item {state}" role="listitem" '
                     f'aria-label="Stage {i+1}: {role}">'
                     f'<span class="tread-route-order">{i+1:02d}</span><span>{role}</span></div>')
    style = '''<style>
    .tread-route-panel{box-sizing:border-box;border:1px solid #416378;border-radius:14px;
      padding:14px;background:#102b40;color:#e8f5fb;font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif}
    .tread-route-panel *{box-sizing:border-box}
    .tread-route-heading{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;
      gap:9px;margin-bottom:12px;color:#cae7ef;font-size:12px;font-weight:750}
    .tread-route-heading strong{color:#95c7d6;letter-spacing:.08em}
    .tread-route-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,195px),1fr));gap:8px}
    .tread-route-item{display:flex;align-items:center;gap:9px;min-width:0;min-height:68px;
      padding:10px 11px;background:#1a374a;border:1px solid #587d8e;border-radius:9px;
      color:#f0fbff;font-size:13px;line-height:1.35;overflow-wrap:anywhere}
    .tread-route-item.done{border-color:#3b9f91}
    .tread-route-item.active{border:2px solid #61e9c9;background:#175264;font-weight:780}
    .tread-route-order{color:#a9d6e4;font-size:12px;font-weight:800;flex-shrink:0}
    .tread-route-foot{margin-top:12px;color:#b6d5e2;font-size:11px;line-height:1.45}
    </style>'''
    body = (f'<div class="tread-route-panel"><div class="tread-route-heading">'
            f'<strong>FULL RECORDED ROUTE</strong><span>{len(route)} recorded stages</span></div>'
            f'<div class="tread-route-grid" role="list">{"".join(items)}</div>'
            '<div class="tread-route-foot">Recorded LangGraph order · sequential specialist execution '
            'where applicable · not a live run</div></div>')
    return style + body
