# Overshoot Pathways Reshape Unequal Heatwave Health Burdens Across Generations

This repository contains the data processing and visualization pipeline for the research on intergenerational heatwave exposure and health risks under climate overshoot scenarios (SSP5-3.4OS).

## 🌟 Research Highlights
- **Birth-Cohort Analysis**: Assessing lifetime heatwave exposure for global cohorts from 1950 to 2120.
- **Overshoot Dynamics**: Investigating how a "peak-and-decline" temperature trajectory (SSP5-3.4OS) reshapes generational risk distribution.
- **Risk Misalignment**: Highlighting the discrepancy between peak exposure (2040 cohort) and peak health risk (2020 cohort) due to elderly physiological vulnerability.
- **Mitigation Impact**: Quantifying the benefits of aggressive mitigation (C2 scenario) in reducing peak health burdens.

## 📂 Repository Structure
- `functions.py`: **Core Analytical Engine.**
  - Climate data remapping and ensemble averaging.
  - Heatwave identification (3-day exceedance streak).
  - Lifetime exposure integration across birth cohorts.
  - Scenario-specific data merging.
- `plot_fig1a.py`: Global trends of heatwave frequency across different SSP pathways.
- `plot_fig2-6.py`: (In Development) Spatial risk maps, intergenerational inequality plots, and cohort-specific health risk projections.

## 🛠 Prerequisites
- **Python**: 3.9+
- **Core Libraries**: `xarray`, `pandas`, `numpy`, `dask` (for processing large CMIP6 datasets).
- **Visualization**: `seaborn`, `matplotlib`, `cartopy` (for spatial mapping).
```bash
pip install xarray pandas numpy seaborn matplotlib dask cartopy netCDF4
