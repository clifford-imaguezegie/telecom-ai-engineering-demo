"""UX-01: public, non-specialist terminology layer for the recorded TEAD AI demo.

This file only provides presentation text. No saved investigation data, evidence,
agent routing, playback state or external services are changed.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Term:
    full: str
    meaning: str
    category: str


# Standards-aligned technical expansions; avoid inventing an expansion for the
# TEAD AI product name or the SP01–SP08 recorded agent identifiers.
TERMS = {
    "5G": Term("Fifth-generation mobile network", "A generation of cellular technology; the demo uses a synthetic 5G network.", "Mobile network"),
    "AI": Term("Artificial Intelligence", "Software techniques that support tasks such as prediction and investigation.", "AI & evaluation"),
    "AMF": Term("Access and Mobility Management Function", "5G Core function handling access and mobility signalling.", "5G Core"),
    "API": Term("Application Programming Interface", "A defined way for software components to exchange requests and responses.", "Software & observability"),
    "BLER": Term("Block Error Rate", "Share of transmitted radio blocks received with errors before correction/retransmission.", "Radio & performance"),
    "CPU": Term("Central Processing Unit", "Computing resource whose load may indicate processing pressure.", "Software & observability"),
    "CU": Term("Central Unit", "Radio-network logical function that connects distributed radio units with other network functions.", "Mobile network"),
    "CU-CP": Term("Central Unit Control Plane", "The CU function managing radio signalling and control decisions.", "Mobile network"),
    "CU-UP": Term("Central Unit User Plane", "The CU function handling user-data traffic.", "Mobile network"),
    "DRB": Term("Data Radio Bearer", "Radio connection resource carrying user-plane data; establishment failures affect service access.", "Radio & performance"),
    "DU": Term("Distributed Unit", "Radio-network function handling lower radio protocol layers for cells.", "Mobile network"),
    "E1": Term("E1 interface", "3GPP interface connecting CU control-plane and user-plane functions.", "Mobile network"),
    "F1": Term("F1 interface", "3GPP interface connecting the radio Central Unit and Distributed Unit.", "Mobile network"),
    "gNodeB": Term("Next Generation Node B", "A 5G radio base station; the displayed sites are synthetic.", "Mobile network"),
    "KPI": Term("Key Performance Indicator", "A measured network service or system-performance indicator.", "Radio & performance"),
    "LLM": Term("Large Language Model", "A language model that can analyse and generate text; the public replay makes no model calls.", "AI & evaluation"),
    "ML": Term("Machine Learning", "Statistical model techniques used here as supporting recorded fault and scope predictions.", "AI & evaluation"),
    "N2": Term("N2 control-plane interface", "Interface for signalling between a 5G radio network and the AMF in the 5G Core.", "5G Core"),
    "NGAP": Term("Next Generation Application Protocol", "Control-plane signalling protocol between NG-RAN and the 5G Core's AMF.", "5G Core"),
    "NR": Term("New Radio", "The 5G radio-access technology used by the modelled cells.", "Mobile network"),
    "PM": Term("Performance Management", "Network counters and metrics sampled at a defined reporting interval; not the complete incident duration.", "Radio & performance"),
    "PRB": Term("Physical Resource Block", "A radio-scheduling resource; high usage may indicate capacity pressure.", "Radio & performance"),
    "QoS": Term("Quality of Service", "Network rules governing different services' priority and treatment.", "Radio & performance"),
    "5QI": Term("5G Quality of Service Identifier", "A 5G QoS class identifier; readings for different 5QI values must not be merged.", "Radio & performance"),
    "RAG": Term("Retrieval-Augmented Generation", "Using retrieved knowledge to support a language model's answer; its impact is not independently proven here.", "AI & evaluation"),
    "RAN": Term("Radio Access Network", "The mobile-network part connecting users through radio cells to the core network.", "Mobile network"),
    "RCA": Term("Root Cause Analysis", "An evidence-grounded explanation of a problem's likely causes and remaining uncertainty.", "AI & evaluation"),
    "RRC": Term("Radio Resource Control", "Radio signalling that establishes and controls the mobile device's connection.", "Radio & performance"),
    "SCTP": Term("Stream Control Transmission Protocol", "Transport protocol used to carry certain network control-plane signalling.", "5G Core"),
    "SINR": Term("Signal-to-Interference-plus-Noise Ratio", "Radio-signal quality relative to interference and background noise.", "Radio & performance"),
    "S-NSSAI": Term("Single Network Slice Selection Assistance Information", "Identifies a network slice, including its slice/service type and optional differentiator.", "5G Core"),
    "UE": Term("User Equipment", "A mobile device or simulated subscriber terminal accessing the network.", "Mobile network"),
    "UTC": Term("Coordinated Universal Time", "The common reference time used for recorded events and measurements.", "Software & observability"),
}

# Terms tailored to the page's most important concepts; all page titles and
# replay controls retain their established names and case identifiers.
PAGE_KEY_TERMS = {
    "Platform Overview": ("5G", "RCA", "ML", "RAG"),
    "Value Proposition & Solutions": ("RCA", "ML", "KPI", "RAN"),
    "Guided Operations Demo": ("5G", "RCA", "ML", "KPI"),
    "Network Overview": ("5G", "RAN", "NR", "CU", "DU", "PM"),
    "Scenario Library": ("PM", "KPI", "DRB", "RAG"),
    "Agentic Replay": ("RCA", "ML", "LLM", "API"),
    "Root Cause Analysis": ("RCA", "DRB", "RRC", "CU-CP"),
    "Engineering Evidence": ("PM", "5QI", "S-NSSAI", "DRB"),
    "Evaluation & Performance": ("RCA", "ML", "LLM", "UTC"),
}


def expanded(term: str) -> str:
    """Standard first-use construction for a known technical abbreviation."""
    item = TERMS[term]
    return f"{item.full} ({term})"


def quick_terms(page: str) -> str:
    """Short, inline first-use legend placed before the page's technical content."""
    return " · ".join(expanded(t) for t in PAGE_KEY_TERMS[page])


def glossary_matches(query: str = ""):
    """Search exact terms, full forms and short meanings, stable by category/name."""
    needle = query.strip().casefold()
    return [(abbr, val) for abbr, val in sorted(TERMS.items(), key=lambda p: (p[1].category, p[0].casefold()))
            if not needle or needle in f"{abbr} {val.full} {val.meaning} {val.category}".casefold()]


def render_page_terms(st, page: str) -> None:
    """Visible first-use expansions without adding another sidebar page."""
    if page not in PAGE_KEY_TERMS:
        return
    st.caption("**Technical terms on this page:** " + quick_terms(page))


def render_sidebar_glossary(st) -> None:
    """On-demand cross-page reference, including short lay explanations."""
    with st.sidebar.expander("📖 Telecom & AI glossary", expanded=False):
        text_input = getattr(st, "text_input", None)
        if not callable(text_input):
            # Minimal offline Streamlit stubs used by legacy playback tests.
            return
        query = text_input("Search a term or meaning", key="tead_glossary_query", placeholder="e.g. DRB, congestion, slice")
        hits = glossary_matches(query)
        if not hits:
            st.caption("No matching term. Try a different word.")
        for abbreviation, item in hits:
            st.markdown(f"**{item.full} ({abbreviation})** — {item.meaning}")
        st.caption("The glossary explains recorded technical language; it does not change the original experiment or diagnosis.")
