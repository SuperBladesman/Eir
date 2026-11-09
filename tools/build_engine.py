"""Build the eir package's engine from Eir.ipynb.

The notebook is the source of the engine. This script copies its code cells
into src/eir/_cells/, one file per cell, so that the package runs the same
code the notebook runs, in the same order, in one namespace. It changes
nothing else, and everything it does change is listed in PLAN below:

* cells that only install packages or describe the notebook are left out;
* the structural self-check (CELL 1c) and the two validation suites are not
  run on import, because every worker process imports the engine; they run
  when eir.validate() is called;
* the reference tables are read from the package's data folder rather than
  from ./Data in the working directory;
* the cells that act on a folder (CELL 9 onwards) are split into the
  definitions, which load with the engine, and the action, which runs when
  eir.check() or eir.check_folder() is called, in notebook order, with the
  folder passed in instead of picked from a dialog.

Each edit must match the notebook exactly once, so a change to the notebook
that touches an edited line stops the build rather than going unnoticed.

    python tools/build_engine.py            # write src/eir/_cells/
    python tools/build_engine.py --check    # fail if they are out of date
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'Eir.ipynb'
OUT = ROOT / 'src' / 'eir' / '_cells'
MANIFEST = ROOT / 'src' / 'eir' / '_manifest.py'

RULE = '# ' + '-' * 75

# One entry per notebook cell, in notebook order.
#   name   file stem, or None to leave the cell out
#   role   'engine' (loads with the package), 'run' (runs on a folder),
#          'check' (runs from eir.validate()), or 'split' (both)
#   split  for 'split', the text the run part starts with
#   run    for 'run' and 'split', the key eir uses to run it
#   edits  (old, new) pairs, each of which must match exactly once
PLAN = [
    dict(cell=0, name='c00_version', role='engine'),
    dict(cell=1, name=None, why='markdown: the notebook guide'),
    dict(cell=2, name=None, why='installs py3Dmol with pip; the package '
                                'declares it as an optional dependency'),
    dict(cell=3, name='c03_helper_functions', role='engine'),
    dict(cell=4, name='c04_structural_self_check', role='check',
         why='scans the source for duplicated or missing definitions; run by '
             'eir.validate() over the packaged cells'),
    dict(cell=5, name='c05_output_control_and_geometry_core', role='engine'),
    dict(cell=6, name='c06_main_functionality', role='engine',
         edits=[('db_manager = DatabaseManager()\n',
                 'db_manager = DatabaseManager(data_dir=EIR_DATA_DIR)'
                 '   # eir package: the bundled tables\n')]),
    dict(cell=7, name='c07_anion_centred_bvs_engine', role='engine'),
    dict(cell=8, name='c08_anion_bvs_wiring', role='engine'),
    dict(cell=9, name='c09_gii_self_test', role='engine'),
    dict(cell=10, name='c10_validation_suite', role='engine',
         edits=[('\n\nVALIDATE()\n\n',
                 '\n\n# VALIDATE()   # eir package: run by eir.validate()\n\n'),
                ('\n\nVALIDATE_SETTINGS()',
                 '\n\n# VALIDATE_SETTINGS()   # eir package: run by '
                 'eir.validate()')]),
    dict(cell=11, name='c11_coordination_quality', role='engine'),
    dict(cell=12, name='c12_pgrm_integrity_gates', role='engine'),
    dict(cell=13, name='c13_shadowing_check', role='engine'),
    dict(cell=14, name='c14_run_batch_analysis', role='run', run='batch',
         edits=[('EIR_CIF_DIRECTORY = select_directory()',
                 'EIR_CIF_DIRECTORY = _EIR_RUN_DIRECTORY'
                 '   # eir package: the folder passed in')]),
    dict(cell=15, name='c15_provenance', role='run', run='provenance'),
    dict(cell=16, name='c16_post_process', role='run', run='postprocess'),
    dict(cell=17, name='c17_per_structure_table', role='split',
         run='structure_table',
         split="if 'dfq' in dir() and dfq is not None:\n"),
    dict(cell=18, name='c18_triage', role='split', run='triage',
         split='if "dfq" in globals() and dfq is not None:\n'
               '    _triage_text = triage(dfq)\n'),
    dict(cell=19, name='c19_shift_test', role='split', run='shift_test',
         split=RULE + '\nCIF_DIRECTORY = None'),
    dict(cell=20, name='c20_figures', role='engine'),
    dict(cell=21, name='c21_measurement_tools', role='engine'),
    dict(cell=22, name='c22_dataset_summary_report', role='engine'),
    dict(cell=23, name='c23_print_dataset_summary', role='run', run='summary'),
    dict(cell=24, name='c24_look_at_one_structure', role='split',
         run='look_at', split=RULE + '\n# Put a code here'),
    dict(cell=25, name='c25_look_at_a_family', role='split',
         run='look_at_family', split=RULE + '\n# Put a composition here'),
    dict(cell=26, name=None, why='empty'),
]

# The order eir.check_folder() runs the actions in. It is the notebook's
# order, top to bottom, less the three that only print or wait for input:
# CELL 10 (provenance) runs before dfq exists and says so, and CELLS 16 and
# 17 do nothing until a code is typed in.
PIPELINE = ['batch', 'postprocess', 'structure_table', 'triage',
            'shift_test', 'summary']

HEADER = ('# Generated by tools/build_engine.py from Eir.ipynb, cell {cell}.\n'
          '# Edit the notebook, not this file, then rebuild.\n'
          '{note}\n')


def _apply(src, edits, where):
    for old, new in edits or []:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f'{where}: edit expected once, found {n} times:\n'
                             f'  {old!r}')
        src = src.replace(old, new)
    return src


def build():
    nb = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
    cells = nb['cells']
    if len(cells) != len(PLAN):
        raise SystemExit(f'Eir.ipynb has {len(cells)} cells and the plan '
                         f'describes {len(PLAN)}. Update PLAN.')
    files, engine, runs, checks, order = {}, [], {}, [], []
    version = None
    for p, c in zip(PLAN, cells):
        src = ''.join(c['source'])
        if p['cell'] == 0:
            version = src.split('"')[1]
        if p['name'] is None:
            continue
        if c['cell_type'] != 'code':
            raise SystemExit(f"cell {p['cell']} is {c['cell_type']}, "
                             f"expected code")
        first = src.splitlines()[0] if src.strip() else ''
        if p['cell'] >= 3 and not first.startswith('#'):
            raise SystemExit(f"cell {p['cell']}: unexpected first line "
                             f"{first!r}; has a cell moved?")
        src = _apply(src, p.get('edits'), f"cell {p['cell']}")
        role = p['role']
        if role == 'split':
            k = src.count(p['split'])
            if k != 1:
                raise SystemExit(f"cell {p['cell']}: split point found "
                                 f"{k} times")
            i = src.index(p['split'])
            head, tail = src[:i].rstrip() + '\n', src[i:]
            ename, rname = 'e' + p['name'][1:], 'r' + p['name'][1:]
            files[ename + '.py'] = HEADER.format(
                cell=p['cell'],
                note=f'# The action at the end of this cell is in '
                     f'{rname}.py.') + head
            files[rname + '.py'] = HEADER.format(
                cell=p['cell'],
                note=f'# The action at the end of the cell; its definitions '
                     f'are in {ename}.py.') + tail
            engine.append(ename + '.py')
            runs[p['run']] = rname + '.py'
            order += [ename + '.py', rname + '.py']
        else:
            prefix = {'engine': 'e', 'run': 'r', 'check': 'k'}[role]
            fname = prefix + p['name'][1:] + '.py'
            files[fname] = HEADER.format(cell=p['cell'], note='') + src
            order.append(fname)
            if role == 'engine':
                engine.append(fname)
            elif role == 'run':
                runs[p['run']] = fname
            else:
                checks.append(fname)

    sha = hashlib.sha256(NOTEBOOK.read_bytes()).hexdigest()
    manifest = (
        '"""Generated by tools/build_engine.py. Do not edit."""\n\n'
        f'ENGINE_VERSION = {version!r}\n'
        f'NOTEBOOK_SHA256 = {sha!r}\n\n'
        '# Loaded, in this order, into one namespace when eir starts.\n'
        'ENGINE_CELLS = [\n'
        + ''.join(f'    {n!r},\n' for n in engine) + ']\n\n'
        '# The actions, by the name eir runs them under.\n'
        'RUN_CELLS = {\n'
        + ''.join(f'    {k!r}: {v!r},\n' for k, v in runs.items()) + '}\n\n'
        '# The order eir.check_folder() runs them in.\n'
        f'PIPELINE = {PIPELINE!r}\n\n'
        '# Run by eir.validate().\n'
        f'CHECK_CELLS = {checks!r}\n\n'
        '# Every packaged cell in notebook order, for the source scan.\n'
        'NOTEBOOK_ORDER = [\n'
        + ''.join(f'    {n!r},\n' for n in order) + ']\n')
    return files, manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--check', action='store_true',
                    help='exit 1 if src/eir/_cells/ is out of date')
    a = ap.parse_args(argv)
    files, manifest = build()
    if a.check:
        stale = [n for n, s in files.items()
                 if not (OUT / n).exists()
                 or (OUT / n).read_text(encoding='utf-8') != s]
        extra = sorted(p.name for p in OUT.glob('*.py') if p.name not in files)
        if not MANIFEST.exists() or MANIFEST.read_text(encoding='utf-8') != manifest:
            stale.append('_manifest.py')
        if stale or extra:
            print('src/eir/_cells/ is out of date with Eir.ipynb:')
            for n in stale:
                print(f'  changed  {n}')
            for n in extra:
                print(f'  extra    {n}')
            print('Run: python tools/build_engine.py')
            return 1
        print(f'src/eir/_cells/ matches Eir.ipynb ({len(files)} cells).')
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob('*.py'):
        if p.name not in files:
            p.unlink()
    for n, s in files.items():
        (OUT / n).write_text(s, encoding='utf-8', newline='\n')
    MANIFEST.write_text(manifest, encoding='utf-8', newline='\n')
    print(f'Wrote {len(files)} cells to {OUT.relative_to(ROOT)} '
          f'and {MANIFEST.relative_to(ROOT)}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
