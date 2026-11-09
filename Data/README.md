# Reference data

Eir reads five tables from this folder. Keep the folder beside `Eir.ipynb`, or start Jupyter in the repository folder.

| File | What it holds | Source |
|---|---|---|
| `bvs_parameters.json` | Bond valence parameters R0 and b for 1,385 cation–anion pairs over 17 anions, keyed `('Mn', 4, 'O')` | Gagné and Hawthorne (2015) where they give a value; otherwise Brown's 2020 compilation of published parameters; Fe⁴⁺–O from Brown (2009). Each entry names its source in `reference`. |
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

How each table entered the history, and when, is in [docs/HISTORY.md](../docs/HISTORY.md).
