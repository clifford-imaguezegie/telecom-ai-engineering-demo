"""UX-01 content acceptance: no new routes, sites, schema or evidence changes."""
from pathlib import Path
import re
import ast
from terminology import TERMS, PAGE_KEY_TERMS, expanded, quick_terms, glossary_matches
from release_identity import RELEASE_VERSION, RELEASE_FILES

ROOT=Path(__file__).resolve().parents[1]
PAGES=['Platform Overview','Value Proposition & Solutions','Guided Operations Demo',
       'Network Overview','Scenario Library','Agentic Replay','Root Cause Analysis',
       'Engineering Evidence','Evaluation & Performance']


def test_all_nine_existing_pages_have_first_use_definitions():
    assert list(PAGE_KEY_TERMS)[:len(PAGES)] == PAGES
    for page in PAGES:
        assert len(PAGE_KEY_TERMS[page]) >= 4
        assert all(key in TERMS for key in PAGE_KEY_TERMS[page])
        assert all(expanded(t) in quick_terms(page) for t in PAGE_KEY_TERMS[page])
        assert ' (' in quick_terms(page)


def test_glossary_has_plain_explanations_and_standard_expansions():
    assert len(TERMS)>=30
    assert expanded('RCA') == 'Root Cause Analysis (RCA)'
    assert expanded('RAG') == 'Retrieval-Augmented Generation (RAG)'
    assert expanded('5QI') == '5G Quality of Service Identifier (5QI)'
    assert expanded('S-NSSAI') == 'Single Network Slice Selection Assistance Information (S-NSSAI)'
    assert expanded('RRC') == 'Radio Resource Control (RRC)'
    assert all(term.full and term.meaning and term.category for term in TERMS.values())
    assert 'TEAD' not in TERMS  # Product naming must not acquire an invented backronym.


def test_search_matches_abbreviation_full_form_and_meaning():
    assert any(k == 'DRB' for k,v in glossary_matches('DRB'))
    assert any(k == 'DRB' for k,v in glossary_matches('data radio bearer'))
    assert any(k == '5QI' for k,v in glossary_matches('slice') ) is False
    assert any(k == 'S-NSSAI' for k,v in glossary_matches('slice'))
    assert glossary_matches('definitely-not-a-telecom-term') == []


def test_text_layer_is_visible_but_not_an_extra_workspace_page():
    s=(ROOT/'app.py').read_text('utf-8')
    assert 'render_page_terms(st,page)' in s
    assert 'render_sidebar_glossary(st)' in s
    assert 'Root Cause Analysis (RCA)' in s
    assert 'fifth-generation (5G)' in s
    page_line=next(line for line in s.splitlines() if line.startswith('PAGES ='))
    assert len(re.findall(r"'[^']+'",page_line)) == 9
    assert 'terminology.py' in RELEASE_FILES
    assert RELEASE_VERSION == 'V1.7.5 RC2.2'


def test_no_new_data_or_network_operations_in_terminology():
    s=(ROOT/'terminology.py').read_text('utf-8')
    tree = ast.parse(s)
    imported = {alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module.split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    assert imported == {'dataclasses'}
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'open', 'eval', 'exec'} for node in ast.walk(tree))
