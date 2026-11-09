# The eir package and the notebook

From 2.1.0, Eir can be installed with pip and run from the command line or from Python. This page explains how the package relates to `Eir.ipynb`, what it does differently, and how it was shown to give the notebook's results.

## One engine, two ways in

The notebook is still the source of the engine. `tools/build_engine.py` copies each of its code cells into `src/eir/_cells/`, one file per cell, and the package loads them in notebook order into one namespace, as Jupyter does. Every function the notebook defines is therefore available, unchanged, as `eir.engine.<name>`:

```python
import eir
eir.engine.look_at(85235, dfq=result.sites)
eir.engine.PGRM_TIER_MEANING
```

The version the engine reports, `EIR_VERSION`, is the notebook's, and it is what the output files are named after (`eir_batch_results_v2.0.46_...`), so Huginn reads a package run exactly as it reads a notebook run. The package has a version of its own (`eir-bvs 2.1.0`), because it adds a command line and a report but changes no result.

`python tools/build_engine.py --check` fails if the cells in `src/eir/_cells/` are not the notebook's. CI runs it on every push.

## What the package does differently

Every difference is listed here, and the build tool lists the edits it makes to the cells. None of them changes a verdict, a sum or an index.

**On loading**

- The cells' printed output while loading is kept in `eir.engine.IMPORT_LOG` rather than shown, because every worker process in a parallel batch loads the engine.
- The structural self-check (CELL 1c), `VALIDATE()` and `VALIDATE_SETTINGS()` are not run on loading, for the same reason. `eir validate` (or `eir.validate()`) runs all three. The structural self-check scans the packaged cells in notebook order, as it scans the saved notebook.
- The reference tables are read from the package (`eir/data`, built from `Data/`) rather than from `./Data` in the working directory. `EIR_DATA_DIR` overrides this.
- The cell that installs py3Dmol with pip is left out; py3Dmol is an optional dependency (`pip install "eir-bvs[viz]"`).

**When it runs**

- The actions in CELLS 9 to 15 run when `eir.check_folder()` is called, in notebook order, with the folder passed in rather than picked from a dialog. Each run starts from the state the engine had on loading, as Restart & Run All would; settings such as `EIR_WORKERS` are kept.
- CELL 10 (provenance) prints only and runs before the table it reads exists, and CELLS 16 and 17 wait for a code to be typed in, so none of the three runs. Their functions are all available.
- The interactive oxidation-state prompt is replaced by an error naming the elements that need a state (`OxidationStatesNeeded`). Pass the states with `--ox` or `oxidation_states={...}`, or put a `config.json` beside the files; both are written as the `config.json` the notebook reads, and override the file.
- `eir.check()` copies the one file into a scratch folder and runs CELLS 9 to 13b there. It stops before CELL 15, the dataset summary and figures, which describe a collection rather than one entry.
- `eir.check_folder()` runs CELL 15 last. If it stops, every table has already been written, so the run is kept and the reason is recorded in `result.notes`.

## The report and the plain-English verdict

`eir check` and `CheckResult.verdict()` print the verdict; `CheckResult.write_report()` writes a one-page HTML report. Both read the engine's columns and decide nothing themselves:

- the tier and its meaning (`structure_pgrm_tier`, `PGRM_TIER_MEANING`);
- the reason, as a sentence, and the evidence and code beside it (`structure_pgrm_reason`, `structure_pgrm_evidence`, `structure_pgrm_code`);
- the number to quote (`gii_recommended`, `gii_recommended_value`, `gii_recommended_sigma`), struck through for EXPUNGE;
- the four facets, the six geometry screens, the per-site table and the anion sums;
- a drawing of every cation position's coordination polyhedron, from the symmetry expansion the sums use (`_viz_local_environment`);
- provenance: versions, oxidation states and their source, parameters and settings.

One note is added where the columns call for it, without changing the verdict: if a geometry screen failed but the verdict does not rest on it, the report says so.

## How the equivalence was shown

`tools/equivalence.py FOLDER` runs the notebook headless on one copy of a folder and the package on another, and compares every CSV in the two `outputs/` folders cell by cell, and the summary, oxidation-state record and run log line by line (less timings). Before 2.1.0 was proposed it was run on 200 ICSD entries: oxide and sulfide spinels, LiNi₀.₅Mn₁.₅O₄, rock salt KCl, CuCl and ZnO, cubic and tetragonal (Ba,Sr)TiO₃, NaFeO₂, sodium layered oxides in R3̄m and P6₃/mmc, and chromium oxides. They were run as one folder and as four separate subsets, and the 200 serially and with two worker processes. Every output was identical. The 200 and the examples were compared again on engine 2.0.46, which runs the examples through the notebook for the first time; again every output was identical.

ICSD entries cannot be redistributed, so CI cannot repeat this. It checks instead that the cells are the notebook's, runs the known-answer suites, and tests the package on the three constructed structures in `examples/`. Run `tools/equivalence.py` on your own sets after changing the engine.

## Changing the engine

1. Edit `Eir.ipynb`, and bump `EIR_VERSION` in its first cell.
2. Run it, and `VALIDATE()`, as before.
3. `python tools/build_engine.py` to copy the cells into the package. If it stops, an edit it makes no longer matches the notebook; update `PLAN` in the tool.
4. `pip install -e ".[test]"`, then `eir validate` and `python -m pytest`, under pandas 2 and pandas 3.
5. `python tools/equivalence.py` on a folder you know.
6. Commit the notebook and `src/eir/_cells/` together.
