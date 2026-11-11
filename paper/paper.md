---
title: 'Eir: bond valence screening of crystal structures, with an integrity verdict'
tags:
  - Python
  - crystallography
  - bond valence
  - crystal structure validation
  - data integrity
  - ICSD
authors:
  - name: Nik Reeves-McLaren
    orcid: 0000-0002-1061-1230
    affiliation: 1
affiliations:
  - name: School of Chemical, Materials and Biological Engineering, University of Sheffield, United Kingdom
    index: 1
    ror: 05krs5044
date: DRAFT
bibliography: paper.bib
---

# Summary

Crystal structures are the starting point for much of materials science. They are used to explain properties, to seed calculations and, increasingly, to train machine-learning models. Most are taken from databases such as the Inorganic Crystal Structure Database (ICSD) [@Zagorac2019], which hold hundreds of thousands of entries refined over more than a century, by every method and program in use at the time. Few users have the time to check the entries they download.

The bond valence model [@Brown2009] offers a physical check. Each bond of length $R$ is given a valence $s = \exp[(R_0 - R)/b]$, where $R_0$ and $b$ are fitted to well-determined structures, and the valences of the bonds around an ion should sum to its oxidation state. The global instability index (GII) [@SalinasSanchez1992] summarises how far a whole structure departs from this.

Eir applies that check to crystallographic information files (CIFs) at database scale. It asks first whether a structure can be assessed at all (can the file be read, can the atoms be where it puts them, is there reference data, and is the model unambiguous) and only then computes bond valence sums and the GII. Every structure receives a verdict (ACCEPT, FLAG, NOT_ASSESSED or EXPUNGE) with the reason and the measurement that decided it. Eir runs as a Jupyter notebook, or as the Python package `eir-bvs` with a command line and a one-page report per structure.

# Statement of need

Errors in deposited structures are rarely corrected, and as structural databases become training data for machine learning they propagate into models that cannot see them [@ReevesMcLaren2026Integrity]. Peer review looks at one refinement at a time; faults that only show across many related entries, or in entries deposited decades ago, pass unnoticed, and nobody checks hundreds of thousands of structures by eye.

Bond valence sums are cheap to compute, but a sum is only as good as the bond lengths and parameters behind it, and a wrong coordinate can produce a good-looking number. ICSD 85235 (TbCrO~3~) has a CrO~6~ octahedron within 0.0004 Å of the mean of every measured Cr^3+^–O bond and a GII of 0.0047 v.u. It also has two oxygen atoms 2.191 Å apart, against a family median of 2.750 Å. Judged on its bond valence sums it is the best of 938 perovskites; judged on its geometry it cannot exist. A screening tool must therefore establish that a structure can be assessed before it reports a sum, and must say why when it cannot.

Eir is for anyone who needs to know which entries in a set of CIFs can be trusted before using them: database curators, those assembling training sets for machine learning, and researchers checking their own Rietveld refinements before deposition.

# State of the field

Several programs compute bond valence sums. SoftBV [@Chen2019], whose parameters were fitted for crystal structure plausibility tests [@Chen2017], and its pathway analyser [@Wong2021] use bond valence site energies to map ion-migration pathways and to screen fast-ion conductors. The `BVAnalyzer` class in pymatgen [@Ong2013] uses bond valence sums to assign oxidation states to a structure. checkCIF and PLATON [@Spek2009; @Spek2020] validate a single refinement at deposition, and flag outliers in geometry, displacement parameters and refinement statistics. None is designed to screen a database: to read CIFs written by many programs over many decades, to decide which entries can be assessed, and to say why the rest cannot.

Eir builds on existing work where it can. It reads CIFs and expands symmetry with gemmi [@Wojdyr2022], and takes its parameters from published compilations and fits [@Gagne2015; @Brown2020; @Chen2017; @Gilson2021]. What it adds is the layer that decides whether a sum should be computed at all, and that layer rests on choices that differ from those of a general-purpose library. Eir does not infer oxidation states from the bond valence sums it is checking, because that would make the check circular; in pymatgen, assigning oxidation states is the purpose of the bond valence module. Adding the verdict logic to such a library would mean reversing its defaults, so I built it as a separate tool that uses the libraries for what they do well.

# Software design

**Geometry before chemistry.** Eir assesses four facets in order, and the first failure stops the assessment: Parse (can the file be read?), Geometry (can the atoms be where the file puts them?), Reference (is there reference data?) and Model (is the deposited description unambiguous?). A failure on P or G gives EXPUNGE, meaning no bond valence result should be quoted; on R, NOT_ASSESSED, meaning part of the analysis is missing rather than wrong; on M, FLAG, meaning the analysis holds, with the ambiguity named. Six independent geometry screens feed the G and M facets (radius ratio, bond valence distance, anion and cation packing, missing bonds, and a half-lattice shift). The shift screen proposes and never corrects: each proposed shift is applied to a copy of the CIF and the whole analysis re-run, so a reported wrong origin is a hypothesis tested and held. The tiers are integrity gates, not a bond valence pass or fail; no gate fires on the GII, which is reported for the user to judge against the structural family.

**Fail loudly.** A silent fallback produces plausible numbers from the wrong chemistry, so Eir avoids them. Where a CIF carries no oxidation states, as Rietveld output rarely does, the notebook asks for them and the package stops and names the elements that need one. A cation with no parameters for its anion stays in the structure and is reported as NOT_ASSESSED, rather than being dropped and leaving a sum that looks complete. CIFs are read by feature: each repair (a placeholder loop, a repeated label, several structures in one file) is made because the file shows that feature, whichever program wrote it, and is recorded. Author-supplied bond lists are set aside, and every bond is computed from the positions.

**Reference data with provenance.** Every bond valence parameter records its source and the anion charge it was fitted for. The table takes Gagné and Hawthorne [-@Gagne2015] first, then Brown's compilation of published values [@Brown2020] by a stated order of precedence, then the softNC1 fits of Chen and Adams [-@Chen2017] where at least three environments were fitted. A script checks every entry against its published source, and entries removed from the table are kept, with their values and the reason, in a separate file. Expected bond lengths come from Gagné's bond length surveys [*e.g.* @Gagne2020], and radii from Shannon [-@Shannon1976].

**One engine, two ways in.** The engine's source is the notebook `Eir.ipynb`, read and run cell by cell by students and by anyone who wants to see how a verdict was reached. The package is built from those cells, with every edit the build makes listed and none changing a result; continuous integration fails if the two drift apart, and on 200 ICSD entries every output of the package matched the notebook's. This is unusual, and it costs a build step. I kept it because the notebook is where a reader can follow the reasoning, and the package is where the same reasoning runs at scale and is tested.

**Tests built from failures.** The notebook carries 29 known-answer tests and further suites for CIF parsing and the gates; the package adds 83 test cases. Many began as a structure that Eir once got wrong. All use small synthetic structures, because ICSD files are licensed and cannot be redistributed. Tests run on Linux, Windows and macOS, with Python 3.11 to 3.13 and with pandas 2 and 3. Each threshold in the code is annotated with the measurement that set it, or marked where there is none.

# Research impact statement

Eir 1.2 underpinned a systematic study of 840 rock salt structures from the ICSD, which characterised the ways bond valence validation fails, from parameter inadequacy to database quality issues [@ReevesMcLaren2026Dalton]. Later versions screened 1,244 ambient-condition spinel structures [@ReevesMcLaren2026Spinels] and the oldest entries in the ICSD [@Gross2026]. Reports of faulty entries from these studies have been sent to FIZ Karlsruhe, which maintains the ICSD; FIZ Karlsruhe has deleted, or is deleting, 141 entries (about 4.3% of those analysed).

Version 2.0.46 was tested against 4,806 ICSD structures in four families (1,881 spinels, 938 perovskites, 1,254 pyrochlores and 733 fluorites), 870 further ICSD entries chosen to test particular chemistries, and 212 CIFs written by thirteen other programs, with every change in a verdict between releases traced to its cause. Releases from 2.0.46 onwards are archived on Zenodo.

# AI usage disclosure

[DRAFT FOR NRM TO SETTLE. Models and versions: to confirm, *e.g.* Anthropic's Claude models through claude.ai and Claude Code, from Eir 1.0 (December 2025) to 2.0.46.]

Eir was developed with generative AI from its first version. I framed each problem, made the design decisions described above (the order of the facets, not inferring oxidation states from the sums being checked, the precedence of parameter sources, reading CIFs by feature), and decided how each fault would be fixed; the AI wrote code and documentation to that specification. Correctness was checked independently of the code that produced it: against known-answer tests, against the published sources of every reference value, by manual review of flagged structures in the published studies, and by regression of each release against the last on thousands of ICSD entries, with every change in a verdict traced to a cause. This paper was drafted with [model] and revised by me. I have reviewed, modified and validated all AI-generated content.

# Acknowledgements

[To confirm: funding, if any, for the work behind Eir.] I thank the students and colleagues in my group whose structures and questions exposed faults that later versions fixed.

# References
