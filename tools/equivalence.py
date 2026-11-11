"""Show that the package gives the notebook's results on a folder of CIFs.

    python tools/equivalence.py my_cifs/ [--workdir DIR] [--workers N]

Copies the folder twice. Runs Eir.ipynb headless on one copy, with two edits
only: the pip-install cell is dropped and the folder picker is replaced by
the folder. Runs eir.check_folder() on the other. Then compares every CSV in
the two outputs/ folders cell by cell, and the summary, the oxidation-state
record and the run log line by line, once the folder path and the run stamp
are normalised. The log's timings are left out, because they differ.

Needs nbclient, nbformat and ipykernel (pip install nbclient ipykernel).
Exits 0 when everything matches. The CIFs are only read; nothing is written
inside the folder you name.

Two kinds of folder cannot be compared, because the notebook stops on them
and the package does not (see docs/PACKAGE.md): one in which no file has an
ICSD code, or in which a file with a code has no author or journal.
"""

import argparse
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = re.compile(r'\d{8}_\d{6}')


def run_notebook(cif_dir, work):
    import nbformat
    from nbclient import NotebookClient
    shutil.copytree(ROOT / 'Data', work / 'Data', dirs_exist_ok=True)
    nb = nbformat.read(ROOT / 'Eir.ipynb', as_version=4)
    cells = [c for c in nb.cells
             if not (c.cell_type == 'code'
                     and c.source.lstrip().startswith('import sys')
                     and 'get_ipython().system' in c.source)]
    assert len(cells) == len(nb.cells) - 1, 'pip-install cell not found'
    picker = 'EIR_CIF_DIRECTORY = select_directory()'
    hits = [c for c in cells if picker in c.source]
    assert len(hits) == 1, 'folder picker not found'
    hits[0].source = hits[0].source.replace(
        picker, f'EIR_CIF_DIRECTORY = {str(cif_dir)!r}')
    nb.cells = cells
    # CELL 1c scans the saved notebook, so save the copy where it will look
    nbformat.write(nb, work / 'Eir_headless.ipynb')
    NotebookClient(nb, timeout=None, kernel_name='python3',
                   resources={'metadata': {'path': str(work)}}).execute()
    nbformat.write(nb, work / 'Eir_headless_executed.ipynb')


def run_package(cif_dir, workers):
    import eir
    eir.check_folder(cif_dir, workers=workers, verbose=False)


def _norm(s, root):
    return STAMP.sub('<STAMP>', s.replace(str(root), '<DIR>'))


def compare(a, b):
    import pandas as pd
    oa, ob = a / 'outputs', b / 'outputs'
    fa = {STAMP.sub('<STAMP>', str(p.relative_to(oa))): p
          for p in oa.rglob('*') if p.is_file()}
    fb = {STAMP.sub('<STAMP>', str(p.relative_to(ob))): p
          for p in ob.rglob('*') if p.is_file()}
    problems = [f'only in the notebook run: {k}' for k in sorted(set(fa) - set(fb))]
    problems += [f'only in the package run: {k}' for k in sorted(set(fb) - set(fa))]
    ncsv = 0
    drop = re.compile(r'(\d+(\.\d+)?\s*(s|ms|min|h)\b|elapsed|ETA|per file|'
                      r'workers|calibration|serial|/s\b|\d+:\d\d)', re.I)
    for k in sorted(set(fa) & set(fb)):
        pa, pb = fa[k], fb[k]
        if k.endswith('.csv'):
            da = pd.read_csv(pa, dtype=str, keep_default_na=False).map(
                lambda x: _norm(x, a))
            db = pd.read_csv(pb, dtype=str, keep_default_na=False).map(
                lambda x: _norm(x, b))
            ncsv += 1
            if list(da.columns) != list(db.columns) or da.shape != db.shape:
                problems.append(f'{k}: shape or columns differ')
                continue
            d = da != db
            if d.values.any():
                c = list(d.columns[d.any()])
                problems.append(f'{k}: {int(d.values.sum())} cells differ, in {c[:6]}')
        elif k.endswith(('.txt', '.json')):
            ta = _norm(pa.read_text(encoding='utf-8', errors='replace'), a)
            tb = _norm(pb.read_text(encoding='utf-8', errors='replace'), b)
            if 'eir_batch_log' in k:
                ta = '\n'.join(l for l in ta.splitlines() if not drop.search(l))
                tb = '\n'.join(l for l in tb.splitlines() if not drop.search(l))
            if ta != tb:
                problems.append(f'{k}: text differs')
    return ncsv, len(set(fa) & set(fb)), problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('folder')
    ap.add_argument('--workdir', help='keep both runs here (default: a '
                                      'temporary folder, removed afterwards)')
    ap.add_argument('--workers', default=None,
                    help="for the package run: 'auto' or a number")
    a = ap.parse_args(argv)
    src = Path(a.folder).resolve()
    tmp = None
    if a.workdir:
        work = Path(a.workdir).resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        tmp = tempfile.TemporaryDirectory(prefix='eir_equivalence_')
        work = Path(tmp.name)
    nb_dir, pkg_dir = work / 'notebook' / src.name, work / 'package' / src.name
    for d in (nb_dir, pkg_dir):
        if d.exists():
            shutil.rmtree(d)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, d, ignore=shutil.ignore_patterns('outputs'))
    t = time.time()
    run_notebook(nb_dir, work / 'notebook')
    t_nb = time.time() - t
    t = time.time()
    run_package(pkg_dir, a.workers)
    t_pkg = time.time() - t
    ncsv, nfiles, problems = compare(nb_dir, pkg_dir)
    print(f'{src.name}: notebook {t_nb:.0f} s, package {t_pkg:.0f} s; '
          f'{nfiles} output files in common, {ncsv} CSVs compared cell by cell')
    if tmp is not None:
        tmp.cleanup()
    if problems:
        print('DIFFERENT')
        for p in problems:
            print('  ' + p)
        return 1
    print('IDENTICAL')
    return 0


if __name__ == '__main__':
    sys.exit(main())
