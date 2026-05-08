# Overshoot Pathways Reshape Unequal Heatwave Health Burdens Across Generations

This repository contains the data processing and visualization pipeline for the research on intergenerational heatwave exposure and health risks under climate overshoot scenarios (SSP5-3.4OS). The paper is under review.

All data and scripts are publicly available; a few remaining scripts are still being finalized and will be uploaded upon acceptance of the paper.

## 🌟 Research Highlights
- **Birth-Cohort Analysis**: Assessing lifetime heatwave exposure for global cohorts from 1950 to 2120.
- **Path-Dependent Risk Reshaping**: Investigating how the "peak-and-decline" temperature trajectory of SSP5-3.4OS alters generational risk distribution.
- **Exposure-Health Risk Misalignment**: Highlighting the discrepancy between peak exposure and peak health risk due to physiological vulnerability.
- **Mitigation Impact**: Quantifying the benefits of aggressive mitigation in reducing peak health burdens.

## 📂 Repository Structure
- `functions.py`: **The Analytical Engine.**
  - **Climate Logic**: Heatwave identification (3-day streaks), frequency, duration, and intensity (°C·day).
  - **Spatial Logic**: Population-weighted aggregation and 1°x1° grid harmonization.
  - **Cohort Logic**: 75-year lifetime exposure integration and overshoot scenario synthesis.
- `plot_fig1.py`: Generates the multi-panel figure covering heatwave frequency, duration, and intensity (2015–2100).
- `plot_fig2.py`: Temporal evolution of heatwave hazards and intergenerational disparities in lifetime exposure under an overshoot pathway.
- `plot_fig3.py`: Lifetime and aged exposure heatwave days across birth cohorts under the SSP5-3.4OS scenario.
- `plot_fig4.py`: Temporal shift between the peak cohorts of lifetime heatwave exposure and heatwave-related health risk.
- `plot_fig5.py`: Projections of heatwave exposure and associated health risks across different birth cohorts for the IPCC AR6 C2 scenario.

## 📊 Data Availability
Raw climate data and intermediate processed results are **not** included in this repository due to size constraints.Users must obtain the following data to replicate the analysis:
- **Climate Projections**: Daily maximum temperature (tasmax) from CMIP6 (Historical, SSP1-2.6, SSP2-4.5, SSP5-8.5, and SSP5-3.4OS) are available via the [ESGF LLNL node](https://esgf-node.llnl.gov/search/cmip6/).
- **Population Data**: 
  - Historical (1950–2020): Based on the UN World Population Prospects (WPP).
  - Future (2020–2100): Gridded SSP1-5 projections (0.5° resolution) derived from cohort-component models.
  - Extended (2100–2200): Assumed constant population distribution by extending 2100 projections to focus on climate-driven risks.
- **Data Integration**: The analysis pipeline in `functions.py` performs spatial harmonization and population-weighting across these multi-source datasets.

## 🛠 Prerequisites
- **Python**: 3.9+
- **Key Libraries**: xarray, pandas, numpy, dask, seaborn, matplotlib, cartopy.

## ✉️ Contact
For questions regarding the methodology detail, please contact:
**Ayzat Tursen** at **Peking University** - ayzat017@gmail.com

For academic collaborations, please contactt:
**Bo Fu** (Supervisor) at **Peking University** - pkufubo@pku.edu.cn
