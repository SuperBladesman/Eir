"""The eir command.

    eir check refined.cif                 verdict in the terminal, report beside the file
    eir check refined.cif --ox Na=1,Mn=3.5,O=-2
    eir batch my_cifs/ [--reports]        what the notebook does, on a folder
    eir validate                          the 24 known-answer tests and the self-checks
"""

import argparse
import os
import sys
from pathlib import Path


def _parse_ox(text):
    if not text:
        return None
    out = {}
    for part in text.replace(';', ',').split(','):
        part = part.strip()
        if not part:
            continue
        if '=' not in part:
            raise argparse.ArgumentTypeError(
                f'"{part}" is not ELEMENT=VALENCE, e.g. Mn=4 or O=-2')
        el, v = (s.strip() for s in part.split('=', 1))
        try:
            out[el] = float(v)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f'"{v}" is not a number (in "{part}")')
    return out


def _version_text():
    from . import __version__
    from ._manifest import ENGINE_VERSION
    return f'eir-bvs {__version__} (Eir engine {ENGINE_VERSION})'


def cmd_check(a):
    from . import api
    cifs = [Path(p) for p in a.cif]
    status = 0
    for i, cif in enumerate(cifs):
        try:
            res = api.check(cif, oxidation_states=a.ox, output_dir=a.outputs,
                            verbose=a.verbose)
        except api.OxidationStatesNeeded as err:
            print(f'{cif.name}: {err}', file=sys.stderr)
            status = max(status, 3)
            continue
        except api.EirError as err:
            print(f'{cif.name}: {err}', file=sys.stderr)
            status = max(status, 2)
            continue
        for r in (res if isinstance(res, list) else [res]):
            if i:
                print()
            print(r.verdict())
            if not a.no_report:
                dest = Path(a.report) if a.report and len(cifs) == 1 else None
                p = r.write_report(dest)
                print(f'\n  Report               {p}')
            if a.strict and r.tier in ('EXPUNGE', 'FLAG', 'NOT_ASSESSED'):
                status = max(status, 1)
    return status


def cmd_batch(a):
    import warnings
    from . import api
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            res = api.check_folder(a.folder, oxidation_states=a.ox,
                                   workers=a.workers, verbose=not a.quiet,
                                   reports=a.reports)
    except api.OxidationStatesNeeded as err:
        print(str(err), file=sys.stderr)
        return 3
    except api.EirError as err:
        print(str(err), file=sys.stderr)
        return 2
    if a.quiet:
        print(repr(res))
    for n in res.notes:
        print(f'Note: {n}')
    print(f'\nOutputs in {res.output_dir}')
    if a.reports:
        print(f'Reports in {res.output_dir / "reports"}')
    return 0


def cmd_validate(a):
    from . import api
    try:
        log = api.validate(verbose=a.verbose)
    except AssertionError as err:
        print(f'FAILED: {err}', file=sys.stderr)
        return 1
    lines = [l for l in log.splitlines()
             if 'PASSED' in l or 'Source scanned' in l]
    for l in lines:
        print(l.strip())
    print('Eir validation passed.')
    return 0


def main(argv=None):
    os.environ.setdefault('MPLBACKEND', 'Agg')
    p = argparse.ArgumentParser(
        prog='eir',
        description='Bond valence screening of crystal structures, with an '
                    'integrity verdict.')
    p.add_argument('--version', action='version', version=_version_text())
    sub = p.add_subparsers(dest='cmd', metavar='COMMAND')

    c = sub.add_parser('check', help='check one or more CIF files',
                       description='Check each CIF and print the verdict. A '
                       'one-page HTML report is written beside each file '
                       '(name.eir.html) unless --no-report is given.')
    c.add_argument('cif', nargs='+', help='CIF file(s), e.g. refined.cif')
    c.add_argument('--ox', type=_parse_ox, metavar='EL=V,...',
                   help='oxidation states, e.g. Na=1,Mn=3.5,O=-2; needed when '
                        'the file does not give them (most Rietveld output). '
                        'Overrides the file.')
    c.add_argument('--report', metavar='PATH',
                   help='where to write the report (one CIF only)')
    c.add_argument('--no-report', action='store_true',
                   help='print the verdict only')
    c.add_argument('--outputs', metavar='DIR',
                   help='keep the full outputs (CSVs, figures, log) in DIR')
    c.add_argument('--strict', action='store_true',
                   help='exit 1 unless every structure is in an ACCEPT tier')
    c.add_argument('-v', '--verbose', action='store_true',
                   help='show everything the run prints')
    c.set_defaults(func=cmd_check)

    b = sub.add_parser('batch', help='check every CIF in a folder',
                       description='Run Eir on every CIF in a folder, as the '
                       'notebook does, writing outputs/ inside it.')
    b.add_argument('folder')
    b.add_argument('--ox', type=_parse_ox, metavar='EL=V,...',
                   help='oxidation states for every file; written to '
                        'config.json in the folder')
    b.add_argument('--workers', default=None,
                   help="'auto' (default) or a number; 1 runs serially")
    b.add_argument('--reports', action='store_true',
                   help='also write one HTML report per structure')
    b.add_argument('-q', '--quiet', action='store_true',
                   help='print a one-line summary instead of the run')
    b.set_defaults(func=cmd_batch)

    v = sub.add_parser('validate', help='run the known-answer tests',
                       description='Run the structural self-check and the '
                       'known-answer test suites the notebook runs on load.')
    v.add_argument('-v', '--verbose', action='store_true')
    v.set_defaults(func=cmd_validate)

    a = p.parse_args(argv)
    if not getattr(a, 'cmd', None):
        p.print_help()
        return 0
    return a.func(a)


if __name__ == '__main__':
    sys.exit(main())
