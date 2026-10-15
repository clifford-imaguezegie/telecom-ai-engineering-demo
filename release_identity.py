"""Traceable public UI release identity, separate from recorded trace IDs."""
from hashlib import sha256
from pathlib import Path
RELEASE_VERSION = 'V1.7.5 RC2'
RELEASE_DATE = '15 Oct 2026'
RELEASE_FILES = ('app.py','guided_story_ui.py','operational_demo.py',
                 'measurement_series.py','network_overview.py','value_solutions.py')


def release_build_id():
    root=Path(__file__).resolve().parent
    digest=sha256()
    for name in RELEASE_FILES:
        digest.update(name.encode('utf-8')+b'\x00')
        digest.update((root/name).read_bytes())
    return digest.hexdigest()[:12]
