# Overshoot pathways reshape unequal heatwave health burdens across generations

This repository contains the Python implementation for analyzing global heatwave frequency and exposure under various CMIP6 climate scenarios (SSP1-2.6, SSP2-4.5, SSP5-8.5, and SSP5-3.4os).

## 📌 Overview
The project focuses on calculating heatwave thresholds based on historical baselines (1850-1900) and projecting future exposure trends through 2100. It includes logic for:
- Spatial remapping and interpolation of CMIP6 climate data.
- 95th percentile threshold calculation.
- Heatwave identification using a 3-day exceedance streak logic.
- Multi-model ensemble (MME) statistical analysis.

## 📂 Project Structure
- `functions.py`: **Core Computational Engine.** Contains all backend logic for data processing, remapping, heatwave identification, and global weighting.
- `plot_fig1a.py`: Script to generate Figure 1a (Global Heatwave Frequency Trend).
- *(Planned)* `plot_fig2.py` to `plot_fig6.py`: Scripts for subsequent spatial risk maps and intergenerational exposure analysis.

## 🛠 Installation & Requirements
This project requires Python 3.x and the following scientific libraries:
- **xarray**: For N-dimensional array processing.
- **pandas**: For tabular data manipulation.
- **numpy**: For numerical operations.
- **seaborn/matplotlib**: For high-quality academic visualization.
- **dask**: For handling large-scale climate datasets efficiently.

You can install the dependencies via pip:
```bash
pip install xarray pandas numpy seaborn matplotlib dask netCDF4
