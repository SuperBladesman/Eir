# How this history was rebuilt

Until November 2026 this repository held two uploads: Eir 1.2, on 16th December 2025, with the results of the rock salt study, and Eir 2.0.41, on 14th September 2026, which replaced it. The reference tables the notebook reads (`Data/`) were kept alongside it rather than uploaded, and every version in between, and since, was kept as a dated copy on the author's own storage.

The history was rebuilt from those copies. It has one commit for every surviving version, in the order the versions were made, dated when each was made. Every released version has a tag.

## Sources

- **The working copies.** Eir was developed as a Jupyter notebook, with each version saved as a new file (`Eir 1.3.ipynb`, `Eir_2_0_17.ipynb`, ...). More than seventy of these survive, from 1.0 (December 2025) to 2.0.45 (October 2026).
- **Delivered copies.** Four versions (1.8.6, 2.0.10, 2.0.44 and the first build of 2.0.13) survive only as the copy first delivered, before any run.
- **The original repository.** The 16th December 2025 commits are reproduced with their own times and content: the licence, the first README, `requirements.txt`, Eir 1.2, the rock salt results, `.gitignore` and the description of the data files. The README edit of 14th September 2026 is reproduced too.
- **The reference data.** See "Data" below.

The 1.2 and 2.0.41 notebooks recovered from the working copies have code identical to the copies uploaded to GitHub.

## How the commits are dated

Each commit carries the time its file was last saved. Where a file was saved again after work on the next version had started, usually because it was being re-run, the commit is dated to the start of the next version instead, and its message says so. Two dates come from better evidence: 1.2 is dated to its upload to GitHub, and 2.0.45 to the morning it was issued, because the copy saved later differs only in its run output.

The final two commits, which move the rock salt results into `paper_data/` and add this documentation, are the only ones made at the time of the rebuild.

## What is missing

- **0.1 to 0.4**, the development versions before 1.0, were not kept.
- **1.8.3** was not saved as a file of its own. Its main change, a Shannon radius lookup for fractional valences, is in 1.8.4.
- **2.0.11 and 2.0.12** were never saved as files of their own. Their changes are in the first build of 2.0.13.
- **2.0.1** was rebuilt over one day, 14th August 2026, and survives as five working copies; all five are here. A sixth copy, saved three days later, already holds the first 2.0.2 changes, and is committed as such.

## The 1.7 draft

A 1.7 draft from April 2026 added pre-flight checks and a visual summary report. Development carried on from 1.6 instead, through 1.6.1 to 1.7.0, so the draft is kept as a single commit on its own tag, `v1.7-draft`, and was never merged.

## Superseded versions

2.0.28, which parallelised the post-processing cell, was superseded the next morning by 2.0.29, which restored the anion-centred sums in the parallel workers. The Bond_Str indices added in 2.0.39 were completed in 2.0.40.

## What was changed for release

Every notebook in the history has been put through the same normalisation, and nothing else:

- outputs and execution counts cleared, because some saved copies ran to 97 MB of results;
- cell metadata removed, and notebook metadata reduced to a standard Python 3 kernel;
- one stable file name, `Eir.ipynb`, in place of a new name for each version, so that `git log -p Eir.ipynb` shows what changed between versions. The original file name is given in each commit message;
- personal names and local paths replaced wherever they appeared: "on [a student's] P2 phases" in a comment became "on a set of P2 layered oxides"; a regression note naming a student's fluorite and pyrochlore sets now gives their sizes only; local file paths in the scratch cells of 1.8.9, 2.0.0 and 2.0.6 became `path/to/`; and a file-name prefix naming a student's dataset became `dataset_CollCode`. Commits containing such an edit say so.

That prefix is the only edit that touches code. From 1.8.1 to the first build of 2.0.13 it was used to shorten file names in the printed report, so the only effect is on how files carrying that prefix are labelled there. Nothing else in the code was changed.

## Data

`Data/` enters the history in the state each table was in when it was used, as far as the surviving copies show:

- `shannon_radii.json`, `common_oxidation_states.json` and `element_categories.json` were last changed in August 2025, before 1.0, and are unchanged throughout.
- `bvs_parameters.json` has four states. 1.0 and 1.1 ran on the 168-pair metal–oxygen set that preceded the merge of 8th December 2025; it survives as `bvs_parameters_deprecated.json` in a copy of the folder taken on 19th December 2025, and that is what the 1.0 commit holds. The merged set of 1,384 pairs is committed from the same copy and dated to the merge. The set of 31st January 2026 adds Fe⁴⁺–O, and stood until 2.0.46. 2.0.46 corrects it against Brown's bvparm2020 (Data/README.md): 32 entries labelled Brown (2020) are in none of the 2009, 2011 and 2020 releases of Brown's compilation; all came from the 168-pair set of 1.0, and 20 more were rows for another anion charge or not cation–anion pairs. Sixteen take Brown's values and 36 are removed, and are kept with their reasons in `bvs_parameters_excluded.json`. Every result before 2.0.46 that involves one of those 52 pairs was computed with the old values.
- `gagne_bond_lengths.json` was added on 21st August 2026 for 2.0.4 and is unchanged since.
