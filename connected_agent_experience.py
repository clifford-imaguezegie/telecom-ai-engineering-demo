"""Presentation-only connected agent journey for TEAD AI's *recorded* traces.

Do not infer network facts, fabricate handovers or introduce network/model calls.
The selected route is withheld until the recorded SP01 routing event appears.
"""
from html import escape

ROUTE_AGENTS = {
    'DIRECT_SUPERVISOR': ['SP01', 'SUPERVISOR', 'FINAL'],
    'LOCAL_SPECIALISTS': ['SP01', 'SP02', 'SP03', 'SP04', 'SP05', 'SP06', 'SP07', 'SUPERVISOR', 'FINAL'],
    'CU_SPECIALIST': ['SP01', 'SP08', 'SUPERVISOR', 'FINAL'],
}
JOIN_FOR_ROUTE = {'DIRECT_SUPERVISOR':'DIRECT_JOIN','LOCAL_SPECIALISTS':'LOCAL_JOIN','CU_SPECIALIST':'CU_JOIN'}
LABELS = {
    'SP01': ('Assess & localise', 'ML + network evidence'),
    'SP02': ('Accessibility KPIs', 'Performance investigation'),
    'SP03': ('Cell & peer', 'Comparison investigation'),
    'SP04': ('Radio analysis', 'Radio investigation'),
    'SP05': ('Processing', 'Compute investigations'),
    'SP06': ('Transport', 'Connectivity evidence'),
    'SP07': ('Configuration', 'Settings and changes'),
    'SP08': ('CU-domain analysis', 'CU processing and boundaries'),
    'SUPERVISOR': ('RCA Supervisor', 'Synthesis and uncertainty'),
    'FINAL': ('Recorded RCA', 'Evidence-backed conclusion'),
    'LOCAL_JOIN': ('Evidence consolidation', 'Recorded handover step'),
    'CU_JOIN': ('Evidence consolidation', 'Recorded handover step'),
    'DIRECT_JOIN': ('Direct review handover', 'Recorded handover step'),
}
ROUTE_LABELS = {
    'DIRECT_SUPERVISOR':'Healthy control · direct Supervisor review',
    'LOCAL_SPECIALISTS':'Cell/site · six sequential specialists',
    'CU_SPECIALIST':'Central Unit · CU specialist review',
}

CONNECTED_CSS = '''<style>
.tead-conn{--navy:#0c1630;--blue:#3557e9;--lime:#c9f271;--cloud:#f4f6fb;box-sizing:border-box;border:1px solid #b8c8eb;background:#f4f6fb;border-radius:19px;padding:16px 16px 13px;margin:12px 0;box-shadow:0 8px 24px rgba(16,38,83,.055);color:#162b58}
.tead-conn *{box-sizing:border-box}
.tead-conn-head{display:flex;justify-content:space-between;gap:12px;align-items:start;flex-wrap:wrap;margin-bottom:13px}
.tead-conn-eyebrow{color:#3557e9;font-size:.69rem;letter-spacing:.10em;font-weight:830;text-transform:uppercase}
.tead-conn-head h3{font-size:1.04rem;line-height:1.24;letter-spacing:-.02em;color:#182e5d;margin:4px 0 2px}
.tead-conn-id{font-size:.75rem;color:#476083;line-height:1.4}
.tead-conn-chip{display:inline-block;background:#e6edff;border:1px solid #bbc9f2;border-radius:99px;padding:6px 10px;font-size:.72rem;font-weight:750;color:#2b4785}
.tead-conn-track{overflow-x:auto;overflow-y:hidden;padding:4px 2px 9px;scrollbar-width:thin;scrollbar-color:#c0cbe5 transparent}
.tead-conn-rail{display:flex;align-items:stretch;gap:3px;min-width:max-content;max-width:none}
.tead-conn-node{position:relative;width:103px;flex:0 0 103px;min-height:96px;border:1px solid #c9d4ed;background:white;border-radius:12px;padding:12px 9px 10px;text-align:center;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:5px;transition:border-color .2s,box-shadow .2s,background .2s}
.tead-conn-node .id{font-weight:860;font-size:.66rem;letter-spacing:.08em;color:#5271b0}
.tead-conn-node b{font-size:.75rem;line-height:1.21;color:#26395e;overflow-wrap:anywhere}
.tead-conn-node small{font-size:.64rem;line-height:1.2;color:#687c9d}
.tead-conn-node.past{border-color:#95b0da;background:#e8f0ff}
.tead-conn-node.active{border:2px solid #3557e9;background:#e7edff;box-shadow:0 0 0 4px rgba(53,87,233,.09);transform:translateY(-1px)}
.tead-conn-node.active .id{color:#244bd2}
.tead-conn-node.pending{opacity:.62}
.tead-conn-node.complete{border-color:#a9c777;background:#edf8d5}
.tead-conn-edge{width:17px;flex:0 0 17px;display:flex;align-items:center;justify-content:center;color:#9cacc8;font-size:1.35rem;font-weight:850;position:relative}
.tead-conn-edge.travel{color:#3557e9}
.tead-conn-edge.travel:after{content:'•';position:absolute;top:27%;left:2px;font-size:14px;color:#3557e9;animation:tead-transfer 1.4s ease-in-out infinite}
@keyframes tead-transfer{0%{transform:translateX(0);opacity:0}30%{opacity:1}100%{transform:translateX(13px);opacity:0}}
.tead-conn-key{font-size:.70rem;line-height:1.45;color:#506381;margin-top:5px}
.tead-conn-key b{color:#1c376e}
.tead-conn-unknown{border:1px dashed #a8b7d5;border-radius:10px;background:#fff;padding:12px;color:#435b82;font-size:.82rem;line-height:1.5}
.tead-conn-unknown span{display:inline-block;margin:7px 8px 0 0;border:1px solid #cad6ef;border-radius:8px;padding:6px 8px;background:#eaf0fc;font-size:.70rem}
.tead-conn-detail{margin:0 0 10px;border:1px solid #c6d3ed;background:#fff;border-radius:12px;padding:12px 15px;color:#283f6c}
.tead-conn-detail .eyebrow{font-size:.68rem;font-weight:780;letter-spacing:.07em;text-transform:uppercase;color:#3557e9}
.tead-conn-detail h4{font-size:.97rem;margin:4px 0 8px;color:#152f67}
.tead-conn-detail .excerpt{padding:10px 12px;border-left:3px solid #3557e9;background:#f0f4ff;color:#374c73;font-size:.81rem;line-height:1.55;white-space:normal;overflow-wrap:anywhere}
.tead-conn-detail .next{color:#476080;font-size:.77rem;line-height:1.5;margin-top:9px}
.tead-conn-footer{font-size:.72rem;color:#566989;line-height:1.45}
@media(max-width:650px){.tead-conn{padding:13px 11px}.tead-conn-node{width:115px;flex-basis:115px}.tead-conn-head h3{font-size:.94rem}}
@media(prefers-reduced-motion:reduce){.tead-conn-edge.travel:after{animation:none;content:none}.tead-conn-node{transition:none}}
</style>'''


def route_sequence(case):
    route = case.get('route_family')
    if route not in ROUTE_AGENTS:
        return []
    sequence = list(ROUTE_AGENTS[route])
    join = JOIN_FOR_ROUTE[route]
    # Show consolidation only if source evidence actually contains that node.
    observed = {str(n.get('name','')).upper() for n in case.get('observed_nodes',[]) if isinstance(n,dict)}
    if join in observed:
        sequence.insert(-2,join)
    return sequence


def agent_state_sequence(case, current_agent='', previously_seen=(), route_unlocked=False, ready=False):
    """Pure trace display state; never exposes case route on unplayed SP01 scenes."""
    if ready or not route_unlocked:
        return []
    route = route_sequence(case)
    current = current_agent if current_agent in route else ''
    # Join events have their own recorded stage; never pretend they are a specialist.
    seen = set(previously_seen)
    return [(agent,'active' if agent==current else
             'complete' if agent=='FINAL' and agent in seen else
             'past' if agent in seen else 'pending') for agent in route]


def connected_agent_html(case, current_agent='', previously_seen=(), route_unlocked=False,
                         ready=False, mode='Guided scene', position_label='', current_detail=''):
    sid = escape(str(case.get('scenario_id','—')))
    title = escape(str(case.get('title','Recorded investigation')))
    route = case.get('route_family')
    path = agent_state_sequence(case,current_agent,previously_seen,route_unlocked,ready)
    active_label = LABELS.get(current_agent,(current_agent,'Recorded stage'))[0]
    status = ('Active now: '+current_agent+' · '+active_label) if path and current_agent else ('Awaiting recorded routing' if not path else 'Recorded route')
    head = (f'<section class="tead-conn" aria-label="Connected recorded agent investigation">'
            f'<div class="tead-conn-head"><div><div class="tead-conn-eyebrow">{escape(mode)} · RECORDED AGENT CONNECTIONS</div>'
            f'<h3>{title}</h3><div class="tead-conn-id">Case {sid} · {escape(position_label)}</div></div>'
            f'<span class="tead-conn-chip">{escape(status)}</span></div>')
    if not path:
        middle = ('<div class="tead-conn-unknown"><b>SP01 · Network Health &amp; Localisation</b>'
                  '<div>Current first stage: assess health and invoke the recorded ML / telemetry tools. The route is revealed only after the saved routing decision.</div>'
                  '<span>Healthy → Supervisor</span><span>Cell/site → SP02–SP07</span><span>CU domain → SP08</span></div>')
    else:
        parts=[]
        for i,(agent,status) in enumerate(path):
            label,subtitle=LABELS.get(agent,(agent,'Recorded stage'))
            accessible='Current recorded stage' if status=='active' else 'Previously presented' if status in ('past','complete') else 'Not yet presented'
            parts.append(f'<div class="tead-conn-node {status}" aria-label="{escape(agent+" "+label+". "+accessible)}">'
                         f'<span class="id">{escape(agent if not agent.endswith("_JOIN") else "JOIN")}</span>'
                         f'<b>{escape(label)}</b><small>{escape(subtitle)}</small></div>')
            if i<len(path)-1:
                next_agent=path[i+1][0]
                animated=next_agent==current_agent and path[i+1][1]=='active'
                parts.append(f'<div class="tead-conn-edge{" travel" if animated else ""}" aria-hidden="true">→</div>')
        middle='<div class="tead-conn-track" tabindex="0" aria-label="Scroll horizontally to inspect the sequential recorded agent route"><div class="tead-conn-rail">'+''.join(parts)+'</div></div>'
    note='<div class="tead-conn-key"><b>How to read:</b> blue = current recorded agent; pale blue = previously shown; white = upcoming. Arrows follow the saved sequential route, not concurrent agent execution. Full tool-level details remain below.</div>'
    return head+middle+note+'</section>'


def _excerpt(text,limit=330):
    if isinstance(text, (dict,list)):
        return 'Structured recorded data — inspect the original fields below.'
    out=' '.join(str(text or '').split())
    return out if len(out)<=limit else out[:limit-1].rsplit(' ',1)[0]+'…'


def agent_context_html(beat, next_beat=None, heading='Current recorded agent'):
    agent=str(beat.get('agent',''))
    title,_=LABELS.get(agent,(agent,'Recorded workflow stage'))
    raw_output=beat.get('output') or ''
    excerpt=_excerpt(raw_output)
    if next_beat:
        nxt=str(next_beat.get('agent',''))
        nxt_name=LABELS.get(nxt,(nxt,'Recorded stage'))[0]
        if nxt==agent:
            next_message='The next recorded event continues within '+nxt_name+'.'
        else:
            next_message='The next recorded event belongs to '+nxt_name+'.'
    else:
        next_message='This is the final recorded presentation event.'
    return (f'<section class="tead-conn-detail"><div class="eyebrow">{escape(heading)} · {escape(agent)}</div>'
            f'<h4>{escape(title)}</h4><div class="excerpt"><strong>Recorded output excerpt:</strong> '
            f'{escape(excerpt or "No separate output text saved for this event. Refer to the original recorded source below.")}</div>'
            f'<div class="next"><strong>Next in the recording:</strong> {escape(next_message)}</div></section>')
