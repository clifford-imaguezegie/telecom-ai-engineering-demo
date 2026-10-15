"""Source-grounded presentation of the synthetic 5G site/CU model and observed tools.

Presentation only. No new telemetry retrieval, model calls, topology synthesis or
network communications. Source object identifiers come from recorded SP01 topology.
"""
from collections import defaultdict
from html import escape


AGENT_ROLES = {
    'SP01': ('Health & Localisation', 'Network assessment, fault family and affected scope'),
    'SP02': ('KPI Specialist', 'Accessibility and component performance evidence'),
    'SP03': ('Cell & Peer Specialist', 'Affected and neighbouring cell comparison'),
    'SP04': ('Radio Specialist', 'Radio-state and resource utilisation checks'),
    'SP05': ('Processing Specialist', 'Processing state and resource pressure'),
    'SP06': ('Transport Specialist', 'Transport, connectivity and interface evidence'),
    'SP07': ('Configuration Specialist', 'Recorded configuration and parameter evidence'),
    'SP08': ('CU-Domain Specialist', 'CU-domain state, signalling and boundary checks'),
    'SUPERVISOR': ('RCA Supervisor', 'Cross-specialist synthesis, ML support and curated knowledge'),
}
TOOL_NAMES = {
    'telemetry_topology': 'Network topology',
    'ml_model_metadata': 'ML model metadata',
    'ml_specialist_summary': 'Fault-family prediction',
    'ml_scope_probabilities': 'Affected-scope prediction',
    'telemetry_network_overview': 'PM / network overview',
    'telemetry_events': 'Event telemetry',
    'telemetry_kpis': 'Accessibility KPIs',
    'telemetry_kpi_components': 'KPI components',
    'telemetry_measurements': 'Cell measurements',
    'telemetry_peer_cells': 'Peer-cell observations',
    'telemetry_radio_state': 'Radio state',
    'telemetry_resource_state': 'Radio resources',
    'telemetry_processing_state': 'Processing state',
    'telemetry_transport_state': 'Transport state',
    'telemetry_configuration': 'Configuration state',
    'telemetry_cu_domain_state': 'CU domain and boundaries',
    'ml_fault_family_probabilities': 'Fault-family ML support',
    'ml_feature_drivers': 'ML feature drivers',
    'supervisor_private_knowledge_search': 'Curated telecom knowledge search',
}


def derive_inventory(entities):
    """Use only recorded managed objects; NR_CELL_CU/DU are two views of 30 cells."""
    sites = defaultdict(lambda: {'domain': None, 'du': None, 'f1': None, 'cu_cells': [], 'du_cells': []})
    cu = defaultdict(lambda: {'cp': None, 'up': None, 'n2': None, 'e1': None, 'amf': []})
    for e in entities:
        site = e.get('site_id')
        domain = e.get('cu_domain_id')
        name = str(e.get('entity_id') or '')
        obj = e.get('operational_scope')
        if domain:
            info = cu[domain]
            if obj == 'CU_CP': info['cp'] = name
            elif obj == 'CU_UP': info['up'] = name
            elif obj == 'N2_PATH': info['n2'] = name
            elif obj == 'E1_PATH': info['e1'] = name
            elif obj == 'AMF_PEER': info['amf'].append(name)
        if not site:
            continue
        info = sites[site]
        if domain:
            if info['domain'] not in (None, domain):
                raise ValueError('Conflicting CU domain assignment for ' + site)
            info['domain'] = domain
        if obj == 'DU': info['du'] = name
        elif obj == 'F1_PATH': info['f1'] = name
        elif e.get('entity_type') == 'NR_CELL_CU': info['cu_cells'].append(name)
        elif e.get('entity_type') == 'NR_CELL_DU': info['du_cells'].append(name)
    output = []
    for site, info in sorted(sites.items()):
        # Do not double-count the CU and DU views as distinct physical cells.
        info['cu_cells'].sort()
        info['du_cells'].sort()
        output.append({'site':site,**info})
    return {'sites':output,'domains':{k:cu[k] for k in sorted(cu)},
            'cell_count':sum(len(s['cu_cells']) for s in output),
            'du_cell_views':sum(len(s['du_cells']) for s in output)}


def observed_tools(cases):
    seen = {agent:set() for agent in AGENT_ROLES}
    for case in cases:
        for item in case.get('evidence_index', []):
            agent, tool = item.get('stage'), item.get('tool')
            if agent in seen and tool:
                seen[agent].add(tool)
    return {a:sorted(names) for a,names in seen.items()}


def topology_html(inventory):
    esc=lambda x:escape(str(x or '—'), quote=True)
    count=len(inventory['sites'])
    dom_count=len(inventory['domains'])
    cells=inventory['cell_count']
    pieces=[f'''<section class="net-inventory" aria-label="Recorded synthetic 5G logical network topology">
      <div class="net-summary"><div><b>{count}</b><span>Modeled gNodeB sites</span></div>
      <div><b>{cells}</b><span>NR cells · {cells//count if count else 0} per site</span></div>
      <div><b>{dom_count}</b><span>CU domains</span></div>
      <div><b>{inventory['du_cell_views']}</b><span>DU-side cell views</span></div></div>
      <div class="net-path"><span>AMF peers</span><em>N2</em><span>CU-CP / CU-UP</span><em>E1 within CU</em><span>F1 / DU</span><em>to cells</em><span>NR cells</span></div>''']
    for domain, obj in inventory['domains'].items():
        group=[x for x in inventory['sites'] if x['domain']==domain]
        amf = ', '.join(sorted(obj['amf'])) or 'Not recorded'
        pieces.append(f'''<div class="net-domain"><div class="net-domain-head"><div>
          <strong>{esc(domain)}</strong><span>{len(group)} modeled sites · {sum(len(x['cu_cells']) for x in group)} NR cells</span></div>
          <div class="net-domain-nodes"><span title="Recorded CU control-plane object">{esc(obj['cp'])}</span><span title="Recorded CU user-plane object">{esc(obj['up'])}</span><span title="Recorded E1 path">{esc(obj['e1'])}</span><span title="Recorded N2 path">{esc(obj['n2'])}</span><span title="Recorded AMF peers">{esc(amf)}</span></div></div>
          <div class="net-domain-connector">F1 paths connect modeled DUs to this CU-domain context</div><div class="net-sites">''')
        for record in group:
            chips=''.join(f'<span title="{esc(cell)}">Cell {i}</span>' for i,cell in enumerate(record['cu_cells'],1))
            pieces.append(f'''<div class="net-site"><div class="net-site-top"><b>gNB site</b><strong>{esc(record['site'])}</strong></div>
              <div class="net-site-du">{esc(record['du'])} <span>· {esc(record['f1'])}</span></div>
              <div class="net-cell-chips">{chips}</div><div class="net-site-foot">{len(record['cu_cells'])} logical NR cells</div></div>''')
        pieces.append('</div></div>')
    pieces.append('''<div class="net-footnote">Source: recorded SP01 topology inventory shared by the nine independent synthetic investigation snapshots. Site IDs are recorded; “gNodeB site” is a logical presentation label, not a separately reported gNB identifier. NR_CELL_CU and NR_CELL_DU are two representations of the same 30 logical cells. Connections are conceptual, not a verified physical cabling or transport diagram.</div></section>''')
    return ''.join(pieces)


def tools_html(toolmap):
    esc=lambda x:escape(str(x),quote=True)
    rows=['<section class="net-tools" aria-label="Observed agent and tool capability map">']
    for agent, (name, purpose) in AGENT_ROLES.items():
        present=toolmap[agent]
        tags=''.join(f'<span title="{esc(t)}">{esc(TOOL_NAMES.get(t,t))}</span>' for t in present)
        rows.append(f'''<div class="net-agent"><div class="net-agent-who"><strong>{esc(agent)}</strong><b>{esc(name)}</b><small>{esc(purpose)}</small></div><div class="net-agent-tools">{tags if tags else '<span>No tool output in included traces</span>'}</div></div>''')
    rows.append('</section>')
    return ''.join(rows)


NETWORK_STYLE = r'''<style>
.net-inventory,.net-tools{color:#173c51;font-family:inherit}
.net-inventory *,.net-tools *{box-sizing:border-box}
.net-inventory{background:#f5fafc;border:1px solid #c4dce4;border-radius:14px;padding:13px 14px;margin:10px 0 14px}
.net-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-bottom:12px}
.net-summary>div{display:flex;flex-direction:column;align-items:center;gap:2px;background:#e6f3f6;border:1px solid #d0e4eb;border-radius:9px;padding:7px}
.net-summary b{font-size:1.28rem;color:#126275}.net-summary span{font-size:.69rem;text-align:center;color:#365f70}
.net-path{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:5px 8px;margin-bottom:12px;font-size:.72rem}
.net-path span{background:#173f55;color:#fff;border-radius:7px;padding:6px 9px;font-weight:700}.net-path em{font-style:normal;color:#43758a;font-size:.64rem;font-weight:750}
.net-domain{border:1px solid #b9d6e2;border-radius:11px;background:#fff;margin:10px 0;padding:10px}
.net-domain-head{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px 12px;background:#eaf6f8;border:1px solid #c6e4e9;border-radius:8px;padding:8px 10px}
.net-domain-head strong{color:#125a70;font-size:.87rem;display:block}.net-domain-head span{font-size:.68rem;color:#526d7a}
.net-domain-nodes{display:flex;gap:4px;flex-wrap:wrap;max-width:70%}.net-domain-nodes span{border:1px solid #c3dce4;background:#fff;border-radius:5px;padding:3px 5px;font-size:.62rem;font-weight:650}
.net-domain-connector{margin:5px 0;text-align:center;color:#547987;font-size:.63rem;letter-spacing:.03em}.net-domain-connector:before{content:'↓ ';color:#218a94;font-weight:900}
.net-sites{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px}
.net-site{background:#fcfeff;border:1px solid #bbd7e1;border-radius:9px;padding:8px;min-width:0}
.net-site-top{display:flex;justify-content:space-between;flex-wrap:wrap;gap:1px 5px}.net-site-top b{font-size:.63rem;color:#628091}.net-site-top strong{font-size:.78rem;color:#15566c}
.net-site-du{margin:6px 0;font-weight:750;font-size:.69rem}.net-site-du span{font-weight:450;color:#557385;font-size:.62rem}
.net-cell-chips{display:flex;flex-wrap:wrap;gap:4px}.net-cell-chips span{flex:1 1 28%;background:#e6f8f1;border:1px solid #b5ded0;border-radius:6px;text-align:center;padding:5px 2px;color:#176857;font-size:.67rem;font-weight:730;white-space:nowrap}
.net-site-foot{text-align:center;font-size:.58rem;color:#69818c;margin-top:6px}
.net-footnote{border-top:1px solid #d8e9ee;padding-top:9px;margin-top:10px;font-size:.69rem;color:#547181;line-height:1.5}
.net-tools{border:1px solid #c8dce4;border-radius:13px;overflow:hidden;margin:10px 0;background:#fff}
.net-agent{display:grid;grid-template-columns:minmax(205px,.9fr) minmax(0,2fr);border-top:1px solid #e0ebef;gap:12px;padding:9px 12px;align-items:center}.net-agent:first-child{border-top:0}
.net-agent-who{display:grid;grid-template-columns:87px minmax(0,1fr);column-gap:7px}.net-agent-who strong{grid-row:span 2;color:#117889;font-size:.70rem;overflow-wrap:anywhere}.net-agent-who b{font-size:.79rem}.net-agent-who small{font-size:.65rem;color:#657d88;line-height:1.4}
.net-agent-tools{display:flex;gap:5px;flex-wrap:wrap}.net-agent-tools span{background:#eef8f9;border:1px solid #d3e8e8;border-radius:6px;padding:5px 7px;color:#225a67;font-size:.69rem}
@media(max-width:1100px){.net-sites{grid-template-columns:repeat(3,minmax(0,1fr))}.net-domain-nodes{max-width:100%}}
@media(max-width:640px){.net-summary{grid-template-columns:repeat(2,minmax(0,1fr))}.net-sites{grid-template-columns:repeat(2,minmax(0,1fr))}.net-agent{grid-template-columns:1fr;gap:5px}.net-path{justify-content:flex-start}}
@media(max-width:380px){.net-sites{grid-template-columns:1fr}}
</style>'''
