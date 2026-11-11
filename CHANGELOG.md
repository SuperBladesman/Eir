# Changelog

Every surviving version of Eir, newest first, with UK dates. Each released version has a tag (`v2.0.45`, `v1.2`, ...). [docs/HISTORY.md](docs/HISTORY.md) explains how the history was recovered and what is missing.

## The eir-bvs package

### eir-bvs 2.1.0 – 11 November 2026

**A command line, a Python interface and a one-page report, on the 2.0.46 engine**

- `pip install` from GitHub; `eir check`, `eir batch` and `eir validate`
  from the command line, and `eir.check()`, `eir.check_folder()` and
  `eir.validate()` from Python.
- One structure in, one page out: the verdict in plain English, the
  evidence and code that decided it, the number to quote, the four facets,
  the six geometry screens, every site against Gagné's measured bond
  lengths, and a drawing of each coordination polyhedron.
- Oxidation states from `--ox Na=1,Mn=4,O=-2` for Rietveld output, which
  rarely carries them.
- The engine is the notebook's own cells, copied by
  `tools/build_engine.py`; CI fails if the two drift apart. No verdict, sum
  or index changes. On 200 ICSD entries every output file matched the
  notebook's, serially and in parallel (docs/PACKAGE.md).
- Tested on Python 3.11 to 3.13 with pandas 2 and 3, on Linux, Windows
  and macOS.

## Eir 2.0 series

### 2.0.46 – 11 November 2026

**Faults found while packaging Eir, by running it on the corpus, and by a battery of CIFs written the way other programs write them**

- A run in which no file has an ICSD code (every Rietveld CIF checked on its
  own), or in which a file with a code has no author or journal, no longer
  stops in `flag_same_source_entries`. Such entries are groups of one.
- The packing gates leave out positions refined to zero occupancy, and any
  pair below the floor whose occupancies sum to one or less, which the model
  can fill one at a time. The rule used to stop at 1.20 Å. A sum over one
  is allowed 0.02, or three standard uncertainties of the occupancies as
  deposited where that is more, so a model over-full only within its own
  error bars is not expunged. The sum is of each position's occupancy, all
  the species on it together: compared label by label, a lithiated
  magnetite (ICSD 155030, Fe at 0.16 on 8a beside a 16c full of Li and Fe,
  1.82 Å away) and two cation-excess magnesium ferrites (67847 and 94870,
  Mg at 0.07 on 16c beside a full 8a) passed, and stay EXPUNGE (G5). ICSD 253190,
  253192 and 261554 (P2-type sodium layered oxides, Na 2b and 2d about
  1.70 Å apart) and 291603 (CrO2, Cr on octahedral and tetrahedral
  interstices) move from EXPUNGE (G5) to FLAG (M1).
- New gate G7, `coordination_incomplete`: a dominant site with fewer
  neighbours than the smallest coordination tabulated for it, summing to
  less than half its valence, is expunged. A CIF giving only the identity
  operation for Pm-3m SrTiO3 used to come out ACCEPT with a GII of 2.07.
  On 4,806 ICSD structures (1,881 spinels, 938 perovskites, 1,254
  pyrochlores, 733 fluorites) it fires once, on ICSD 69461, a record
  already expunged on G2.
- The packing scan is given the oxidation states the CIF states, so N(3-)
  or S(2-) beside oxygen is an anion rather than a cation. 2.0.45 tested
  their bonds against the cation floor and expunged ICSD 172231 and 51587
  (Mo-N, oxynitride pyrochlores), 14955 (Cd-S, an oxysulfide pyrochlore)
  and 84078 (Zr-S, a Zr(O,S)2 fluorite) on G5. Bond selection, likewise,
  no longer pairs two species the CIF states are anions: N-O, S-O, H-O,
  Se-S and Te-S were selected as bonds, found no bond valence parameters
  and left the structure NOT_ASSESSED (R1). A hydride sharing a position
  with oxygen (the fluorite oxyhydrides LnHO) is now summed with it, as the
  other shared anions have been since 2.0.44; where the pair has no
  parameters (Ho-H, Dy-H, Er-H), the site is NOT_ASSESSED (R1) rather than
  summed without it. A valence of zero, a pair with inverted signs and an
  element typed with both signs are left to the electronegativity rule, as
  before.
- Every type symbol and label is read one way (`parse_atom_symbol`), and the
  atom_site and atom_type loops are rewritten into ICSD's own form before
  anything else reads the file (`normalise_atom_types`; an ICSD file passes
  through unchanged). 2.0.45 summed an upper-case `SN4+` as Sn(2+), stopped
  the run on `CO2+` (a scan of every line read `O2+` as oxygen at +2),
  failed on `Mn2.5+`, dropped a file with no `_atom_site_type_symbol` column
  without recording a failure, and did not recognise deuterium. Labels are
  read against the formula, so `HO1` in Mg(OH)2 is hydrogen.
- One rule decides which species are anions where no valence is stated, in
  the packing scan and in bond selection alike: an amphoteric species is a
  cation beside a more electronegative O or F, or beside a more
  electronegative amphoteric species of another group (P or As against S),
  and otherwise an anion (a sulfoselenide, a chalcohalide, a nitride
  chloride). Two such anions are no longer paired as a bond.
- A hydride given only as a supplied oxidation state (`--ox H=-1`) is now
  summed where it shares oxygen's position.
- Hydrogen sites are summed and reported but gate nothing, so a hydroxide
  refined with its H located is no longer expunged on G1 for its O-H bond.
- A Zintl anion (Sn(4-), Sb(3-); the bond valence table has no parameters
  with Sn, Sb, Ge, Pb or Bi as the anion) fails with that reason, and the
  package reports it as NOT_ASSESSED (R1, `unsupported_anion`) rather than
  as an unreadable file.
- CELL 11 no longer stops on a table with no bond lengths.
- `bl_delta_mean`, `bl_ratio_min` and `bl_delta_min` are written for every
  site, null where not computable, so the summary no longer stops on a run
  with no measured minimum (ICSD 35327, CrO2, on its own).
- **A reading stage before anything else reads a file**
  (`read_cif_structures`, CELL 3). 212 CIFs written by thirteen other
  programs (FullProf, Jana2006, Jana2020, GSAS-II, EXPGUI, TOPAS, MAUD,
  VESTA, CrystalMaker, Materials Studio, pymatgen, and COD and AMCSD files)
  failed in a handful of ways, and no way belonged to one program, so each
  step tests the file for one feature and repairs that, whoever wrote it:
  - a bond list is set aside and bonds are computed from the positions, as
    for every ICSD entry. A loop of `?` placeholders (FullProf, Jana) left
    no bonds at all, and an author's partial list (a Jana2006 Sr3LiRuO6,
    Ru-O only) left Sr and Li out of the sums;
  - each data block holding atom sites is a structure of its own, reported
    as `<file>__<block>.cif`. Only the first block was read, and the first
    block FullProf and Jana write, `global`, holds no atoms. Two blocks may
    share a name;
  - a label used for several atoms (VESTA's `XX`, CrystalMaker's shared
    sites) is made unique;
  - an unquoted value of several words is quoted, and `data_` followed by
    a space is read. An item given twice with the same value is read once;
    one given twice with different values keeps its first, unless it
    defines the structure (a cell edge or angle, the space group, an atom
    site or atom type column), when the file is not read and the reason
    names the item and both values;
  - operations listed in an origin no table holds are moved to a tabulated
    setting, with every position moved by the same vector, which is the
    same structure exactly: CrystalMaker's majorite (AMCSD 0001231) lists
    I41/a with its origin half a lattice vector out, and stopped with "No
    M-X bonds found";
  - a file with no atom sites (a GSAS-II template), atom sites written as
    single items, Cartesian coordinates only, or a block with no cell is a
    failure that says so.
  Where anything changes, the file as read is written to
  `outputs/as_read/`, and every later cell reads it there (`cif_path_for`).
  An ICSD entry is read unchanged: all 4,807 in the four corpora pass
  through byte for byte. Who wrote, refined and deposited the file is
  recorded (`cif_written_by`, `cif_refined_with`, `cif_database`), with
  `cif_read_from`, `cif_block` and `cif_reading_notes`, and decides
  nothing: 101 of the 212 had passed through COD, which rewrites what is
  deposited.
- **A polyanion's own edge is not a packing contact.** Two ligands bonded to
  the same centre and closer than the 2.35 Å floor are not tested by G2,
  and the shortest such edge is reported as `polyanion_edge_min`. Each
  centre-ligand pair (C-O, N-O, B-O, B-F, Si-O, Si-F, P-O, P-F, S-O, Se-O,
  As-O, Cl-O; `POLYANION_PAIRS`) has a longest bond and a smallest
  ligand-centre-ligand angle, set above the longest bond in structures that
  pass every other gate (C-O 1.42 Å in a pyrocarbonate bridge, N-O 1.40 Å in
  an orthonitrate). The angle keeps a crushed polyanion on the floor: a CO3
  at 70° has a 1.47 Å edge from ordinary bonds. Calcite-type carbonates were
  expunged for their CO3 edge (2.2 Å), and NaPF6 or LiBF4 would have been
  for their F-F edges (2.26 and 2.25 Å). An edge at or above the floor, such
  as the O-O edge of a silicate tetrahedron in a spinel, is tested as
  before.
- **A halogen the CIF states is positive is a cation.** Cl, Br and I were
  anions whatever the file said, so each Cl-O bond of a perchlorate,
  chlorate or chlorite was read as two anions 1.4-1.8 Å apart: 42 of 49
  ICSD lithium, sodium and potassium chlorine oxysalts were expunged on G2,
  the anion-centred sums took Cl(7+) for an anion, and bond selection paired
  the alkali cation with Cl. Two species the file states are both positive
  are no longer a bond pair. An element the file types with both signs (a
  chloride perchlorate) is left as before.
- **G1 sets aside alternative positions.** A contact below the 1.20 Å floor
  between two positions whose occupancies sum to one or less, within the
  same allowance the packing gates use, is two orientations of one group
  rather than a bond, and is listed in `alternative_contacts_set_aside`. The
  anion-centred sums leave out the same pairs. 35 of 114 ICSD nitrates and
  nitrites carried such a pair, 29 of them NaNO2, NaNO3, KNO2 and KNO3.
- **A ligand that moves with its centre is weighted given the centre.** A
  bond inside a polyanion (a `POLYANION_PAIRS` bond) counts at the far end's
  occupancy over this site's, at most one, in the cation and anion sums
  alike, because wherever a nitrite's N is, its two O are too. Every other
  bond keeps the plain occupancy. ICSD 152184, NaNO2 with N and O each at
  0.5, summed N(3+) to 1.44 and was expunged on G7 for bonds it has. Where
  the conditional weights would give a centre more ligands than it can take
  (four for ClO4, six for SiO6), or a ligand more than two centres, the
  model spreads one group over more positions than any orientation fills,
  and the plain occupancies stand: high-temperature cubic NaClO4 (ICSD
  117375) would otherwise have summed Cl(7+) to 53. The ligands weighted
  given their centre are listed in `ligand_occupancy_conditional`.
- **Two monovalent cations may come closer.** The cation floor was measured
  on perovskites, pyrochlores and spinels and expunged Li2O and Li3N on G5
  for Li-Li contacts of 2.31 and 2.10 Å. A floor scaled by ionic radius does
  not separate these from the faults G5 exists for: Li3N sits at 1.38 times
  the radius sum, inside the 1.06 to 1.40 of the perovskites it condemns.
  Charge does. A pair of cations of charge one or less (an alkali metal
  whatever the file says) is held to 2.00 Å (`MONOVALENT_PAIR_MIN`); any
  other pair stays at 2.40 Å. The contact that decides, with its floor, is
  reported as `cation_cation_contact`.
- **Mobile ions on partly filled positions are a FLAG** (M11,
  `mobile_ions_close`), not an EXPUNGE: a contact below the floor between
  two monovalent cations whose positions are both partly filled, as the
  mobile ion of an ionic conductor often is, is read as positions never
  filled together, whatever the refined occupancies sum to. A full position
  beside it, or a cation of higher charge, still gives G5
  (`cation_contact_partly_occupied` says which). Li10GeP2S12 written by
  VESTA (Li 0.691 on positions 1.73 Å apart) leaves EXPUNGE, and is
  NOT_ASSESSED (R3) for want of measured Li-S lengths; no ICSD entry of the
  5,676 changes on it.
- **Molecular carbon is NOT_ASSESSED** (R1, `molecular_carbon`). Carbon
  bonded to C, H or N (a MOF linker, an organic or hybrid perovskite cation,
  a cyanide, a carbide's C2 unit) is outside what bond valence sums
  describe. 39 such structures among the 212 came out EXPUNGE on G7, G1 or
  G2, or failed; the reason now names the bond. A carbonate, or a carbide's
  isolated carbon, is assessed as before.
- **The bond valence table is checked against its sources.** 32 entries
  labelled Brown (2020) are in none of the 2009, 2011 and 2020 releases of
  Brown's compilation; all came from the hand-compiled table of 1.0, and
  none records a source. Fourteen of those pairs now take Brown's row by the
  merge rule (V2+-O 1.79 to 1.70 Å, Yb2+-O 2.08 to 1.989, Ni3+-O 1.70 to
  1.75, Hg+-O 1.74 to 1.90, Os4+, W4+, Tc4+, S2+ and six actinide pairs);
  eighteen have no Brown row and are removed (Pr4+-O, Re4+ and Re6+-O,
  U3+-O, Ag2+-O, Ra2+-O and others). Seventeen entries were Brown rows for
  an anion charge other than Eir's (Pr3+-Se(1-) used for Pr3+-Se(2-),
  Fe3+-C(2+) for C(4-)): two take the row at the ordinary charge and
  fifteen are removed; three more were not cation-anion pairs. 1,385
  entries to 1,349; the 36 removed are kept, with their values and why, in
  `Data/bvs_parameters_excluded.json`. Each entry now records
  `anion_charge` and `brown_code`, the loader leaves out one fitted for
  another anion charge, and `tools/audit_bv_table.py` checks the table
  against Brown's file.
- **Chen and Adams (2017) fill gaps and replace unpublished values.** Their
  softNC1 parameters (IUCrJ 4, 614, Table S1), fitted to 15,523 ICSD
  cation environments over the first coordination shell, enter by the same
  merge rule as any other published source: 105 for pairs nothing else
  covers (Re4+ and Re6+-O, Ag3+-O, Au+-O, Dy3+-S, Yb2+-S, many selenides,
  tellurides, arsenides and phosphides) and 73 in place of Brown's private
  communications (Ni3+-O, V2+-O, Co2+-S, Mn2+-S, Cr3+-S, P5+-F and others).
  Pairs fitted to fewer than three environments are left out. 1,349 entries
  to 1,454. On the ordered sites of the test sets that use a replaced pair,
  the median deviation from valence falls from 16.4% to 2.5% for Ni3+-O
  (the RNiO3 nickelates), 26.7% to 6.7% for Co2+-S, 20.5% to 5.2% for
  Ru6+-O and 14.4% to 9.8% for Cr3+-S. No verdict changes on the 4,806, the
  870 or the 200; the GII changes on 216 entries, nine of them ACCEPT or
  FLAG; three NOT_ASSESSED entries (two thiospinels and a telluride) move
  from R1 to R3.
  On the 212, two GaAs files move from R1 to R3, and Hf2S (pymatgen, a
  metal-rich subsulfide given Hf(4+)) from R1 to EXPUNGE on G7. Tried in
  place of Brese and O'Keeffe's extrapolated rows too, softNC1 was better
  for some pairs and worse for others, so those stay.
- **Equal-rank rows take the more recent fit; Np4+-O from Gilson and Burns
  (2021).** Where two published sources of equal rank differ, the table
  takes the more recent, unless Brown restricts it to a context ("from
  transition metal complexes"): Pu4+-O Diwu et al. (2010) in place of
  Zachariasen (1978), Sm2+-O Trzesowska et al. (2006), Cu3+-N Mahapatra et
  al. (1996). Np4+-O takes Gilson and Burns (2021), Coord. Chem. Rev. 445,
  213994, refitted on well-refined Np(IV) structures (R0 2.054 Å, b 0.417).
  No other published fit was found for Pr4+-O, U3+-O, Np3+-O or Ra2+-O,
  which stay R1. Six corpus entries change GII, all NOT_ASSESSED: NpO2
  0.2% to 2.5% from valence, PuO2 1.2% to 0.6%.
- A cation with no parameters for its anion at any valence is NOT_ASSESSED
  (R1). It used to be dropped, and a file whose only pair it was failed as
  unreadable: RaO, or W2C and Mo2C among the 212, which are now R1. An anion
  the table has nothing for (a Zintl anion, boron in a boride) is left out
  as before.
- On the 4,806 ICSD structures of the four sets no verdict changes. 44
  NOT_ASSESSED entries change their reason from R3 to R1: 37 Pr4+ oxides
  (31 fluorites, 6 perovskites), two U3+ pyrochlores, one Pm oxide and four
  spinels with ICSD's unspecified metal M. The GII changes on 152, of which
  10 are ACCEPT or FLAG: five LiNi0.5Mn1.5O4 and NiAl2O4 spinels (Ni3+),
  two Pr pyrochlores, two uranium fluorites and one LaVO3. Brown's values
  move the Os4+ and Tc4+ perovskites from GII 0.41-0.76 to 0.09-0.32; his
  Ni3+-O, a private communication and the only one he lists, puts the
  rare-earth nickelates RNiO3 at 3.4-3.7 for a valence of 3, where the
  unsourced 1.70 gave 2.9-3.2; Chen and Adams's published fit, below, now
  replaces it. On the 870 ICSD exports, five iodine azide
  entries that failed as unreadable now expunge on G2 with the other
  azides; on the 212, W2C and Mo2C are R1; on the 200, no verdict changes.
- The structural self-check scans its own notebook. It took the newest
  notebook in the folder that mentioned EIR_VERSION anywhere, so with Huginn
  3.9.3 beside it (which names the Eir version it reads) it scanned Huginn
  and reported every function missing, and in a folder of several Eir
  versions it could scan the wrong one. It now takes the notebook Jupyter
  names in JPY_SESSION_NAME, or else the newest whose code sets this
  EIR_VERSION. Found on NRM's first Windows run of 2.0.46, whose outputs on
  53 fluorites otherwise match the cloud run of the same commit in every
  column.
- The GII takes each label's element from its type symbol before its first
  letters. CrystalMaker labels the Si on majorite's octahedral position
  `MgOc2`; the index took magnesium's sum for it, and post-processing
  stopped on its own consistency check. ICSD labels lead with their element,
  so there the two agree.
- `eir.check()` on a file holding several structures returns one result per
  structure, including any that cannot be read, and the one-page report
  says how the file was read. A run in which nothing can be read still
  writes the failed-files table.
- On the 212: EXPUNGE 40 to 8, the ACCEPT tiers 57 to 75, NOT_ASSESSED 17
  to 65 (each with its reason), and "No M-X bonds found" 77 to 50, which
  are the elements, alloys and intermetallics, with no anion to bond to.
  On the 4,806 ICSD structures of the four sets nothing changes in any
  column: no entry needs the reading stage, none holds a polyanion edge
  below the floor or molecular carbon, and every label leads with its
  element.
- On 870 ICSD entries exported to test the halogen, alternative-position,
  conditional-weight, polyanion and lithium changes (polyanion salts,
  lithium oxides and nitrides, and anions bonded to each other):
  EXPUNGE 570 to 459, ACCEPT and FLAG 204 to 290, NOT_ASSESSED 72 to 97.
  Li3N 33 expunged to 3, Li2O and related lithium oxides 18 to 4,
  perchlorates, chlorates and chlorites 44 to 3, nitrates and nitrites 43
  to 22 (21 to NOT_ASSESSED: no measured N(3+)-O bond lengths), carbonates
  45 to 41. Peroxides, superoxides, disulfides, polysulfides and azides do
  not change (see the README's known limitations). On the 200 no verdict
  changes; on the 4,806 only the two magnesium ferrites under the packing
  gates; the G5 evidence of 26 entries now names the pair and its floor.
- 29 VALIDATE tests, four gate tests and 43 parsing tests in CELL 7b
  (`VALIDATE_GATES()`, `VALIDATE_PARSING()`, which need the gates defined),
  seventeen end-to-end parsing cases in `tests/test_parsing.py`, 29
  end-to-end reading cases in `tests/test_reading.py` and seven on the
  parameter table in `tests/test_parameters.py`, which fail on the commit
  before the table was corrected (552f19c). The new tests fail on
  2.0.45, apart from the controls: one parsing test and six of the
  seventeen cases, which 2.0.45 already got right. The first sixteen reading
  cases also fail on 2.0.46 as it stood before the reading stage, and the
  13 added or changed since (halogens, alternatives, polyanion limits,
  repeated items, the lithium floor, the conditional weight, positions and
  mobile ions) on 2.0.46 as it stood before them; one more is a control. On 200 ICSD
  entries the only verdicts that change are the four structures named under
  the packing gates; the sulfoselenide spinel 640368 stays NOT_ASSESSED
  (R1), now for the In-Se pair it has no parameters for rather than a Se-S
  "bond".

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
