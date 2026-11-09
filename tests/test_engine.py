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
    assert 'ALL 27 TESTS PASSED' in log
    assert 'ALL GATE TESTS PASSED' in log
    assert 'ALL SETTING TESTS PASSED' in log


def test_import_is_quiet(capsys):
    import eir
    eir.engine  # noqa: B018  (loads the engine)
    out = capsys.readouterr()
    assert out.out == ''
    assert 'GII SELF-TEST' in eir.engine.IMPORT_LOG.getvalue()
