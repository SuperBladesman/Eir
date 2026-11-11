"""Eir: bond valence screening of crystal structures, with an integrity verdict.

    import eir
    r = eir.check('refined.cif', oxidation_states={'Na': 1, 'Mn': 4, 'O': -2})
    print(r.verdict())             # plain-English verdict and the number to quote
    r.write_report()               # refined.eir.html, one page

    f = eir.check_folder('cifs/')  # the notebook's full pipeline on a folder
    f.structures                   # one row per structure

    eir.validate()                 # the known-answer tests

The engine loads on first use, which takes a second or two.
"""

__version__ = '2.1.0'

from ._manifest import ENGINE_VERSION  # noqa: E402

__all__ = ['check', 'check_folder', 'validate', 'engine', 'CheckResult',
           'FolderResult', 'EirError', 'OxidationStatesNeeded',
           '__version__', 'ENGINE_VERSION']

_API = {'check', 'check_folder', 'validate', 'CheckResult', 'FolderResult',
        'EirError', 'OxidationStatesNeeded'}


def __getattr__(name):
    if name in _API:
        from . import api
        return getattr(api, name)
    if name == 'engine':
        # every function the notebook defines, e.g. eir.engine.look_at
        from . import _engine
        return _engine
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def __dir__():
    return sorted(set(globals()) | _API | {'engine'})
