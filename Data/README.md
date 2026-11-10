# Reference data

Eir reads five tables from this folder, and a sixth file records what was taken out of one of them. Keep the folder beside `Eir.ipynb`, or start Jupyter in the repository folder. The installed package carries a copy of this folder as `eir/data`; set `EIR_DATA_DIR` to use another.

| File | What it holds | Source |
|---|---|---|
| `bvs_parameters.json` | Bond valence parameters R0 and b for 1,349 cation–anion pairs over 13 anions, keyed `('Mn', 4, 'O')`. Each entry records the anion charge it was fitted for (`anion_charge`) and, for Brown's compilation, the row's reference code (`brown_code`) | Gagné and Hawthorne (2015) where they give a value; otherwise Brown's 2020 compilation (bvparm2020); Fe⁴⁺–O from Brown (2009). Each entry names its source in `reference`. |
| `bvs_parameters_excluded.json` | The 36 entries taken out of `bvs_parameters.json` in 2.0.46, with the values they had and why. Eir does not read it. | |
| `gagne_bond_lengths.json` | Mean, standard deviation, minimum and maximum bond lengths, and sample sizes, for 596 ion configurations bonded to O²⁻ and N³⁻ | Gagné's aggregated bond length surveys. The `_metadata` block lists the six papers and the source page. |
| `shannon_radii.json` | Effective ionic radii by element, valence and coordination number | Shannon (1976) |
| `common_oxidation_states.json` | The usual oxidation states of each element, used only where neither the CIF nor a `config.json` gives one | Compiled for Eir |
| `element_categories.json` | Element groups (alkali metals, 3d transition metals, lanthanides, ...) | Compiled for Eir |

The values are published measurements and fits. If you use them, please cite the original sources:

- O. C. Gagné and F. C. Hawthorne, *Acta Cryst.*, 2015, **B71**, 562–578.
- I. D. Brown, *Chem. Rev.*, 2009, **109**, 6858–6919.
- I. D. Brown, bond valence parameter compilation (bvparm2020), International Union of Crystallography.
- The bond length surveys: O. C. Gagné and F. C. Hawthorne, *Acta Cryst.*, 2016, **B72**, 602–625; O. C. Gagné, *Acta Cryst.*, 2018, **B74**, 49–62; O. C. Gagné and F. C. Hawthorne, *Acta Cryst.*, 2018, **B74**, 63–78 and 79–96; O. C. Gagné and F. C. Hawthorne, *IUCrJ*, 2020, **7**, 581–629; O. C. Gagné, *ChemRxiv*, 2020, 11626974.
- R. D. Shannon, *Acta Cryst.*, 1976, **A32**, 751–767.

Eir uses Gagné and Hawthorne (2015) first and Brown (2020) as fallback, not Brown and Altermatt (1985). This matters for any comparison with published GII values.

## The bond valence table

**Which row.** Where a source gives more than one row for a pair, the table takes Gagné and Hawthorne (2015) first, then Brown and Altermatt (1985), then Brese and O'Keeffe (1991), then any other published source, and unpublished sources last: Brown's private communications (reference code `e`), Sidey's (`bi`) and Hu's nitride values listed as "to be published" (`bq`). 196 entries are Brown's private communications and four are Hu's, because nothing else in the compilation covers the pair. Where two rows of equal rank differ (14 pairs), the 2025 merge did not take them in a fixed order; `tools/audit_bv_table.py` lists them. Two of those are Hu's spin-state values for Co²⁺–N and Cr²⁺–N, where the table takes high spin.

**The anion's charge.** The table is keyed without the anion's charge, so an entry is used for the charge Eir gives that anion: O(2−), S(2−), Se(2−), Te(2−), N(3−), P(3−), As(3−), C(4−), the halides and H(1−). Every entry records the charge it was fitted for, and Eir does not load one fitted for another (CELL 2, `bv_table_entries`). A table written for an earlier Eir, with no `anion_charge`, loads as before. A structure that types an anion at another charge, such as O(1−) in a superoxide or Se(1−) in a polyselenide, is still summed with the ordinary parameters; that is the homopolar-unit work, not yet done.

**What 2.0.46 changed.** Until 2.0.46 the table held 32 entries labelled Brown (2020) that are in none of the 2009, 2011 and 2020 releases of Brown's compilation: all came from the hand-compiled 168-pair table of Eir 1.0 and were carried into the 2025 merge. Fourteen of those pairs are in Brown (2020) and now take its values (V²⁺–O 1.79 → 1.70 Å, Yb²⁺–O 2.08 → 1.989, Ni³⁺–O 1.70 → 1.75, Hg⁺–O 1.74 → 1.90, and Ac³⁺, Pa⁴⁺, Np⁴⁺, Pu³⁺, Pu⁴⁺ and Am⁴⁺ among them); eighteen are not (Pr⁴⁺–O, Re⁶⁺–O, U³⁺–O, Ag²⁺–O, Ra²⁺–O and others), and were removed. Seventeen more were Brown rows for an anion charge other than the one Eir uses (Pr³⁺–Se(1−), Fe³⁺–C(2+), In³⁺–Co(1−), S²⁺–S(2+) and others): two, S²⁺–N and S²⁺–S, now take Brown's row at the ordinary charge, and fifteen, for which Brown has none, were removed. Three were not cation–anion pairs at all (O(2−)–O, N(3−)–N, I(0)–I) and were removed. A cation with no parameters for its anion is not assessed (R1); before 2.0.46, one with none at any valence was dropped and the file reported as unreadable.

**Valence 9.** 376 entries carry valence 9, Brese and O'Keeffe's notation for a valence they did not state. Eir looks parameters up at the stated valence, so these are never used in a sum.

**Checking it.** `python tools/audit_bv_table.py PATH/TO/bvparm2020.cif` checks every entry against Brown's file, which is distributed by the IUCr and is not in this repository.

How each table entered the history, and when, is in [docs/HISTORY.md](../docs/HISTORY.md).
