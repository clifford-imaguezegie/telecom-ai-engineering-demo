"""V1.7.4: executive-facing outcome cards preserve evidence/claim boundaries."""
from pathlib import Path
import sys, json, gzip, re
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from value_solutions import page_html, BENEFITS, SOLUTIONS
from presentation import phase_execution_ranges

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))


def cases():
    return [json.load(gzip.open(ROOT / 'data/cases' / f'{sid}.json.gz', 'rt', encoding='utf-8'))
            for sid in MANIFEST['scenario_order']]


def metric_cards():
    html = page_html(cases())
    section = html.split('<div class="vs-metrics">', 1)[1].split('</div>\n<div class="vs-foot">', 1)[0]
    return html, section


def test_four_cards_communicate_values_in_agreed_order():
    html, section = metric_cards()
    assert section.count('class="vs-metric"') == 4
    headlines = re.findall(r'<strong>(.*?)</strong><div class="vs-unit">', section)
    assert headlines == ['&lt; 25 sec', '&lt; 5 min', '98.7%', 'Cross-domain']
    assert 'Network health assessment' in section
    assert 'Evidence-grounded RCA' in section
    assert 'CU evidence payload reduction' in section
    assert 'Unified engineering intelligence' in section
    assert 'Experimental recordings' not in section


def test_headline_thresholds_supported_by_source_evidence():
    spans = phase_execution_ranges(cases())
    assert spans['sp01']['max'] < 25
    assert spans['incident']['max'] < 300
    assert spans['sp01']['count'] == 9
    assert spans['incident']['count'] == 8


def test_cu_payload_is_not_misrepresented_as_token_or_cost_savings():
    html, section = metric_cards()
    assert '17.29 MB → about 227 KB' in section
    assert 'not token cost' in section
    assert 'not a measured reduction in tokens or billed cost' in html
    assert 'production MTTR or financial benefits have not been measured' in html
    assert '~17M' not in html and '260k tokens' not in html


def test_card_four_is_architectural_value_not_unverified_commercial_metric():
    html, section = metric_cards()
    assert 'Specialist findings synthesized into a traceable RCA' in section
    assert 'Cross-domain' in section
    assert 'cost savings achieved' not in section.lower()


def test_benefits_solutions_and_page_structure_preserved():
    html, _ = metric_cards()
    assert len(BENEFITS) == 4
    assert len(SOLUTIONS) == 6
    assert html.count('class="vs-solution"') == 6
    assert html.count('class="vs-benefit"') == 4
    assert 'Path from demonstration to operator adoption' in html
