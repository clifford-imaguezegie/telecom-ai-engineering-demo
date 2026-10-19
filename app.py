"""Telecom AI Engineering — Evidence-Grounded Investigation Replay (offline V1).

The Streamlit interface never calls original notebook, LangGraph, LangSmith,
RAG/LLMs, MCP telemetry, or any external service. It reads only bundled gzip.
"""
import gzip
import json
import re
import time
from storyboard import AGENT_ROLES, build_story, workflow_svg, workflow_overview_html, evidence_preview
from operational_demo import (guided_sequence, executive_sequence, get_run_durations, event_trace_offset,
                              format_clock, sp01_tools_unlocked, available_agents)
from html import escape
from presentation import agent_label, format_duration, agent_execution_rows, benchmark_summary, phase_execution_ranges
from guided_story_ui import flow_html, evidence_html, focus_html, boundary_html, phase_for, board_html
from network_overview import derive_inventory, observed_tools, topology_html, tools_html, NETWORK_STYLE, AGENT_ROLES, TOOL_NAMES
from value_solutions import render_page as render_value_solutions_page
from measurement_series import partition_measurements
from release_identity import release_build_id, RELEASE_VERSION, RELEASE_DATE
from terminology import render_page_terms, render_sidebar_glossary
from connected_agent_experience import connected_agent_html, agent_context_html, CONNECTED_CSS
from observatory_experience import OBSERVATORY_CSS, render_observatory_home
import ec_reference_experience as ref
from ec_reference_experience import REFERENCE_CSS, EXTRAS as EC_REF_EXTRAS
from ec_clarity_experience import (WORKSPACES, LEGACY_TO_WORKSPACE, STYLE as EC_CLARITY_STYLE,
    render_challenge, render_architecture, render_case_stories, render_agent_flow)
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
try:
 from streamlit.components.v1 import html as embed_workflow_html
except ImportError:
 # Lightweight local test stub has no Streamlit package hierarchy.
 embed_workflow_html = st.components.v1.html

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
PAGES = ['Platform Overview','Value Proposition & Solutions','Guided Operations Demo','Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis','Engineering Evidence','Evaluation & Performance']

st.set_page_config(page_title='TEAD AI | Agentic Telecom Network Investigation & RCA',page_icon='📡',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
.block-container {padding-top:1.5rem;padding-bottom:3rem;max-width:1500px}
[data-testid="stSidebar"]{background:#101e30}
/* Sidebar labels are light, but SELECT BOX text/icons must contrast with its background. */
[data-testid="stSidebar"]{color:#edf7fb}
[data-testid="stSidebar"] :is(h1,h2,h3,p,label){color:#edf7fb}
[data-testid="stSidebar"] [data-baseweb="select"] > div{
  background:#173c51!important;border:2px solid #80cbd0!important;box-shadow:0 0 0 1px rgba(128,203,208,.15)!important
}
[data-testid="stSidebar"] [data-baseweb="select"] :is(div,span,input){color:#ffffff!important;-webkit-text-fill-color:#ffffff!important}
[data-testid="stSidebar"] [data-baseweb="select"] svg{fill:#ffffff!important;color:#ffffff!important}
[data-testid="stSidebar"] [data-baseweb="select"] [role="button"]{color:#ffffff!important}
[data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div{outline:2px solid #73cdd1;outline-offset:1px}
h1,h2,h3{letter-spacing:-.025em}
.hero{padding:1.4rem 1.7rem;border-radius:14px;border:1px solid #28435e;background:linear-gradient(118deg,#10283d 10%,#153d51 100%);color:#f6f9fc;margin-bottom:1.1rem}
.hero .eyebrow{font-size:.77rem;letter-spacing:.17em;color:#96bed0;text-transform:uppercase;font-weight:700}
.hero h1{margin:.18rem 0 .35rem 0;font-size:1.9rem;font-weight:740;color:#fff}
.hero .sub{color:#c3d7e4;font-size:.91rem}
.note{font-size:.86rem;color:#6b7b8b}
.ops-hero{padding:1.3rem 1.5rem;border-radius:15px;background:linear-gradient(110deg,#102b42,#123e48);color:#edf8fb;border:1px solid #29536a;margin:.7rem 0 1rem 0;box-shadow:0 8px 28px rgba(12,30,48,.12)}
.ops-eyebrow{font-size:.73rem;font-weight:750;letter-spacing:.13em;color:#a6cbd4}
.ops-head{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
.ops-headline{font-size:1.46rem;font-weight:760;letter-spacing:-.025em;margin:.22rem 0}
.ops-sub{color:#c4dce3;font-size:.9rem;line-height:1.6}
.ops-pill{display:inline-block;border:1px solid #6597a7;background:#1c4d5b;padding:7px 11px;border-radius:22px;color:#e3fbf4;font-size:.76rem;font-weight:700;letter-spacing:.045em}
.ops-pill.alert{background:#793c35;border-color:#d88772;color:#fff2ee}
.ops-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#74efd1;margin-right:6px;box-shadow:0 0 0 4px rgba(116,239,209,.1);animation:opsblink 1.5s infinite}
@keyframes opsblink{50%{opacity:.35;transform:scale(.85)}}
.ops-stage{border-radius:13px;border:1px solid #34586b;background:#10263b;color:#e9f4fb;padding:1rem 1.2rem;margin:.6rem 0}
.ops-stage .role{letter-spacing:.13em;color:#8cc9db;font-size:.69rem;font-weight:750}
.ops-stage .act{font-size:1.17rem;font-weight:750;margin:.4rem 0}
.ops-stage .message{color:#b8d2e1;font-size:.9rem;line-height:1.6}
/* Main theatre: workflow and rolling messages remain together in the viewport. */
.ops-theatre-note{font-size:.78rem;color:#96bed0;margin-top:-.15rem}
.ops-compact{background:#10263b;border:1px solid #34586b;color:#eef7fb;border-radius:12px;padding:.8rem .95rem;margin-bottom:.5rem}
.ops-compact .tag{color:#9dd2df;text-transform:uppercase;font-size:.69rem;letter-spacing:.09em;font-weight:750;margin-bottom:.3rem}
.ops-compact .title{font-size:1.02rem;font-weight:760;line-height:1.3;margin:.2rem 0 .6rem}
.ops-compact .desc{font-size:.81rem;line-height:1.43;color:#d5e8ef;overflow-wrap:anywhere;max-height:88px;overflow-y:auto}
.ops-compact.output{border-color:#287d70;background:#113533}
.ops-compact.input{background:#152e43}
.ops-milestone{border:1px solid #294860;border-radius:10px;padding:.75rem;background:#f3f8fb;height:100%}
.ops-milestone .number{font-weight:790;font-size:1.55rem;color:#123c58;line-height:1.2}
.ops-milestone .label{font-size:.8rem;font-weight:720;color:#1e465c;margin:.25rem 0}
.ops-milestone .detail{font-size:.73rem;color:#46637a;line-height:1.35}
.ops-architecture{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:10px 0}
.ops-architecture .step{padding:10px 9px;background:#edf5f8;border-radius:9px;border:1px solid #cce0e8;color:#19445b}
.ops-architecture .step strong{display:block;font-size:.81rem}
.ops-architecture .step span{font-size:.72rem;display:block;margin-top:4px;color:#456578;line-height:1.4}
.ops-value{border:1px solid #cee3df;background:#f4faf8;border-radius:12px;padding:1.1rem 1.3rem;color:#1b4f49}
.ops-value strong{font-size:1.1rem}
.ops-value p{font-size:.84rem;color:#41645f;line-height:1.55}
@media(max-width:760px){.ops-architecture{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.ops-milestone .number{font-size:1.2rem}}

/* V1.6.2 — single-frame primary architecture view; V1.6.1 full diagram retained in disclosure. */
.tead-oneframe{box-sizing:border-box;border:1px solid #cbdfe9;background:linear-gradient(135deg,#f5fafe,#f8fbfd);border-radius:16px;padding:15px 16px 10px;color:#163e54;max-width:100%}
.tead-oneframe *{box-sizing:border-box}
.tead-oneframe .of-top{display:flex;align-items:center;justify-content:space-between;gap:9px;margin-bottom:10px;flex-wrap:wrap}
.tead-oneframe .of-top strong{font-size:.97rem;color:#113b56}
.tead-oneframe .of-tag{font-size:.65rem;font-weight:750;letter-spacing:.07em;color:#4b7791;text-transform:uppercase}
.tead-oneframe .of-columns{display:grid;grid-template-columns:minmax(195px,.94fr) minmax(360px,1.83fr) minmax(208px,.98fr);gap:9px;align-items:stretch}
.tead-oneframe .of-left{display:flex;flex-direction:column;gap:8px;min-width:0}
.tead-oneframe .of-card{border:1px solid #cee0eb;border-radius:12px;background:#fff;padding:11px 11px 10px;min-width:0;box-shadow:0 2px 9px rgba(16,63,91,.04)}
.tead-oneframe .of-assess{background:#ecf6fc;border-color:#aad3e8;flex:1}
.tead-oneframe .of-route{background:#f1effb;border-color:#d1c6f0}
.tead-oneframe .of-stage{display:flex;align-items:start;gap:8px;margin:0 0 6px}
.tead-oneframe .of-n{height:25px;width:25px;flex:none;display:flex;align-items:center;justify-content:center;background:#244b70;border-radius:50%;color:#fff;font-size:.85rem;font-weight:850}
.tead-oneframe .of-route .of-n{background:#7360b5}
.tead-oneframe .of-supervisor .of-n{background:#188469}
.tead-oneframe .of-rca .of-n{background:#e2faf2;color:#0a625c}
.tead-oneframe .of-title{font-size:.85rem;font-weight:850;line-height:1.21;overflow-wrap:break-word;color:#173e58}
.tead-oneframe .of-sub{font-size:.67rem;line-height:1.35;color:#557285;margin-top:3px}
.tead-oneframe .of-chips{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px;margin-top:9px}
.tead-oneframe .of-chip{background:#fff;border:1px solid #cbdfea;border-radius:7px;padding:6px 4px;text-align:center;font-size:.67rem;line-height:1.25;color:#24536e;font-weight:700}
.tead-oneframe .of-route-question{padding:7px 8px;background:#fff;border:1px solid #dcd5ee;border-radius:7px;font-size:.73rem;font-weight:780}
.tead-oneframe .of-route-hint{margin-top:6px;font-size:.64rem;color:#655d8c;line-height:1.32}
.tead-oneframe .of-paths{position:relative;min-width:0;display:flex;flex-direction:column;gap:8px}
.tead-oneframe .of-paths:before{content:'➜';position:absolute;top:calc(50% - 8px);left:-13px;color:#54799b;font-weight:900;font-size:1rem}
.tead-oneframe .of-path-head{display:flex;align-items:center;justify-content:space-between;gap:6px;padding:0 2px;min-height:25px}
.tead-oneframe .of-path-head strong{font-size:.81rem;color:#173c53}
.tead-oneframe .of-path-head span{font-size:.62rem;color:#667b87}
.tead-oneframe .of-lane{border:1px solid;border-radius:10px;padding:8px 10px;position:relative;min-width:0}
.tead-oneframe .of-lane:after{content:'➜';position:absolute;right:-14px;top:calc(50% - 10px);font-size:1.13rem;z-index:2;font-weight:900}
.tead-oneframe .of-lane.healthy{background:#ecfaf2;border-color:#a7d9b9}
.tead-oneframe .of-lane.healthy:after{color:#26966b}
.tead-oneframe .of-lane.site{background:#fff7e9;border-color:#ebcc93;flex:1;display:flex;flex-direction:column}
.tead-oneframe .of-lane.site:after{color:#c68a2f}
.tead-oneframe .of-lane.cu{background:#f3effe;border-color:#d1c2f1}
.tead-oneframe .of-lane.cu:after{color:#8566be}
.tead-oneframe .of-lane-heading{display:flex;align-items:baseline;justify-content:space-between;gap:5px;flex-wrap:wrap}
.tead-oneframe .of-lane-heading strong{font-size:.76rem;color:#20475e}
.tead-oneframe .of-lane-heading span{font-size:.62rem;color:#557180}
.tead-oneframe .of-lane-detail{font-size:.66rem;color:#506879;line-height:1.3;margin-top:3px}
.tead-oneframe .of-sequence{display:flex;gap:3px;align-items:stretch;margin-top:7px;width:100%}
.tead-oneframe .of-agent{border:1px solid #ead5b0;background:#fffdf8;border-radius:6px;padding:5px 2px;flex:1 1 0;min-width:0;text-align:center}
.tead-oneframe .of-agent b{font-size:.67rem;display:block;color:#77490c;line-height:1.1}
.tead-oneframe .of-agent span{font-size:.60rem;display:block;color:#684e2c;line-height:1.24;margin-top:2px;overflow-wrap:break-word}
.tead-oneframe .of-connector{align-self:center;font-size:.72rem;font-weight:850;color:#a98040;flex:0 0 auto}
.tead-oneframe .of-outcome{min-width:0;display:flex;flex-direction:column;gap:8px}
.tead-oneframe .of-supervisor{background:#eaf8f3;border-color:#aad8ca;flex:1}
.tead-oneframe .of-supervisor .of-sub{margin-top:8px}
.tead-oneframe .of-tasks{display:flex;flex-direction:column;gap:5px;margin-top:10px}
.tead-oneframe .of-tasks span{display:block;font-size:.68rem;line-height:1.35;color:#235e53;background:#fff;border-radius:6px;border:1px solid #d1e7e0;padding:6px 7px}
.tead-oneframe .of-tasks span:before{content:'✓';color:#148c73;margin-right:4px;font-weight:900}
.tead-oneframe .of-rca{background:#0b6068;border:1px solid #107c7c;border-radius:10px;color:#fff;padding:10px}
.tead-oneframe .of-rca .of-title{color:#fff}
.tead-oneframe .of-rca .of-sub{color:#d4f4ef}
.tead-oneframe .of-bottom{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px;border-top:1px solid #cddfea;margin-top:10px;padding-top:9px}
.tead-oneframe .of-bottom b{color:#274e64;font-size:.70rem}
.tead-oneframe .of-bottom span{font-size:.67rem;color:#587587}
.tead-oneframe .of-notice{font-size:.66rem;color:#5a7183;line-height:1.32;margin-top:7px}
@media(max-width:1210px){.tead-oneframe .of-columns{grid-template-columns:minmax(150px,.88fr) minmax(260px,1.55fr) minmax(160px,.9fr)}.tead-oneframe .of-agent span{font-size:.55rem}.tead-oneframe .of-tasks span{font-size:.63rem}}
.tead-oneframe .of-tag{font-size:.70rem}
.tead-oneframe .of-sub{font-size:.74rem}
.tead-oneframe .of-title{font-size:.91rem}
.tead-oneframe .of-chip{font-size:.73rem}
.tead-oneframe .of-route-question{font-size:.78rem}
.tead-oneframe .of-route-hint{font-size:.71rem}
.tead-oneframe .of-path-head strong{font-size:.86rem}
.tead-oneframe .of-path-head span{font-size:.69rem}
.tead-oneframe .of-lane-heading strong{font-size:.82rem}
.tead-oneframe .of-lane-heading span{font-size:.69rem}
.tead-oneframe .of-lane-detail{font-size:.73rem}
.tead-oneframe .of-site-note{font-size:.71rem;line-height:1.25;color:#9b6c34;margin-top:auto;padding-top:8px}
.tead-oneframe .of-agent b{font-size:.75rem}
.tead-oneframe .of-agent span{font-size:.69rem}
.tead-oneframe .of-tasks span{font-size:.72rem}
.tead-oneframe .of-bottom span{font-size:.72rem}
.tead-oneframe .of-notice{font-size:.72rem}
@media(max-width:850px){.tead-oneframe .of-columns{grid-template-columns:1fr 1.4fr}.tead-oneframe .of-outcome{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr}.tead-oneframe .of-lane:after{display:none}.tead-oneframe .of-paths:before{display:none}}
@media(max-width:560px){.tead-oneframe .of-columns{grid-template-columns:1fr}.tead-oneframe .of-outcome{grid-column:auto;display:flex}.tead-oneframe .of-paths:before{display:none}.tead-oneframe .of-route,.tead-oneframe .of-assess{flex:auto}.tead-oneframe .of-sequence{flex-wrap:wrap}.tead-oneframe .of-agent{flex:1 0 27%}.tead-oneframe .of-connector{display:none}.tead-oneframe .of-agent span{font-size:.65rem}.tead-oneframe .of-lane{padding:10px}.tead-oneframe .of-notice{margin-top:9px}}

/* V1.6.1 — source-grounded, conditional infographic; all other pages/cockpit unchanged. */
.tead-flow{--navy:#153a58;--mint:#20836f;--amber:#a86717;--violet:#7661bf;background:linear-gradient(180deg,#f7fbfe 0%,#eff6fb 100%);border:1px solid #cbdce9;border-radius:18px;padding:clamp(13px,2.0vw,25px);color:#173950;box-shadow:0 8px 26px rgba(18,58,83,.055)}
.tead-flow *{box-sizing:border-box}
.tead-flow .flow-topline{display:flex;justify-content:space-between;align-items:start;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.tead-flow .flow-topline .label{font-size:.69rem;font-weight:850;color:#416f8f;letter-spacing:.10em;text-transform:uppercase}
.tead-flow .flow-topline .note{font-size:.69rem;color:#55758a;line-height:1.4;max-width:410px;text-align:right}
.tead-flow .flow-headline{font-size:1.23rem;line-height:1.15;font-weight:850;color:#103552;margin:4px 0}
.tead-flow .flow-foundation{display:grid;grid-template-columns:1.06fr 52px 1fr;gap:8px;align-items:stretch;margin-bottom:14px}
.tead-flow .flow-card{position:relative;background:#fff;border:1px solid #c8dce9;border-radius:13px;padding:14px;min-width:0;box-shadow:0 3px 10px rgba(23,65,96,.035)}
.tead-flow .flow-card.sp01{background:linear-gradient(135deg,#edf7fd,#ffffff);border-color:#a5d4ec}
.tead-flow .flow-card.route{background:linear-gradient(135deg,#f2effe,#ffffff);border-color:#d0c6f5}
.tead-flow .flow-stage-head{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.tead-flow .flow-stage-id{flex:none;display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;background:#23476f;color:#fff;font-weight:850;font-size:1.05rem}
.tead-flow .flow-card.route .flow-stage-id{background:#7361bc}
.tead-flow .flow-stage-title{font-weight:850;font-size:.96rem;line-height:1.24;color:#143954}
.tead-flow .flow-stage-sub{font-size:.72rem;line-height:1.4;color:#536e80;margin-top:2px}
.tead-flow .flow-inputs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:10px}
.tead-flow .flow-input{border-radius:9px;background:#e8f3fb;border:1px solid #cfdfed;padding:8px 5px;text-align:center;min-width:0}
.tead-flow .flow-input .symbol{display:block;font-size:1rem;color:#22658b;line-height:1.25}
.tead-flow .flow-input b{display:block;font-size:.68rem;line-height:1.24;color:#153d5a;margin-top:4px}
.tead-flow .flow-input span:last-child{display:block;font-size:.62rem;color:#527087;line-height:1.25;margin-top:3px}
.tead-flow .flow-arrow-inline{display:flex;align-items:center;justify-content:center;color:#557b9f;font-weight:900;font-size:1.75rem;line-height:1}
.tead-flow .flow-decision{display:flex;align-items:center;gap:12px;min-height:68px;border-radius:11px;border:1px solid #ddd4f4;background:#faf8ff;padding:9px 12px;margin-top:9px}
.tead-flow .flow-decision-icon{flex:none;display:flex;align-items:center;justify-content:center;width:43px;height:43px;transform:rotate(45deg);border:2px solid #7053bf;border-radius:8px;background:#f0eafa;color:#5440a6}
.tead-flow .flow-decision-icon span{transform:rotate(-45deg);font-weight:900;font-size:1.2rem}
.tead-flow .flow-decision b{display:block;font-size:.87rem;color:#18394f}
.tead-flow .flow-decision small{display:block;color:#5f6b8a;font-size:.70rem;line-height:1.4}
.tead-flow .flow-routing-hint{border-radius:8px;background:#edeafc;margin-top:7px;padding:7px 9px;font-size:.70rem;color:#5a5190}
.tead-flow .flow-to-routes{font-weight:830;color:#6e7684;font-size:.71rem;text-align:center;letter-spacing:.06em;margin:4px 0 8px}
.tead-flow .flow-to-routes:before{content:'↓';display:block;font-size:1.1rem;color:#537698;line-height:1.3}
.tead-flow .flow-network{display:grid;grid-template-columns:minmax(0,1fr) 38px minmax(225px,0.39fr);grid-template-rows:auto auto auto;gap:8px 3px;align-items:stretch}
.tead-flow .flow-lane{display:flex;align-items:center;gap:12px;min-width:0;border:1px solid;border-radius:12px;padding:11px 12px;background:#fff}
.tead-flow .flow-lane.healthy{background:#edfaf3;border-color:#acdcc0}
.tead-flow .flow-lane.cell{background:#fff7e9;border-color:#eccf9b}
.tead-flow .flow-lane.cu{background:#f4efff;border-color:#d2c3f2}
.tead-flow .flow-lane .lane-mark{width:9px;border-radius:7px;align-self:stretch;flex:none;background:#2ba36e}
.tead-flow .flow-lane.cell .lane-mark{background:#da963e}
.tead-flow .flow-lane.cu .lane-mark{background:#9476cf}
.tead-flow .lane-content{min-width:0;flex:1}
.tead-flow .lane-head{display:flex;gap:10px;justify-content:space-between;flex-wrap:wrap;align-items:baseline;margin-bottom:5px}
.tead-flow .lane-head strong{font-size:.84rem;color:#14394d}
.tead-flow .lane-head small{font-size:.69rem;color:#4f7180}
.tead-flow .lane-details{font-size:.76rem;line-height:1.46;color:#3a5b6b}
.tead-flow .flow-sequence{display:flex;align-items:stretch;gap:3px;margin-top:8px}
.tead-flow .flow-agent{border:1px solid #e6c78c;background:#fffaf1;border-radius:8px;padding:7px 4px;flex:1 1 0;min-width:0;text-align:center}
.tead-flow .flow-agent b{font-size:.72rem;display:block;color:#6c4419}
.tead-flow .flow-agent span{display:block;font-size:.63rem;line-height:1.25;color:#6f5138;margin-top:2px;overflow-wrap:normal}
.tead-flow .flow-step-arrow{flex:none;color:#9c7e55;font-size:.83rem;font-weight:900;display:flex;align-items:center;justify-content:center;width:10px}
.tead-flow .flow-sp08{font-size:.83rem;font-weight:820;color:#523b91;padding:7px 12px;border:1px solid #d5c8ed;background:#fff;border-radius:8px;display:inline-flex;gap:8px;align-items:center;margin-top:4px}
.tead-flow .flow-sp08 small{font-size:.70rem;font-weight:500;color:#6e6196}
.tead-flow .flow-into-supervisor{font-size:1.55rem;color:#63839b;font-weight:900;display:flex;justify-content:center;align-items:center}
.tead-flow .flow-into-supervisor.healthy{color:#26996c}
.tead-flow .flow-into-supervisor.cell{color:#c98e31}
.tead-flow .flow-into-supervisor.cu{color:#8869c5}
.tead-flow .flow-convergence{grid-column:3;grid-row:1/span 3;border:1px solid #acd4cb;border-radius:13px;background:linear-gradient(145deg,#e8f8f2,#f9fdfd);padding:13px;display:flex;flex-direction:column;justify-content:space-between;gap:12px;min-width:0}
.tead-flow .flow-convergence .flow-stage-id{background:#17886d}
.tead-flow .flow-synthesis-actions{display:grid;gap:6px;margin:8px 0}
.tead-flow .flow-synthesis-actions span{display:block;padding:9px 9px;border-radius:8px;border:1px solid #cde8df;background:#fff;font-size:.72rem;line-height:1.38;color:#225e57}
.tead-flow .flow-convergence-arrow{text-align:center;font-weight:850;color:#25816b;font-size:1.1rem;line-height:1.1}
.tead-flow .flow-final{border:1px solid #1a7f7a;border-radius:11px;background:linear-gradient(130deg,#0e5c64,#0f7072);color:#fff;padding:12px}
.tead-flow .flow-final .flow-stage-id{background:#fff;color:#0f636d;width:28px;height:28px;font-size:.88rem}
.tead-flow .flow-final .flow-stage-title{color:#fff;font-size:.88rem}
.tead-flow .flow-final p{font-size:.73rem;line-height:1.43;color:#e8faf8;margin:6px 0 0}
.tead-flow .flow-support{margin-top:13px;border-top:1px solid #d0e1ec;padding-top:11px}
.tead-flow .flow-support h4{font-size:.88rem;color:#214763;margin:0 0 7px}
.tead-flow .flow-support-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.tead-flow .flow-support-item{border:1px solid #d6e2ed;border-radius:9px;background:#fff;padding:9px;font-size:.70rem;line-height:1.44;color:#466477}
.tead-flow .flow-support-item strong{display:block;font-size:.74rem;color:#1b526b;margin-bottom:3px}
.tead-flow .flow-caption{font-size:.70rem;color:#55778a;line-height:1.4;margin-top:10px}
@media(max-width:1020px){.tead-flow .flow-foundation{grid-template-columns:1fr 25px 1fr}.tead-flow .flow-network{grid-template-columns:minmax(0,1fr) 26px minmax(210px,.42fr)}.tead-flow .flow-sequence{flex-wrap:wrap}.tead-flow .flow-agent{flex:1 0 24%}.tead-flow .flow-step-arrow{flex:0 0 9px}}
@media(max-width:790px){.tead-flow .flow-foundation{grid-template-columns:1fr;gap:0}.tead-flow .flow-foundation > .flow-arrow-inline{transform:rotate(90deg);height:26px}.tead-flow .flow-network{grid-template-columns:minmax(0,1fr);grid-template-rows:auto}.tead-flow .flow-convergence{grid-column:auto;grid-row:auto}.tead-flow .flow-into-supervisor{display:none}.tead-flow .flow-lane{position:relative;margin-bottom:9px}.tead-flow .flow-lane:after{content:"↘ To Supervisor";position:absolute;bottom:-13px;right:12px;background:#f7fbfe;border:1px solid #d4e1eb;border-radius:20px;padding:2px 8px;font-size:.61rem;font-weight:780;color:#436980}.tead-flow .flow-convergence:before{content:"↓ SELECTED ROUTE CONVERGES HERE";text-align:center;font-size:.67rem;font-weight:820;color:#23745f}.tead-flow .flow-sequence{flex-wrap:nowrap}.tead-flow .flow-agent{flex:1 1 0}.tead-flow .flow-support-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.tead-flow .flow-topline .note{text-align:left}}
@media(max-width:520px){.tead-flow .flow-inputs{grid-template-columns:repeat(2,minmax(0,1fr))}.tead-flow .flow-sequence{flex-direction:column;gap:3px}.tead-flow .flow-step-arrow{transform:rotate(90deg);height:11px;width:auto}.tead-flow .flow-agent{flex:auto;padding:8px}.tead-flow .flow-support-grid{grid-template-columns:1fr}.tead-flow .flow-lane{padding:10px 8px}.tead-flow .flow-stage-title{font-size:.91rem}.tead-flow .flow-decision{align-items:start}}
.tead-performance{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:10px 0}
.tead-performance-card{border:1px solid #d0e0e8;border-radius:12px;padding:14px;background:#f8fbfd;color:#173950}
.tead-performance-card .label{font-size:.78rem;color:#496a7e;font-weight:700}
.tead-performance-card .threshold{font-size:1.65rem;font-weight:800;letter-spacing:-.035em;line-height:1.25;margin:6px 0}
.tead-performance-card .limits{display:flex;flex-wrap:wrap;justify-content:space-between;gap:5px 10px;font-size:.76rem;border-top:1px solid #d9e7ed;padding-top:8px}
.tead-lesson-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:10px 0}
.tead-lesson{padding:14px;border:1px solid #d1e1e8;border-radius:12px;background:#f8fbfd;color:#24475c}
.tead-lesson strong{font-size:.89rem;color:#153b51;display:block;margin-bottom:5px}
.tead-lesson p{font-size:.8rem;line-height:1.5;margin:5px 0}
.tead-footnote{font-size:.75rem;line-height:1.48;color:#657987}
@media(max-width:1150px){.tead-flow-grid{grid-template-columns:1fr;gap:7px}.tead-flow-arrow{transform:rotate(90deg);height:19px}.tead-flow-stage{padding:11px}.tead-capabilities{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:650px){.tead-performance,.tead-lesson-grid,.tead-capabilities{grid-template-columns:1fr}.tead-performance-card .threshold{font-size:1.45rem}}

.ops-kpi{border:1px solid #365e6c;background:#173244;border-radius:12px;padding:.9rem;height:100%;color:#f0fbff;min-height:112px}
.ops-kpi .name{font-size:.72rem;letter-spacing:.06em;color:#a6c9d5;text-transform:uppercase}
.ops-kpi .value{font-size:1.12rem;font-weight:800;margin:.5rem 0 .2rem;overflow-wrap:anywhere}
.ops-kpi .desc{font-size:.75rem;color:#c0d8e0}
.route-box{background:#f6f9fc;border:1px solid #dce8f1;padding:.8rem 1rem;border-radius:10px;font-size:.88rem;line-height:2.15}
@media (prefers-color-scheme:dark){.route-box{background:#1a2631;border:1px solid #405261}}
.wrap-value{border:1px solid #cbdbe5;background:#f3f8fa;border-radius:10px;padding:12px 14px;min-height:90px}
.wrap-value span{display:block;color:#496778;font-size:.78rem;margin-bottom:8px}
.wrap-value strong{display:block;color:#14384c;font-size:1.12rem;line-height:1.28;overflow-wrap:anywhere;white-space:normal}
[data-testid="stVerticalBlock"]{scroll-margin-top:1rem}

/* V1.5.0 unified cockpit: compact presentation only; evidence and other pages retain layout. */
.tread-guided-marker{display:none;height:0;overflow:hidden}
.block-container:has(.tread-guided-marker){padding-top:.32rem;padding-bottom:1.2rem}
.block-container:has(.tread-guided-marker) > [data-testid="stVerticalBlock"]{gap:.48rem!important}
.cockpit-kicker{font-size:.67rem;font-weight:820;letter-spacing:.11em;color:#478296;text-transform:uppercase;margin:0 0 2px}
.cockpit-heading{font-size:1.22rem;line-height:1.2;font-weight:790;color:#13354c;margin:0}
.cockpit-guidance{font-size:.75rem;line-height:1.35;color:#5b7283;margin-top:3px}
.cockpit-status{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;border:1px solid #346274;
 background:linear-gradient(115deg,#102d43,#164450);color:white;border-radius:12px;padding:10px 15px;margin:2px 0 0}
.cockpit-status .overline{font-size:.67rem;letter-spacing:.1em;color:#add6df;font-weight:750}
.cockpit-status .name{font-size:1.04rem;font-weight:790;line-height:1.2;margin:2px 0}
.cockpit-status .detail{font-size:.73rem;color:#cee5ed;line-height:1.3}
.cockpit-status .right{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.cockpit-status .stat{min-width:70px;border-left:1px solid #527487;padding-left:10px}
.cockpit-status .stat b{font-size:.97rem;font-variant-numeric:tabular-nums;display:block;line-height:1.25}
.cockpit-status .stat span{font-size:.63rem;color:#c3d9e4;display:block;line-height:1.2}
.cockpit-status .flag{font-size:.63rem;font-weight:790;padding:5px 8px;background:#1a5261;border:1px solid #5a9baa;border-radius:15px;white-space:nowrap}
.cockpit-status .flag.alert{background:#794037;border-color:#c78875}
.cockpit-timeline{font-size:.71rem;color:#456073;display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:-2px}
.cockpit-timeline strong{color:#133d54}
.cockpit-layout-label{font-size:.69rem;color:#557587;font-weight:650;margin-top:-2px}
.cockpit-activity{height:250px;display:flex;flex-direction:column;gap:6px;min-width:0}
.cockpit-activity-head{font-size:.76rem;line-height:1.2;color:#17394f;font-weight:790;display:flex;justify-content:space-between;gap:8px;align-items:baseline}
.cockpit-activity-head small{font-size:.69rem;color:#637a89;font-weight:500;white-space:nowrap}
.cockpit-activity-cards{display:grid;grid-template-rows:repeat(3,minmax(0,1fr));gap:5px;flex:1;min-height:0}
.cockpit-evidence{border-radius:9px;padding:8px 10px;min-width:0;overflow:hidden;border:1px solid #315669;color:#eaf6fa;background:#123147}
.cockpit-evidence.action{background:#153a4c}
.cockpit-evidence.output{background:#124640;border-color:#2d766b}
.cockpit-evidence .tag{font-size:.60rem;letter-spacing:.08em;text-transform:uppercase;font-weight:820;color:#a9d8e3;line-height:1.15}
.cockpit-evidence.output .tag{color:#a6ebd5}
.cockpit-evidence .value{font-size:.74rem;line-height:1.3;color:#edf9fd;margin-top:3px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
.cockpit-show-more{font-size:.67rem;color:#567284;line-height:1.2}
.block-container:has(.tread-guided-marker) [data-testid="stSlider"]{padding-top:0!important;padding-bottom:0!important}
.block-container:has(.tread-guided-marker) [data-testid="stButton"] button{min-height:2.1rem}
.block-container:has(.tread-guided-marker) div[data-testid="stRadio"] > label{font-size:.74rem}
@media(max-width:960px){.cockpit-status .right{gap:7px}.cockpit-status .stat{min-width:55px;padding-left:6px}}
@media(max-width:740px){.cockpit-status .right{width:100%;justify-content:space-between}.cockpit-activity{height:auto;min-height:250px}.cockpit-evidence{min-height:73px}}

/* V1.7.0 — legible progressive investigation story. Presentation only. */
.block-container:has(.tread-guided-marker){padding-top:1.4rem!important}
.gs-intro{font-size:.78rem;color:#436778;margin:1px 0 6px;line-height:1.45}
.gs-help{padding:8px 12px;border:1px solid #bee0dd;background:#f1fbf9;border-radius:9px;color:#245d58;font-size:.75rem;margin:0 0 6px}
.gs-help b{color:#174e47}
.gs-progress{display:flex;gap:9px;align-items:center;justify-content:space-between;flex-wrap:wrap;font-size:.72rem;color:#446c7d;margin:4px 0 6px}
.gs-progress b{color:#153e57}
.gs-status{border:1px solid #2c6473;background:#123a4b;color:white;border-radius:12px;padding:9px 14px;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:1px 0 5px}
.gs-status .gs-status-small{display:block;font-size:.63rem;letter-spacing:.08em;font-weight:780;color:#a0e4e7}
.gs-status b{display:block;font-size:.90rem;line-height:1.3;margin:3px 0 1px}
.gs-status .gs-status-desc{display:block;font-size:.70rem;color:#c6e4e8}
.gs-status .gs-duration{border-left:1px solid #518895;padding-left:12px;flex-shrink:0;font-size:.68rem;color:#c4dee0}
.gs-status .gs-duration strong{display:block;font-size:.94rem;color:#fff;font-variant-numeric:tabular-nums}
.gs-route{background:#f3f9fc;border:1px solid #c8dfe9;border-radius:12px;padding:10px 12px;color:#15394e;margin:5px 0 8px;max-width:100%;box-sizing:border-box}
.gs-route *{box-sizing:border-box}
.gs-flow-heading,.gs-board-head{display:flex;justify-content:space-between;align-items:center;gap:7px;margin-bottom:8px;flex-wrap:wrap;font-size:.70rem;color:#45687e}
.gs-flow-heading b,.gs-board-head b{color:#143e58;font-size:.75rem;letter-spacing:.06em}
.gs-flow-grid{display:grid;grid-template-columns:minmax(124px,1.05fr) 17px minmax(250px,2.45fr) 17px minmax(121px,1.1fr) 17px minmax(119px,1fr);gap:5px;align-items:stretch}
.gs-node{display:flex;flex-direction:column;justify-content:center;background:white;border:1px solid #b5d0dd;border-radius:9px;padding:10px;min-width:0}
.gs-node b{font-size:.80rem;line-height:1.23;color:#193e54;overflow-wrap:anywhere}
.gs-node small{font-size:.65rem;color:#547387;line-height:1.3;margin-top:5px}
.gs-eyebrow{font-size:.61rem;letter-spacing:.08em;color:#417792;font-weight:780;margin-bottom:6px}
.gs-node.active{border:2px solid #16a591;box-shadow:0 0 0 2px rgba(22,165,145,.12);background:#effaf6}
.gs-node.done{background:#e9f7ef;border-color:#a3cdb7}
.gs-node.gs-final.active{background:#e8fbf4}
.gs-arrow{color:#48809a;font-size:20px;font-weight:900;display:flex;justify-content:center;align-items:center}
.gs-branches{display:grid;grid-template-rows:auto auto auto;gap:5px;min-width:0}
.gs-path{border:1px solid #d6e1e8;border-radius:7px;background:#fff;display:flex;align-items:center;gap:9px;padding:5px 8px;min-width:0;flex-wrap:wrap;min-height:28px}
.gs-path b{font-size:.65rem;letter-spacing:.02em;color:#315e77;min-width:130px}
.gs-path small{font-size:.61rem;color:#607f90;line-height:1.2}
.gs-path.chosen{background:#eaf8f3;border:2px solid #18a58f;padding:4px 7px}
.gs-path.chosen b{color:#126e60}
.gs-path.muted{opacity:.36}
.gs-path.waiting{background:#fff;opacity:.78}
.gs-specialists{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.gs-specialist{font-size:.57rem;font-weight:850;padding:3px 5px;border-radius:5px;background:#e8eef3;color:#376276;border:1px solid #d1dfe9}
.gs-specialist.active{background:#c2f2e7;border-color:#16a58f;color:#086d59}
.gs-specialist.done{background:#d6e8db;border-color:#9ec1ad;color:#2f7354}
.gs-flow-note{font-size:.65rem;color:#668092;margin-top:7px;line-height:1.28}
.gs-evidence-wrap{margin:4px 0 8px}
.gs-evidence-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.gs-evidence{min-width:0;min-height:101px;max-height:101px;overflow:hidden;background:#f3f7fa;border:1px dashed #bcd2db;border-radius:10px;padding:9px 11px;box-sizing:border-box}
.gs-evidence.revealed{border:1px solid #9fcac4;background:#ebf9f4}
.gs-evidence.new{border:2px solid #13a58e;background:#dcf8eb;padding:8px 10px;box-shadow:0 0 0 2px #c5f2e4}
.gs-evidence-head{display:flex;justify-content:space-between;align-items:start;gap:5px;margin-bottom:4px}
.gs-evidence-head span{font-size:.64rem;color:#316f7e;font-weight:820;letter-spacing:.04em}
.gs-evidence-head strong{font-size:.55rem;letter-spacing:.03em;white-space:nowrap}
.gs-await{color:#94a9b0}.gs-received{color:#388374}.gs-new{color:#07846c}
.gs-evidence b{display:block;color:#184459;font-size:.72rem;line-height:1.2}
.gs-evidence p{font-size:.67rem;line-height:1.29;color:#527185;margin:4px 0 0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
.gs-evidence.pending p{color:#879cab}
.gs-focus{padding:11px 14px 10px;border:1px solid #c4dfe5;border-radius:12px;background:#fff;color:#1a3c52;margin:2px 0 8px}
.gs-focus-top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}
.gs-scene{font-weight:850;font-size:.69rem;color:#1d7d83;letter-spacing:.08em}
.gs-scene-agent{color:#7b96a2;font-size:.66rem}
.gs-focus h3{font-size:1.08rem;line-height:1.26;color:#14394e;margin:5px 0 6px;font-weight:800}
.gs-focus>p{font-size:.78rem;color:#4a6c7b;margin:6px 0;line-height:1.44}
.gs-why{font-size:.74rem;color:#496b7f;margin:5px 0}
.gs-why b{color:#185374}
.gs-result{border-left:4px solid #1e9e8d;padding:7px 9px;background:#edf9f5;border-radius:0 7px 7px 0;margin:8px 0 0}
.gs-result>b{display:block;font-size:.66rem;color:#137965;letter-spacing:.05em}
.gs-result p{font-size:.80rem;line-height:1.38;color:#194d4a;margin:3px 0}
.gs-focus .gs-source-note{font-size:.66rem;color:#768d98;margin:5px 0 0}
.gs-boundary{background:#fff8e9;border:2px solid #dea345;border-radius:12px;color:#5e471f;padding:14px 17px;margin:7px 0}
.gs-boundary>b{font-size:.67rem;color:#936016;letter-spacing:.06em}
.gs-boundary h3{font-size:1.08rem;margin:6px 0;color:#6b4518}
.gs-boundary p{font-size:.78rem;line-height:1.5;margin:6px 0}
@media(max-width:1040px){.gs-flow-grid{grid-template-columns:minmax(107px,1fr) 13px minmax(185px,2fr) 13px minmax(107px,1fr) 13px minmax(108px,1fr);gap:3px}.gs-node{padding:7px}.gs-node b{font-size:.72rem}.gs-path{padding:4px}.gs-path b{min-width:105px;font-size:.62rem}.gs-path small{font-size:.56rem}}
@media(max-width:720px){.gs-flow-grid{grid-template-columns:1fr;gap:4px}.gs-arrow{transform:rotate(90deg);font-size:15px;height:16px}.gs-branches{grid-template-columns:1fr;gap:4px}.gs-path{min-height:36px}.gs-evidence-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.gs-evidence{min-height:110px;max-height:110px}.gs-status{flex-wrap:wrap}.gs-status .gs-duration{border-left:0;padding-left:0}}
@media(max-width:420px){.gs-evidence-grid{grid-template-columns:1fr}.gs-evidence{min-height:82px;max-height:100px}.gs-route{padding:9px}}


/* V1.7.1a — prevent the first Guided Demo eyebrow from being cropped by
   Streamlit's compact first-block layout. Scoped to this page only. */
.block-container:has(.tread-guided-marker) .cockpit-kicker{
  display:block;
  box-sizing:border-box;
  padding-top:12px!important;
  line-height:1.5!important;
}

/* V1.7.1 — explicit timing + context-specific results, no independent time simulation. */
.block-container:has(.tread-guided-marker){padding-top:1.7rem!important}
.cockpit-heading{padding-top:2px;line-height:1.35;margin-bottom:2px}
.gs-timeline{border:1px solid #b7d7e2;background:#edf9fb;border-radius:9px;padding:7px 11px;margin:4px 0 8px;color:#254f61}
.gs-timeline-stats{display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px 12px;font-size:.69rem;font-variant-numeric:tabular-nums}
.gs-timeline-stats b{font-size:.62rem;color:#0d5f6f;margin-right:5px;letter-spacing:.06em}
.gs-timeline-track{height:9px;border-radius:10px;overflow:hidden;background:#c5dce3;margin:7px 0 4px}
.gs-timeline-fill{height:100%;border-radius:10px;background:#128d81;transition:width .22s ease}
.gs-timeline-note{color:#4f7382;font-size:.60rem;line-height:1.2}
.gs-rca-board .gs-evidence{min-height:150px;max-height:160px}
.gs-rca-board .gs-rca-primary{border:2px solid #159979;background:#d8f9e8;box-shadow:0 0 0 2px rgba(21,153,121,.12)}
.gs-rca-board .gs-evidence b{font-size:.79rem;line-height:1.25;display:block;overflow-wrap:anywhere;white-space:normal}
.gs-rca-board .gs-evidence p{display:block;overflow-wrap:anywhere;white-space:normal}
.gs-rca-board .gs-evidence{max-height:none;min-height:150px;height:auto;overflow:visible}
.gs-history{display:flex;align-items:center;flex-wrap:wrap;gap:5px;margin:5px 0 0;font-size:.61rem;color:#417082}
.gs-history b{font-size:.61rem;margin-right:4px;color:#235369}
.gs-history-chip{background:#dff5e9;border:1px solid #b0dccc;color:#165949;border-radius:5px;padding:4px 6px;font-variant-numeric:tabular-nums}
.gs-focus-final{background:#eafaf1;border-color:#6bbda6}
.gs-focus-final .gs-result{background:#d9f7e9;border-left-color:#11856e}
.gs-focus-final .gs-result p{font-size:.92rem;line-height:1.5}
@media(max-width:720px){.gs-timeline-stats{display:grid;grid-template-columns:1fr 1fr}.gs-timeline-stats span:last-child{grid-column:1/-1}.gs-rca-board .gs-evidence{min-height:155px;max-height:none;height:auto}}
</style>''',unsafe_allow_html=True)

# Presentation-only layer; all recorded evidence and model logic remain unchanged.
st.markdown(OBSERVATORY_CSS,unsafe_allow_html=True)
st.markdown(CONNECTED_CSS,unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_manifest():
 return json.loads((DATA/'manifest.json').read_text('utf-8'))

@st.cache_data(show_spinner=False,max_entries=20)
def load_case(sid):
 if sid not in load_manifest()['scenario_order']:raise ValueError('Unknown scenario identifier')
 with gzip.open(DATA/'cases'/f'{sid}.json.gz','rt',encoding='utf-8') as f:return json.load(f)

@st.cache_data(show_spinner=False,max_entries=35)
def load_evidence(sid,eid):
 case=load_case(sid)
 item=next((e for e in case['evidence_index'] if e['evidence_id']==eid),None)
 if item is None:raise ValueError('Unknown evidence identifier')
 path=BASE/item['file']
 if not path.resolve().is_relative_to((DATA/'evidence').resolve()):raise ValueError('Invalid evidence path')
 with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)

def pretty(v,none='Not identified'):
 if v is None or v=='' or v==[]:return none
 if isinstance(v,bool):return 'Yes' if v else 'No'
 if isinstance(v,(int,float)):return f'{v:,.2f}'
 if isinstance(v,dict):return str(v.get('label') or v.get('fault_family') or v.get('scope_class') or v.get('root_cause') or v)
 return str(v).replace('_',' ')

def display_tool_name(tool):
 # Preserve exact LangSmith tool identifiers for trace lookup and provenance.
 # Only the user-facing description adopts the curated knowledge-base name.
 if tool == 'supervisor_private_knowledge_search':
  return 'Curated Telecom Knowledge Base Search'
 return tool

def nice_time(val):
 if not val:return '—'
 try:return datetime.fromisoformat(str(val).replace('Z','+00:00')).strftime('%d %b %Y  %H:%M UTC')
 except ValueError:return str(val)

def heading(title,desc=None):
 st.subheader(title)
 if desc:st.caption(desc)

def route_text(c):
 """Public-facing route summary while trace identifiers remain in engineer view."""
 if c['route_family']=='LOCAL_SPECIALISTS':
  return 'Network Localisation → KPI → Cell & Peer → Radio → Processing → Transport → Configuration → RCA Supervisor (recorded sequential route)'
 if c['route_family']=='CU_SPECIALIST':
  return 'Network Localisation → CU-Domain & Boundary Analysis → Evidence Consolidation → RCA Supervisor'
 return 'Network Health Assessment → RCA Supervisor (healthy control)'

def run_badge(c):
 return 'HEALTHY / NO INCIDENT' if not c['derived_display']['incident_present'] else 'INCIDENT DETECTED'

def count_caps(c):
 x=c.get('data_inventory',{})
 return x.get('telemetry_rows',0),x.get('cell_kpi_rows',0),x.get('subnetwork_kpi_rows',0)

def evidence_by_tool(c,tool):
 return next((e for e in c['evidence_index'] if e['tool']==tool),None)

def query_network(c):
 a=evidence_by_tool(c,'telemetry_network_overview')
 return load_evidence(c['scenario_id'],a['evidence_id'])['result'] if a else {}

def network_chart(c,metric='partial_drb_accessibility_pct',by='five_qi'):
 rows=query_network(c).get('subnetwork_kpis',[])
 if not rows:return st.info('Recorded subnetwork KPI rows unavailable for this case.')
 frame=pd.DataFrame(rows).sort_values('interval_start_utc')
 frame['time']=pd.to_datetime(frame['interval_start_utc'],utc=True)
 fig=go.Figure()
 for key,group in frame.groupby(by,sort=True):
  fig.add_trace(go.Scatter(x=group.time,y=group[metric],mode='lines+markers',name=f'5QI {key}',line={'width':2},marker={'size':5}))
 fig.update_layout(height=325,margin={'l':10,'r':10,'t':18,'b':15},yaxis={'title':metric.replace('_',' ').title(),'ticksuffix':'%'},xaxis={'title':'Recorded observation time (UTC)'},legend={'orientation':'h','y':1.15},hovermode='x unified',template='plotly_white')
 st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
 st.caption('Source: recorded telemetry_network_overview • subnetwork KPIs • 15-minute PM intervals. This is replay data, not live telemetry.')

def data_field_sections(data,show_json=False):
 if not isinstance(data,dict):st.write(data);return
 # Avoid repeating huge bulky objects in front-end narrative views.
 for field in ['rationale','analysis_summary','diagnosis','selection_rationale']:
  if data.get(field) and isinstance(data[field],str):st.markdown(f'**{field.replace("_"," ").title()}** — {data[field]}')
 for field in ['observations','supported_observations','positive_metrics','candidate_fault_families','supported_hypotheses','weakened_hypotheses','contradictions','uncertainties','uncertainty','limitations','remaining_uncertainty','remaining_questions','supporting_evidence','recommendations']:
  v=data.get(field)
  if v:
   with st.expander(field.replace('_',' ').title(),expanded=field in ['observations','supported_hypotheses']):
    if isinstance(v,list):
     for entry in v:
      if isinstance(entry,str):st.markdown('• '+entry)
      else:st.json(entry,expanded=False)
    else:st.json(v,expanded=False) if isinstance(v,dict) else st.write(v)
 if 'domain_analysis' in data and data['domain_analysis']:
  with st.expander('Specialist domain analysis — original structured record'):
   st.json(data['domain_analysis'],expanded=False)
 if show_json:
  with st.expander('Full recorded stage output (JSON)'):
   st.json(data,expanded=False)

def state_summary(c):
 d=c['derived_display']
 a,b,cc=st.columns(3)
 for col,title,val in [(a,'Observed condition',run_badge(c)),(b,'Final scope',pretty(d['scope_class'])),(cc,'Trace execution',format_duration(c['trace_duration_seconds']))]:
  with col:
   st.markdown(f'<div class="wrap-value"><span>{escape(title)}</span><strong>{escape(val)}</strong></div>',unsafe_allow_html=True)
 st.caption('Full recorded Supervisor diagnosis is available under Original detailed Supervisor diagnosis.')



def render_rca_outcome(case):
    """Source-backed executive reading layer; saved Supervisor outputs remain intact."""
    su=case['stage_data']['supervisor_output']
    scope=su.get('final_scope') or {}
    sites=scope.get('affected_sites') or []
    domains=scope.get('affected_cu_domains') or []
    cells=scope.get('affected_cells') or []
    st.subheader('Investigation outcome at a glance')
    if not su.get('incident_present'):
        st.success('No material incident supported by this recorded assessment. No specialist escalation was required.')
        st.caption('The healthy control was reviewed by the RCA Supervisor without knowledge-base retrieval.')
        return
    st.markdown('**Recorded likely fault mechanism:** '+str((su.get('root_cause_assessment') or {}).get('root_cause') or su.get('root_cause_family') or 'Not established'))
    st.markdown('**Affected scope:** '+str(len(sites))+' site(s), '+str(len(cells))+' cell(s), '+str(len(domains))+' CU domain(s)')
    if sites:st.caption('Sites: '+', '.join(map(str,sites)))
    st.markdown('**Recorded execution time:** '+format_duration(case.get('trace_duration_seconds'))+' · **Agent confidence class:** '+str((su.get('root_cause_assessment') or {}).get('confidence') or 'Unreported'))
    x,y=st.columns(2)
    with x:
        st.markdown('**Key supporting observations**')
        for v in (su.get('supporting_evidence') or [])[:3]:st.markdown('• '+str(v))
        alternatives=su.get('contradictory_evidence') or []
        if alternatives:
            st.markdown('**Weakened competing explanations**')
            for v in alternatives[:2]:st.markdown('• '+str(v))
    with y:
        st.markdown('**Uncertainty and evidence gaps**')
        for v in (su.get('residual_uncertainty') or ['No further limitation recorded in the Supervisor final output.'])[:3]:st.markdown('• '+str(v))
        st.markdown('**Recommended engineering follow-up**')
        for v in (su.get('recommendations') or ['See original Supervisor report.'])[:2]:st.markdown('• '+str(v))
    if case['scenario_id']=='M05I0005':
        st.caption('Engineering interpretation: the recorded CU-CP delay, CPU, memory and queue increases support processing pressure, but do not independently prove resource exhaustion or the precise RRC failure mechanism. RRC NoReply/MaxRetrans cause counters and the initiating trigger were not established in this record.')
    elif case['scenario_id']=='M05I0003':
        st.caption('ML interpretation: the recorded fault-family support of 0.525 is modest and uncalibrated, not independent diagnostic certainty. Radio resource and accessibility measurements provide the stronger incident evidence; exact DRB failure-cause codes were not available.')
    st.caption('This summary is extracted from the recorded Supervisor output and is not a new RCA. A HIGH class is the agent’s recorded judgement, not independently calibrated probability or validation of the exact physical failure mechanism.')

def kb_list(label, values, empty='Not recorded in this Supervisor output'):
 """Show Supervisor-recorded knowledge grounding text without raw retrieved passages."""
 st.markdown(f'**{label}**')
 if not values:
  st.caption(empty)
 elif isinstance(values,list):
  for text in values:st.write('• '+str(text))
 else:
  st.write(str(values))

def render_kb_contribution(supervisor):
 """Recorded RAG contribution, not a live search, direct source quotation or causal claim."""
 k=supervisor.get('knowledge_base_contribution')
 heading('Curated Telecom Knowledge Base | RAG reasoning contribution',
         'The original Supervisor recorded how external telecom-domain knowledge informed mechanism assessment and discrimination between competing explanations.')
 if not isinstance(k,dict):
  st.info('No structured knowledge-base contribution was recorded in this investigation.')
  return
 if not k.get('used'):
  st.info('Knowledge-base retrieval was not used for this healthy-network investigation. The Supervisor concluded directly from available network evidence.')
  st.caption('Recorded knowledge-base contribution: NONE / NOT_USED. No retrieval is simulated in this replay.')
  return
 a,b,d=st.columns(3)
 with a:st.metric('RAG contribution','Used')
 with b:st.markdown(f'<div class="wrap-value"><span>Contribution type</span><strong>{escape(pretty(k.get("contribution_type")))}</strong></div>',unsafe_allow_html=True)
 with d:st.markdown(f'<div class="wrap-value"><span>Evidence weight</span><strong>{escape(pretty(k.get("evidence_weight")))}</strong></div>',unsafe_allow_html=True)
 st.markdown('**1. Question asked by the Supervisor**')
 for q in k.get('queries') or []:st.info(str(q))
 st.markdown('**2. Knowledge-informed fault mechanism**')
 kb_list('Mechanism interpretation',k.get('mechanism_summary'))
 left,right=st.columns(2)
 with left:kb_list('Hypotheses supported by domain knowledge',k.get('supported_hypotheses'))
 with right:kb_list('Competing hypotheses assessed',k.get('competing_hypotheses_discussed'))
 st.markdown('**3. Discriminating network observations**')
 expected,observed,missing=st.columns(3)
 with expected:kb_list('What the mechanism predicts',k.get('discriminating_observations_expected'))
 with observed:kb_list('Incident observations cited by Supervisor',k.get('incident_observations_confirming_mechanism'))
 with missing:kb_list('Evidence not available / not observed',k.get('incident_observations_missing'),empty='No missing observations listed')
 st.markdown('**4. Limits of the contribution**')
 kb_list('Recorded limitations',k.get('limitations'),empty='No additional limitations recorded in this field')
 st.caption('Provenance: Supervisor final knowledge_base_contribution field from the selected LangSmith trace. These are the Supervisor’s recorded interpretations, not redistributed retrieval passages, formal document citations or a measured causal RAG performance gain. Deterministic network observations carry primary weight; knowledge is SUPPORTING evidence.')

@st.cache_data(show_spinner=False,max_entries=12)
def load_storyboard(sid):
 c = load_case(sid)
 return build_story(c,lambda eid:load_evidence(sid,eid))

def friendly_replay_text(value):
 """Translate source-only trace IDs in the public theatre, not the saved evidence."""
 text=str(value or '')
 aliases={'SP01':'Localisation Agent','SP02':'KPI Agent','SP03':'Cell & Peer Agent',
          'SP04':'Radio Agent','SP05':'Processing Agent','SP06':'Transport Agent',
          'SP07':'Configuration Agent','SP08':'CU-Domain Agent'}
 return re.sub(r'\bSP0[1-8]\b',lambda match:aliases[match.group(0)],text)


def compact_beat_content(beat):
 """Short, synchronised theatre messages; complete raw text remains in detail expander."""
 def card(kind,label,text,limit=320):
  value=' '.join(friendly_replay_text(text or 'No separate field recorded for this stage.').split())
  short=value if len(value)<=limit else value[:limit-1].rstrip()+'…'
  return f'<div class="ops-compact {kind}"><div class="tag">{escape(label)}</div><div class="desc">{escape(short)}</div></div>'
 return (card('input','Incoming evidence / handover',beat.get('input')),
         card('action','Agent action / tool call',beat.get('action')),
         card('output','Recorded output / feedback',beat.get('output'),450))


def render_detailed_investigation_flow():
    """Responsive static infographic of the actual three alternative trace routes.

    The runtime architecture and recorded execution data are unchanged. The
    desktop panel emphasises true route convergence; mobile stacks the lanes.
    """
    st.markdown("""<section class="tead-flow" role="group" aria-label="TEAD AI investigation flow with conditional healthy, cell-site and CU-domain paths">
  <div class="flow-topline"><div><div class="label">TEAD AI · RECORDED NETWORK INVESTIGATIONS</div><div class="flow-headline">From network evidence to a traceable diagnosis</div></div><div class="note">Three alternative routes, one evidence-grounded conclusion.<br>Illustrates completed synthetic-network LangGraph runs, not live inference.</div></div>
  <div class="flow-foundation">
    <div class="flow-card sp01"><div class="flow-stage-head"><span class="flow-stage-id">1</span><div><div class="flow-stage-title">Network Assessment &amp; Localisation</div><div class="flow-stage-sub">SP01 · Network Health &amp; Localisation Agent</div></div></div><div class="flow-stage-sub">Assess PM and event telemetry across the scenario observation window, check network health and identify the likely fault family and affected scope.</div>
      <div class="flow-inputs"><div class="flow-input"><span class="symbol">◈</span><b>ML 01</b><span>Fault-family support</span></div><div class="flow-input"><span class="symbol">◎</span><b>ML 02</b><span>Affected-scope support</span></div><div class="flow-input"><span class="symbol">▥</span><b>Network</b><span>Overview telemetry</span></div><div class="flow-input"><span class="symbol">⌁</span><b>Events</b><span>Event telemetry</span></div></div>
    </div>
    <div class="flow-arrow-inline" aria-hidden="true">➜</div>
    <div class="flow-card route"><div class="flow-stage-head"><span class="flow-stage-id">2</span><div><div class="flow-stage-title">Intelligent Routing</div><div class="flow-stage-sub">Conditional decision from SP01 evidence</div></div></div>
      <div class="flow-decision"><div class="flow-decision-icon" aria-hidden="true"><span>?</span></div><div><b>Incident detected?</b><small>No → healthy direct review · Yes → investigate the supported cell/site or CU-domain scope</small></div></div>
      <div class="flow-routing-hint">Select exactly one recorded route for the case. Cell/site and CU paths are alternatives, not sequential stages.</div>
    </div>
  </div>
  <div class="flow-to-routes" aria-hidden="true">CONDITIONAL INVESTIGATION ROUTES</div>
  <div class="flow-network">
    <div class="flow-lane healthy"><div class="lane-mark"></div><div class="lane-content"><div class="lane-head"><strong>✓ Healthy network</strong><small>NO INCIDENT · SP01 → SUPERVISOR</small></div><div class="lane-details">No specialist escalation. The assessment goes directly to Supervisor review and a no-incident conclusion.</div></div></div>
    <div class="flow-into-supervisor healthy" aria-hidden="true">➜</div>
    <div class="flow-lane cell"><div class="lane-mark"></div><div class="lane-content"><div class="lane-head"><strong>3 · Cell / Site Investigation</strong><small>INCIDENT · SIX SEQUENTIAL SPECIALISTS</small></div><div class="lane-details">Domain evidence is investigated in the original recorded order:</div>
      <div class="flow-sequence" aria-label="SP02 KPI, then SP03 Cell and Peer, then SP04 Radio, then SP05 Processing, then SP06 Transport, then SP07 Configuration">
        <div class="flow-agent"><b>SP02</b><span>KPI</span></div><div class="flow-step-arrow" aria-hidden="true">➜</div><div class="flow-agent"><b>SP03</b><span>Cell &amp; Peer</span></div><div class="flow-step-arrow" aria-hidden="true">➜</div><div class="flow-agent"><b>SP04</b><span>Radio</span></div><div class="flow-step-arrow" aria-hidden="true">➜</div><div class="flow-agent"><b>SP05</b><span>Processing</span></div><div class="flow-step-arrow" aria-hidden="true">➜</div><div class="flow-agent"><b>SP06</b><span>Transport</span></div><div class="flow-step-arrow" aria-hidden="true">➜</div><div class="flow-agent"><b>SP07</b><span>Configuration</span></div>
      </div></div></div>
    <div class="flow-into-supervisor cell" aria-hidden="true">➜</div>
    <div class="flow-lane cu"><div class="lane-mark"></div><div class="lane-content"><div class="lane-head"><strong>3 · CU-Domain Investigation</strong><small>INCIDENT · ALTERNATIVE SPECIALIST PATH</small></div><div class="flow-sp08"><span>SP08</span><small>CU-Domain &amp; Boundary Analysis</small></div><div class="lane-details">CU and boundary evidence are investigated without invoking SP02–SP07 for this route.</div></div></div>
    <div class="flow-into-supervisor cu" aria-hidden="true">➜</div>
    <div class="flow-convergence"><div><div class="flow-stage-head"><span class="flow-stage-id">4</span><div><div class="flow-stage-title">Supervisor · Evidence Synthesis</div><div class="flow-stage-sub">Every selected route terminates here</div></div></div>
      <div class="flow-synthesis-actions"><span>▣ Consolidate recorded evidence and specialist findings</span><span>≋ Examine supporting and competing explanations</span><span>▤ Apply knowledge-base RAG support when applicable</span><span>✓ Preserve missing measurements and uncertainty</span></div></div>
      <div class="flow-convergence-arrow" aria-hidden="true">↓</div>
      <div class="flow-final"><div class="flow-stage-head"><span class="flow-stage-id">5</span><div><div class="flow-stage-title">Recorded Root Cause Analysis</div></div></div><p>Finding or healthy outcome · Affected scope · Supporting evidence · Alternatives · Confidence qualification · Traceability</p></div>
    </div>
  </div>
  <div class="flow-support"><h4>Supporting capabilities · used when required, not extra execution stages</h4><div class="flow-support-grid">
    <div class="flow-support-item"><strong>▦ Network evidence</strong>15-minute synthetic 5G telemetry, original measurements, tool responses and case scope</div>
    <div class="flow-support-item"><strong>⚙ ML &amp; domain tools</strong>SP01-invoked prediction tools and specialist engineering measurements</div>
    <div class="flow-support-item"><strong>▤ Knowledge &amp; context</strong>Curated RAG contributions only where recorded; not proof of causal accuracy</div>
    <div class="flow-support-item"><strong>◎ Evaluation &amp; provenance</strong>Saved LangSmith traces, measured execution times, original evidence and post-run evaluation</div>
  </div>
  <div class="flow-caption">Arrows represent alternative recorded routes converging on one Supervisor. The six cell/site specialists run sequentially; SP08 is a separate CU-domain path. The healthy control bypasses specialist investigation. Nothing on this page invokes a live agent, telemetry service or LLM.</div>
</section>""", unsafe_allow_html=True)
    st.caption('Original trace evidence is retained in the scenario, replay and engineering-evidence pages. This diagram explains orchestration; it does not claim real-time network automation or validated production performance.')


def render_investigation_flow():
    """Compact one-frame source-grounded view, with complete v1.6.1 route on demand."""
    st.subheader('End-to-End Investigation Flow')
    st.caption('One-frame architecture: SP01 → one selected route → Supervisor → recorded RCA. Full engineering detail remains available below.')
    st.markdown("""<section class="tead-oneframe" role="group" aria-label="TEAD AI compact one-frame investigation overview: SP01, alternative routes, Supervisor and RCA">
  <div class="of-top"><strong>From network assessment to evidence-grounded RCA</strong><span class="of-tag">RECORDED SYNTHETIC 5G INVESTIGATIONS</span></div>
  <div class="of-columns">
    <div class="of-left">
      <div class="of-card of-assess"><div class="of-stage"><span class="of-n">1</span><div><div class="of-title">Network Assessment &amp; Localisation</div><div class="of-sub">SP01 · PM and event telemetry · selected scenario observation window</div></div></div>
        <div class="of-chips"><div class="of-chip">ML 01<br>Fault family</div><div class="of-chip">ML 02<br>Affected scope</div><div class="of-chip">Network<br>telemetry</div><div class="of-chip">Event<br>telemetry</div></div>
      </div>
      <div class="of-card of-route"><div class="of-stage"><span class="of-n">2</span><div><div class="of-title">Intelligent Routing</div><div class="of-sub">Decision from SP01 evidence</div></div></div><div class="of-route-question">Incident detected?</div><div class="of-route-hint">Select one recorded path: Healthy, Cell/Site or CU-Domain.</div></div>
    </div>
    <div class="of-paths"><div class="of-path-head"><strong>3 · Conditional Investigation Paths</strong><span>Alternatives · not consecutive branches</span></div>
      <div class="of-lane healthy"><div class="of-lane-heading"><strong>✓ Healthy</strong><span>NO INCIDENT</span></div><div class="of-lane-detail">Direct Supervisor review · no specialist escalation</div></div>
      <div class="of-lane site"><div class="of-lane-heading"><strong>Cell / Site Incident</strong><span>SIX SEQUENTIAL SPECIALISTS</span></div><div class="of-sequence" aria-label="Sequential SP02 KPI, SP03 Cell and Peer, SP04 Radio, SP05 Processing, SP06 Transport, SP07 Configuration">
        <div class="of-agent"><b>SP02</b><span>KPI</span></div><span class="of-connector">›</span><div class="of-agent"><b>SP03</b><span>Cell &amp; Peer</span></div><span class="of-connector">›</span><div class="of-agent"><b>SP04</b><span>Radio</span></div><span class="of-connector">›</span><div class="of-agent"><b>SP05</b><span>Processing</span></div><span class="of-connector">›</span><div class="of-agent"><b>SP06</b><span>Transport</span></div><span class="of-connector">›</span><div class="of-agent"><b>SP07</b><span>Config.</span></div>
      </div><div class="of-site-note">Recorded tools and domain evidence · complete specialist records remain inspectable</div></div>
      <div class="of-lane cu"><div class="of-lane-heading"><strong>CU-Domain Incident</strong><span>ALTERNATIVE TO SP02–SP07</span></div><div class="of-lane-detail"><b>SP08</b> · CU-Domain &amp; Boundary Analysis</div></div>
    </div>
    <div class="of-outcome"><div class="of-card of-supervisor"><div class="of-stage"><span class="of-n">4</span><div><div class="of-title">Evidence Synthesis</div><div class="of-sub">One Supervisor for every selected route</div></div></div><div class="of-tasks"><span>Correlate recorded findings</span><span>Evaluate competing causes</span><span>RAG support when recorded</span><span>Qualify gaps and uncertainty</span></div></div>
      <div class="of-rca"><div class="of-stage"><span class="of-n">5</span><div><div class="of-title">Recorded Root Cause Analysis</div><div class="of-sub">Diagnosis or healthy outcome · Evidence · Scope · Alternatives · Traceability</div></div></div></div>
    </div>
  </div>
  <div class="of-bottom"><b>SUPPORTING CAPABILITIES</b><span>ML &amp; telemetry tools · Domain knowledge &amp; RAG · LangSmith traces · Post-run evaluation</span></div>
  <div class="of-notice">Three alternative recorded routes converge on the same Supervisor. SP02–SP07 execute sequentially for cell/site incidents; SP08 is a separate CU route. Diagram does not represent live network analysis.</div>
</section>""", unsafe_allow_html=True)
    with st.expander('Detailed investigation flow — full agents, tools, and provenance (V1.6.1 diagram preserved)', expanded=False):
        render_detailed_investigation_flow()


def _mmss(seconds, decimals=1):
    if seconds is None:
        return '—'
    minutes = int(float(seconds) // 60)
    remain = float(seconds) - minutes * 60
    return f'{minutes:02d}:{remain:04.{decimals}f}'


def render_execution_performance(cases):
    """Data-derived min/max from the exact nine bundled frozen case records."""
    metrics = phase_execution_ranges(cases)
    st.subheader('Recorded Execution Performance')
    st.caption('Minimum and maximum observed across nine completed experimental scenarios. Headline is the next whole-second upper threshold, not a production SLA.')
    specs = [
        ('Network Assessment &amp; Localisation · SP01', 'sp01', '&lt; 00:25', 'All recorded cases'),
        ('Specialist Investigation · SP02–SP08', 'specialists', '&lt; 01:52', 'Eight incident cases'),
        ('Evidence Synthesis &amp; RCA · Supervisor', 'supervisor', '&lt; 02:54', 'Eight incident cases'),
        ('End-to-End Incident Investigation', 'incident', '&lt; 04:33', 'Eight incident cases'),
    ]
    cards = []
    for label, key, threshold, scope in specs:
        measurement = metrics[key]
        if not measurement:
            continue
        # Keep the original public < threshold motif, but derive its limit from the actual max.
        from math import floor
        upper = floor(measurement['max']) + 1
        mm, ss = divmod(upper, 60)
        bound = f'&lt; {mm:02d}:{ss:02d}'
        cards.append(f'<div class="tead-performance-card"><div class="label">{label}</div><div class="threshold">{bound}</div>'
                     f'<div class="limits"><span>Minimum observed: <b>{_mmss(measurement["min"])}</b></span>'
                     f'<span>Maximum observed: <b>{_mmss(measurement["max"])}</b></span></div>'
                     f'<div class="tead-footnote">{scope} · n={measurement["count"]}</div></div>')
    st.markdown('<div class="tead-performance">'+''.join(cards)+'</div>',unsafe_allow_html=True)
    healthy = metrics['healthy']
    if healthy:
        st.caption(f'Healthy control: {_mmss(healthy["min"])} end-to-end (no specialist route). Phase ranges can come from different cases and must not be summed. The full trace includes small orchestration overhead; saved judge evaluation is post-run.')
    st.caption('These are observed LangSmith chain times on synthetic cases, not live-network diagnostic accuracy, a guaranteed response time or demonstrated MTTR/OPEX savings. Playback viewing time is separate.')


def render_platform_learnings():
    st.subheader('Key Learnings from Network Investigations')
    st.caption('Lessons derived from the nine recorded investigation traces; observations are not proof of production impact.')
    lessons = [
        ('Fast initial localisation', 'SP01 consistently completed within 25 seconds across the nine recorded scenarios; its two ML predictions are supporting signals alongside telemetry.'),
        ('Conditional routing avoids unnecessary work', 'The healthy control reached direct Supervisor review; incidents followed cell/site or CU-domain specialist paths appropriate to their recorded scope.'),
        ('Multi-domain corroboration matters', 'Specialists compared supporting and competing explanations across radio, KPI, processing, transport, configuration and CU evidence rather than trusting a single anomaly.'),
        ('Supervisor synthesis dominates time', 'In incident runs, Supervisor RCA was a substantial share of wall time. Context engineering and synthesis efficiency deserve targeted benchmarking.'),
        ('Uncertainty and provenance are essential', 'Saved conclusions disclose unavailable failure-cause counters, uncertainty and the distinction between recorded judgement and calibrated confidence.'),
    ]
    st.markdown('<div class="tead-lesson-grid">'+''.join(
        f'<div class="tead-lesson"><strong>{escape(title)}</strong><p>{escape(detail)}</p></div>' for title,detail in lessons
        )+'</div>',unsafe_allow_html=True)


def render_engineering_learnings():
    st.subheader('Engineering Learnings — Efficiency, Tokens & Cost')
    st.caption('Development learnings from M05_06C / M05_06D optimisation work. These are distinct from the nine public replay measurements.')
    blocks = [
       ('~98.7% smaller evidence representation', 'A historical SP08 experimental representation reduced raw CU-domain evidence from approximately 17.29 MB to 227 KB through deterministic restructuring. This is byte-size reduction, NOT proven token/cost savings.'),
       ('Context should be engineered, not simply enlarged', 'Earlier SP02 experiments encountered an approximately 195,500-token request with a 4,096-token output ceiling. Deduplicated, lossless engineer-view tables now prepare structured evidence for model reasoning.'),
       ('Inference cost requires explicit controls', 'Early experiments exposed expensive provider routing, extra self-validation passes and corrective retries. Cost controls favour bounded calls, logged failures and avoiding repeated large-context inference.'),
       ('Right-size the model to the agent task', 'Development evaluated Gemma 12B/26B/31B options. Model selection must compare reasoning correctness, structured-output compliance, tool behaviour, latency and cost on matched scenarios.'),
       ('Technical resilience matters', 'A JSON parse failure showed that removing excessive retries is not the same as removing all recovery. Bounded technical retries and visible error reporting help avoid blocked handovers.'),
       ('Optimise evidence first, then measure quality', 'Deterministic evidence restructuring retains original raw records for audit while keeping root-cause interpretation with specialists and Supervisor. Quantify quality, token count, cost and latency together.'),
    ]
    st.markdown('<div class="tead-lesson-grid">'+''.join(
       f'<div class="tead-lesson"><strong>{escape(title)}</strong><p>{escape(detail)}</p></div>' for title,detail in blocks
       )+'</div>',unsafe_allow_html=True)
    with st.expander('Engineering measurement boundaries and next optimisation experiments',expanded=False):
        st.markdown("""**Measured historical example:** the SP08 payload-size reduction concerns the encoded evidence representation; it is not a measured model-token reduction, cost saving or proof that quality was unchanged.

**Engineering controls observed or developed:** deterministic lossless engineer views, bounded evidence requests, no routine second validation pass, restrictive provider routing, response-format checks and explicit technical failure logging. They are architecture changes, not proof of a particular percentage saving.

**Next benchmark:** compare matched M05_06C and M05_06D scenarios on input/output tokens, number of model calls, actual billed cost, p50/p95 latency, retries, completion success, evidence recall, localisation correctness and RCA quality. Preserve prompt/model/provider configuration and separate diagnostic evaluation from runtime inference.

**Interpretation:** the public recorded demo does not run inference. Its exported child-token and cost fields are incomplete and must not be used as evidence of free inference or quantified savings.""")

def architecture_diagram():
    """Reader-friendly architecture, with SP01 as initiator of BOTH ML calls and telemetry.

    Trace identifiers deliberately stay in technical drill-down and provenance only.
    """
    st.subheader('Solution Architecture — How the Investigation Works')
    st.caption('A conceptual overview. The animated graph in the demo follows each real recorded execution route.')
    st.markdown("""<div style="border:1px solid #d1e1e9;border-radius:14px;padding:18px;background:#f3f8fb;color:#163449">
<div style="max-width:710px;margin:auto;text-align:center;padding:12px;border-radius:11px;background:#13344a;color:#f8ffff"><strong>1. Network Health &amp; Localisation Agent</strong><div style="color:#c7dfe8;font-size:.84rem;margin-top:5px">Initiates assessment · invokes intelligence tools · interprets evidence · determines routing</div></div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ requests ↓</div>
<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;max-width:850px;margin:auto">
<div style="padding:11px;background:#e0effb;border:1px solid #a9cee1;border-radius:9px"><strong>ML prediction: Fault family</strong><div style="font-size:.82rem">What could be wrong?</div></div>
<div style="padding:11px;background:#e0effb;border:1px solid #a9cee1;border-radius:9px"><strong>ML prediction: Fault scope</strong><div style="font-size:.82rem">Where is the fault likely located?</div></div>
<div style="padding:11px;background:#e4f4f0;border:1px solid #b8dbd2;border-radius:9px"><strong>Network Overview Telemetry</strong><div style="font-size:.82rem">Measured KPIs and network performance</div></div>
<div style="padding:11px;background:#e4f4f0;border:1px solid #b8dbd2;border-radius:9px"><strong>Network Event Telemetry</strong><div style="font-size:.82rem">Recorded events and operational context</div></div>
</div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ evidence returns to the localisation agent ↓</div>
<div style="max-width:710px;margin:auto;text-align:center;padding:11px;border-radius:10px;background:#174b62;color:#fff"><strong>2. Assessment, Fault Localisation &amp; Routing</strong><div style="font-size:.82rem;color:#ddf4fa">Evaluate incident materiality and affected site, cell or CU domain</div></div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ conditional investigation route ↓</div>
<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;max-width:850px;margin:auto">
<div style="padding:11px;border-radius:9px;background:#e4f4ed;border:1px solid #9ccab4"><strong>Healthy network</strong><div style="font-size:.82rem">Direct Supervisor review; no specialist escalation</div></div>
<div style="padding:11px;border-radius:9px;background:#fef2df;border:1px solid #e8c68d"><strong>Material incident</strong><div style="font-size:.82rem">Sequential specialist analysis (cell/site recordings) or CU-domain analysis; investigate tools, measurements and competing causes</div></div>
</div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓ investigation evidence ↓</div>
<div style="max-width:710px;margin:auto;text-align:center;padding:11px;border-radius:10px;background:#173d53;color:#f4fcff"><strong>3. RCA Supervisor &amp; Evidence Synthesis</strong><div style="font-size:.82rem;color:#d3eaf0">Correlates agent results; uses Curated Telecom Knowledge Base when needed to assess fault mechanisms and hypotheses</div></div>
<div style="text-align:center;color:#36627b;font-size:1.4rem;line-height:1.5">↓</div>
<div style="max-width:710px;margin:auto;text-align:center;padding:12px;border-radius:10px;background:#0f6159;color:#fff"><strong>4. Evidence-Grounded Root Cause Analysis</strong><div style="font-size:.82rem;color:#e1f8f4">Supported diagnosis · affected network scope · causal reasoning · uncertainties · recorded execution time</div></div>
</div>""",unsafe_allow_html=True)
    st.caption('The two ML models are tools called by the Localisation Agent, not independent agents. In V1 this is replayed from recorded synthetic-network investigations, not a live network scan.')


def render_solution_intro(cases, include_architecture=True):
 """Measured visitor milestones; one SP01 completion, not separate latency clocks."""
 b = benchmark_summary(cases)
 st.markdown("""<div style="font-size:1.01rem;line-height:1.5;margin:.15rem 0 .65rem">
 <strong>From complex network investigations to evidence-grounded RCA in under five minutes.</strong>
 Telecom fault diagnosis often involves manually correlating performance counters, alarms, configuration,
 and multi-domain telemetry. TEAD AI demonstrates how ML-assisted localisation, conditional LangGraph
 orchestration, specialist engineering analysis, and knowledge-grounded Supervisor reasoning can produce
 a traceable RCA conclusion. The experimental architecture illustrates a pathway to <strong>faster engineering decisions and governed autonomous-network operations</strong>; production benefits remain unvalidated.
 <br><br><strong>What is this?</strong> An experimental 5G investigation system evaluated on
 <strong>nine completed synthetic-network scenarios</strong> (eight incidents and one healthy control).
 The public site shows inspectable <strong>recorded executions</strong>, not live network diagnosis.
 </div>""", unsafe_allow_html=True)
 st.markdown('**Demonstrated investigation milestones**')
 x,y,z = st.columns(3)
 facts = [
  (x, '< 25 sec', 'Assess network health',
   f"SP01 assessment • {b['health_assessment_under_25sec']}/{b['health_assessment_total']} recorded scenarios"),
  (y, f"{b['localisation_under_25sec']}/{b['localisation_total']}", 'Localise affected scope',
   'Incident cases • same SP01 execution (under 25 sec)'),
  (z, '< 5 min', 'Evidence-grounded RCA',
   f"Full incident investigation • {b['incident_rca_under_5min']}/{b['incident_total']} incident scenarios"),
 ]
 for col,num,title,detail in facts:
  with col:
   st.markdown(f'<div class="ops-milestone"><div class="number">{escape(str(num))}</div><div class="label">{escape(title)}</div><div class="detail">{escape(detail)}</div></div>',unsafe_allow_html=True)
 st.caption('SP01 took 15.0–24.3 seconds across nine recorded synthetic-network scenarios. Health assessment and initial affected-scope localisation share the same SP01 completion timestamp; they are not independent timed milestones. The eight incident RCA results completed in under five minutes. These observations are not production SLAs or validated MTTR savings.')
 if include_architecture:
  architecture_diagram()


def render_value_proposition():
 st.markdown("""<div class="ops-value"><strong>From network data to actionable engineering intelligence</strong>
 <p><b>Detect faster. Localise intelligently. Diagnose with evidence.</b> The demonstration illustrates how
 agent-led ML and telemetry assessment, coordinated specialist investigations and knowledge-grounded
 Supervisor reasoning could reduce manual evidence correlation, improve diagnostic consistency and
 make specialist expertise more accessible.</p>
 <p>Production MTTR, OPEX reduction, remediation and sustained monitoring outcomes require validation in an operating network;
 this is a recorded, inspectable investigation demonstration, not an operational SLA.</p></div>""",unsafe_allow_html=True)


def cockpit_activity_html(beat, stage, total):
    """Compact, source-grounded input/action/output cards for the visible cockpit.

    This is display-only. Full saved text remains in the inspector below.
    """
    labels=(('input','INCOMING / HANDOVER','input'),
            ('action','AGENT ACTION / TOOL','action'),
            ('output','RECORDED RESULT','output'))
    cards=[]
    for kind,label,field in labels:
        value=' '.join(friendly_replay_text(beat.get(field) or 'No separate field recorded for this stage.').split())
        # Clamp the HTML payload as well as the visible two-line text; full original
        # content is available below, and huge agent prompts need not enter the cockpit DOM.
        short=value if len(value)<=360 else value[:359].rsplit(' ',1)[0].rstrip()+'…'
        cards.append(f'<div class="cockpit-evidence {kind}"><div class="tag">{label}</div>'
                     f'<div class="value" title="{escape(short,quote=True)}">{escape(short)}</div></div>')
    return (f'<section class="cockpit-activity" aria-label="Recorded stage evidence">'
            f'<div class="cockpit-activity-head">{escape(agent_label(beat["agent"]))}'
            f'<small>Step {stage}/{total}</small></div>'
            f'<div class="cockpit-activity-cards">{"".join(cards)}</div>'
            '<div class="cockpit-show-more">Full messages and tool evidence below · source records unchanged</div></section>')


def cockpit_status_html(item, case, status, alert, durations, elapsed, current_offset):
    """One compact status strip in place of a full-page hero plus four metrics."""
    return (f'<section class="cockpit-status" aria-label="Current recorded investigation status">'
            f'<div><div class="overline">{escape(item["act"])} · RECORDED INVESTIGATION</div>'
            f'<div class="name">{escape(case["title"])}</div>'
            f'<div class="detail">{escape(case["scenario_id"])} · {escape(status)}</div></div>'
            '<div class="right">'
            f'<div class="stat"><b>{escape(format_clock(elapsed))}</b><span>Viewing timer</span></div>'
            f'<div class="stat"><b>{escape(format_clock(durations["sp01"]))}</b><span>Original SP01</span></div>'
            f'<div class="stat"><b>{escape(format_clock(durations["total"]))}</b><span>Original total</span></div>'
            f'<div class="stat"><b>{escape(format_clock(current_offset))}</b><span>Trace offset</span></div>'
            f'<span class="flag{" alert" if alert else ""}">{escape(status)}</span></div></section>')

def _seek_from_widget(player_key, seek_key, last):
    """Consume a current slider event, never one from a retired replay instance.

    A reset remounts the scene slider under a new generation. This guard
    prevents an in-flight update from the old component reinstating a terminal
    scene after the user's Restart click.
    """
    play = st.session_state[player_key]
    if player_key.startswith('ops_player_'):
        generation = int(play.get('seek_generation', 0))
        active_seek = player_key + '_seek' + ('_' + str(generation) if generation else '')
        if seek_key != active_seek:
            return
    index = int(st.session_state[seek_key])
    play['index'] = max(0, min(last, index))
    if 'started' in play:  # Guided demo: seeking reveals the chosen recorded scene.
        play['started'] = True
    play['playing'] = False
    play['last_tick'] = time.monotonic()
    if 'carry' in play:
        play['carry'] = 0.


def _set_playhead(play, seek_key, index, last):
    """Synchronise the widget only when a playback control advances position."""
    play['index'] = max(0, min(last, int(index)))
    st.session_state[seek_key] = play['index']


@st.fragment(run_every='1s')
def cinematic_replay(sid):
 """Autoplay of saved evidence only. A refresh advances one authored beat, not a live run."""
 c=load_case(sid)
 beats=load_storyboard(sid)
 key='cinema_'+sid
 if key not in st.session_state:
  st.session_state[key]={'index':0,'playing':False,'seconds':16,'last_tick':time.monotonic()}
 player=st.session_state[key]
 last=len(beats)-1
 seek_key='cinema_seek_'+sid
 if seek_key not in st.session_state:st.session_state[seek_key]=player['index']
 now=time.monotonic()
 if player['seconds']==0:player['playing']=False  # Manual step mode
 if player['playing'] and now-player['last_tick']>=player['seconds']:
  _set_playhead(player,seek_key,player['index']+1,last)
  player['last_tick']=now
  if player['index']==last:player['playing']=False

 ctrl=st.columns([1.25,.9,.85,.85,1.6])
 with ctrl[0]:
  if st.button('⏸ Pause' if player['playing'] else '▶ Play',type='primary',use_container_width=True,key='cinema_play_'+sid,disabled=player['seconds']==0):
   if not player['playing'] and player['index']==last:_set_playhead(player,seek_key,0,last)
   player['playing']=not player['playing']; player['last_tick']=time.monotonic()
   st.rerun(scope='fragment')
 with ctrl[1]:
  if st.button('◀ Back',disabled=player['index']==0,use_container_width=True,key='cinema_back_'+sid):
   player['playing']=False;_set_playhead(player,seek_key,player['index']-1,last);player['last_tick']=time.monotonic();st.rerun(scope='fragment')
 with ctrl[2]:
  if st.button('Next ▶',disabled=player['index']==last,use_container_width=True,key='cinema_next_'+sid):
   player['playing']=False;_set_playhead(player,seek_key,player['index']+1,last);player['last_tick']=time.monotonic();st.rerun(scope='fragment')
 with ctrl[3]:
  if st.button('↺ Restart',use_container_width=True,key='cinema_restart_'+sid):
   _set_playhead(player,seek_key,0,last);player['playing']=False;player['last_tick']=time.monotonic();st.rerun(scope='fragment')
 with ctrl[4]:
  pace_options=[8,16,30,60,120,0]
  speed=st.selectbox('Reading pace',pace_options,
                     index=pace_options.index(player['seconds']) if player['seconds'] in pace_options else 1,
                     format_func=lambda v:'Manual · Back / Next' if v==0 else f'{v}s to read each recorded event',
                     key='cinema_speed_'+sid)
  if speed!=player['seconds']:
   player['seconds']=speed;player['last_tick']=time.monotonic()
   if speed==0:player['playing']=False

 st.slider('Presentation timeline',min_value=0,max_value=last,format='%d',key=seek_key,
           on_change=_seek_from_widget,args=(key,seek_key,last))
 idx=player['index']
 beat=beats[idx]
 st.progress((idx+1)/len(beats),text=f'PLAYBACK {idx+1} / {len(beats)}  •  {"PLAYING" if player["playing"] else "PAUSED"}  •  {agent_label(beat["agent"])}')
 # The route remains unknown until the original SP01 routing result appears.
 route_known=any(b['agent']=='SP01' and b['kind'] in ('decision','handover') for b in beats[:idx+1])
 previously_seen=[b['agent'] for b in beats[:idx+1]]
 st.markdown(connected_agent_html(c,beat['agent'],previously_seen,route_unlocked=route_known,
             mode='Recorded event',position_label=f'Event {idx+1}/{len(beats)}'),unsafe_allow_html=True)
 # A nearby control row stays accessible while the visitor reads the active agent.
 rback,rnext,rpause=st.columns(3)
 with rback:
  if st.button('◀ Previous event',key='cinema_readback_'+sid,disabled=idx==0,use_container_width=True):
   player['playing']=False;_set_playhead(player,seek_key,idx-1,last);st.rerun(scope='fragment')
 with rnext:
  if st.button('Next recorded event ▶',key='cinema_readnext_'+sid,disabled=idx==last,use_container_width=True):
   player['playing']=False;_set_playhead(player,seek_key,idx+1,last);st.rerun(scope='fragment')
 with rpause:
  if st.button('⏸ Pause reading',key='cinema_readpause_'+sid,disabled=not player['playing'],use_container_width=True):
   player['playing']=False;st.rerun(scope='fragment')
 with st.expander('View complete recorded agent route',expanded=False):
  st.html(workflow_overview_html(beats,idx))
  embed_workflow_html(workflow_svg(c['route_family'],beats,idx),height=250,scrolling=False)
 st.markdown(f'#### Recorded event {idx+1:02d} — {beat["title"]}')
 st.markdown(agent_context_html(beat,beats[idx+1] if idx<last else None,
                             heading='Active event · original recorded output'),unsafe_allow_html=True)
 panels=st.columns([1,1,1.12])
 with panels[0]:
  st.markdown('**📥 INPUT / HANDOVER**')
  st.info(beat['input'] or 'No separate input detail saved for this stage.')
 with panels[1]:
  st.markdown('**⚙️ AGENT ACTION / TOOL CALL**')
  st.write(beat['action'] or 'Recorded analysis stage.')
 with panels[2]:
  st.markdown('**📤 RECORDED OUTPUT / FEEDBACK**')
  st.success(beat['output'] or 'No separate output detail saved in this field.')
 if beat.get('timestamp'):
  st.caption('Original recorded tool start: '+nice_time(beat['timestamp']))
 st.caption('Provenance: '+beat['source']+(('  ·  Evidence ID: `'+beat['evidence_id']+'`') if beat['evidence_id'] else ''))
 if c['route_family']=='LOCAL_SPECIALISTS':
  st.caption('Recorded execution: the six cell/site specialists ran sequentially in this experiment. Parallel execution was deferred to avoid instability with large investigation inputs.')
 st.caption('Playback pacing is illustrative, not the original execution timing. Original node timestamps/durations are available under the technical stage inspector. No network scan, LLM, RAG, or tool call is executed here.')
 with st.expander('Original recorded source for the current beat'):
  stage=c['stages'][beat['stage_index']]
  st.markdown('**Saved stage:** '+stage['label']+' · `'+stage['key']+'`')
  if beat['evidence_id']:
   ev=load_evidence(sid,beat['evidence_id'])
   st.json({'tool':ev.get('tool'),'evidence_id':beat['evidence_id'],'result_keys':list((ev.get('result') or {}).keys()) if isinstance(ev.get('result'),dict) else [],'source_stage':ev.get('stage')},expanded=False)
   st.caption('Large recorded tool responses remain accessible on Engineering Evidence rather than rendered unfiltered here.')
  else:
   st.json(c['stage_data'][stage['key']],expanded=False)
 if beat['agent']=='FINAL':
  if st.button('Open Root Cause Analysis →',key='cinema_rca_'+sid):
   st.session_state['requested_page']='Root Cause Analysis';st.rerun()


# Guided operations presentation: all inputs and outputs are frozen trace records.
# This fragment is a media player, never a monitor, a model invocation or an agent run.
def guided_sp01_cards(sid, unlocked):
    cases = load_case(sid)
    labels = [
        ('ml_specialist_summary', 'ML 01 · Fault family', 'WHAT'),
        ('ml_scope_probabilities', 'ML 02 · Affected scope', 'WHERE'),
        ('telemetry_network_overview', 'Network Overview Telemetry', 'KPI evidence'),
        ('telemetry_events', 'Network Event Telemetry', 'Event evidence'),
    ]
    cols=st.columns(4)
    for col,(tool,title,hint) in zip(cols,labels):
        e=next((x for x in cases['evidence_index'] if x['stage']=='SP01' and x['tool']==tool), None)
        visible=tool in unlocked and e is not None
        value='Awaiting Localisation Agent'; desc='Recorded tool not yet presented'
        if visible:
            payload=load_evidence(sid,e['evidence_id'])['result']
            if tool=='ml_specialist_summary':
                hit=payload.get('top_fault_family') or {}
                value=pretty(hit.get('label'))
                desc=f"ML score {float(hit.get('probability',0)):.1%} · uncalibrated"
            elif tool=='ml_scope_probabilities':
                hits=payload.get('ranked_scopes') or []
                value=pretty(hits[0].get('label')) if hits else 'No scope predicted'
                desc=(f"ML score {float(hits[0].get('probability',0)):.1%} · uncalibrated" if hits else 'Not recorded')
            elif tool=='telemetry_network_overview':
                rows=payload.get('subnetwork_kpis') or []
                value=f'{len(rows)} KPI observations'
                desc='Recorded 15-minute PM measurements'
            else:
                events=payload if isinstance(payload,list) else payload.get('events',[])
                value=f'{len(events)} returned events'
                desc='Recorded event telemetry (zero is a valid result)'
        with col:
            st.markdown(f"""<div class="ops-kpi"><div class="name">{escape(title)}</div>
              <div class="value">{escape(value)}</div><div class="desc">{escape(desc)}</div> </div>""",unsafe_allow_html=True)
    st.caption('These are outputs called by the Network Health & Localisation Agent. The two ML prediction outputs do not independently initiate investigations; their probabilities are supporting, uncalibrated evidence.')


def guided_agent_drilldown(case, current_agent, current_beat):
    sid=case['scenario_id']
    agents=available_agents(case)
    if not agents:return
    with st.expander('🔎 Engineer drill-down — inspect any recorded agent, its tools and outputs',expanded=False):
        st.caption('All panels inspect stored execution records. Choosing an agent does not start a new investigation.')
        follow='↪ Follow highlighted agent'
        choice=st.selectbox('Agent to inspect',[follow]+agents,
                          format_func=lambda a:a if a==follow else agent_label(a,include_id=True),
                          key='ops_agent_pick_'+sid)
        pick=(current_agent if current_agent in agents else 'SUPERVISOR') if choice==follow else choice
        src_stages=[s for s in case['stages'] if s['agent']==pick]
        st.markdown('**Original analytical stages · '+agent_label(pick,include_id=True)+'**')
        current_index=current_beat['stage_index']
        matching_key=case['stages'][current_index]['key'] if current_index < len(case['stages']) else None
        default_stage=next((i for i,v in enumerate(src_stages) if v['key']==matching_key),0)
        stage=st.selectbox('Saved stage',src_stages,index=default_stage,
                           format_func=lambda x:x['label'],
                           key='ops_stage_pick_'+sid+'_'+pick+(('_follow_'+str(current_index)) if choice==follow else ''))
        data_field_sections(case['stage_data'][stage['key']],show_json=True)
        if pick=='SUPERVISOR' and stage['key']=='supervisor_output':
            render_kb_contribution(case['stage_data']['supervisor_output'])
        evs=[e for e in case['evidence_index'] if e['stage']==pick]
        if evs:
            st.markdown('**Agent-initiated tool calls and recorded replies**')
            e=st.selectbox('Evidence artifact',evs,
                format_func=lambda v:display_tool_name(v['tool'])+' · '+v['evidence_id'][-8:],
                key='ops_evidence_pick_'+sid+'_'+pick)
            payload=load_evidence(sid,e['evidence_id'])
            st.info(evidence_preview(e,payload))
            with st.expander('Evidence metadata and safe data preview'):
                st.json({'tool':display_tool_name(e['tool']),'source_tool_identifier':e['tool'],
                         'evidence_id':e['evidence_id'],'reason':e.get('reason'),
                         'result_keys':list(payload.get('result',{}).keys()) if isinstance(payload.get('result'),dict) else [],
                         'stored_data_type':type(payload.get('result')).__name__},expanded=False)
                st.caption('For complete KPI measurements, source series, and evidence IDs use Engineering Evidence. Third-party retrieved knowledge passages are not in this public dataset.')
        agent_nodes=[n for n in case['observed_nodes'] if n['name']==pick and n.get('depth')==1]
        if agent_nodes:
            n=agent_nodes[0]
            st.caption(f"Saved {agent_label(pick)} execution: {format_duration(n.get('duration_seconds'))} · {nice_time(n.get('start_time'))} to {nice_time(n.get('end_time'))}")


def _restart_guided_player(player_key):
    """Atomically reset the guided player *before* Streamlit redraws widgets.

    Streamlit button callbacks run before the next script/fragment render. This
    is intentionally a replacement state object with a new slider identity:
    neither a stale mounted seek value nor an old mutable player reference may
    bring a completed state back after Reset.
    """
    previous = st.session_state[player_key]
    previous_generation = int(previous.get('seek_generation', 0))
    previous_seek = player_key + '_seek' + ('_' + str(previous_generation) if previous_generation else '')
    if previous_seek in st.session_state:
        # Callback executes before UI instantiation; retiring widget state is safe.
        st.session_state[previous_seek] = 0
    st.session_state[player_key] = {
        'index': 0, 'playing': False, 'seconds': previous['seconds'],
        'last_tick': time.monotonic(), 'carry': 0.,
        'presentation_elapsed': 0., 'started': False,
        'seek_generation': int(previous.get('seek_generation', 0)) + 1,
    }


def _activate_guided_context(selected_sid, player_sid, include_healthy, executive):
    """A newly selected Guided journey starts Ready, even if previously visited.

    Player state is keyed by recording and viewing mode so normal rerenders and
    visits to other application pages can preserve a paused presentation. The
    old behaviour also reused *stale* scene positions when visitors changed
    scenario or presentation and returned to a prior recording. Detect a real
    selection-context transition before mounting the player fragment and reset
    the destination's cached player with the existing generation-safe Restart
    operation. This also protects against late events from its retired slider.
    """
    context = (selected_sid, player_sid, bool(include_healthy), bool(executive))
    previous = st.session_state.get('ops_guided_active_context')
    if previous is not None and previous != context:
        key = ('ops_player_' + player_sid + '_' + str(include_healthy)
               + ('_executive' if executive else ''))
        if key in st.session_state:
            _restart_guided_player(key)
    st.session_state['ops_guided_active_context'] = context


@st.fragment(run_every='1s')
def guided_operations_player(selected_sid, include_healthy, executive=False):
    """V1.7.0 staged story of independent saved traces, not a live network simulation.

    Compatibility: uses the same recorded playlist, player key structure, slider
    callback, complete-route inspector, and original evidence drill-down.
    """
    healthy_sid='M05I0017'
    healthy=load_case(healthy_sid)
    incident=load_case(selected_sid)
    timeline=guided_sequence(healthy,load_storyboard(healthy_sid),
        incident if selected_sid!=healthy_sid else None,
        load_storyboard(selected_sid) if selected_sid!=healthy_sid else [],
        include_healthy=include_healthy or selected_sid==healthy_sid)
    if executive:
        timeline=executive_sequence(timeline)
    if not timeline:
        st.warning('No recorded investigation selected.')
        return
    key='ops_player_'+selected_sid+'_'+str(include_healthy)+('_executive' if executive else '')
    if key not in st.session_state:
        st.session_state[key]={'index':0,'playing':False,'seconds':18 if executive else 22,
                               'last_tick':time.monotonic(),'carry':0.,
                               'presentation_elapsed':0.,'started':False}
    play=st.session_state[key]
    last=len(timeline)-1
    seek_key=key+'_seek'+('_'+str(play['seek_generation']) if play.get('seek_generation',0) else '')
    if seek_key not in st.session_state:
        st.session_state[seek_key]=play['index']
    now=time.monotonic()
    previous_index=play['index']
    boundary_index=next((i for i in range(len(timeline)-1)
        if timeline[i]['scenario_id']!=timeline[i+1]['scenario_id']),None)
    # Final recorded RCA is a terminal view: do not accrue presentation time
    # or restart it implicitly after arriving at the final scene.
    if play['playing'] and play['index']>=last:
        play['playing']=False
        play['carry']=0.
    # Explicit comparison boundary: never advance into the second trace automatically.
    if play['playing'] and boundary_index is not None and play['index']==boundary_index:
        play['playing']=False
        play['carry']=0.
    if play.get('seconds')==0:play['playing']=False  # Manual step mode
    if play['playing']:
        play['started']=True
        dt=max(0.,min(now-play['last_tick'],3.))
        play['carry']+=dt
        play['presentation_elapsed']+=dt
        while play['index']<last:
            current_kind=timeline[play['index']]['beat']['kind']
            hold=play['seconds'] * (1.0 if executive else
                (1.5 if current_kind in {'decision','rag','feedback','handover','report'} else 1.0))
            if play['carry']<hold:
                break
            # Never automatically blur the boundary between separate recordings.
            if boundary_index is not None and play['index']==boundary_index:
                play['playing']=False
                play['carry']=0.
                break
            play['carry']-=hold
            play['index']+=1
        if play['index']>=last:
            play['playing']=False
            play['carry']=0.
    if play['index']!=previous_index:
        _set_playhead(play,seek_key,play['index'],last)
    play['last_tick']=now

    # Controls are above the evidence; one identifiable result changes per scene.
    controls=st.columns([1.1,.85,.85,.9,1.45])
    with controls[0]:
        if st.button('✓ Completed · Restart to replay' if play.get('started') and play['index']==last else
                     '⏸ Pause' if play['playing'] else '▶ Play',type='primary',
                     disabled=(play.get('started') and play['index']==last) or play['seconds']==0,
                     use_container_width=True,key=key+'_play'):
            if boundary_index is not None and play['index']==boundary_index and play.get('started'):
                play['playing']=False
            else:
                play['started']=True
                play['playing']=not play['playing']
            play['carry']=0.
            play['last_tick']=time.monotonic()
            st.rerun(scope='fragment')
    with controls[1]:
        if st.button('◀ Back',disabled=not play.get('started') or play['index']==0,
                     use_container_width=True,key=key+'_back'):
            play['playing']=False
            _set_playhead(play,seek_key,play['index']-1,last)
            play['carry']=0.
            st.rerun(scope='fragment')
    with controls[2]:
        if st.button('Next ▶',disabled=play.get('started') and play['index']==last,
                     use_container_width=True,key=key+'_next'):
            play['playing']=False
            if not play.get('started'):
                play['started']=True
            elif boundary_index is None or play['index']!=boundary_index:
                _set_playhead(play,seek_key,play['index']+1,last)
            play['carry']=0.
            st.rerun(scope='fragment')
    with controls[3]:
        if st.button('↺ Restart',use_container_width=True,key=key+'_restart',
                     on_click=_restart_guided_player,args=(key,)):
            # A *full-app* rerun remounts the scene slider and controls after
            # the callback's atomic reset. Fragment-only resets occasionally
            # left the old completed widgets mounted in live Cloud sessions.
            st.rerun()
    with controls[4]:
        speeds=[8,12,18,30,60,120,0] if executive else [10,15,22,40,75,120,0]
        speed=st.selectbox('Reading pace',speeds,
                           index=speeds.index(play['seconds']) if play['seconds'] in speeds else 2,
                           format_func=lambda x:'Manual · Back / Next' if x==0 else f'{x}s to read a scene',
                           key=key+'_pace')
        if speed!=play['seconds']:
            play['seconds']=speed
            if speed==0:play['playing']=False
            play['carry']=0.

    # Preserved seek callback and stage inspector; collapsed to remove visual competition.
    with st.expander('Jump to a recorded scene',expanded=False):
        st.slider('Playback position',min_value=0,max_value=last,key=seek_key,
                  on_change=_seek_from_widget,args=(key,seek_key,last))
        st.caption('Presentation scene numbers are not original LangSmith execution times.')
    idx=play['index']
    base=timeline[idx]
    sid=base['scenario_id']
    beat=base['beat']
    case=healthy if sid==healthy_sid else incident
    item=dict(base,case=case)
    ready=not play.get('started')
    phase,title,why=phase_for(item)
    if ready:
        name='Ready to start'
    elif beat['agent']=='FINAL':
        name='Recorded investigation complete'
    else:
        name=title
    original=get_run_durations(case)
    st.markdown(
        '<div class="gs-status"><div><span class="gs-status-small">'
        +escape('RECORDING A · HEALTHY CONTROL' if sid==healthy_sid else
                'RECORDING B · SEPARATE INCIDENT' if include_healthy and selected_sid!=healthy_sid else
                'RECORDED INCIDENT')
        +'</span><b>'+escape(case['title'])+'</b><span class="gs-status-desc">'
        +escape(name+' · '+case['scenario_id'])+'</span></div>'
        +'<div class="gs-duration"><strong>'+escape(format_clock(original['total']))
        +'</strong>Original recorded duration</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="gs-progress"><b>'+escape('Scene 0 · Ready' if ready else
        f'Chapter {phase}/{3 if not case["derived_display"]["incident_present"] else 6} · Overall scene {idx+1}/{len(timeline)}' if include_healthy and selected_sid!=healthy_sid else f'Chapter {phase}/{3 if not case["derived_display"]["incident_present"] else 6} · Scene {idx+1}/{len(timeline)}')+'</b><span>'
        +('PAUSED · Press Play to begin' if ready else
          'PLAYING · Next evidence will appear in sequence' if play['playing'] else
          'COMPLETED · Select Restart or review the RCA below' if play['index']==last else
          'PAUSED · Use Next to follow changes')+'</span></div>',unsafe_allow_html=True)
    # Separate view/presentation time from original recorded trace time; seek uses
    # saved timestamps only, and never fabricates an intermediate runtime marker.
    case_positions=[i for i,x in enumerate(timeline) if x['scenario_id']==sid]
    this_case_index=case_positions.index(idx)
    scene_pct=0 if ready else round(100*(this_case_index+1)/len(case_positions))
    original_offset=event_trace_offset(case,beat) if not ready else None
    if original_offset is None and not ready:
        for earlier in reversed(case_positions[:this_case_index+1]):
            value=event_trace_offset(case,timeline[earlier]['beat'])
            if value is not None:
                original_offset=value
                break
    if ready:
        time_marker='Awaiting first recorded marker'
    elif original_offset is None:
        time_marker='No exact marker for this scene'
    elif event_trace_offset(case,beat) is None:
        time_marker='Last recorded marker '+format_clock(original_offset)
    else:
        time_marker=format_clock(original_offset)+' elapsed in recorded run'
    st.markdown(
        '<section class="gs-timeline" aria-label="Presentation and recorded investigation progress">'
        '<div class="gs-timeline-stats">'
        '<span><b>SCENE PROGRESS</b> '+escape(f'{this_case_index+1 if not ready else 0}/{len(case_positions)} · {scene_pct}%')+'</span>'
        '<span><b>WATCH TIME</b> '+escape(format_clock(play['presentation_elapsed']))+'</span>'
        '<span><b>ORIGINAL TRACE</b> '+escape(time_marker)+' / '+escape(format_clock(original['total']))+'</span>'
        '</div><div class="gs-timeline-track" role="progressbar" aria-label="Recorded scene presentation progress" '
        'aria-valuenow="'+str(scene_pct)+'" aria-valuemin="0" aria-valuemax="100">'
        '<div class="gs-timeline-fill" style="width:'+str(scene_pct)+'%"></div></div>'
        '<div class="gs-timeline-note">Scene progress and watch time are presentation indicators; original trace time comes from recorded timestamps.</div>'
        '</section>',unsafe_allow_html=True)
    # Shared connected-agent map: do not reveal the route before SP01's
    # original saved decision/handover, and never join two independent traces.
    same_case_history=[x['beat'] for x in timeline[:idx+1]
                       if x['scenario_id']==sid] if not ready else []
    known_route=not ready and any(b['agent']=='SP01' and
        b['kind'] in ('decision','handover') for b in same_case_history)
    st.markdown(connected_agent_html(case,beat['agent'],
            [b['agent'] for b in same_case_history],route_unlocked=known_route,
            ready=ready,mode='Guided scene',
            position_label='Ready' if ready else f'Scene {this_case_index+1}/{len(case_positions)}'),
            unsafe_allow_html=True)
    # Reading controls immediately adjacent to the agent map.
    rback,rnext,rpause=st.columns(3)
    with rback:
        if st.button('◀ Previous scene',disabled=ready or idx==0,
                     use_container_width=True,key=key+'_readback'):
            play['playing']=False
            _set_playhead(play,seek_key,idx-1,last)
            play['carry']=0.;st.rerun(scope='fragment')
    with rnext:
        if st.button('Next recorded scene ▶',
                     disabled=(not ready and (idx==last or
                         (boundary_index is not None and idx==boundary_index))),
                     use_container_width=True,key=key+'_readnext'):
            play['playing']=False
            if not play.get('started'):
                play['started']=True
            elif boundary_index is None or play['index']!=boundary_index:
                _set_playhead(play,seek_key,idx+1,last)
            play['carry']=0.;st.rerun(scope='fragment')
    with rpause:
        if st.button('⏸ Pause reading',disabled=not play['playing'],
                     use_container_width=True,key=key+'_readpause'):
            play['playing']=False;play['carry']=0.;st.rerun(scope='fragment')
    # Preserve the original progressively revealed evidence and exact findings.
    st.markdown(board_html(item,timeline,idx,ready=ready),unsafe_allow_html=True)
    if not ready:
        next_in_case=next((x['beat'] for x in timeline[idx+1:]
                           if x['scenario_id']==sid),None)
        st.markdown(agent_context_html(beat,next_in_case,
                      heading='Current scene · original recorded evidence'),unsafe_allow_html=True)
    st.markdown(focus_html(item,idx+1,len(timeline),ready=ready),unsafe_allow_html=True)
    with st.expander('Original compact routing diagram',expanded=False):
        st.markdown(flow_html(item,timeline[:idx+1] if not ready else [],ready=ready),unsafe_allow_html=True)

    at_boundary=boundary_index is not None and idx==boundary_index and play.get('started')
    if at_boundary:
        st.markdown(boundary_html(healthy_sid,selected_sid),unsafe_allow_html=True)
        if st.button('Continue → Open the separate incident recording',type='primary',key=key+'_continue'):
            play['playing']=False
            play['carry']=0.
            play['presentation_elapsed']=0.
            _set_playhead(play,seek_key,boundary_index+1,last)
            st.rerun(scope='fragment')
    elif ready:
        st.markdown('<div class="gs-help"><b>Start here:</b> Press Play or Next. '
                    'Watch the route and evidence tiles highlight as each saved result arrives. '
                    'No live agents or network calls are started.</div>',unsafe_allow_html=True)

    st.caption('This is a narrated replay of saved synthetic-network experiments. '
               'The original run duration above is not the presentation playback timer. '
               'ML confidence values are uncalibrated supporting evidence, not network truth.')
    # Complete older technical views remain accessible instead of competing for attention.
    case_beats=load_storyboard(sid)
    active_index=next(i for i,b in enumerate(case_beats) if b['sequence']==beat['sequence'])
    with st.expander('View complete recorded agent route',expanded=False):
        st.html(workflow_overview_html(case_beats,active_index))
    with st.expander('Full current-stage messages and localisation evidence (click to inspect)',expanded=False):
        st.caption('Original trace provenance: '+beat['source']+
                   (' · '+beat['evidence_id'] if beat.get('evidence_id') else ''))
        st.markdown('**Incoming context / handover**')
        st.write(beat['input'] or 'No separate input recorded.')
        st.markdown('**Agent action / tool request**')
        st.write(beat['action'] or 'No action detail recorded.')
        st.markdown('**Recorded output / feedback**')
        st.write(beat['output'] or 'No output detail recorded.')
        if beat['agent']=='SP01' or any(x['scenario_id']==sid and
              x['beat']['agent']=='SP01' and x['beat']['kind']=='decision'
              for x in timeline[:idx+1]):
            st.markdown('**Network Health & Localisation Agent · Two ML predictions + two telemetry services**')
            unlocked=sp01_tools_unlocked(timeline,idx) if not ready else set()
            guided_sp01_cards(sid,unlocked)
            if 'telemetry_network_overview' in unlocked:
                with st.expander('📈 Inspect the recorded 15-minute accessibility trend (network telemetry)'):
                    network_chart(case)
    if case['route_family']=='LOCAL_SPECIALISTS':
        st.caption('The actual cell/site investigation ran SP02–SP07 sequentially. '
                   'Executive view selects representative recorded specialist findings; '
                   'Full Engineering replay preserves the complete director-cut sequence.')
    guided_agent_drilldown(case,beat['agent'],beat)
    if beat['agent']=='FINAL' and not ready:
        if st.button('View complete Root Cause Analysis →',key=key+'_rca'):
            st.session_state['selected_scenario']=sid
            st.session_state['requested_page']='Root Cause Analysis'
            st.rerun()


def _workspace_changed():
    """Record an explicit destination change, not a fragment refresh."""
    st.session_state['page_navigation_epoch'] = int(st.session_state.get('page_navigation_epoch', 0)) + 1
    st.session_state['page_navigation_pending'] = True


def _restore_destination_context():
    """Scroll the containing Streamlit app to its new page heading once.

    The HTML component has no network calls, no persistence, and no access to
    evidence. It only interacts with its own hosting page for scroll recovery.
    This is a presentational enhancement; browsers that restrict iframe parent
    access still display the native page and sidebar normally.
    """
    if not st.session_state.pop('page_navigation_pending', False):
        return
    epoch = int(st.session_state.get('page_navigation_epoch', 0))
    embed_workflow_html('''<script>
    (() => {
      const epoch = '__EPOCH__';
      const reset = () => {
        try {
          const host = window.parent;
          const doc = host.document;
          const candidates = [doc.scrollingElement,
            doc.querySelector('[data-testid="stAppViewContainer"]'),
            doc.querySelector('section.main'), doc.querySelector('main')];
          candidates.forEach(el => { if (el) el.scrollTop = 0; });
          host.scrollTo(0, 0);
        } catch (_) { /* browser sandbox may refuse parent access */ }
      };
      reset();
      requestAnimationFrame(reset);
      setTimeout(reset, 90);
    })();
    </script>'''.replace('__EPOCH__',str(epoch)), height=0, scrolling=False)


# Original presentation sections retained without altering source logic.

def _tc_legacy_rca():
 heading('Root Cause Analysis','This is the recorded Supervisor conclusion, not an independently inferred or regenerated RCA.')
 su=c['stage_data']['supervisor_output'];d=c['derived_display']
 render_rca_outcome(c)
 st.divider()
 with st.expander('Original detailed Supervisor diagnosis',expanded=False):
  st.write(su.get('diagnosis') or 'No material incident supported.')
 state_summary(c)
 if su.get('incident_present'):
  cl,cr=st.columns([1,1]);
  with cl:
   heading('Fault assessment')
   st.markdown('**Fault family**');st.write(pretty(su.get('root_cause_family')))
   st.markdown('**Root cause statement**');st.write((su.get('root_cause_assessment') or {}).get('root_cause','Not established'))
   st.markdown('**Recorded confidence class**');st.write((su.get('root_cause_assessment') or {}).get('confidence','Not recorded'))
   st.markdown('**Target component**');st.write(pretty(su.get('target_component')))
   st.markdown('**Affected domain**');st.write(pretty(su.get('target_cu_domain_id')))
   st.markdown('**Affected site(s)**');st.write(', '.join((su.get('final_scope') or {}).get('affected_sites') or []) or pretty(su.get('target_site_id')))
   if su.get('target_component_justification'):st.caption(su['target_component_justification'])
  with cr:
   heading('Supporting evidence')
   for row in su.get('supporting_evidence') or []:st.markdown('• '+str(row))
  st.divider();left,right=st.columns(2)
  with left:
   heading('Contradictory or alternative evidence')
   alt=su.get('contradictory_evidence') or []
   if alt:
    for v in alt:st.markdown('• '+str(v))
   else:st.write('No contradictory evidence listed in the final Supervisor record. Check specialist analysis for weakened hypotheses.')
  with right:
   heading('Residual uncertainty')
   for v in su.get('residual_uncertainty') or ['No residual uncertainty recorded.']:st.markdown('• '+str(v))
  heading('Engineering recommendations')
  for i,v in enumerate(su.get('recommendations') or [],1):st.markdown(f'**{i}.** {v}')
 else:
  st.success('The original Supervisor concluded that no material accessibility incident was supported by available recorded measurements.')
  for v in su.get('supporting_evidence') or []:st.markdown('• '+str(v))
 st.divider()
 render_kb_contribution(su)
 st.divider()
 heading('Investigation agents · execution time & tools',
         'Per-agent wall-clock execution and separately summed LLM invocation spans. Recorded cell/site specialist runs were sequential. Agent runtime includes tool and LLM work; do not confuse individual LLM spans with full-chain wall time.')
 records=agent_execution_rows(c)
 if records:
  shown=[{k:v for k,v in row.items() if k in ['Agent','Purpose','Agent runtime','LLM inference (spans)','Tools used']} for row in records]
  st.dataframe(pd.DataFrame(shown),hide_index=True,use_container_width=True)
  with st.expander('Specialist timing and tool attribution details'):
   for row in records:
    st.markdown(f"**{row['Agent']} · {row['Agent runtime']}** (original `{row['ID']}`)")
    st.caption(row['Purpose'])
    st.write(f"LLM inference: {row['LLM inference (spans)']} across {row['LLM calls']} recorded invocation(s). Tools: {row['Tools used']}.")
  st.caption('Wall-clock runtime is measured from each agent’s saved LangSmith chain. LLM inference is the sum of its recorded LLM spans, not the complete agent runtime; tool names correspond to saved evidence. Neither is an independent production latency benchmark.')
 with st.expander('Recorded Supervisor specialist agreement and scope'):
  st.json({'specialist_agreement':su.get('specialist_agreement'), 'final_scope':su.get('final_scope'),'time_windows':su.get('time_windows')},expanded=False)


def _tc_legacy_engineering():
 heading('Engineering Evidence Explorer','Review the source measurements that the completed investigation consulted. Values are preserved from the LangSmith tool outputs.')
 tab1,tab2,tab3=st.tabs(['Accessibility KPIs','Operational measurements','Evidence provenance'])
 with tab1:
  n=query_network(c)
  granularity=st.radio('Granularity',['Subnetwork (5QI)','NRCellDU/CU object (5QI)'],horizontal=True)
  metric=st.selectbox('Accessibility KPI',['partial_drb_accessibility_pct','total_drb_accessibility_pct'],format_func=lambda x:x.replace('_',' ').title())
  if granularity=='Subnetwork (5QI)':network_chart(c,metric)
  else:
   x=n.get('cell_kpis',{}); groups=x.get('groups',[]) if isinstance(x,dict) else []
   ids=sorted({g.get('static',{}).get('entity_id') for g in groups if g.get('static',{}).get('entity_id')})
   if ids:
    target=c['stage_data']['supervisor_output'].get('target_cells') or []
    preferred=target[0].get('nr_cell_cu_id') if target and isinstance(target[0],dict) else None
    sel=st.selectbox('NR CU cell',ids,index=ids.index(preferred) if preferred in ids else 0)
    qivals=sorted({g.get('static',{}).get('five_qi') for g in groups if g.get('static',{}).get('entity_id')==sel})
    qi=st.selectbox('5QI',qivals)
    g=next((a for a in groups if a.get('static',{}).get('entity_id')==sel and a.get('static',{}).get('five_qi')==qi),None)
    if g:
     df=pd.DataFrame({'interval_start_utc':g['timestamps'],metric:g['series'].get(metric,[])})
     df['interval_start_utc']=pd.to_datetime(df['interval_start_utc'],utc=True)
     f=go.Figure(go.Scatter(x=df['interval_start_utc'],y=df[metric],mode='lines+markers',name=metric))
     f.update_layout(height=300,template='plotly_white',margin={'l':8,'r':8,'b':10,'t':15},yaxis_title='Accessibility (%)',xaxis_title='UTC')
     st.plotly_chart(f,use_container_width=True)
     st.dataframe(df,hide_index=True,use_container_width=True)
    st.caption(f"Lossless columnar replay: {len(groups)} source groups, {x.get('source_row_count', '—')} original cell-KPI rows.")
  if n.get('events'):st.dataframe(pd.DataFrame(n['events']),hide_index=True,use_container_width=True)
 with tab2:
  available=[]
  for ev in c['evidence_index']:
   if ev['tool'].startswith('telemetry_') and ev['tool'] not in ['telemetry_network_overview','telemetry_topology','telemetry_events']:
    available.append(ev)
  if not available:st.info('No additional specialist telemetry requested in this healthy-control route.')
  else:
   selected=st.selectbox('Recorded telemetry tool',available,format_func=lambda e:agent_label(e['stage'])+' · '+display_tool_name(e['tool'])+' · '+str(e.get('reason') or 'recorded response')[:44]+' · '+e['evidence_id'][-7:])
   result=load_evidence(sid,selected['evidence_id'])['result']
   fields=[]
   if isinstance(result,dict):
    fields=[(k,v) for k,v in result.items() if isinstance(v,dict) and v.get('groups') is not None]
    if result.get('groups') is not None:fields=[('measurements',result)]+fields
   if fields:
    field_keys=[k for k,_ in fields]
    name=st.selectbox('Evidence dataset',field_keys)
    x=dict(fields)[name]
    groups=x.get('groups') or []
    if groups:
     allmetrics=sorted({(g.get('static') or {}).get('metric_name') for g in groups if (g.get('static') or {}).get('metric_name')})
     if allmetrics:
      metric=st.selectbox('Metric',allmetrics)
      gs=[g for g in groups if (g.get('static') or {}).get('metric_name')==metric]
     else:
      gs=groups
     names=[]
     for i,g in enumerate(gs):
      static=g.get('static') or {}
      labels=[f"{static.get('entity_id','object')}"]
      if static.get('operational_category'):labels.append(str(static['operational_category']))
      labels.append(f"source group {i+1}")
      names.append((' · '.join(labels),i))
     chosen=st.selectbox('Entity / recorded group',names,format_func=lambda z:z[0])
     g=gs[chosen[1]];static=g.get('static') or {}
     try:
      raw_df, partitions=partition_measurements(g)
     except ValueError as exc:
      st.error('Recorded group schema is not chart-safe: '+str(exc))
      st.stop()
     # Select a complete per-row dimensional identity, rather than assuming
     # every row in one encoded group belongs to a single continuous series.
     if not partitions:
      st.info('No recorded observations in the selected measurement group.')
      st.stop()
     options=list(range(len(partitions)))
     index=st.selectbox('Recorded series dimensions',options,format_func=lambda i:partitions[i]['label'])
     part=partitions[index]
     df=part['frame'].copy()
     st.caption(f"{part['label']} · {len(df)} original observations · {len(partitions)} distinct source series in this group. Dimensions come from recorded per-row columns.")
     quantitative=[k for k in ['value_float','value_int','value_bool','partial_drb_accessibility_pct','total_drb_accessibility_pct'] if k in df and pd.to_numeric(df[k],errors='coerce').notna().any()]
     if not part['safe_to_plot']:
      st.warning('Chart suppressed: more than one observation shares the same timestamp and full recorded dimensional identity. Source rows remain available for review; no aggregation or arbitrary line joining is performed.')
     elif quantitative:
      metric_value=st.selectbox('Value column',quantitative)
      plot_values=pd.to_numeric(df[metric_value],errors='coerce')
      fig=go.Figure(go.Scatter(x=pd.to_datetime(df['interval_start_utc'],utc=True),y=plot_values,
                              mode='lines+markers',name=part['label']))
      fig.update_layout(height=310,template='plotly_white',margin={'l':10,'r':10,'b':10,'t':15},
                        yaxis_title=static.get('unit') or metric_value,xaxis_title='UTC')
      st.plotly_chart(fig,use_container_width=True)
     else:
      st.info('State/categorical telemetry; source values shown in the table.')
     st.dataframe(df,hide_index=True,use_container_width=True)
     st.caption(f"Source: {selected['evidence_id']} · {x.get('representation','recorded data')} · {x.get('source_row_count','—')} source rows · {len(groups)} groups. No rows or dimensions were discarded or silently aggregated.")
     with st.expander('Recorded entity metadata'):st.json(static,expanded=False)
   else:
    st.caption('The selected tool returned structured recorded evidence rather than a columnar time series.')
    st.json(result,expanded=False)
 with tab3:
  st.write('**Data origin:** Frozen synthetic 5G RAN scenario processed in a completed LangGraph execution, exported from LangSmith.')
  st.dataframe(pd.DataFrame([{k:(display_tool_name(e.get(k)) if k=='tool' else e.get(k)) for k in ['stage','tool','evidence_id','compressed_bytes','reason']} for e in c['evidence_index']]),hide_index=True,use_container_width=True)
  v=st.selectbox('Inspect exact recorded tool response',c['evidence_index'],format_func=lambda e:e['stage']+' / '+display_tool_name(e['tool'])+' / '+e['evidence_id'][-9:])
  if v['tool']=='supervisor_private_knowledge_search':st.info('Only raw curated knowledge-base retrieval passages are withheld. The exact Supervisor query, mechanism reasoning, hypothesis comparison and observation checks are visible in Root Cause Analysis and the Supervisor final replay stage.')
  with st.expander('Raw recorded response (read-only)'):
   st.json(load_evidence(sid,v['evidence_id'])['result'],expanded=False)


def _tc_legacy_results():
 heading('Evaluation & Performance','Separate operational runtime measurements and trace integrity from post-run evaluations of the corresponding saved runs.')
 run=c['saved_postrun_evaluation'];a,b,d=st.columns(3)
 a.metric('Recorded trace duration',format_duration(c['trace_duration_seconds']))
 b.metric('LangSmith run nodes',len(c['observed_nodes']))
 d.metric('Recorded evidence artifacts',len(c['evidence_index']))
 st.divider();heading('Recorded execution profile')
 nodes=pd.DataFrame(c['observed_nodes'])
 x=nodes[(nodes['depth']==0) | (nodes['name'].isin(['SP01','SP02','SP03','SP04','SP05','SP06','SP07','SP08','SUPERVISOR']))]
 st.dataframe(x[['name','run_type','start_time','end_time','duration_seconds','total_tokens','total_cost']],hide_index=True,use_container_width=True)
 st.caption('Token and cost fields in the export are not reliable proof of original inference usage or zero cost. Treat missing/zero accounting as unavailable unless independently reconciled. Post-run exact-match and judge scores are reported from notebook exports; field-level comparison records and full judging rubric are not in this public replay, so displayed percentages are not independently reproducible here.')
 tokens=pd.to_numeric(nodes.loc[nodes['run_type']=='llm','total_tokens'],errors='coerce').dropna()
 if len(tokens):st.caption(f"Summed reported tokens across LLM node records (not a billing estimate): {int(tokens.sum()):,}.")
 else:st.caption('No complete per-LLM token counts were recorded in exported child nodes. No synthetic usage estimate is shown.')
 with st.expander('Cross-scenario phase timing breakdown (nine recorded runs)',expanded=False):
  phases=phase_execution_ranges([load_case(x) for x in manifest['scenario_order']])
  table=[]
  for record in phases['rows']:
   table.append({'Case':record['scenario_id'], 'Scenario':record['title'], 'SP01 (s)':round(record['sp01_seconds'],2) if record['sp01_seconds'] is not None else None,
                 'Specialists (s)':round(record['specialist_seconds'],2) if record['specialist_seconds'] is not None else None,
                 'Supervisor (s)':round(record['supervisor_seconds'],2) if record['supervisor_seconds'] is not None else None,
                 'Total (s)':round(record['end_to_end_seconds'],2)})
  st.dataframe(pd.DataFrame(table),hide_index=True,use_container_width=True)
  st.caption('Depth-one agent chain wall times from original traces; incident specialist time is the sum of sequential participating specialists. Per-phase extrema can belong to different runs. Root duration includes orchestration; judge assessment occurs later.')
 heading('Saved post-run notebook evaluation')
 if not run.get('matches_selected_trace_filename'):
  st.warning('The saved notebook export reference differs from the selected trace. Treat the evaluation as unmatched until reconciled.')
 else:st.info('The updated notebook references this same LangSmith export timestamp. This evaluation is a post-run assessment and was not available to agents during their investigation.')
 score1,score2,score3=st.columns(3)
 score1.metric('Post-run judge score',f"{run.get('judge_score_out_of_5'):.2f} / 5" if run.get('judge_score_out_of_5') is not None else '—')
 score2.metric('Post-run exact match',f"{run.get('structured_exact_match_rate')*100:.1f}%" if run.get('structured_exact_match_rate') is not None else '—')
 score3.metric('Post-run deterministic checks',pretty(run.get('deterministic_status')))
 st.caption(f"The selected {sid} post-run result reports "
            + (f"{run['structured_exact_match_rate']*100:.1f}% exact match" if run.get('structured_exact_match_rate') is not None else 'an unavailable exact-match rate')
            + '. The full field-level breakdown and judging rubric are not included in this saved export; the percentage does not establish independent real-network RCA accuracy.')
 st.write('**Post-run path check:** '+str(run.get('path_check'))+'  ·  **Supervisor schema:** '+str(run.get('supervisor_schema'))+'  ·  **Post-run judge status:** '+str(run.get('judge_status')))
 st.caption(f"Source: saved notebook cell {run.get('notebook_source_cell')}, reported trace export {run.get('reported_trace_basename')}")
 st.divider();heading('Source provenance & verification')
 st.markdown(f"**Trace ID:** `{c['trace_id']}`")
 st.markdown(f"**Export selected:** {nice_time(c['exported_at_utc'])}")
 st.markdown(f"**Source filename:** `{c['source_filename']}`")
 st.markdown(f"**Original source SHA-256:** `{c['source_sha256']}`")
 st.markdown(f"**Reported execution mode (original run):** `{c['recorded_execution_mode']}` — the present application is offline static replay.")
 st.markdown('**Original run status:** '+str(c['run_status']))
 warn=c.get('recorded_warnings') or {};n=sum(len(v) if isinstance(v,list) else 0 for v in warn.values());st.caption(f'{n} exported runtime warnings across recorded warning lists (expand for details).')
 with st.expander('Raw trace runtime warnings'):st.json(warn,expanded=False)
 st.divider();heading('Scope and controls')
 st.write('V1 replays original operational results without model inference or live telemetry. The original ML outputs are supporting probabilistic evidence and are explicitly uncalibrated; they are not ground truth. Post-run grading is never supplied to the replayed agentic decision stages.')
 st.caption('V2 (deferred) would require live retrieval/authentication, LangGraph execution, MCP adapters, access policies, observability, and cost controls. None are enabled in V1.')


# TEAD_EC_CLARITY_SEVEN_WORKSPACES_V1
st.markdown(EC_CLARITY_STYLE,unsafe_allow_html=True)
# TEAD_EC_REFERENCE_UX_C4 · E/C visual system on the new seven visitor workspaces
st.markdown(REFERENCE_CSS+EC_REF_EXTRAS,unsafe_allow_html=True)

# Scenario selection is persistent business state, not ephemeral widget state.
# Streamlit may delete a widget key when it disappears from a page.
manifest=load_manifest()
_valid_scenarios=manifest['scenario_order']
_default_scenario='M05I0003'

def sync_scenario_from(widget_key):
    candidate=st.session_state.get(widget_key)
    if candidate in _valid_scenarios:
        st.session_state['selected_scenario']=candidate

def sync_scenario_picker(widget_key):
    # Set widget values before drawing them, using the persistent scenario ID.
    canonical=st.session_state['selected_scenario']
    if st.session_state.get(widget_key)!=canonical:
        st.session_state[widget_key]=canonical

st.sidebar.markdown('### ◈ TEAD AI')
st.sidebar.caption('Agentic Network Investigation & RCA · Connected Agent UX preview')
st.sidebar.caption('Agentic Telecom Network Investigation & Root Cause Analysis (RCA)')
st.sidebar.caption(f'{RELEASE_VERSION} · build {release_build_id()} · {RELEASE_DATE}')
st.sidebar.divider()
if 'requested_page' in st.session_state:
    requested = st.session_state.pop('requested_page')
    requested = LEGACY_TO_WORKSPACE.get(requested, requested)
    if requested != st.session_state.get('nav_page'):
        st.session_state['page_navigation_epoch'] = int(st.session_state.get('page_navigation_epoch', 0)) + 1
        st.session_state['page_navigation_pending'] = True
    st.session_state['nav_page'] = requested
if st.session_state.get('selected_scenario') not in _valid_scenarios:
    st.session_state['selected_scenario']=_default_scenario
if 'nav_page' not in st.session_state:
    st.session_state['nav_page']='The Challenge'
# Seven clear workspaces; retain historical routes for test and deep-link compatibility.
page=st.sidebar.radio('Workspace',WORKSPACES,key='nav_page',on_change=_workspace_changed)
opts={x:f"{x} · {next(c['title'] for c in manifest['cases'] if c['scenario_id']==x)}" for x in _valid_scenarios}
sync_scenario_picker('sidebar_scenario_picker')
st.sidebar.selectbox('Select scenario ▾',options=_valid_scenarios,format_func=lambda x:opts[x],
                     key='sidebar_scenario_picker',on_change=sync_scenario_from,args=('sidebar_scenario_picker',))
render_sidebar_glossary(st)
sid=st.session_state['selected_scenario']
c=load_case(sid)
_restore_destination_context()
st.sidebar.divider()
st.sidebar.caption('RECORDED INVESTIGATION DEMO')
st.sidebar.caption('No live agents, telemetry, Large Language Model (LLM) calls, Application Programming Interface (API) keys or paid inference.')
st.sidebar.caption('Synthetic experimental network • not production operations')

def _ref_nav_changed():
 st.session_state['nav_page']=st.session_state['ref_nav_choice']
 _workspace_changed()

def _ref_evidence_banner(case):
 from html import escape as _e
 return ('<div class="case-banner"><strong>'+_e(str(case.get('scenario_id','—')))
         +' · '+_e(str(case.get('title','Recorded network investigation')))
         +'</strong><br>Original saved evidence; no live network actions.</div>')

if page in WORKSPACES:
 ref.brand(st)
 # E/C uses horizontal navigation as the primary visitor interaction.
 if st.session_state.get('ref_nav_choice')!=page:
  st.session_state['ref_nav_choice']=page
 st.radio('Explore',WORKSPACES,horizontal=True,key='ref_nav_choice',on_change=_ref_nav_changed)

if page not in ('Guided Operations Demo','Platform Overview','The Challenge','Architecture','Case Stories','Agent Flow','Evidence Room','Results'):
 st.markdown(f'''<div class="hero"><div class="eyebrow">TEAD AI · TELECOM ENGINEERING INTELLIGENCE</div><h1>TEAD AI — Agentic Telecom Network Investigation &amp; Root Cause Analysis</h1><div class="sub">Machine Learning (ML)-assisted network assessment · Multi-agent engineering investigation · Evidence-grounded RCA</div></div>''',unsafe_allow_html=True)

if page!='Guided Operations Demo':
 render_page_terms(st,page)

if page=='The Challenge':
 ref.challenge(st,[load_case(x) for x in manifest['scenario_order']])

elif page=='Network Overview':
 # Source-backed network-only introduction; agents live on Architecture.
 ref_inventory_id=manifest['scenario_order'][0]
 ref_case=load_case(ref_inventory_id)
 ref_topology_ref=evidence_by_tool(ref_case,'telemetry_topology')
 ref_entities=(load_evidence(ref_inventory_id,ref_topology_ref['evidence_id'])['result'].get('entities') or []) if ref_topology_ref else []
 ref_inventory=derive_inventory(ref_entities)
 st.markdown(NETWORK_STYLE,unsafe_allow_html=True)
 st.subheader('Recorded Network Topology')
 ref.network(st,ref_inventory,topology_html)
 # Original recorded agent-tool map is available but no longer duplicates
 # the default architecture narrative.
 with st.expander('Technical appendix · recorded agent tools',expanded=False):
  st.markdown('**Agent and Tool Capability Map**')
  ref_cases=[load_case(x) for x in manifest['scenario_order']]
  st.markdown(tools_html(observed_tools(ref_cases)),unsafe_allow_html=True)
 st.info('Next: open **Case Stories** to follow an incident, **Agent Flow** to see recorded handovers, or **Evidence Room** to inspect RCA and measurements.')

elif page=='Architecture':
 ref.architecture(st)
 with st.expander('Original comprehensive technical architecture and source attribution',expanded=False):
  render_investigation_flow()
  architecture_diagram()

elif page=='Case Stories':
 ref_choice=st.selectbox('Choose a recorded network investigation',options=_valid_scenarios,
           format_func=lambda v:opts[v],index=_valid_scenarios.index(sid),key='ref_case_stories')
 if ref_choice!=sid:
  st.session_state['selected_scenario']=ref_choice
  sid=ref_choice;c=load_case(sid)
 ref.story(st,c,load_storyboard(sid))

elif page=='Agent Flow':
 ref_choice=st.selectbox('Choose a recorded network investigation',options=_valid_scenarios,
           format_func=lambda v:opts[v],index=_valid_scenarios.index(sid),key='ref_agent_flow')
 if ref_choice!=sid:
  st.session_state['selected_scenario']=ref_choice
  sid=ref_choice;c=load_case(sid)
 ref.agent_flow(st,c,load_storyboard(sid),embed_workflow_html)

elif page=='Evidence Room':
 ref.evidence_intro(st)
 st.markdown(_ref_evidence_banner(c),unsafe_allow_html=True)
 evidence_view=st.radio('Choose evidence view',['RCA & diagnosis','Network measurements & provenance'],horizontal=True,key='tc_evidence_view')
 if evidence_view=='RCA & diagnosis':_tc_legacy_rca()
 else:_tc_legacy_engineering()

elif page=='Results':
 # TEAD_CANDIDATE4_1_TRACE_FAITHFUL_COPY — presentation-only results wiring
 ref.results_intro(st,[load_case(x) for x in manifest['scenario_order']])
 render_execution_performance([load_case(x) for x in manifest['scenario_order']])
 with st.expander('Original trace measurements, post-run evaluations and provenance',expanded=False):
  _tc_legacy_results()

if page=='Platform Overview':
 # The visitor journey is presentation only. It does not change replay data.
 intro_cases=[load_case(x) for x in manifest['scenario_order']]
 render_observatory_home(st,intro_cases)
 st.subheader('Choose your experience')
 st.caption('Follow a real recorded scenario in plain English, watch specialist handovers, or inspect the supporting engineering evidence.')
 b1,b2,b3=st.columns(3,gap='small')
 with b1:
  if st.button('▶ Watch the investigation',key='obs_watch',type='primary',use_container_width=True):
   st.session_state['selected_scenario']='M05I0003'
   st.session_state['requested_page']='Guided Operations Demo';st.rerun()
 with b2:
  if st.button('Explore the agent handovers →',key='obs_agents',use_container_width=True):
   st.session_state['selected_scenario']='M05I0005'
   st.session_state['requested_page']='Agentic Replay';st.rerun()
 with b3:
  if st.button('Inspect an evidence-backed RCA →',key='obs_rca',use_container_width=True):
   st.session_state['selected_scenario']='M05I0003'
   st.session_state['requested_page']='Root Cause Analysis';st.rerun()
 st.caption('The three shortcuts open completed recordings. They do not run live analysis or trigger network changes.')
 with st.expander('Measured milestones and detailed conditional architecture',expanded=False):
  heading('Discover TEAD AI','Evidence-grounded investigation and RCA in under five minutes — using recorded synthetic 5G experiments, not live production data.')
  render_solution_intro(intro_cases,include_architecture=False)
  render_investigation_flow()
  render_execution_performance(intro_cases)
 with st.expander('Detailed Architecture — original technical explanation (preserved)',expanded=False):
  architecture_diagram()
 with st.expander('Engineering learnings, value and limitations',expanded=False):
  render_platform_learnings()
  render_engineering_learnings()
  render_value_proposition()
  st.caption('Future development: live adapters, operational resilience, measured inference economics, evidence sufficiency and policy-bounded actions require separate testing before production claims.')

elif page=='Value Proposition & Solutions':
 render_value_solutions_page(st, [load_case(x) for x in manifest['scenario_order']])

elif page=='Guided Operations Demo':
 st.markdown('<span class="tread-guided-marker" aria-hidden="true"></span><div class="cockpit-kicker">TEAD AI · AGENTIC NETWORK INVESTIGATION</div><div class="cockpit-heading">Guided Operations Demo</div>',unsafe_allow_html=True)
 render_page_terms(st,page)
 main_sid=sid if sid!='M05I0017' else 'M05I0003'
 st.markdown('<div class="gs-intro">Follow one recorded fifth-generation (5G) network investigation from SP01 (Network Health & Localisation) through evidence arrival, conditional routing, specialist analysis and Supervisor Root Cause Analysis (RCA). <b>Nothing updates until you press Play or Next.</b></div>',unsafe_allow_html=True)
 mode_col,scene_col=st.columns([1,1],gap='small')
 with mode_col:
  experience=st.radio('Visitor experience',['Executive overview (key scenes)','Full engineering replay'],horizontal=True)
 with scene_col:
  if sid=='M05I0017':
   modes=['Healthy control only']
  else:
   modes=['Incident walkthrough (recommended)','Healthy control only','Compare healthy + separate incident']
  mode=st.radio('Presentation',modes,horizontal=True)
 if mode.startswith('Compare'):
  st.caption('**Two independent experimental recordings.** The healthy control is shown first; playback stops at an explicit boundary before the selected incident. These are not successive states of one live network.')
 elif mode=='Healthy control only':
  st.caption('**Healthy-network control · M05I0017.** This is a standalone saved execution with no material incident and no specialist escalation.')
 else:
  st.caption('**Selected synthetic incident: '+main_sid+'.** Follow only this recorded case. The four evidence tiles begin empty and reveal results in source order.')
 st.info('Explore a different recorded investigation with **Select scenario ▾** in the left sidebar. The replay will use that scenario’s original saved evidence and RCA; no live investigation is started.')
 player_sid='M05I0017' if mode=='Healthy control only' else main_sid
 include_healthy=mode=='Healthy control only' or mode.startswith('Compare')
 executive=experience.startswith('Executive')
 _activate_guided_context(sid,player_sid,include_healthy,executive)
 guided_operations_player(player_sid,include_healthy,executive=executive)
 with st.expander('About this demonstration and next steps',expanded=False):
  render_value_proposition()
  st.markdown('Open **Agentic Replay** for every recorded call, **Engineering Evidence** for Key Performance Indicator (KPI) series, **Root Cause Analysis** for diagnosis or **Evaluation & Performance** for trace measurements.')

elif page=='Network Overview':
 heading('Synthetic 5G Network Overview','The network model, its evidence sources and the agent/tool capabilities used in our recorded experiments. Detailed individual incident findings are in Scenario Library.')
 # All nine selected recordings carry identical topology inventories. Read the
 # first source directly, rather than inventing site, DU, CU or NR-cell IDs.
 reference_id=manifest['scenario_order'][0]
 reference_case=load_case(reference_id)
 topology_ref=evidence_by_tool(reference_case,'telemetry_topology')
 reference_entities=(load_evidence(reference_id,topology_ref['evidence_id'])['result'].get('entities') or []) if topology_ref else []
 inventory=derive_inventory(reference_entities)
 st.markdown(NETWORK_STYLE,unsafe_allow_html=True)
 st.subheader('Recorded Network Topology')
 st.caption('Ten modeled gNodeB sites, three logical NR cells per site, and shared CU-domain context. Object identities and logical relationships below come from the recorded topology service.')
 st.markdown(topology_html(inventory),unsafe_allow_html=True)
 st.caption('The nine scenarios represent independent synthetic network snapshots sharing this topology inventory. PM refers to performance-management telemetry; the reporting interval is documented in Engineering Evidence and source metadata.')
 st.divider()
 heading('Investigation evidence sources','Recorded PM and event telemetry, topology, radio, processing, transport and configuration observations are combined with supporting ML outputs and curated domain knowledge.')
 feeds=[
  ('Network & PM evidence','Accessibility KPIs · Network state · Cell and peer measurements'),
  ('Radio & resources','Radio state · Resource utilisation · Processing telemetry'),
  ('Transport & configuration','Transport interfaces · Configuration state · CU-domain/boundary state'),
  ('ML & domain knowledge','Fault family · Affected scope · Feature drivers · Curated telecom knowledge retrieval'),
 ]
 feed_html='<div class="ops-architecture">'+''.join(f'<div class="step"><strong>{escape(title)}</strong><span>{escape(desc)}</span></div>' for title,desc in feeds)+'</div>'
 st.markdown(feed_html,unsafe_allow_html=True)
 st.divider()
 heading('Agent and Tool Capability Map','Each agent is shown with evidence tools actually observed across the nine recorded experiments. This is a logical architecture overview, not live execution or a disclosure of private prompts.')
 recorded_cases=[load_case(x) for x in manifest['scenario_order']]
 toolmap=observed_tools(recorded_cases)
 st.markdown(tools_html(toolmap),unsafe_allow_html=True)
 st.caption('SP01 selects the investigation route. Cell/site incidents use SP02–SP07 sequentially, CU-domain cases use SP08 instead, and healthy cases go directly to Supervisor review. Not every agent or tool is invoked in every scenario.')
 with st.expander('Exact recorded agent → tool identifiers and provenance',expanded=False):
  rows=[{'Agent':a,'Role':AGENT_ROLES[a][0], 'Observed tool ID':t,'Visitor label':TOOL_NAMES.get(t,t)} for a, names in toolmap.items() for t in names]
  st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
  st.caption('Observed tool IDs originate from the nine frozen evidence indexes. Raw curated knowledge passages, model prompts and credentials are not distributed. For exact tool inputs/outputs, use Agentic Replay and Engineering Evidence.')
 st.info('Next: open **Case Stories** to understand an incident, **Agent Flow** to watch the actual handovers, or **Evidence Room** for recorded measurements and RCA.')

elif page=='Scenario Library':
 heading('Scenario Library','Choose one of the nine completed LangSmith investigations. All incident classifications below come from recorded Supervisor outputs.')
 sync_scenario_picker('library_case_selection')
 st.selectbox('Choose a recorded investigation',options=_valid_scenarios,
     format_func=lambda x:opts[x],key='library_case_selection',
     on_change=sync_scenario_from,args=('library_case_selection',))
 st.caption('One scenario is selected by default. Use the dropdown above to explore any of the nine completed cases.')
 left,right=st.columns([1,1.6]);d=c['derived_display']
 with left:
  st.caption('SELECTED INVESTIGATION')
  st.header(c['title'])
  st.caption('Trace reference: '+sid)
  st.markdown('**Recorded status:** '+run_badge(c))
  st.markdown('**Fault family:** '+pretty(d['fault_family']))
  st.markdown('**Affected scope:** '+pretty(d['scope_class']))
  st.markdown('**Incident window:** '+nice_time(d['incident_start_utc'])+' — '+nice_time(d['incident_end_utc']))
  st.markdown('**Scenario window:** '+nice_time(c['scenario_window'].get('window_start_utc'))+' — '+nice_time(c['scenario_window'].get('window_end_utc')))
  if st.button('Open agentic replay',type='primary',use_container_width=True):
   st.session_state['requested_page']='Agentic Replay';st.session_state['replay_'+sid]=0;st.rerun()
 with right:
  heading('Supervisor outcome')
  st.write(d.get('diagnosis') or 'No incident diagnosed.')
  st.markdown('**Execution route**')
  st.code(route_text(c),language=None)
  st.caption(f"{len(c['observed_nodes'])} recorded LangSmith run nodes · {len(c['evidence_index'])} distinct recorded evidence outputs")
  with st.expander('Original public investigation task'):
   st.write(c['scenario_window'].get('task','—'))
  st.info('This replay shows the outcome of an already completed investigation. Selecting another scenario does not execute a new investigation.')
 st.divider()
 heading('Selected Scenario — Recorded PM Evidence','Case-specific accessibility trends and original performance observations are reviewed here, rather than in the network-wide topology overview.')
 metric=st.radio('Recorded accessibility KPI', ['partial_drb_accessibility_pct','total_drb_accessibility_pct'],format_func=lambda v:v.replace('_',' ').title(),horizontal=True)
 network_chart(c,metric)
 st.divider()
 heading('Investigation Portfolio','Nine independent saved experimental scenarios; the results below are drawn from selected recorded outputs.')
 cases=manifest['cases']
 kb_map={x['scenario_id']:load_case(x['scenario_id'])['stage_data']['supervisor_output'].get('knowledge_base_contribution') or {} for x in cases}
 overview=pd.DataFrame([{'Case':x['scenario_id'],'Scenario':x['title'],'Incident':'Yes' if x['incident_present'] else 'No','Scope':x['scope_class'],'Fault family':x['fault_family'] or 'None','RAG contribution':pretty(kb_map[x['scenario_id']].get('contribution_type'),none='Not used'),'Recorded duration':format_duration(x['trace_duration_seconds'])} for x in cases])
 st.dataframe(overview,hide_index=True,use_container_width=True)
 st.caption(f"Recorded knowledge-base retrieval was used in {sum(bool(k.get('used')) for k in kb_map.values())} of {len(cases)} scenarios. This measures reported use, not improvements in RCA accuracy.")
 with st.expander('Selected case — Curated Telecom Knowledge Base contribution',expanded=False):
  selected_kb=c['stage_data']['supervisor_output'].get('knowledge_base_contribution') or {}
  if selected_kb.get('used'):
   st.write('The selected case used recorded knowledge retrieval to assess possible mechanisms. The original reasoning is available in Root Cause Analysis and the Supervisor stage of Agentic Replay.')
   for q in selected_kb.get('queries') or []:st.info(q)
   st.caption(f"Recorded contribution: {pretty(selected_kb.get('contribution_type'))} · evidence weight: {pretty(selected_kb.get('evidence_weight'))}. These are completed recorded lookups, not live RAG calls.")
  else:
   st.info('The selected scenario was investigated without a recorded knowledge-base lookup; none is fabricated.')

elif page=='Agentic Replay':
 heading('Agentic Investigation Replay','Technical drill-down of a completed investigation: original agent stages, routing, tool evidence and Supervisor RCA. For the narrated version, use Guided Operations Demo.')
 st.caption('Selected recorded case: **'+sid+' — '+c['title']+'**. Change the case with **Select scenario ▾** in the left sidebar; this does not trigger live inference.')
 mode=st.radio('Replay mode',['▶ Animated workflow','Recorded-stage inspector'],horizontal=True,key='replay_mode')
 if mode=='▶ Animated workflow':
  st.caption('Play or scrub through the original recorded investigation. A highlighted agent indicates the point being *presented*, not an active live process.')
  cinematic_replay(sid)
 else:
  heading('Recorded-stage inspector','Reveal the actual saved localisation, specialist, and Supervisor reasoning stages in sequence. This is navigation through recorded outputs—not rerunning models.')
  stages=c['stages']; key='replay_'+sid
  if key not in st.session_state:st.session_state[key]=0
  step=st.session_state[key];step=min(step,len(stages)-1)
  col1,col2,col3,col4=st.columns([.8,.8,4,.8])
  with col1:
   if st.button('◀ Previous',disabled=step==0,use_container_width=True):st.session_state[key]=step-1;st.rerun()
  with col2:
   if st.button('Next ▶',disabled=step>=len(stages)-1,use_container_width=True):st.session_state[key]=step+1;st.rerun()
  with col3:
   new=st.select_slider('Recorded stage',options=list(range(len(stages))),value=step,format_func=lambda i:f'{i+1:02d} — {stages[i]["label"]}')
   if new!=step:st.session_state[key]=new;st.rerun()
  with col4:st.metric('Stage',f'{step+1}/{len(stages)}')
  st.progress((step+1)/len(stages))
  st.write('**Recorded routing:** '+route_text(c))
  if c['route_family']=='LOCAL_SPECIALISTS':st.caption('The recorded cell/site investigation ran six specialist chains sequentially; the stage navigator follows the saved order.')
  active=stages[step];item=c['stage_data'][active['key']]
  st.subheader(f"{agent_label(active['agent'],include_id=True)}  /  {active['label']}")
  if active['key']=='sp01_evidence_cycle_1':
   st.write('The Network Health & Localisation Agent requested the following evidence before localising the suspected incident:')
   for name,v in item.items():st.markdown(f"• **{name}** · `{v.get('evidence_id')}`")
  elif active['key']=='supervisor_output':
   st.markdown('**Final recorded decision**')
   st.write(item.get('diagnosis') or 'No issue')
   st.markdown('**Fault family:** '+pretty(item.get('root_cause_family')))
   st.markdown('**Scope:** '+pretty(item.get('scope_class')))
   data_field_sections(item,show_json=True)
   st.divider()
   render_kb_contribution(item)
  else:
   data_field_sections(item,show_json=True)
  with st.expander('All recorded LangSmith nodes and timestamps'):
   df=pd.DataFrame(c['observed_nodes'])[['name','run_type','depth','start_time','duration_seconds','status','total_tokens','total_cost']]
   st.dataframe(df,hide_index=True,use_container_width=True,height=350)

elif page=='Root Cause Analysis':
 _tc_legacy_rca()

elif page=='Engineering Evidence':
 _tc_legacy_engineering()

elif page=='Evaluation & Performance':
 _tc_legacy_results()

st.divider()
if page in WORKSPACES: ref.footer(st)
st.caption('TEAD AI • RECORDED INVESTIGATION REPLAY • SYNTHETIC TEST NETWORK • ALL TIMESTAMPS IN UTC')
