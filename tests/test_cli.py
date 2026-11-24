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


def test_batch_counts_a_file_with_no_assessable_site_as_failed(tmp_path):
    # #55: "files read 2 of 2 ... 0 failed" with one structure row was the fault
    import glob
    import pandas as pd
    from test_reading import MG, OX, mgo
    (tmp_path / 'ok.cif').write_text(mgo([MG, OX]))
    (tmp_path / 'empty.cif').write_text(mgo([MG, ('O1', 'O2-', 0, 0.5, 0.5, 1)]))
    r = run('batch', tmp_path, '-q', '--workers', '1')
    assert r.returncode == 0, r.stderr
    assert '1 structure(s)' in r.stdout and '1 unreadable' in r.stdout, r.stdout
    log = glob.glob(str(tmp_path / 'outputs' / 'eir_batch_log_*.txt'))
    assert '1 failed' in open(log[0], encoding='utf-8').read()
    failed = glob.glob(str(tmp_path / 'outputs' / 'eir_batch_failed_*.csv'))
    assert len(failed) == 1
    f = pd.read_csv(failed[0])
    assert list(f['filename']) == ['empty.cif']
    assert 'No cation site could be assessed' in f['error'].iloc[0]
