# Reference data

Eir reads five tables from this folder, and a sixth file records what was taken out of one of them. Keep the folder beside `Eir.ipynb`, or start Jupyter in the repository folder. The installed package carries a copy of this folder as `eir/data`; set `EIR_DATA_DIR` to use another.

| File | What it holds | Source |
|---|---|---|
| `bvs_parameters.json` | Bond valence parameters R0 and b for 1,454 cation–anion pairs over 13 anions, keyed `('Mn', 4, 'O')`. Each entry records the anion charge it was fitted for (`anion_charge`); Brown's rows give their reference code (`brown_code`), and Chen and Adams's the number of environments fitted (`n_environments`) | Gagné and Hawthorne (2015) where they give a value; otherwise Brown's 2020 compilation (bvparm2020); otherwise, or where Brown has only an unpublished value, Chen and Adams (2017, softNC1); Fe⁴⁺–O from Brown (2009) and Np⁴⁺–O from Gilson and Burns (2021). Each entry names its source in `reference`. |
| `bvs_parameters_excluded.json` | The 126 entries taken out of or changed in `bvs_parameters.json` in 2.0.46, with the values they had and why (a pair changed twice keeps the earlier value under `replaced_before`). Eir does not read it. | |
| `gagne_bond_lengths.json` | Mean, standard deviation, minimum and maximum bond lengths, and sample sizes, for 596 ion configurations bonded to O²⁻ and N³⁻ | Gagné's aggregated bond length surveys. The `_metadata` block lists the six papers and the source page. |
| `shannon_radii.json` | Effective ionic radii by element, valence and coordination number | Shannon (1976) |
| `common_oxidation_states.json` | The usual oxidation states of each element, used only where neither the CIF nor a `config.json` gives one | Compiled for Eir |
| `element_categories.json` | Element groups (alkali metals, 3d transition metals, lanthanides, ...) | Compiled for Eir |

The values are published measurements and fits. If you use them, please cite the original sources:

- O. C. Gagné and F. C. Hawthorne, *Acta Cryst.*, 2015, **B71**, 562–578.
- H. Chen and S. Adams, *IUCrJ*, 2017, **4**, 614–625 (softNC1 parameters, supporting information Table S1).
- S. E. Gilson and P. C. Burns, *Coord. Chem. Rev.*, 2021, **445**, 213994 (Np⁴⁺–O, section 2.3).
- H. Diwu *et al.*, *Inorg. Chem.*, 2010, **49**, 3337–3342 (Pu⁴⁺–O, as listed by Brown).
- I. D. Brown, *Chem. Rev.*, 2009, **109**, 6858–6919.
- I. D. Brown, bond valence parameter compilation (bvparm2020), International Union of Crystallography.
- The bond length surveys: O. C. Gagné and F. C. Hawthorne, *Acta Cryst.*, 2016, **B72**, 602–625; O. C. Gagné, *Acta Cryst.*, 2018, **B74**, 49–62; O. C. Gagné and F. C. Hawthorne, *Acta Cryst.*, 2018, **B74**, 63–78 and 79–96; O. C. Gagné and F. C. Hawthorne, *IUCrJ*, 2020, **7**, 581–629; O. C. Gagné, *ChemRxiv*, 2020, 11626974.
- R. D. Shannon, *Acta Cryst.*, 1976, **A32**, 751–767.

Eir uses Gagné and Hawthorne (2015) first and Brown (2020) as fallback, not Brown and Altermatt (1985). This matters for any comparison with published GII values.

## The bond valence table

**Which row.** Where a source gives more than one row for a pair, the table takes Gagné and Hawthorne (2015) first, then Brown and Altermatt (1985), then Brese and O'Keeffe (1991), then any other published source, and unpublished sources last: Brown's private communications (reference code `e`), Sidey's (`bi`) and Hu's nitride values listed as "to be published" (`bq`). Chen and Adams (2017) count as another published source, so their values fill pairs Brown and Gagné do not cover and replace unpublished ones; they do not replace a published row. 123 entries remain Brown's private communications and four are Hu's, because no published source covers the pair. Where published rows of equal rank from different sources differ, the table takes the more recent fit, unless Brown restricts it to a context such as "from transition metal complexes"; so Pu⁴⁺–O takes Diwu et al. (2010) over Zachariasen (1978), Sm²⁺–O Trzesowska et al. (2006) over Palenik (2003), and Cu³⁺–N Mahapatra et al. (1996). Np⁴⁺–O, which Brown gives only from Zachariasen (1978) and a private communication, takes Gilson and Burns (2021), refitted by the method of Diwu et al. on well-refined Np(IV) structures (R0 2.054 Å, b 0.417). Rows of one source that differ (Hu's spin-state values for Co²⁺–N and Cr²⁺–N, where the table takes high spin, and a few papers giving two fits) are listed by `tools/audit_bv_table.py`.

**The anion's charge.** The table is keyed without the anion's charge, so an entry is used for the charge Eir gives that anion: O(2−), S(2−), Se(2−), Te(2−), N(3−), P(3−), As(3−), C(4−), the halides and H(1−). Every entry records the charge it was fitted for, and Eir does not load one fitted for another (CELL 2, `bv_table_entries`). A table written for an earlier Eir, with no `anion_charge`, loads as before. A structure that types an anion at another charge, such as O(1−) in a superoxide or Se(1−) in a polyselenide, is still summed with the ordinary parameters; that is the homopolar-unit work, not yet done.

**What 2.0.46 changed.** Until 2.0.46 the table held 32 entries labelled Brown (2020) that are in none of the 2009, 2011 and 2020 releases of Brown's compilation: all came from the hand-compiled 168-pair table of Eir 1.0 and were carried into the 2025 merge. Fourteen of those pairs are in Brown (2020) and now take its values (V²⁺–O 1.79 → 1.70 Å, Yb²⁺–O 2.08 → 1.989, Ni³⁺–O 1.70 → 1.75, Hg⁺–O 1.74 → 1.90, and Ac³⁺, Pa⁴⁺, Np⁴⁺, Pu³⁺, Pu⁴⁺ and Am⁴⁺ among them); eighteen are not (Pr⁴⁺–O, Re⁶⁺–O, U³⁺–O, Ag²⁺–O, Ra²⁺–O and others), and were removed. Seventeen more were Brown rows for an anion charge other than the one Eir uses (Pr³⁺–Se(1−), Fe³⁺–C(2+), In³⁺–Co(1−), S²⁺–S(2+) and others): two, S²⁺–N and S²⁺–S, now take Brown's row at the ordinary charge, and fifteen, for which Brown has none, were removed. Three were not cation–anion pairs at all (O(2−)–O, N(3−)–N, I(0)–I) and were removed. Five of the removed pairs (Ag³⁺–O, Au⁺–O, Re⁴⁺–O, Re⁶⁺–O and Pr³⁺–Se) now take Chen and Adams's values. A cation with no parameters for its anion is not assessed (R1); before 2.0.46, one with none at any valence was dropped and the file reported as unreadable.

**Chen and Adams (2017).** Their softNC1 set (IUCrJ 4, 614; supporting information, Table S1) fits R0, with b varying by pair, to 15,523 cation environments from the ICSD (one anion type, ambient conditions, no mixed occupancy), counting the first coordination shell only, as Eir does. Their softBV set counts higher shells too and is not used. 178 softNC1 entries are in the table: 105 for pairs nothing else covers (Re⁴⁺ and Re⁶⁺–O, Ag³⁺–O, Au⁺–O, Dy³⁺–S, Yb²⁺–S, many selenides, tellurides, arsenides and phosphides) and 73 in place of unpublished values (Ni³⁺–O, V²⁺–O, Co²⁺–S, Mn²⁺–S, Cr³⁺–S, P⁵⁺–F and others). Left out: pairs fitted to fewer than three environments (38), homopolar pairs, pseudo-atoms (cyanide N, X-ray H, unresolved ammonium) and Sb(3−) as an anion. Each entry gives `n_environments`. On the ordered, non-homopolar sites of the test sets that use a replaced pair, the median deviation from valence fell from 16.4% to 2.5% for Ni³⁺–O (43 sites, the RNiO₃ nickelates), 26.7% to 6.7% for Co²⁺–S, 20.5% to 5.2% for Ru⁶⁺–O, 14.4% to 9.8% for Cr³⁺–S and 3.1% to 1.6% for P⁵⁺–F. Tried in place of Brese and O'Keeffe's extrapolated rows as well, softNC1 was better for some pairs and worse for others (Li⁺–N, Al³⁺–S, Al³⁺–Se), so those rows stay.

**Valence 9.** 376 entries carry valence 9, Brese and O'Keeffe's notation for a valence they did not state. Eir looks parameters up at the stated valence, so these are never used in a sum.

**Checking it.** `python tools/audit_bv_table.py PATH/TO/bvparm2020.cif PATH/TO/yc5011sup1.txt` checks every entry against Brown's file, distributed by the IUCr, and the softNC1 entries against the text of Chen and Adams's supporting information (`pdftotext -layout yc5011sup1.pdf`), including that every pair the rule calls for is there. Neither file is in this repository.

How each table entered the history, and when, is in [docs/HISTORY.md](../docs/HISTORY.md).
