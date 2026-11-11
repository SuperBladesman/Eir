"""The engine is the notebook's code, and it passes its own checks."""
import subprocess
import sys

import pytest

from conftest import ROOT


def test_cells_match_notebook():
    if not (ROOT / 'Eir.ipynb').exists():
        pytest.skip('Eir.ipynb is not in this source tree')
    r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_engine.py'),
                        '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_engine_version():
    import eir
    assert eir.ENGINE_VERSION == eir.engine.EIR_VERSION


def test_validate():
    import eir
    log = eir.validate()
    assert 'STRUCTURAL SELF-CHECK PASSED' in log
    assert 'ALL 29 TESTS PASSED' in log
    assert 'ALL GATE TESTS PASSED' in log
    assert 'ALL PARSING TESTS PASSED' in log
    assert 'ALL SETTING TESTS PASSED' in log


def test_import_is_quiet(capsys):
    import eir
    eir.engine  # noqa: B018  (loads the engine)
    out = capsys.readouterr()
    assert out.out == ''
    assert 'GII SELF-TEST' in eir.engine.IMPORT_LOG.getvalue()


def test_self_check_scans_its_own_notebook(tmp_path, monkeypatch):
    # The structural self-check (CELL 1c) finds the notebook it scans. A
    # notebook that only mentions EIR_VERSION (Huginn names the version it
    # reads) or sets another version must not be taken for it, even when
    # newer: 2.0.46 as first issued scanned Huginn 3.9.3 and reported every
    # function missing.
    import json
    import os
    import re
    import time
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / 'src' / 'eir' / '_cells'
           / 'k04_structural_self_check.py').read_text(encoding='utf-8')
    start = src.index('_path = _Path(NOTEBOOK) if NOTEBOOK else None')
    end = src.index('if _path is None or not _path.exists():')

    def nb(path, code):
        path.write_text(json.dumps({'cells': [
            {'cell_type': 'code', 'source': code}]}), encoding='utf-8')

    nb(tmp_path / 'Eir_2_0_46.ipynb', 'EIR_VERSION = "2.0.46"\n')
    time.sleep(0.05)
    nb(tmp_path / 'Eir_2_0_45.ipynb', 'EIR_VERSION = "2.0.45"\n')
    nb(tmp_path / 'Huginn.ipynb', "CONFIG = {'EXPECTED_EIR_VERSION': '2.0.46'}\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('JPY_SESSION_NAME', raising=False)
    ns = {'_Path': Path, '_json': json, '_os': os, '_re': re,
          'NOTEBOOK': None, 'EIR_VERSION': '2.0.46'}
    exec(src[start:end], ns)
    assert ns['_path'].name == 'Eir_2_0_46.ipynb'
