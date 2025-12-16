# Eir v1.2 - Automated Bond Valence Sum Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Automated Bond Valence Sum (BVS) analysis tool for crystallographic structure validation and database quality assessment.

## Overview

Eir performs high-throughput BVS analysis on crystal structures from ICSD CIF files or GSAS-II refinement outputs. The tool uses proper crystallographic symmetry operations via pymatgen to correctly handle all space groups, with particular robustness for high-symmetry cases (R-3m, P63/mmc) common in layered oxides and rock salt structures.

## Key Features

- **Automatic coordination number detection** using adaptive gap analysis with Jahn-Teller awareness
- **Mixed/partial occupancy support** for solid solutions and disordered structures
- **3D visualization** of problematic sites (BVS deviation > 30%) using py3Dmol
- **Batch processing** with summary CSV output
- **Statistical analysis** with outlier detection and z-scores
- **Ambient vs high-pressure separation** for condition-dependent analysis
- **Publication metadata extraction** from ICSD CIF files
- **Config file support** for hands-free batch processing

## Installation

### Requirements

- Python 3.9 or higher
- Jupyter Notebook (recommended for interactive use)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: 3D Visualization

For interactive 3D visualization of problematic sites:

```bash
pip install py3Dmol
```

## Quick Start

### Method 1: Interactive Mode (No Config)

1. Open `Eir_1_2.py` in Jupyter Notebook
2. Place CIF files in a folder
3. Run all cells
4. Enter oxidation states when prompted

### Method 2: Batch Mode (with Config File)

Create `config.json` in your CIF directory:

```json
{
  "Na": 1,
  "Ni": 2,
  "Mn": 4,
  "O": -2
}
```

Then run all cells - walks away for coffee! ☕

## Input Files

### ICSD CIF Files
- Filename format: `YourCustomFileName_CollCode123456.cif`
- CollCode automatically extracted from filename
- Handles diverse CIF format variations

### GSAS-II Files
- Requires both `.lst` (refinement output) and `.cif` files
- Must have matching base names
- Place in same directory

## Output

### Main CSV File: `YYYYMMDD_HHMMSS_bvs_results.csv`

Core columns:
- `File`: Input filename
- `CollCode/Phase`: ICSD CollCode or phase name
- `Space_Group`: Crystallographic space group
- `Element`: Chemical element analyzed
- `Site_Label`: Crystallographic site label
- `CN`: Coordination number (adaptive gap detection)
- `BVS`: Calculated bond valence sum
- `Formal_Charge`: Expected oxidation state
- `Deviation`: BVS - Formal_Charge (valence units)
- `GII`: Global Instability Index (structure-wide metric)

Extended columns (if available):
- `Year`, `Journal`, `Authors`: Publication metadata
- `Measurement_Temperature_K`, `Measurement_Pressure_GPa`: Conditions
- `R_factor`, `Density`: Refinement quality indicators

### 3D Visualization
- Automatically displays for sites with |deviation| > 30%
- Interactive rotation and zooming in Jupyter
- Bond colors indicate valence contributions
- Helps diagnose coordination problems

### Console Output
- Measurement condition distribution
- Ambient vs high-pressure statistics
- Outlier detection with z-scores
- Consensus values by element
- Quality verdicts (VALIDATED / QUESTIONABLE / EXCLUDE)
- Problematic sites summary

## Interpreting Results

### Bond Valence Sum (BVS)

The BVS should approximately equal the formal oxidation state:

- **|Deviation| < 0.2 v.u.**: Well-bonded, structurally sound ✓
- **0.2 < |Deviation| < 0.3 v.u.**: Borderline, check for size mismatch or strain
- **|Deviation| > 0.3 v.u.**: Over-bonded (negative) or under-bonded (positive) ⚠️
- **|Deviation| > 0.5 v.u.**: Severe problem - inspect 3D visualization ⛔

### Global Instability Index (GII)

Structure-wide stability metric:

- **GII < 0.20 v.u.**: Stable, well-ordered structure ✓
- **0.20 < GII < 0.40 v.u.**: Moderate strain, possibly acceptable
- **GII > 0.40 v.u.**: Significant structural instability ⚠️
- **GII > 0.60 v.u.**: Severe problems - synthesis likely difficult ⛔

**Note:** The traditional 0.2 v.u. threshold is system-dependent. See Miller & Rondinelli, *APL Mater.* **11** (2023) for discussion.

### Coordination Numbers (CN)

Expected values for common geometries:

- **CN = 4**: Tetrahedral
- **CN = 6**: Octahedral (most transition metals in oxides)
- **CN = 8**: Cubic
- **CN = 1-3**: Likely indicates missing bonds or structural problems

## Common Issues & Solutions

### Issue: "No bond valence parameters found"

**Cause:** Element/oxidation state combination not in Gagné & Hawthorne database  
**Solution:** Check oxidation state assignment or add parameters manually

### Issue: Very high GII (>1.0) for literature structures

**Possible causes:**
- Mixed-phase sample (XRD refinement artefact)
- Metastable structure
- Genuine severe strain (synthesis should be difficult)
- Check 3D visualization for coordination issues

### Issue: High deviation but coordination looks correct

**Solution:** 
- Check 3D visualization
- May be Jahn-Teller distortion (expected for Mn³⁺, Cu²⁺)
- Consider wrong oxidation state assignment
- For alkaline earth oxides (Ca, Sr, Ba), parameter inadequacy known

### Issue: All structures show CN = 1-2 instead of 6

**Solution:** Already fixed in v1.0+ using proper pymatgen symmetry operations. If still occurring, check CIF file quality.

## Technical Details

### Adaptive Gap Detection (v1.1+)

Intelligently determines coordination sphere boundaries:

- Considers both absolute gap size (default 0.05 Å minimum)
- Evaluates relative gap ratio (gap/bond length)
- Special handling for Jahn-Teller distorted ions (Mn³⁺, Cu²⁺)
- Prevents over-splitting of distorted but valid coordination

### 3D Visualization (v1.1+)

- Automatic triggering for |deviation| > 30%
- Shows central atom, coordinating atoms, and bonds
- Bond colors encode valence contributions
- Interactive rotation/zoom in Jupyter
- Helps diagnose missing bonds, wrong oxidation states

### High-Pressure Handling (v1.2+)

- Automatic separation of ambient vs high-pressure structures
- Condition-dependent statistics
- Warnings for high-P structures (BVS parameters fitted to ambient)

## Citation

### Software

If you use Eir in your research, please cite:

```bibtex
@software{reeves2025eir,
  author = {Reeves-McLaren, Nik},
  title = {Eir: Automated Bond Valence Sum Analysis Tool},
  year = {2025},
  version = {1.2},
  url = {https://github.com/[username]/Eir}
}
```

### Manuscript

For the systematic database quality assessment methodology:

```bibtex
@article{reeves2026bvs,
  author = {Reeves-McLaren, Nik},
  title = {Automated Bond Valence Sum Analysis for Crystallographic Database 
           Quality Assessment: A Systematic Study of Rock Salt Oxides, Halides, 
           and Chalcogenides},
  journal = {Dalton Transactions},
  year = {2026},
  doi = {[DOI to be added after publication]}
}
```

### BVS Parameters

Please also cite the underlying parameter compilation:

```bibtex
@article{gagne2015bvs,
  author = {Gagné, Olivier Charles and Hawthorne, Frank Christopher},
  title = {Comprehensive derivation of bond-valence parameters for ion pairs 
           involving oxygen},
  journal = {Acta Crystallographica Section B},
  volume = {71},
  number = {5},
  pages = {562--578},
  year = {2015},
  doi = {10.1107/S2052520615016297}
}
```

## Version History

- **v1.2 (Dec 2025)**: Enhanced analysis with ambient/high-P separation, statistical outlier detection, quality verdicts
- **v1.1 (Dec 2025)**: Config file support, 3D visualization, adaptive gap detection, consistent naming
- **v1.0 (Dec 2025)**: Complete rewrite with pymatgen for proper crystallographic symmetry
- **v0.4**: Experimental supercell approach
- **v0.3**: Initial ICSD CIF compatibility (incomplete)
- **v0.2**: Mixed occupancy support
- **v0.1**: Original GSAS-II only version

## Data Files from Manuscript

The `paper_data/` directory contains processed validation results for 840 rock salt structures analyzed in the Dalton Transactions manuscript:

- `All_Assessable_Structures.csv`: Complete validation results (612 structures)
- `Excluded_No_Parameters.csv`: Structures lacking BVS parameters (154)
- `Type1_Parameter_Inadequacy.csv`: Systematic parameter failures (107)
- `Types3-5_Methodological_Limitations.csv`: Disorder-related failures (95)
- `Type6_Database_Quality.csv`: Database quality issues (13)
- `Borderline_Structures.csv`: Structures requiring manual review (79)

See `paper_data/README.md` for detailed descriptions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Nik Reeves-McLaren** 
School of Chemical Materials and Biological Engineering  
University of Sheffield  
Email: nik.reeves-mclaren@sheffield.ac.uk

## Acknowledgements

- Bond valence parameters from Gagné & Hawthorne (2015) and Brown (2020)
- Crystallographic operations via [pymatgen](https://pymatgen.org/)
- CIF parsing via [PyCifRW](https://pypi.org/project/PyCifRW/) and [gemmi](https://gemmi.readthedocs.io/)
- 3D visualization via [py3Dmol](https://pypi.org/project/py3Dmol/)

## Contributing

Bug reports and feature requests welcome! Please use the GitHub issue tracker.

For major changes, please open an issue first to discuss what you would like to change.

## Frequently Asked Questions

**Q: Can I use this for non-rock salt structures?**  
A: Yes! Eir works for any structure with available BVS parameters. The manuscript focused on rock salts but the tool is general-purpose.

**Q: What do I do if my element/oxidation state lacks parameters?**  
A: Check the Brown (2020) compilation at https://www.iucr.org/resources/data/datasets/bond-valence-parameters or consider alternative oxidation states.

**Q: Can I use this for neutron diffraction data?**  
A: Yes, if your CIF file contains proper atomic coordinates and symmetry information.

**Q: How do I cite specific version 1.2?**  
A: Include version number in software citation and consider creating a Zenodo release for permanent DOI.
