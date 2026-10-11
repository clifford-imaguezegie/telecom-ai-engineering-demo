"""Pure, deterministic presentation adapter for saved LangSmith investigation records.

No telemetry queries, LLM calls, invented measurements, source-passage distribution,
or wall-clock simulation. Playback is a guided presentation of saved evidence, NOT a
re-execution or a claim that parallel agents ran sequentially.
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
            target=('parallel specialist investigation (KPI, cell/peer, radio, processing, transport, configuration)' if branch=='LOCAL_SPECIALISTS' else 'CU-Domain & Boundary Analysis Agent' if branch=='CU_SPECIALIST' else 'direct RCA Supervisor review')
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
            add(join,'join','Specialist handover reaches correlation join',
                'Recorded SP01 and specialist findings, where applicable',
                'Collect the branch results for Supervisor synthesis.',
                f"Recorded graph route uses {join}. Local specialist reports are presented one by one, although their analytical branch was parallel.",i,'Recorded LangGraph route')
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


def _node_positions(route_family):
    if route_family=='LOCAL_SPECIALISTS':
        p={'SP01':(115,195),'LOCAL_JOIN':(830,195),'SUPERVISOR':(1052,195),'FINAL':(1238,195)}
        for i,n in enumerate(['SP02','SP03','SP04','SP05','SP06','SP07']):p[n]=(510,55+56*i)
    elif route_family=='CU_SPECIALIST':
        p={'SP01':(155,185),'SP08':(426,185),'CU_JOIN':(701,185),'SUPERVISOR':(974,185),'FINAL':(1238,185)}
    else:
        p={'SP01':(170,185),'DIRECT_JOIN':(512,185),'SUPERVISOR':(853,185),'FINAL':(1190,185)}
    return p


def workflow_svg(route_family, story, active_index):
    """Self-contained source-independent SVG; only stage-backed active statuses."""
    p=_node_positions(route_family)
    current=story[active_index]['agent']
    completed={b['agent'] for b in story[:active_index]}
    edges=[]
    if route_family=='LOCAL_SPECIALISTS':
        for n in ['SP02','SP03','SP04','SP05','SP06','SP07']:
            edges.extend([('SP01',n),(n,'LOCAL_JOIN')])
        edges += [('LOCAL_JOIN','SUPERVISOR'),('SUPERVISOR','FINAL')]
    elif route_family=='CU_SPECIALIST':
        edges=[('SP01','SP08'),('SP08','CU_JOIN'),('CU_JOIN','SUPERVISOR'),('SUPERVISOR','FINAL')]
    else:
        edges=[('SP01','DIRECT_JOIN'),('DIRECT_JOIN','SUPERVISOR'),('SUPERVISOR','FINAL')]
    parts=['<svg role="img" aria-label="Recorded agent routing and active presentation stage" viewBox="0 0 1345 395" preserveAspectRatio="xMidYMid meet" style="width:100%;height:auto;display:block">',
           '<defs><marker id="flowArrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#62849c" stroke-width="1.5"/></marker></defs>']
    for a,b in edges:
        xa,ya=p[a];xb,yb=p[b]
        left=xa+(69 if a.startswith('SP') or a=='SUPERVISOR' else 64)
        right=xb-(69 if b.startswith('SP') or b=='SUPERVISOR' else 64)
        is_done=a in completed and b in completed|{current}
        col='#22bc93' if is_done else '#62849c'
        parts.append(f'<path d="M {left} {ya} C {(left+right)/2:.0f} {ya}, {(left+right)/2:.0f} {yb}, {right} {yb}" stroke="{col}" stroke-width="{2.8 if is_done else 1.7}" fill="none" marker-end="url(#flowArrow)"/>')
    for agent,(x,y) in p.items():
        if agent==current:stroke='#46e6b5';fill='#154f62';status='IN FOCUS'
        elif agent in completed:stroke='#22b995';fill='#1c4250';status='REVIEWED'
        else:stroke='#53768b';fill='#172d42';status='QUEUED'
        r=69 if agent.startswith('SP') or agent=='SUPERVISOR' else 63
        height=43
        if agent==current:
            parts.append(f'<rect x="{x-r-5}" y="{y-27}" width="{2*r+10}" height="56" rx="15" fill="none" stroke="#46e6b5" stroke-width="2" class="activepulse"/>')
        parts.append(f'<rect x="{x-r}" y="{y-22}" width="{2*r}" height="{height}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        # Public-friendly role names only; internal SP IDs remain in technical provenance.
        name={'SP01':'Network Health','SP02':'Accessibility KPI','SP03':'Cell & Peer','SP04':'Radio Analysis',
              'SP05':'Processing','SP06':'Transport','SP07':'Configuration','SP08':'CU & Boundary',
              'SUPERVISOR':'RCA Supervisor','LOCAL_JOIN':'Evidence Join','CU_JOIN':'CU Join',
              'DIRECT_JOIN':'Direct Review','FINAL':'Final RCA'}.get(agent,agent)
        sub={'SP01':'ML + telemetry','SUPERVISOR':'Evidence synthesis','FINAL':'Recorded report',
             'LOCAL_JOIN':'Parallel branches','CU_JOIN':'CU branch','DIRECT_JOIN':'Healthy control',
             'SP02':'KPI evidence','SP03':'Cell comparisons','SP04':'Radio evidence',
             'SP05':'Processing evidence','SP06':'Transport evidence','SP07':'Config evidence',
             'SP08':'CU-domain evidence'}.get(agent,'')
        parts.append(f'<text x="{x}" y="{y-4}" font-size="12.5" text-anchor="middle" font-weight="700" fill="#eaf6ff">{escape(name)}</text>')
        parts.append(f'<text x="{x}" y="{y+11}" font-size="10" text-anchor="middle" fill="#a8cddd">{escape(sub)}</text>')
        if agent==current:
            parts.append(f'<text x="{x}" y="{y+46}" font-size="10" text-anchor="middle" fill="#51e8c2" font-weight="bold">{status}</text>')
    parts.append('</svg>')
    markup=''.join(parts)
    style='''<style>body{margin:0;background:#0d1d30;font-family:system-ui,Arial,sans-serif} .frame{background:linear-gradient(130deg,#0c2135,#102c40);border:1px solid #284b62;border-radius:15px;padding:8px 8px 0}.activepulse{animation:pulse 1.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}@keyframes pulse{0%,100%{opacity:.34}50%{opacity:1}}.foot{font:12px system-ui;color:#9ab9c6;margin:0 20px 10px}</style>'''
    return '<!DOCTYPE html><html><head><meta charset="utf-8">'+style+'</head><body><div class="frame">'+markup+'<div class="foot">Agent routing from recorded LangGraph · animated highlighting indicates replay focus (not a live execution)</div></div></body></html>'
