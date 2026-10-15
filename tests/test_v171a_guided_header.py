"""V1.7.1a: scope heading clearance to the Guided Operations page."""
from pathlib import Path

APP = (Path(__file__).resolve().parents[1]/"app.py").read_text(encoding="utf-8")

def test_guided_eyebrow_has_internal_headroom():
    selector = ".block-container:has(.tread-guided-marker) .cockpit-kicker"
    rule = APP.split(selector+"{",1)[1].split("}",1)[0]
    assert "padding-top:12px!important" in rule
    assert "line-height:1.5!important" in rule
    assert "display:block" in rule

def test_guided_label_and_existing_hero_still_exist():
    assert "TEAD AI · AGENTIC NETWORK INVESTIGATION" in APP
    assert "Guided Operations Demo</div>" in APP
    assert "TEAD AI — Agentic Telecom Network Investigation" in APP
