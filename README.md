# Eir

**Bond valence screening of crystal structures, with an integrity verdict.**

[![Licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
[![Paper: Dalton Trans. 2026](https://img.shields.io/badge/paper-Dalton%20Trans.%202026%2C%2055%2C%202868-informational.svg)](https://doi.org/10.1039/D5DT03003J)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Version 2.0.46](https://img.shields.io/badge/version-2.0.46-green.svg)

Eir reads a folder of CIF files and asks two questions of each structure:

1. **Can this entry be assessed at all?** Can the file be read, can the atoms be where it says, is there reference data, and is the deposited model unambiguous?
2. **If so, what does the bond valence model say?**

The order matters. A bond valence sum is computed from bond lengths, so a length that cannot be right makes every number built on it meaningless, and often good-looking. ICSD 85235 (TbCrO₃) has a chromium octahedron within 0.0004 Å of the mean of every measured Cr³⁺–O bond, a global instability index (GII) of 0.0047, and two oxygens 2.191 Å apart against a family median of 2.750 Å. Judged on its chemistry it is the best structure in a 938-entry perovskite set; judged on its geometry it is impossible.

Eir was written to screen the Inorganic Crystal Structure Database (ICSD) at scale. Version 1.2 accompanied the rock salt study in *Dalton Transactions* (2026). The current version, 2.0.46, is a rebuild that checks the geometry before it reads the chemistry.

## What Eir checks

Four facets, asked in order. The first failure stops the assessment.

| | Facet | Asks | On failure |
|---|---|---|---|
| **P** | Parse | Can the file be read? | EXPUNGE |
| **G** | Geometry | Can the atoms be where the file puts them? | EXPUNGE |
| **R** | Reference | Is there reference data to assess it? | NOT_ASSESSED |
| **M** | Model | Is the deposited description unambiguous? | FLAG |

EXPUNGE means no bond valence result should be quoted. NOT_ASSESSED means part of the analysis is missing, not wrong. FLAG means the analysis stands, with the ambiguity named. A structure that passes all four is ACCEPT, or one of three named caveat tiers: ACCEPT_HOMOVALENT and ACCEPT_HETEROVALENT for shared sites, and ACCEPT_IMPRECISE where the deposited uncertainties make the index imprecise.

`structure_pgrm_tier` holds the verdict, `pgrm_reason` what failed, and `pgrm_evidence` the measurement that decided it.

These gates replace and contain the six-type failure taxonomy of the *Dalton Transactions* paper (Type 2 → R1, 3 → M1, 4 → M3, 5 → M2, 6A → M6, 7 → M4). What they add is the G facet. The taxonomy was derived on rock salts, where every atom sits on a special position and a coordinate error is impossible by construction; in every family with positional freedom, geometry faults dominate.

Six independent geometry screens feed the G and M facets, reported separately because they see different things:

| Screen | What it sees |
|---|---|
| Radii ratio | Shortest cation–anion contact against the Shannon radii |
| Bond-valence distance | The same contact against the ion's own parameters |
| Anion–anion packing | Two anions closer than their electron clouds allow |
| Cation–cation packing | The same for the cation sublattice |
| Coordination | Whether bonds are missing, rather than too short |
| Half-lattice shift | Whether a cation sits on the wrong origin |

The shift screen proposes and never corrects. Each proposal is applied to a copy of the CIF and the whole analysis re-run, so `cation_on_wrong_origin` means the hypothesis was tested and held.

## Getting started

You need Python 3.11 or later. Eir is tested with Python 3.11 to 3.13 and with pandas 2 and 3, on Linux, Windows and macOS.

```bash
pip install "git+https://github.com/SuperBladesman/Eir.git"
```

### Check one structure

```bash
eir check examples/MgO.cif
```

```
MgO.cif  ·  Mg O  ·  F m -3 m

  ACCEPT               Nothing wrong found
  Bond valence         Quote GII = 0.049 ± 0.000 v.u.

  Report               examples/MgO.eir.html
```

The verdict comes first, in plain English, then the number to quote. Beside the CIF Eir writes a one-page report: the verdict and what decided it, the four facets, the six geometry screens, every site against the bond lengths measured for that ion, and a drawing of each coordination polyhedron.

Most Rietveld programs write element symbols without charges, and Eir does not guess oxidation states. Give them with `--ox`, or put a `config.json` beside the file:

```bash
eir check refined.cif --ox Na=1,Ni=2,Mn=4,O=-2
```

Try it on the constructed structures in [examples/](examples/): `MgO.cif` passes, `MgO_wrong_cell.cif` carries a lattice parameter as a transcription error might, and `SrTiO3_refined.cif` needs `--ox Sr=2,Ti=4,O=-2`.

### From Python

```python
import eir

r = eir.check('examples/SrTiO3_refined.cif', oxidation_states={'Sr': 2, 'Ti': 4, 'O': -2})
r.tier, r.code                 # ('ACCEPT', '-')
r.quote                        # ('gii', 0.1774, 0.00033): the index to quote, its value, its sigma
print(r.verdict())
r.write_report()               # examples/SrTiO3_refined.eir.html; in Jupyter, r on its own shows it
```

### A folder of CIFs

```bash
eir batch my_cifs/ --reports
```

This runs the same pipeline as the notebook, on every CIF in the folder, and writes the same `outputs/` folder inside it (below), with one report per structure in `outputs/reports/` if asked. From Python, `eir.check_folder('my_cifs/')` returns the per-site and per-structure tables.

### Check the installation

```bash
eir validate
```

runs the 28 tests against structures whose answers are known by hand, the four gate tests, the 43 parsing tests (type symbols, labels, bond lists, data blocks and symmetry as other programs write them, polyanions, molecular carbon, anions, hydrogen, halogens stated positive, alternative positions, the lithium floor, mobile ions) and the structural self-check. Run it again after changing anything.

### The notebook

`Eir.ipynb` is the source of the engine, and still runs as before:

```bash
git clone https://github.com/SuperBladesman/Eir.git
cd Eir
pip install -r requirements.txt jupyterlab
jupyter lab Eir.ipynb
```

1. **Run the cells from the top.** Eir reads its reference tables from `Data/`, so start Jupyter in the repository folder.
2. **Check the installation.** CELL 6 runs `VALIDATE()`. It raises if any test fails.
3. **Point it at your CIFs.** CELL 9 asks for a folder and processes every CIF in it. Oxidation states come from a `config.json` in that folder, from the CIF itself, or interactively:

   ```json
   {"Na": 1, "Ni": 2, "Mn": 4, "O": -2}
   ```

4. **Post-process.** CELLS 10 to 15 add provenance, coordination quality and the integrity gates, the per-structure table, triage, the shift tests, figures and the summary report. CELLS 16 and 17 look at one structure, or one family, in detail.

The package runs the notebook's own cells, and gives its results file for file. [docs/PACKAGE.md](docs/PACKAGE.md) explains how, lists everything the package does differently, and describes how the two were compared.

ICSD CIFs work as downloaded. Eir repairs the common faults in ICSD exports (non-ASCII bytes, reverse rhombohedral settings, symmetry given only as a space group number) before it parses anything.

## What a run produces

Results are written to an `outputs/` folder inside the CIF folder:

```
outputs/
  eir_batch_results_v<version>_<stamp>.csv      per site, raw
  ..._quality.csv                               per site, screened
  ..._structures.csv                            one row per structure
  eir_batch_failed_v<version>_<stamp>.csv       parse failures, with reasons
  eir_summary.txt                               the narrative summary
  eir_shift_test_<stamp>.csv + shifted_cifs/    the audit trail for proposed shifts
  eir_screens, eir_gii, eir_cation_anion,
  eir_gii_vs_wagii (.pdf and .png)              figures
  latest.txt                                    which run is the newest
  reports/<name>.eir.html                       one page per structure (--reports)
```

`_structures.csv` filtered to `structure_pgrm_tier == 'EXPUNGE'` is the list of reportable errors. Each row carries the ICSD code, year, journal, reason and measurement.

## Reading the results

- **The tiers are integrity gates, not a bond valence pass or fail.** No gate fires on the GII, and ACCEPT structures can carry a high one. If the question is whether structures "fail BVS", choose a GII criterion and apply it to the ACCEPT tiers.
- **Quote `gii_recommended_value`.** Eir reports three instability indices: `gii` weights every site equally, `wagii` weights by occupancy, and `gii_site_averaged` combines the sums on a shared site first. They agree whenever every cation site carries the same occupancy. `gii_recommended` names the right one for each structure, and the summary states the choice for the dataset.
- **The GII is cation-only.**
- **ACCEPT_HETEROVALENT means a valence span of 2 or more on one position**, so Y³⁺/Zr⁴⁺ and Gd³⁺/Ce⁴⁺ count as homovalent.
- **GII thresholds depend on the family.** The often-quoted 0.20 v.u. comes from simple ordered structures; spinels and many perovskites routinely exceed it while being perfectly stable. Read the number against the family, and always beside the tier.
- **Parameters:** Gagné and Hawthorne (2015), with Brown (2020) as fallback; not Brown and Altermatt (1985). This matters for any comparison with published GII values.
- **Every threshold carries its measurement** in the comment beside it. Where one does not, the comment says so.

## Reference data

`Data/` holds the five tables Eir reads: bond valence parameters, Gagné's measured bond lengths, Shannon radii, common oxidation states and element categories. [Data/README.md](Data/README.md) gives the source of each.

## Versions

The current engine is **2.0.46**, packaged as **eir-bvs 2.1.0**, which adds the command line, the Python interface and the report without changing a result. The last released engine is 2.0.45 (23rd October 2026). Every surviving earlier version is tagged, from `v1.0` (December 2025) onwards, and [CHANGELOG.md](CHANGELOG.md) describes each one.

To reproduce the rock salt study, use the version that accompanied it:

```bash
git checkout v1.2
```

The machine-readable results of that study are in [paper_data/](paper_data/). From 1.7.4 the GII follows the published root-mean-square definition; the 1.7.4 entry in the changelog describes the index reported before that, which Eir still reports as `gii_legacy`.

The history in this repository was rebuilt in 2026 from dated copies of every version. [docs/HISTORY.md](docs/HISTORY.md) explains how, and lists what is missing.

## Known limitations

- Two ICSD entries, 213392 and 38769, are not yet caught by the gates.
- The packing gates (G2, G5) leave out positions refined to zero occupancy and any pair of positions the model can fill one at a time, whose occupancies sum to one or less. Where a close pair's occupancies sum to more than one, some such pairs must be filled together, so the model implies the contact and the gate stands. Anion-disorder models refined that way, such as pyrochlores with oxygen on the 8b site beside a nearly full 48f, are still expunged; review them by hand.
- G7, which expunges a site missing bonds, was set on the 200-entry regression set, where it fires on nothing. On 4,806 ICSD spinels, perovskites, pyrochlores and fluorites it fires once, on ICSD 69461, which G2 already expunges.
- Anions bonded to each other (peroxides, superoxides, disulfides such as pyrite, polysulfides, azides) are expunged on G2 for their own O-O, S-S or N-N bond, and their cations would be summed with parameters fitted for O(2-), S(2-) or N(3-), which on these compounds put cation sums up to 55% over valence. Cations bonded to each other (hyponitrite and dinitramide N-N, closo-borate B-B) are expunged on G5 the same way. Read any verdict on such a structure as not assessed.
- On a position shared by two anions, the coordination-quality columns written by CELL 7 (`contact_anion`, `expected_contact`, `shortest_contact_ratio`) describe the first-listed species. The bond valence sums use every species.
- An ion with no measured bond lengths in Gagné's survey is reported as NOT_ASSESSED (R3). Transuranic ions, Pa, fluorides, N³⁺ (nitrites), Pr⁴⁺, Tc⁴⁺, Tc⁵⁺ and Ru⁶⁺ are among them.

Each will gain a `VALIDATE()` test as it is addressed.

## Citing Eir

If you use Eir, please cite the paper:

> N. Reeves-McLaren, Automated Bond Valence Sum Analysis for Crystallographic Database Quality Assessment: A Systematic Study of Rock Salt Oxides, Halides, and Chalcogenides, *Dalton Trans.*, 2026, **55**, 2868. https://doi.org/10.1039/D5DT03003J

and name the version you used. [CITATION.cff](CITATION.cff) has both in machine-readable form, and GitHub's "Cite this repository" button reads it.

Please also cite the sources of the reference data: Gagné and Hawthorne (2015) for the bond valence parameters, and Gagné's bond length surveys (listed in `Data/gagne_bond_lengths.json`).

## Licence

MIT, © Nik Reeves-McLaren, University of Sheffield. See [LICENSE](LICENSE).

Questions and bug reports are welcome as GitHub issues.
