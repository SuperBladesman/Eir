"""The Eir engine.

This module is the notebook's code. tools/build_engine.py copies each code
cell of Eir.ipynb into _cells/, and importing this module executes them, in
notebook order, in this module's namespace, as Jupyter executes a notebook in
its own. Every function the notebook defines is therefore an attribute of
this module, with the behaviour it has in the notebook.

Two things differ from a notebook session, and only two:

* what the cells print while loading is kept in IMPORT_LOG rather than shown,
  because every worker process in a batch imports this module;
* the actions (CELL 9 onwards) run when run_pipeline() is called rather than
  when the module loads, and each run starts from the state the module had on
  loading, as "Restart & Run All" would.

Use the public interface in eir.api; this module is its machinery.
"""

import contextlib as _contextlib
import copy as _copy
import io as _io
import os as _os
from pathlib import Path as _P

from . import _manifest

_CELL_DIR = _P(__file__).resolve().parent / '_cells'


def _find_data_dir():
    """The reference tables: $EIR_DATA_DIR, the installed copy, or Data/ at
    the root of a source checkout (an editable install)."""
    env = _os.environ.get('EIR_DATA_DIR')
    candidates = ([_P(env)] if env else []) + [
        _P(__file__).resolve().parent / 'data',
        _P(__file__).resolve().parents[2] / 'Data',
    ]
    for c in candidates:
        if (c / 'bvs_parameters.json').exists():
            return str(c)
    raise FileNotFoundError(
        'Eir cannot find its reference tables (bvs_parameters.json and four '
        'others). Looked in: ' + ', '.join(str(c) for c in candidates)
        + '. Reinstall eir-bvs, or set EIR_DATA_DIR to the folder holding them.')


def _compile_cell(name):
    path = _CELL_DIR / name
    return compile(path.read_text(encoding='utf-8'), str(path), 'exec',
                   dont_inherit=True)


def reset_state():
    """Return the module to the state it had on loading: forget every name a
    previous run created, and empty the registers and caches the cells keep
    at module level. Settings (EIR_WORKERS, VERBOSE, ...) are kept."""
    g = globals()
    for k in [k for k in g if k not in _LOADED_NAMES]:
        del g[k]
    for k, v in _LOADED_STATE.items():
        cur = g.get(k)
        if type(cur) is not type(v):
            g[k] = _copy.deepcopy(v)
        elif isinstance(cur, dict):
            cur.clear()
            cur.update(_copy.deepcopy(v))
        elif isinstance(cur, list):
            cur[:] = _copy.deepcopy(v)
        else:
            cur.clear()
            cur.update(_copy.deepcopy(v))


def run_cell(key):
    """Run one of the notebook's actions (see _manifest.RUN_CELLS)."""
    exec(_compile_cell(_manifest.RUN_CELLS[key]), globals())


def run_pipeline(directory, steps=None):
    """Run the notebook's actions on one folder, from CELL 9 to CELL 15, as
    Restart & Run All would after picking that folder. `steps` runs a prefix
    or subset of _manifest.PIPELINE instead, in pipeline order."""
    reset_state()
    globals()['_EIR_RUN_DIRECTORY'] = str(_P(directory).resolve())
    wanted = _manifest.PIPELINE if steps is None else steps
    for key in _manifest.PIPELINE:
        if key not in wanted:
            continue
        run_cell(key)
        # CELL 9 sets df to None, or to an empty frame, when no file could
        # be read; every later cell would then stop on a missing dfq.
        if key == 'batch':
            _df = globals().get('df')
            if _df is None or not len(_df):
                break


def run_checks():
    """The checks the notebook runs as it loads: the structural scan of the
    source (CELL 1c), then VALIDATE() and VALIDATE_SETTINGS() (CELL 6), which
    the package defers, and VALIDATE_GATES() (CELL 7b), which it runs on
    loading too."""
    import json as _json
    import tempfile as _tempfile
    cells = [{'cell_type': 'code', 'metadata': {}, 'outputs': [],
              'execution_count': None,
              'source': (_CELL_DIR / n).read_text(encoding='utf-8')}
             for n in _manifest.NOTEBOOK_ORDER]
    with _tempfile.TemporaryDirectory() as d:
        nb = _P(d) / 'Eir_packaged_cells.ipynb'
        nb.write_text(_json.dumps({'cells': cells, 'metadata': {},
                                   'nbformat': 4, 'nbformat_minor': 5}),
                      encoding='utf-8')
        globals()['NOTEBOOK'] = str(nb)
        src = (_CELL_DIR / _manifest.CHECK_CELLS[0]).read_text(encoding='utf-8')
        # The cell sets NOTEBOOK = None to auto-detect; point it at the cells.
        line = '\nNOTEBOOK = None '
        if src.count(line) != 1:
            raise RuntimeError('CELL 1c no longer sets NOTEBOOK = None on a '
                               'line of its own; update run_checks().')
        src = src.replace(line, f'\nNOTEBOOK = {str(nb)!r} ', 1)
        exec(compile(src, str(_CELL_DIR / _manifest.CHECK_CELLS[0]), 'exec',
                     dont_inherit=True), globals())
    if globals().get('_fail'):
        raise AssertionError('Structural self-check failed: '
                             + '; '.join(globals()['_fail']))
    VALIDATE()            # noqa: F821  (defined by the cells)
    VALIDATE_SETTINGS()   # noqa: F821
    if 'VALIDATE_GATES' in globals():          # engine 2.0.46 onwards
        VALIDATE_GATES()  # noqa: F821
    return True


EIR_DATA_DIR = _find_data_dir()
IMPORT_LOG = _io.StringIO()

with _contextlib.redirect_stdout(IMPORT_LOG):
    for _cell in _manifest.ENGINE_CELLS:
        exec(_compile_cell(_cell), globals())
del _cell

# The state a fresh notebook session has once every definition has run.
_LOADED_NAMES = frozenset(globals()) | {'_LOADED_NAMES', '_LOADED_STATE'}
_LOADED_STATE = {
    _k: _copy.deepcopy(_v) for _k, _v in globals().items()
    if _k.startswith('_') and not _k.startswith('__')
    and type(_v) in (dict, list, set)
}
