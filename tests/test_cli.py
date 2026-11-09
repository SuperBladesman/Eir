"""The eir command."""
import subprocess
import sys

import eir


def run(*args):
    return subprocess.run([sys.executable, '-m', 'eir.cli', *map(str, args)],
                          capture_output=True, text=True)


def test_version():
    r = run('--version')
    assert r.returncode == 0
    assert eir.__version__ in r.stdout and eir.ENGINE_VERSION in r.stdout


def test_check(examples):
    r = run('check', examples / 'MgO.cif')
    assert r.returncode == 0, r.stderr
    assert 'ACCEPT' in r.stdout
    assert (examples / 'MgO.eir.html').exists()


def test_check_needs_oxidation_states(examples):
    r = run('check', examples / 'SrTiO3_refined.cif', '--no-report')
    assert r.returncode == 3
    assert '--ox' in r.stderr


def test_check_with_ox(examples):
    r = run('check', examples / 'SrTiO3_refined.cif', '--ox', 'Sr=2,Ti=4,O=-2',
            '--no-report')
    assert r.returncode == 0, r.stderr
    assert 'ACCEPT' in r.stdout


def test_strict(examples):
    r = run('check', examples / 'MgO_wrong_cell.cif', '--no-report', '--strict')
    assert r.returncode == 1
    assert 'EXPUNGE' in r.stdout


def test_bad_ox():
    r = run('check', 'x.cif', '--ox', 'Mn')
    assert r.returncode == 2
