# Contributing to Eir

Eir is maintained by Nik Reeves-McLaren at the University of Sheffield, alongside research and teaching. Issues and pull requests are read and answered as time allows; there is no guaranteed response time.

## Reporting a structure Eir gets wrong

A structure Eir gets wrong is the most useful report there is. Many of the fixes in the changelog began as one, and each became a test. Please open an issue with:

- the version: `eir --version` for the package, or `EIR_VERSION` at the top of the notebook, and which of the two you ran;
- your Python and pandas versions (`python -c "import sys, pandas; print(sys.version, pandas.__version__)"`);
- the structure. For an ICSD entry, give its collection code rather than attaching the CIF: ICSD files are licensed by FIZ Karlsruhe and should not be posted publicly. For your own refinement, attach the CIF if you are free to share it, with the oxidation states you used (`--ox`);
- what Eir reported (tier, reason and code, or the error) and what you expected, and why.

Questions about what a verdict means are welcome as issues too. [Reading the results](README.md#reading-the-results) in the README and the one-page report (`eir check`) answer most of them.

## Changing the code

`Eir.ipynb` is the source of the engine. The package's cells in `src/eir/_cells/` are copied from it by `tools/build_engine.py`, and CI fails if the two differ, so edit the notebook, never the copied cells. [docs/PACKAGE.md](docs/PACKAGE.md) explains how the two relate.

1. Edit `Eir.ipynb` and raise `EIR_VERSION`. Add a `VALIDATE()` test, or a case in `tests/`, that fails before your change and passes after it.
2. Run `VALIDATE()` in the notebook.
3. Copy the cells into the package: `python tools/build_engine.py`.
4. Install and test under pandas 2 and pandas 3, which change text handling: `pip install -e ".[test]"`, then `eir validate` and `python -m pytest`.
5. Show that the notebook and the package still agree on a folder of CIFs you know: `python tools/equivalence.py FOLDER`.
6. Describe the change in `CHANGELOG.md`, under the new version: what was wrong, what changed, and what it does to results.

Changes to the reference tables in `Data/` need a published source, named in [Data/README.md](Data/README.md). An entry taken out of `bvs_parameters.json` goes into `bvs_parameters_excluded.json` with its values and the reason, and `python tools/audit_bv_table.py` (which needs Brown's `bvparm2020.cif` from the IUCr) must pass.

Never commit files that cannot be redistributed: ICSD CIFs, Brown's parameter files, or supporting information from papers. The tests use small synthetic structures for this reason.

## Releases

Each release is tagged (`v2.0.46`) and published as a GitHub release, which Zenodo archives with its own DOI. Before tagging, date the changelog entry, update `version` and `date-released` in `CITATION.cff` and `version` in `.zenodo.json`, and after Zenodo has archived the release, add its DOI to `CITATION.cff` and the README. `tests/test_release.py` checks that the versions agree.

## Licence

By contributing you agree that your contribution is released under the [MIT licence](LICENSE).
