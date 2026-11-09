# Changelog

Every surviving version of Eir, newest first, with UK dates. Each released version has a tag (`v2.0.45`, `v1.2`, ...). [docs/HISTORY.md](docs/HISTORY.md) explains how the history was recovered and what is missing.

## Eir 2.0 series

### 2.0.45 – 23 October 2026

**The standard continuous shape measure**

- cshm is now the continuous shape measure of Pinsky and Avnir as SHAPE
  reports it, minimised over translation, rotation, scale and every pairing
  of ligands with reference vertices (T-4, SP-4, OC-6, TPR-6), so the
  result is independent of ligand order and starting orientation.
- Reproduces the published distances (octahedron to trigonal prism 16.737,
  tetrahedron to square 33.333).
- Reported only: no tier, code or sum uses cshm.
- 24 VALIDATE tests.

### 2.0.44 – 19 October 2026

**Shared anion sites, per-label valences, a void guard**

- An anion position shared by two species (O/F, O/N, O/S) is summed over
  every species on it, each with its own occupancy, R0 and b.
- Where a CIF lists one element at two valences, each label is summed at
  the valence it reports.
- For soft-b ions (Os5+, Re5+) a shell stops at a 1.5x void when the
  contacts beyond it are longer than any bond Gagné records for that ion.
- 23 VALIDATE tests. On a 733-entry fluorite set and a 1,254-entry
  pyrochlore set, 95 structures change, each attributable to one of these
  three changes.

### 2.0.43 – 9 October 2026

**Fractional and unparameterised valences**

- A fractional valence (ICSD's U4+ 4.064) is checked at the integer
  valences either side, which the calculation already interpolates
  between. This matters for 73 entries of a 733-entry fluorite set.
- An integer valence with no parameters (Th5+) keeps its cation, so the
  site is reported as R1 by name.
- 19 VALIDATE tests.

### 2.0.42 – 6 October 2026

**Actinide valences**

- Bond-type selection checks parameters at the structure's own valences,
  so Ac, Pa, Np, Pu, Am, Cm, Bk, Cf and Po, which are absent from
  common_oxidation_states.json, are assessed wherever parameters exist.

### 2.0.41 – 27 August 2026

**Image-merge tolerance in ångströms**

- site_multiplicities merges symmetry images within an absolute distance
  rather than 0.02 fractional (0.17 Å in an 8.4 Å spinel cell), so a site
  close to a special position stays distinct from it.
- The Bond_Str columns reach the per-structure CSV.
- PGRM_IMPRECISE_SIGMA re-examined and kept; the note on vacancies
  clarified in three places; the nitride bond-length reference added.

Uploaded to GitHub on 14th September 2026.

### 2.0.40 – 26 August 2026

**Bond_Str indices completed**

- The Bond_Str indices use Eir's existing site_multiplicities, resolving a
  name clash introduced in 2.0.39.

### 2.0.39 – 26 August 2026

**The Bond_Str family of instability indices**

- gii_bondstr_old, _a, _b and _c, named for what Bond_Str prints, plus the
  occupancy-weighted discrepancy used before 1.7.5.

Completed in 2.0.40.

### 2.0.38 – 25 August 2026

**Cell parameter uncertainties**

- The cell's esds now reach the bond lengths, so structures with every atom
  on a fixed special position (all 503 rock salts in the WAGII set) carry
  the uncertainty of their cell.

### 2.0.37 – 25 August 2026

**The freeze version**

- PGRM_PREMODERN_YEAR moved from 1980 to 1950, by measurement.
- index_imprecise per structure and cn_shell_confidence per site.
- within_element_z, _flag and _n retired; IMPLAUSIBLE_FRACTION deleted.
- R4 no_index; wagii_sigma.

### 2.0.36 – 24 August 2026

**M10, polyhedron size against the ion**

- A fourth question about distance, and the first not about the shortest
  bond: is the whole polyhedron too small or too large for the ion in it?
  ICSD 160115 (Y2Sn2O7) has a regular SnO6 at 1.946 Å against Gagné's
  2.054(24) Å, and a BVS of 6.00 against 4.

### 2.0.35 – 24 August 2026

**One symmetry expansion throughout**

- The six places that expand the asymmetric unit into a neighbour list now
  share one routine, which wraps images into the cell and sizes the
  translation block to cover the full search sphere. The first version in
  the series to change the headline numbers.

### 2.0.34 – 24 August 2026

**Outputs/latest.txt**

- Each run writes latest.txt naming its version, stamp, output stem and
  structure count, so the newest results can be found without sorting
  filenames.

### 2.0.33 – 24 August 2026

**Gii_recommended_value follows the shell correction**

- gii_recommended_value is refreshed after the shell correction, so it
  always matches the index that gii_recommended names (186 of 3,291
  structures updated), with the original kept as
  gii_recommended_value_uncorrected. No tier count changes.

### 2.0.32 – 24 August 2026

**Shell correction extended to the site-averaged indices**

- apply_shell_correction recomputes the site-averaged indices as well as
  gii and wagii (ICSD 15787), keeping gii_site_averaged_uncorrected. 138 of
  151 withheld sigmas now resolve; coverage 3,266 of 3,291 structures.

### 2.0.31 – 24 August 2026

**ACCEPT_IMPRECISE**

- Sigmas for the site-averaged and recommended indices, so that the caveat
  tier covers the whole corpus, and the largest esd on any coordinate.
- ACCEPT_IMPRECISE, a caveat tier for sound structures whose index
  carries a large uncertainty.

### 2.0.30 – 24 August 2026

**Uncertainties from the deposited esds**

- Deposited standard uncertainties propagated to bond valence: bvs_sigma
  per site and gii_sigma per structure, with their sources and the number
  of refined parameters. No existing column changes.

### 2.0.29 – 24 August 2026

**Anion-centred sums in the parallel workers**

- The anion-centred sums run in the parallel workers, restoring
  gii_all_sites.

This version produced the frozen numbers for the three-family study: 3,291
perovskites, pyrochlores and spinels.

### 2.0.28 – 23 August 2026

**CELL 11 in parallel**

- CELL 11 parallelised, with one scheduler instead of three.

Superseded by 2.0.29, which restores the anion-centred sums in the
parallel workers; the equivalence harness identified the difference.

### 2.0.27 – 23 August 2026

**CELL 9 in parallel**

- The batch runs over as many workers as the machine supports: CELL 9
  went from 20 min 58 s to 3 min 19 s with seven workers.

### 2.0.26 – 23 August 2026

**Faster merging of duplicate points**

- Three linear scans for "is there already a point within tol of this one"
  replaced; outputs proved identical by an equivalence harness.

### 2.0.25 – 23 August 2026

**Named caveat tiers**

- ACCEPT_HOMOVALENT and ACCEPT_HETEROVALENT, so the tier says what the
  caveat is and anyone can filter on it.
- gii_recommended; one definition of the tier list.

### 2.0.24 – 23 August 2026

**A progress feed for CELL 11**

### 2.0.23 – 23 August 2026

**M8 and the shell correction refined**

- M8 applies to the dominant species on a site.
- apply_shell_correction recomputes the distance ratio.
- M8 defers to cn_fault where that is already set.
- Parameters looked up for the actual anion.

### 2.0.22 – 23 August 2026

**M8 and G6**

- M8 shortest_contact_implausible, the bond-valence distance screen, as a
  flag rather than a gate.
- G6 contact_below_measured_minimum, against Gagné's measured minima, as a
  gate.

### 2.0.21 – 22 August 2026

**Correct shells that reach the second sphere**

- apply_shell_correction() replaces the sum only where all three hold: the
  shell reached the outer sphere, Gagné measured the boundary for that ion
  configuration, and an adaptive sum exists.

### 2.0.20 – 22 August 2026

**Shells that reach the second sphere**

- Li on the spinel 8a site has four oxygens near 2.0 Å and twelve beyond,
  and the shell was reaching into the second sphere. A spread test now
  marks cn_fault = shell_reaches_outer_sphere. Measured on 938
  perovskites, 472 pyrochlores and 1,881 spinels.

### 2.0.19 – 22 August 2026

**Formula labels in the batch feed**

- Formulae shown in full up to 20 characters, and a shortened one ends in
  '~'.

### 2.0.18 – 22 August 2026

**A batch feed that names the file first**

- Each file's block now starts with its name, distinct markers separate
  steps from results, and the full per-site stream goes to a log.

### 2.0.17 – 22 August 2026

**Flagged and tested sites counted separately**

- n_within_element_flagged counts flagged sites (204 on the pyrochlores),
  and n_within_element_tested reports how many could be tested.

### 2.0.16 – 22 August 2026

**Two new columns exported**

- A new column renamed to keep it distinct from the existing
  gii_all_sites; both new columns reach the CSV; a guard checks for name
  collisions.

### 2.0.15 – 22 August 2026

**Contact floor applied before the sum**

- The absolute contact floor is applied before the shell and sum are
  built, not recorded afterwards.
- Fd-3m origin choices 1 and 2 checked and confirmed.
- The cation floor no longer applies to hydrogen; an explicit import gemmi
  in CELL 1.
- The summary describes the radii-ratio screen's role more precisely.
- Six new tests; all 16 built-in tests pass.

### 2.0.14 – 22 August 2026

**Packing screen refinements**

- The pair filter and the distance bucket now agree.
- The search window (rmax = 4.0 Å, scaled for oxides) is stated
  explicitly.
- Exceptions in the screen are reported rather than returned as empty
  results.

### 2.0.13 – 22 August 2026

**Cell-by-cell audit; new introduction**

- PGRM gates replace the BVS-derived tier throughout; cation-cation
  packing floor; measured bond lengths; the adaptive shell boundary
  exported.
- Normaliser translations and origin-choice offsets derived from the space
  group rather than hard-coded.
- A per-structure table and four figures.
- Every bare except narrowed, five duplicated definitions consolidated, the
  Huginn export retired.
- A new introduction: what Eir asks, in what order, and why.

### 2.0.13 (as first built) – 22 August 2026

**Eir 2.0.13, first build (with 2.0.11 and 2.0.12)**

- 2.0.11: tiers are no longer derived from the BVS; this cell computes
  evidence and PGRM classifies it afterwards. Read failures are recorded
  and reported.
- 2.0.12: a structural self-check cell (1c); the cation-cation packing
  floor used as a gate (59 structures across three families, 19 of them
  seen by no other screen); the anion's free positional parameter reported.
- 2.0.13: the geometric eccentricity and the bond-valence vector sum
  reported as separate quantities.

2.0.11 and 2.0.12 were never saved as files of their own.

### 2.0.10 – 22 August 2026

**One verdict per structure**

- The A-to-F quality tier and the INCLUDE / CAUTION / EXCLUDE
  recommendation, derived from the BVS and GII, retired in favour of the
  PGRM gates, so each structure carries a single verdict. CELL 10 reports
  provenance and oxidation-state alternatives.

### 2.0.9 – 22 August 2026

**PGRM integrity gates**

- Four facets asked in order, the first failure stopping the assessment:
  Parse, Geometry, Reference, Model. Severity is decided by the geometry
  before any chemistry is read, so a structure with a physically
  impossible contact (ICSD 220506 has a La-O contact of 1.008 Å) is
  identified as such rather than judged by the sum it produces.

### 2.0.8 – 22 August 2026

**Interpolate across CN; seed from the canonical shell**

- Expected lengths interpolated across coordination number, as for the bond
  lengths themselves (30 of 77 test sites had fallen through to the fit).
- The adaptive shell is seeded from the canonical shell. Seeded from the
  gap shell, Mn in ICSD 11616 stayed at CN 2 with a BVS of 7.21.

### 2.0.7 – 22 August 2026

**Adaptive bond-valence cut-off, reported**

- An adaptive cut-off, reported but not canonical; a single cut-off had
  given Li+ a coordination number of 16.

### 2.0.6 – 22 August 2026

**Half-lattice shift screen generalised**

- Allowed translations derived from each structure's own symmetry; groups
  that admit too many (P1 and the like) stand the screen down.
- Each site compared at its own CN rather than an assumed six.
- Named fields in place of a positional tuple, and the screen reports
  whenever it stands down.

### 2.0.5 – 21 August 2026

**Observed against measured bond lengths, reported**

- Each bond compared with Gagné's measured range in ångströms. Reported,
  never flagged: an extreme-value screen needs large samples, and the
  high-CN configurations are exactly the small ones.

### 2.0.4 – 21 August 2026

**Measured bond lengths; measurement tools**

- Expected bond lengths from Gagné's survey, with Shannon additivity as the
  flagged fallback (bl_source says which).
- A measurement-tools cell that changes no result: each tool answers a
  question about the analysis by measuring it.

### Data – 21 August 2026

**Add Gagné's measured bond lengths**

Mean bond lengths from refined inorganic structures, per ion
configuration, aggregated by O. C. Gagné (596 configurations, 202 ions,
bonded to O2- and N3-). Source and references are recorded in the file's
_metadata block.

### 2.0.3 (revision 4b) – 21 August 2026

**Radii-ratio threshold follows the new shell**

- Under the bond-valence shell perovskite A sites sit at CN 12, not 8 or 9,
  so the radii-ratio threshold's slope with CN was re-derived rather than
  carried over.

### 2.0.3 – 21 August 2026

**The bond-valence coordination shell**

- The canonical shell is every neighbour reaching BV_SUM_CUTOFF, an
  absolute distance per ion pair, rather than the largest gap; the
  ECoN-weighted sum, which needs no shell, is reported beside it.
- An absolute contact floor is tested before anything else (rule 1), and a
  site with no parameters leaves a record (rule 2).
- CIF bytes repaired before gemmi sees them (rule 0); parse failures keep
  their reason; bare excepts narrowed.

### 2.0.2 – 21 August 2026

**Anion engine, new screens, dual shell**

- Anion-centred BVS engine: multiplicity-weighted means, the worst site and
  what coordinates it, a bond-valence (not distance) termination.
- Anion-anion packing screen; anions decided from the structure rather
  than a fixed list.
- Coordination plausibility (missing bonds) and half-lattice shift screens;
  each shift proposal is applied to a copy and the analysis re-run
  (CELL 13b).
- Coordination shell guard: the gap CN is kept only where ECoN agrees, and
  a dual-shell sum over the full distance shell is reported beside it.
- Radii-ratio screen rewritten on the full Shannon table (the old table had
  no lanthanides) with a CN-dependent threshold.
- Sites refined to zero occupancy excluded from the GII.
- WAGII and site-averaged GII, with the index to quote chosen per
  structure; the A-site radii override retired.
- Cell 1b renumbered so that two cells can no longer both be "CELL 2"; a
  self-check confirms each cell completed.

### 2.0.2 (first cells) – 17 August 2026

**Eir 2.0.2, first cells (saved as Eir_2_0_1 (6))**

- The first 2.0.2 changes, added to the 2.0.1 notebook, starting with how
  the coordination shell is decided: in the broad, distorted shells of
  perovskite A sites the largest gap in the bond list is not always the
  shell boundary.

### 2.0.1 – 14 August 2026

**Rebuilt on a single gemmi parse**

- pymatgen removed; one gemmi parse feeds everything.
- Native per-site geometry schema: coordination geometry, distortion
  indices, polyhedral volume, off-centring, bond-valence vector sum and
  continuous shape measure.
- Within-element outlier pass, and the per-polyhedron geometry file written
  from the native columns.

The same code was saved again as "Eir_2_0_1 (5).ipynb" on 17th August.

### 2.0.1 (working copy 4) – 14 August 2026

**Native geometry**

- Native per-site geometry: ECoN, shell CN, bond angles, geometry
  classification and distortion indices, computed without pymatgen.

### 2.0.1 (working copy 3) – 14 August 2026

**Quiet output by default**

- VERBOSE switch: the per-structure debug stream is off by default; result
  lines, deviation warnings and the 3D views are always shown.

### 2.0.1 (working copy 2) – 14 August 2026

**Structure-type analysers removed**

- The spinel and other structure-type analysers taken out of Eir.

### 2.0.1 (working copy 1) – 14 August 2026

**The rebuild begins**

First of the copies saved on 14th August 2026, the day of the rebuild on a
single gemmi parse.

### 2.0.0 – 13 August 2026

**A general structure assessment**

- A new assessor that reports geometry true of any structure and makes only
  the judgements that are pure physics. Structure-type judgements are left
  to a structure-aware tool downstream (Huginn).
- Large A-site cations handled correctly by geometry_plausible.
- A per-polyhedron geometry table written for downstream tools.

## Eir 1.x series

### 1.8.9 – 11 August 2026

**Last of the 1.x line**

- Symmetry images deduplicated by true separation rather than snapped
  coordinates, so images either side of a grid boundary merge correctly.
- Each anion species tested against its own radius in the radii screen, so
  sulfides and other non-oxides are screened on their own terms.
- Per-atom CIF valences reach the batch as well as single structures.

### 1.8.8 – 28 July 2026

**Rounding; distinct column names**

- Values rounded before they are stored or compared.
- Core columns renamed core_* so that they stay distinct from the
  post-processor's columns of similar meaning.

### 1.8.7 – 27 July 2026

**Charge-balance tolerance; EIR_VERSION**

- Charge-balance tolerance raised from 0.01 to 0.05, so formulae quoted to
  two decimals (Na0.67Ni0.33Ti0.67O2 computes to 4.0100) balance within
  rounding, while an imbalance of a third of a valence unit is still
  caught.
- A single EIR_VERSION constant at the top of the notebook.

### 1.8.6 – 27 July 2026

**Clearer handling of unusual CIFs**

- CIFs that declare only _space_group_IT_number are read.
- A site with no bonds is reported as such, not as a CIF parse error.
- A negative occupancy is reported as a data error rather than clamped to
  zero.
- The viewer falls back to the first coordination shell.

### 1.8.5 – 27 July 2026

**Built-in validation suite; rebuilt site viewer**

- VALIDATE(): reference structures with answers known by hand, generated
  on the fly and self-calibrating, so that parsing, symmetry expansion,
  coordination, the sum, the GII and occupancy weighting are tested
  independently of the parameter file. Run it after any change.
- The 3D viewer draws the polyhedron Eir actually counted, with the
  distance on each bond and the next neighbours shown faintly.

### 1.8.4 – 27 July 2026

**CIF valences used in bond classification**

- Element-level valences from the CIF are passed to classify_bond_pair, so
  its explicit-valence rule is used in preference to the electronegativity
  heuristic.
- Geometry fields record which ligand species they describe.
- Shannon radius lookup with fractional valences. That lookup was written
  for 1.8.3, which does not survive as a separate file.

### 1.8.2 – 27 July 2026

**Diagnosis detail, all-site GII, in-run percentile**

- bvs_diagnosis_detail splits both_deviate on whether any polyhedron is
  distorted, separating Jahn-Teller strain from structural or data faults.
- gii_all_sites, the all-atom convention, beside the cation-only gii.
- gii_percentile_in_run: each structure's place within its own dataset,
  since the 0.20 v.u. rule of thumb does not hold for over-constrained
  families such as spinels.

### 1.8.1 – 27 July 2026

**Numbered cells; ECoN; observational diagnoses**

- The notebook reorganised into thirteen numbered cells.
- max_bond_distance raised from 3.5 to 4.2 Å. At 3.5 Å the shell boundary
  in layered oxides often lay outside the candidate list; on a
  142-structure test set this corrected 122 of 965 cation sites to CN 6.
- Hoppe's effective coordination number (ECoN), a Shannon-radii
  plausibility test, and observational labels in place of the interpretive
  bvs_diagnosis. Thresholds are written to cfg_* columns, so every output
  CSV records how it was made.

### 1.8.0 – 27 July 2026

**Anion-centred bond valence sums**

- The sum at each anion site, over its neighbouring cations, weighted by
  cation occupancy and with no gap cut. A cation-only BVS cannot tell a
  parameter offset from real strain; the anion sum can.
- Symmetry images merged by a 0.02 Å distance tolerance, not a grid, and
  only within a label, so both species on a mixed site survive.
- Self-test on two generated CIFs.

### 1.7.5 – 27 July 2026

**Hand-calculated test of the GII correction**

- _test_gii_fix(): three sites worked by hand. All fully occupied, GII =
  WAGII = 0.1354 and gii_legacy = 0.0800; with the Na sites half occupied,
  GII is unchanged and WAGII = 0.1392.

### 1.7.4 – 27 July 2026

**Jahn-Teller axial recovery; GII to the published definition**

- For strong Jahn-Teller octahedral cations the largest gap in the bond
  list is the equatorial-axial gap. The axial pair is now restored when it
  sits within MAX_JT_AXIAL_RATIO of the equatorial mean, while genuine
  square-planar and square-pyramidal sites are left alone.
- GII and WAGII now follow the published root-mean-square definitions
  (Salinas-Sanchez et al., J. Solid State Chem., 1992, 100, 201). The index
  reported under that name by earlier versions, a valence-normalised mean
  absolute deviation (sum|S - V| / sum V), is retained as gii_legacy for
  comparison with earlier results. The code labels this change 1.7.5; it
  was first saved in this file.

### 1.7.3 – 24 July 2026

**Generalised anion positional parameters**

- Anion positional parameters generalised beyond the spinel u, with u_eff
  checked for every space group.

### 1.7.2 – 17 May 2026

**Anti-site disorder; repeat entries from one paper**

- A minority species is no longer EXPUNGEd when the same element is the
  majority on another site (anti-site exchange, e.g. Na/Ti between layers).
- A dataset-level pass flags several entries from the same source paper.

### 1.7.1 – 13 May 2026

**Version number only**

No change to the analysis: the title and a blank line.

### 1.7.0 – 10 May 2026

**Data integrity tiers (ACCEPT, FLAG, EXPUNGE)**

- Every site and structure is given a tier for how far its BVS can be
  trusted.
- Site occupancies extracted and minority species identified.
- New columns: integrity_tier, flag_reason, occupancy, is_minority_species,
  and a structure-level tier summary.
- Version banner updated (it still read 1.5).

### 1.6.1 – 7 May 2026

**CIFs in the reverse rhombohedral setting**

- Older ICSD CIFs written in the reverse (HR) setting are relabelled and
  their symmetry operators regenerated from the space group number, so that
  gemmi can read them.

### 1.6 – 24 April 2026

**Fractional valences; non-stoichiometric spinels**

- Fractional valences kept (Mn 3.5 in LiMn2O4), preferring the _atom_type
  loop value over the symbol.
- Bond valence parameters interpolated between the neighbouring integer
  valences.
- Spinel inversion computed only for stoichiometric AB2X4; other
  compositions report the site distribution instead.
- Duplicate structural parameter columns consolidated;
  B_site_small_cation_fraction added.

### 1.7 draft – 20 April 2026

**Pre-flight checks and a visual summary (not continued)**

- Pre-flight cell: Python and library versions, data files and CIF format
  detection, before any batch is run.
- A visual summary report: figures and a structured text summary.

Development carried on from 1.6 instead (1.6.1, then 1.7.0), so this draft
sits on its own tag, v1.7-draft, and was never merged.

### 1.5 – 1 April 2026

**Flagging refinements**

- The Type 6 (pre-modern structure) flag now fires as intended.
- Type 5 disorder detection reads the occupancy string.
- Element symbols parsed in full from formulae, so Sr, Si, Sm and Sc are
  no longer read as sulfur.
- Oxidation-state logging made robust; one version string throughout.

### 1.4.2 – 31 March 2026

**Per-atom valences for mixed-valence structures**

- Per-atom valences from the CIF take priority, so Fe2+ and Fe3+ on
  different sites are summed separately; valence_source records where each
  valence came from.
- The GII iterates over site labels rather than elements.
- WAGII, the occupancy-weighted index, reported beside the GII.
- Type 8 flag: Shannon radius deviation above 7% on fully occupied,
  single-cation sites.
- ICSD citation fields that run over several lines (long journal names) are
  parsed correctly.

### Data – 31 January 2026

**Add the Fe4+-O bond valence parameters**

Fe(IV)-O, R0 = 1.78 Å, b = 0.37 (Brown 2009, Table 2). 1,385 pairs.

### 1.4 – 30 January 2026

**Oxidation states from the CIF; Type 7 flags; spinel parameters**

- Oxidation states read from the CIF (_atom_type loop, or symbols such as
  Fe3+), with a charge-balance check.
- Type 7 flags for missing or ambiguous valences, flags for Types 2 to 6 per
  structure, and a CSV of problem files for review.
- Spinel analyser: anion u parameter, cell parameters and Wyckoff symbols
  with multiplicities.

### 1.3 – 28 January 2026

**4+2 Jahn-Teller octahedra and real site occupancies**

- A CN 4 result with two further bonds within 25% of the first-shell mean
  is recognised as a 4+2 Jahn-Teller octahedron and counted as six.
- Occupancy strings built from the CIF's own occupancies rather than an
  equal split between the species on a site.
- Each cation-anion pair checked for parameters before it is used.
- Optional structure-type analysers (cell 3.5).

### 1.2 – 16 December 2025

**The version published with the rock salt study**

- Measurement temperature and pressure read from each CIF (pressure in kPa,
  as the CIF standard has it) and classified, so that ambient-condition
  structures can be separated from the rest.
- Bond selection across several anion types, using the merged parameters.
- Fixes: each element matched to its own label on mixed sites;
  'poor_metals' renamed 'post_transition_metals'.

This is the code behind Reeves-McLaren, Dalton Trans., 2026, 55, 2868
(DOI 10.1039/D5DT03003J): 840 rock salt structures from the ICSD.

### 1.1 – 8 December 2025

**Config files, 3D site viewer, adaptive gap detection**

- Oxidation states from a config.json in the CIF folder, so a batch runs
  without prompts; interactive entry remains the fallback.
- py3Dmol view of any site whose BVS deviates by more than 30%.
- Adaptive gap detection for Jahn-Teller distorted sites (Mn3+, Cu2+), and
  Jahn-Teller ion detection.
- ICSD publication metadata and a geometry validation step in the output.

### Data – 8 December 2025

**Merged bond valence parameters (1,384 cation-anion pairs)**

Gagné and Hawthorne (2015) merged with Brown's 2020 compilation, keeping
for each pair the best-graded source: Gagné and Hawthorne first, then Brown
and Altermatt (1985), then Brese and O'Keeffe (1991). 1,384 cation-anion pairs over 17 anions, against 168
metal-oxygen pairs before, which is what made the halides and chalcogenides
of the rock salt study assessable.

The file was created on 8th December 2025 and next changed on 31st January
2026. The content committed here is from a copy taken on 19th December
2025, the closest surviving copy.

### 1.0 – 5 December 2025

**Bond valence sum analysis of ICSD and GSAS-II structures**

- Batch bond valence sums (BVS) and global instability index (GII) for a
  folder of ICSD CIFs, or GSAS-II refinement output (.lst with its .cif).
- Coordination number from gap analysis of the sorted bond list, with a
  0.05 Å minimum gap.
- Mixed and partial occupancy on a site (e.g. Cr0.8Ti0.2).
- Symmetry expanded over a 3x3x3 supercell so that atoms on special
  positions in R-3m and P6_3/mmc are handled correctly.
- Data/ holds the Shannon radii, common oxidation states and element
  categories (unchanged since August 2025) and the 168-pair metal-oxygen
  bond valence parameter set that preceded the merge of 8th December
  (it survives as bvs_parameters_deprecated.json).

The development versions before this one (0.1 to 0.4: GSAS-II only, mixed
occupancy, first ICSD support, a supercell experiment) were not kept.
