"""The release metadata agree with each other and with the code.

Zenodo reads .zenodo.json and ignores CITATION.cff when both are present;
GitHub's "Cite this repository" reads CITATION.cff. The two must name the
same software, version and author, and the version must be the engine's.
"""
import json
import re
from pathlib import Path

import eir

ROOT = Path(__file__).resolve().parents[1]


def cff(field, text=None):
    text = text or (ROOT / 'CITATION.cff').read_text(encoding='utf-8')
    m = re.search(rf'^{field}:\s*"?(.*?)"?\s*$', text, re.M)
    return m.group(1) if m else None


def test_zenodo_and_citation_files_agree():
    z = json.loads((ROOT / '.zenodo.json').read_text(encoding='utf-8'))
    text = (ROOT / 'CITATION.cff').read_text(encoding='utf-8')
    assert z['version'] == cff('version', text) == eir.ENGINE_VERSION
    assert z['title'] == cff('title', text)
    assert z['upload_type'] == 'software' and z['license'] == 'mit'
    assert cff('license', text) == 'MIT'
    orcid = z['creators'][0]['orcid']
    # every author entry in CITATION.cff (software and paper) carries it
    assert text.count(f'orcid: "https://orcid.org/{orcid}"') == text.count('family-names:')


def test_package_version_matches_pyproject():
    toml = (ROOT / 'pyproject.toml').read_text(encoding='utf-8')
    assert re.search(r'^version = "(.*)"', toml, re.M).group(1) == eir.__version__


def test_the_released_versions_have_a_changelog_entry():
    log = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    released = cff('date-released')
    for v in (f'eir-bvs {eir.__version__}', eir.ENGINE_VERSION):
        m = re.search(rf'^### {re.escape(v)} – (.+)$', log, re.M)
        assert m, v
        assert m.group(1) != 'unreleased', (v, 'CHANGELOG still says unreleased')
    assert released and re.fullmatch(r'\d{4}-\d{2}-\d{2}', released)


def test_the_readme_gives_the_citation_doi():
    doi = cff('doi')
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert doi and f'https://doi.org/{doi}' in readme, doi
