# plot_fig4.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import os
from functions import calculate_cohort_metrics_simple, find_gbd_region_optimized

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SAVE_DIR = os.path.join(BASE_DIR, 'global_analysis')
    
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # --- Data Preparation ---
    # Note: ts_matrix (Year x GBD_Region) should be pre-calculated from your ensemble averaging scripts.
    
    # Define birth cohorts for analysis
    map_cohorts = np.arange(1950, 2121, 1)    # 1-year step for smooth spatial mapping
    bar_cohorts = np.arange(1950, 2121, 10)   # 10-year step for clear bar charts

    peak_exp_years = {}
    peak_risk_years = {}

    print("Processing regional metrics and identifying peak years...")
    for region in ts_matrix.columns:
        # Calculate metrics using the logic encapsulated in functions.py
        days, risks = calculate_cohort_metrics_simple(ts_matrix[region], map_cohorts)
        peak_exp_years[region] = map_cohorts[np.argmax(days)]
        peak_risk_years[region] = map_cohorts[np.argmax(risks)]

    # --- Spatial Mapping Data (Panel A) ---
    # Load low-resolution world map from geopandas datasets
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = world[world['name'] != 'Antarctica']
    
    # Map GBD regions and results to the GeoDataFrame
    world['gbd_region'] = world['name'].apply(find_gbd_region_optimized)
    world['peak_exp'] = world['gbd_region'].map(peak_exp_years)
    world['peak_risk'] = world['gbd_region'].map(peak_risk_years)

    # --- Plotting Configuration ---
    fig = plt.figure(figsize=(20, 16), facecolor='white', dpi=300)
    # Define grid: Top for maps, Bottom for regional trend
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2], hspace=0.2, wspace=0.05)

    # =========================================================================
    # PANEL A: Spatial Distribution of Peak Years
    # =========================================================================
    proj = ccrs.Robinson()
    
    # A1: Peak Exposure (Blues) - Shows when physical heat threat is highest
    ax_a1 = fig.add_subplot(gs[0, 0], projection=proj)
    world.plot(column='peak_exp', ax=ax_a1, cmap='Blues', vmin=2050, vmax=2120,
               transform=ccrs.PlateCarree(), edgecolor='black', lw=0.1)
    ax_a1.set_title('A1. Peak Exposure Cohort (Birth Year)', loc='left', fontweight='bold', fontsize=15)

    # A2: Peak Health Risk (Reds) - Shows when weighted vulnerability risk is highest
    ax_a2 = fig.add_subplot(gs[0, 1], projection=proj)
    world.plot(column='peak_risk', ax=ax_a2, cmap='Reds', vmin=2020, vmax=2080,
               transform=ccrs.PlateCarree(), edgecolor='black', lw=0.1)
    ax_a2.set_title('A2. Peak Health Risk Cohort (Birth Year)', loc='left', fontweight='bold', fontsize=15)

    for ax in [ax_a1, ax_a2]:
        ax.add_feature(cfeature.OCEAN, facecolor='#f4f4f4')
        ax.set_global()
        ax.outline_patch.set_visible(False)

    # =========================================================================
    # PANEL B: Population Pyramid Style Comparison (Global Average)
    # =========================================================================
    global_series = ts_matrix.mean(axis=1)
    g_days, g_risks = calculate_cohort_metrics_simple(global_series, bar_cohorts)

    ax_b_left = fig.add_subplot(gs[1, :]) # Span full width for the pyramid
    ax_b_right = ax_b_left.twiny()        # Shared Y-axis, mirrored X-axis

    BAR_H = 7
    # Left side: Lifetime Exposure Days (Blue)
    ax_b_left.barh(bar_cohorts, g_days, height=BAR_H, color='#4575b4', alpha=0.8, label='Exposure')
    ax_b_left.set_xlabel('← Lifetime Exposure Days', color='#4575b4', fontweight='bold', fontsize=13)
    ax_b_left.invert_xaxis()
    ax_b_left.set_xlim(8000, 0)

    # Right side: Weighted Health Risk (Red)
    ax_b_right.barh(bar_cohorts, g_risks, height=BAR_H, color='#d73027', alpha=0.8, label='Health Risk')
    ax_b_right.set_xlabel('Weighted Health Risk →', color='#d73027', fontweight='bold', fontsize=13)
    ax_b_right.set_xlim(0, 1500)

    # Annotate peak cohorts for Global Average
    p_exp_yr = bar_cohorts[np.argmax(g_days)]
    p_risk_yr = bar_cohorts[np.argmax(g_risks)]
    
    # Left indicator
    ax_b_left.axhline(p_exp_yr, color='#4575b4', ls='--', lw=2)
    ax_b_left.text(7800, p_exp_yr + 2, f'Exposure Peak: {p_exp_yr}', 
                   color='#4575b4', fontweight='bold', fontsize=11)
    
    # Right indicator
    ax_b_right.axhline(p_risk_yr, color='#d73027', ls='--', lw=2)
    ax_b_right.text(1450, p_risk_yr + 2, f'Risk Peak: {p_risk_yr}', 
                    color='#d73027', fontweight='bold', ha='right', fontsize=11)

    # Final visual formatting
    ax_b_left.set_yticks(bar_cohorts)
    ax_b_left.set_yticklabels(bar_cohorts, fontweight='bold')
    ax_b_left.set_ylabel('Birth Cohort (Year)', fontsize=13)
    ax_b_left.set_title('B. Global Average Evolution: Exposure vs. Health Risk', 
                    loc='left', pad=40, fontweight='bold', fontsize=16)
    ax_b_left.grid(axis='x', ls=':', alpha=0.5)

    # --- Export ---
    plt.tight_layout()
    output_name = "Figure_4_Risk_Assessment_Final.pdf"
    plt.savefig(os.path.join(SAVE_DIR, output_name), bbox_inches='tight')
    print(f"Success: {output_name} generated in {SAVE_DIR}")
    plt.show()

if __name__ == "__main__":
    main()
