"""The public interface: check one structure, check a folder, validate.

    import eir
    r = eir.check('refined.cif', oxidation_states={'Na': 1, 'Mn': 3.5, 'O': -2})
    print(r.verdict())
    r.write_report('refined.eir.html')

    f = eir.check_folder('my_cifs/')          # what the notebook does
    f.structures                              # one row per structure

Both run the notebook's own pipeline (CELL 9 to CELL 15) on a folder, so a
result from here is the result the notebook would give.
"""

import contextlib
import glob
import io
import json
import os
import re
import shutil
import sys
import tempfile
import warnings
from pathlib import Path


__all__ = ['check', 'check_folder', 'validate', 'CheckResult', 'FolderResult',
           'OxidationStatesNeeded', 'EirError']


# What engine 2.0.46 writes into a failure when the file types an element as
# an anion that the bond valence table has no parameters for in that role
# (_unsupported_anion_note).
_UNSUPPORTED_ANION = 'typed as an anion'


class EirError(RuntimeError):
    """Eir could not produce a result. The message says why."""


class OxidationStatesNeeded(EirError):
    """The file does not say what the oxidation states are, and Eir needs
    them. Pass oxidation_states={...}, or put a config.json beside the CIF."""

    def __init__(self, elements):
        self.elements = sorted(elements)
        example = ','.join(f'{e}=?' for e in self.elements)
        super().__init__(
            'The oxidation states of ' + ', '.join(self.elements)
            + ' are not given in the file, and Eir does not guess them. '
            'Pass them with oxidation_states={...} (from the command line, '
            f'--ox {example}), or put a config.json beside the CIF, for '
            'example {"Na": 1, "Mn": 4, "O": -2}.')


def _engine():
    from . import _engine as e
    return e


class _Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            try:
                st.flush()
            except Exception:
                pass


@contextlib.contextmanager
def _capture(verbose):
    """Record everything the cells print; show it too if verbose."""
    buf = io.StringIO()
    out = _Tee(buf, sys.stdout) if verbose else buf
    err = _Tee(buf, sys.stderr) if verbose else buf
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            warnings.catch_warnings():
        if not verbose:
            warnings.simplefilter('ignore')
        yield buf


@contextlib.contextmanager
def _settings(e, workers=None):
    """Temporarily set engine options, and replace the interactive
    oxidation-state prompt with an error that says what is missing."""
    saved = {'EIR_WORKERS': e.EIR_WORKERS,
             'prompt_for_oxidation_states': e.prompt_for_oxidation_states}

    def _no_prompt(elements):
        raise OxidationStatesNeeded(elements)

    try:
        if workers is not None:
            e.EIR_WORKERS = 'auto' if workers in (0, 'auto') else int(workers)
        e.prompt_for_oxidation_states = _no_prompt
        yield
    finally:
        for k, v in saved.items():
            setattr(e, k, v)


def _write_config(folder, oxidation_states):
    clean = {}
    for k, v in (oxidation_states or {}).items():
        try:
            v = float(v)
        except (TypeError, ValueError):
            raise EirError(f'Oxidation state for {k} is not a number: {v!r}')
        clean[str(k)] = int(v) if v == int(v) else v
    (Path(folder) / 'config.json').write_text(json.dumps(clean, indent=2),
                                              encoding='utf-8')


def _latest(outdir, pattern):
    hits = sorted(glob.glob(str(Path(outdir) / pattern)), key=os.path.getmtime)
    return Path(hits[-1]) if hits else None


def _failures(outdir, log_text):
    """{filename: reason} for files the batch could not read."""
    out = {}
    f = _latest(outdir, 'eir_batch_failed_*.csv')
    if f is not None:
        import pandas as pd
        for _, r in pd.read_csv(f).iterrows():
            out[str(r['filename'])] = str(r['error'])
    log = _latest(outdir, 'eir_batch_log_*.txt')
    text = log.read_text(encoding='utf-8', errors='replace') if log else log_text
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'\s*\[\d+/\d+\]\s+(.+?)\s{2,}FAILED\s+(.*)', line)
        if m:
            reason = [m.group(2).strip()]
            for nxt in lines[i + 1:i + 6]:
                if not nxt.strip() or nxt.lstrip().startswith(('----', '[')):
                    break
                reason.append(nxt.strip())
            out.setdefault(m.group(1).strip() + '.cif', ' '.join(reason))
    return out


class FolderResult:
    """What a run over a folder produced.

    sites       the per-site table (the notebook's dfq)
    structures  one row per structure (dfs), with the integrity verdict
    failed      {filename: reason} for files that could not be read
    output_dir  the outputs/ folder the run wrote
    summary     the dataset summary (eir_summary.txt)
    log         everything the run printed
    """

    def __init__(self, folder, sites, structures, failed, output_dir, summary,
                 log, oxidation_states):
        self.folder = Path(folder)
        self.sites = sites
        self.structures = structures
        self.failed = failed
        self.output_dir = Path(output_dir)
        self.summary = summary
        self.log = log
        self.oxidation_states = oxidation_states
        self.notes = []     # what the package did that the notebook would not

    def __len__(self):
        return 0 if self.structures is None else len(self.structures)

    def results(self):
        """One CheckResult per structure, in table order."""
        if self.structures is None:
            return []
        out = []
        for _, row in self.structures.iterrows():
            fn = row['filename']
            s = self.sites[self.sites['filename'] == fn]
            out.append(CheckResult(self.folder / str(fn), row, s, self))
        return out

    def write_reports(self, directory=None):
        """One HTML report per structure; returns the paths written."""
        d = Path(directory) if directory else self.output_dir / 'reports'
        d.mkdir(parents=True, exist_ok=True)
        paths = []
        for r in self.results():
            p = d / (Path(str(r.structure['filename'])).stem + '.eir.html')
            r.write_report(p)
            paths.append(p)
        return paths

    def __repr__(self):
        n = len(self)
        tiers = ''
        if n and 'structure_pgrm_tier' in self.structures.columns:
            vc = self.structures['structure_pgrm_tier'].value_counts()
            tiers = ', '.join(f'{k} {v}' for k, v in vc.items())
        return (f'<eir.FolderResult {self.folder.name}: {n} structure(s)'
                + (f'; {tiers}' if tiers else '')
                + (f'; {len(self.failed)} unreadable' if self.failed else '')
                + '>')


class CheckResult:
    """The verdict on one structure.

    tier, code, reason, evidence   the integrity verdict and what decided it
    quote                          (index name, value, sigma) to quote, or None
    structure                      the per-structure row
    sites                          its per-site rows
    """

    def __init__(self, cif, structure, sites, run=None, failure=None):
        self.cif = Path(cif)
        self.structure = structure
        self.sites = sites
        self.run = run
        self.failure = failure

    def _get(self, k):
        if self.structure is None:
            return None
        v = self.structure.get(k)
        try:
            if v != v:
                return None
        except Exception:
            pass
        return v

    @property
    def readable(self):
        return self.failure is None

    @property
    def _unsupported_anion(self):
        # Engine 2.0.46 names an anion it has no parameters for (Sn(4-) in
        # Mg2Sn) in the failure. The file was read; it cannot be assessed,
        # which is NOT_ASSESSED, not EXPUNGE.
        return bool(self.failure) and _UNSUPPORTED_ANION in self.failure

    @property
    def tier(self):
        if self._unsupported_anion:
            return 'NOT_ASSESSED'
        return 'EXPUNGE' if self.failure else self._get('structure_pgrm_tier')

    @property
    def code(self):
        if self._unsupported_anion:
            return 'R1'
        return 'P' if self.failure else self._get('structure_pgrm_code')

    @property
    def reason(self):
        if self._unsupported_anion:
            return 'unsupported_anion'
        return ('unreadable_file' if self.failure
                else self._get('structure_pgrm_reason'))

    @property
    def evidence(self):
        if self.failure:
            return re.sub(r'^Failed to parse CIF file:\s*', '', self.failure)
        return self._get('structure_pgrm_evidence')

    @property
    def quote(self):
        name = self._get('gii_recommended')
        val = self._get('gii_recommended_value')
        if name is None or val is None:
            return None
        return name, float(val), self._get('gii_recommended_sigma')

    def explanation(self):
        from .explain import explain
        return explain(self)

    def verdict(self):
        """A few lines of plain text: the verdict and the number to quote."""
        from .explain import verdict_text
        return verdict_text(self)

    def report_html(self):
        from .report import build_report
        return build_report(self)

    def write_report(self, path=None):
        """Write the one-page HTML report; returns its path."""
        p = Path(path) if path else self.cif.with_suffix('.eir.html')
        p.write_text(self.report_html(), encoding='utf-8')
        return p

    def _repr_html_(self):
        from .report import build_report
        return build_report(self, fragment=True)

    def __repr__(self):
        q = self.quote
        qs = (f'; {q[0]} {q[1]:.3f}' if q and self.tier != 'EXPUNGE' else '')
        return f'<eir.CheckResult {self.cif.name}: {self.tier}{qs}>'


def _read_outputs(e, outdir):
    dfq = e.__dict__.get('dfq')
    dfs = None
    if dfq is not None:
        dfs = e.build_structure_table(dfq)
    summ = outdir / 'eir_summary.txt'
    ox = _latest(outdir, 'oxidation_states_used_*.json')
    return (dfq, dfs,
            summ.read_text(encoding='utf-8') if summ.exists() else None,
            json.loads(ox.read_text(encoding='utf-8')) if ox else None)


def check_folder(folder, oxidation_states=None, *, workers=None,
                 verbose=True, reports=False):
    """Run Eir on every CIF in a folder, as the notebook does, writing the
    same outputs/ folder inside it. Returns a FolderResult.

    oxidation_states  {element: valence}, written to config.json in the
                      folder (replacing any there) and used for every file
    workers           'auto' (the default), or a number; 1 runs serially
    verbose           show the run as it goes (it is recorded either way)
    reports           also write one HTML report per structure
    """
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise EirError(f'Not a folder: {folder}')
    if not list(folder.glob('*.cif')):
        raise EirError(f'No .cif files in {folder}')
    if oxidation_states:
        _write_config(folder, oxidation_states)
    e = _engine()
    summary_error = None
    with _capture(verbose) as buf, _settings(e, workers):
        e.run_pipeline(folder, steps=[k for k in e._manifest.PIPELINE
                                      if k != 'summary'])
        # CELL 15 describes the whole run. Every table is written before it
        # starts, so if it stops, the results stand and the reason is kept.
        if e.__dict__.get('dfq') is not None:
            try:
                e.run_cell('summary')
            except Exception as err:
                import traceback
                summary_error = f'{type(err).__name__}: {err}'
                print('\n  eir: the dataset summary (CELL 15) stopped: '
                      + summary_error)
                print(traceback.format_exc())
    log = buf.getvalue()
    outdir = folder / 'outputs'
    dfq, dfs, summary, ox = _read_outputs(e, outdir)
    res = FolderResult(folder, dfq, dfs, _failures(outdir, log), outdir,
                       summary, log, ox)
    if summary_error:
        res.notes.append('Dataset summary not written: ' + summary_error)
        warnings.warn('The dataset summary (CELL 15) stopped: '
                      f'{summary_error}. The tables in {outdir} are complete.',
                      RuntimeWarning, stacklevel=2)
    if reports:
        res.write_reports()
    return res


def check(cif, oxidation_states=None, *, output_dir=None, verbose=False):
    """Check one CIF and return its CheckResult.

    The file is copied into a scratch folder and run through the full
    pipeline there, so the verdict is the one a folder run would give it.
    A config.json beside the CIF is used, as a folder run would use it,
    unless oxidation_states is given.

    output_dir  keep the run's outputs/ folder (CSVs, figures, log) here
    """
    cif = Path(cif).resolve()
    if not cif.is_file():
        raise EirError(f'No such file: {cif}')
    with tempfile.TemporaryDirectory(prefix='eir_',
                                     ignore_cleanup_errors=True) as tmp:
        run_dir = Path(tmp) / 'run'
        run_dir.mkdir()
        shutil.copy2(cif, run_dir / cif.name)
        if oxidation_states:
            _write_config(run_dir, oxidation_states)
        elif (cif.parent / 'config.json').exists():
            shutil.copy2(cif.parent / 'config.json', run_dir / 'config.json')
        e = _engine()
        # Everything up to the shift test: the dataset summary and figures
        # (CELL 15) describe a collection, and say nothing about one entry.
        steps = [k for k in e._manifest.PIPELINE if k != 'summary']
        with _capture(verbose) as buf, _settings(e, workers=1):
            e.run_pipeline(run_dir, steps=steps)
        log = buf.getvalue()
        outdir = run_dir / 'outputs'
        dfq, dfs, summary, ox = _read_outputs(e, outdir)
        failed = _failures(outdir, log)
        if output_dir is not None:
            dest = Path(output_dir).resolve()
            shutil.copytree(outdir, dest, dirs_exist_ok=True)
            outdir = dest
    run = FolderResult(cif.parent, dfq, dfs, failed, outdir, summary, log, ox)
    if dfs is None or not len(dfs):
        reason = failed.get(cif.name) or next(iter(failed.values()), None)
        if reason is None:
            reason = 'the file produced no sites to assess'
        return CheckResult(cif, None, None, run, failure=reason)
    results = run.results()
    for r in results:
        r.cif = cif
    return results[0] if len(results) == 1 else results


def validate(verbose=False):
    """Run the checks the notebook runs as it loads: the structural scan of
    the source, and the known-answer and Fd-3m setting suites. Raises
    AssertionError if any fails; returns the printed record otherwise."""
    e = _engine()
    with _capture(verbose) as buf:
        e.run_checks()
    return buf.getvalue()
