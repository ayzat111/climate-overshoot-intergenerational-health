# plot_fig1.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# =============================================================================
# 1. CONFIGURATION AND GLOBAL SETTINGS
# =============================================================================
DATA_FILES = {
    'frequency': 'heatwave_exposure_2014-2100_ssp534full.csv',
    'duration': 'hw_days_global_mean_2014-2100_ssp534full.csv',
    'intensity': 'global_intensity_2014-2100_ssp534full.csv'
}

# Consistent color palette for CMIP6 scenarios
# SSP126: Green, SSP245: Orange, SSP585: Red, SSP534os: Black
COLOR_MAP = {'ssp126': '#2ca02c', 'ssp245': '#ff7f0e', 
             'ssp585': '#d62728', 'ssp534os': '#000000'}
ORDER = ['ssp126', 'ssp245', 'ssp585', 'ssp534os']

def plot_subpanel(ax, data_type, title, ylabel, y_col):
    """
    Generalized function to plot ensemble trends with uncertainty shading.
    """
    csv_path = DATA_FILES[data_type]
    
    if not os.path.exists(csv_path):
        ax.text(0.5, 0.5, f'Data Missing:\n{csv_path}', 
                ha='center', va='center', color='red')
        print(f"Warning: {csv_path} not found.")
        return

    # Load and prepare data
    df = pd.read_csv(csv_path)
    
    # Standardize column names if necessary (handling frequency vs others)
    target_col = y_col
    if target_col not in df.columns and 'heatwave_exp' in df.columns:
        target_col = 'heatwave_exp'
    
    # Calculate Multi-Model Ensemble (MME) stats
    stats = df.groupby(['scenario', 'year'])[target_col].agg(['mean', 'std']).reset_index()

    for scen in ORDER:
        if scen not in stats['scenario'].unique():
            continue
        
        tmp = stats[stats['scenario'] == scen]
        
        # Plot ensemble mean trend
        ax.plot(tmp['year'], tmp['mean'], label=scen, 
                color=COLOR_MAP[scen], linewidth=2.0)
        
        # Plot uncertainty range (±1 standard deviation)
        ax.fill_between(tmp['year'], 
                        tmp['mean'] - tmp['std'], 
                        tmp['mean'] + tmp['std'], 
                        color=COLOR_MAP[scen], alpha=0.15)

    # Subpanel aesthetics
    ax.set_title(title, loc='left', fontweight='bold', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlim(2015, 2099)
    ax.grid(True, linestyle='--', alpha=0.3)

def main():
    # Set global plotting style
    sns.set_style('white')
    
    # Create a 3-panel vertical figure (Standard for multi-metric time series)
    fig, axes = plt.subplots(3, 1, figsize=(9, 14), sharex=True)

    # --- Panel A: Frequency ---
    plot_subpanel(axes[0], 'frequency', 'a) Global Heatwave Frequency', 
                  'Frequency (events/year)', 'heatwave_exp')

    # --- Panel B: Duration ---
    plot_subpanel(axes[1], 'duration', 'b) Global Annual Heatwave Duration', 
                  'Total Days (days)', 'hw_days')

    # --- Panel C: Intensity ---
    plot_subpanel(axes[2], 'intensity', 'c) Global Cumulative Intensity', 
                  'Intensity (°C·day)', 'intensity')

    # Final refinements
    axes[2].set_xlabel('Year', fontsize=11)

    # Unified legend placed at the top
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=4, frameon=False, fontsize=11)

    plt.tight_layout()
    
    # Save as high-resolution PDF for publication
    output_filename = 'Figure_1_Global_Trends.pdf'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    print(f"Successfully generated Figure 1: {output_filename}")
    plt.show()

if __name__ == "__main__":
    main()
