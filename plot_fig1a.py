# plot_fig1a.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Configuration and Data Path
# This script expects the processed CSV output (frequency data)
CSV_NAME = 'heatwave_exposure_2014-2100_ssp534full.csv'

def main():
    # Load the processed global mean heatwave frequency data
    try:
        df_all = pd.read_csv(CSV_NAME)
    except FileNotFoundError:
        print(f"Error: {CSV_NAME} not found.")
        print("Please ensure the calculation logic in functions.py has been executed ")
        print("to generate the necessary intermediate CSV files.")
        return

    # 2. Plotting Configurations
    sns.set_style('white')
    plt.figure(figsize=(8, 5))
    
    # Define a consistent color palette (Matching Figure 1b)
    # SSP126: Green, SSP245: Orange, SSP585: Red, SSP534os: Black
    color_map = {'ssp126': '#2ca02c', 'ssp245': '#ff7f0e', 
                 'ssp585': '#d62728', 'ssp534os': '#000000'}
    order = ['ssp126', 'ssp245', 'ssp585', 'ssp534os']

    # 3. Statistics and Data Visualization
    # Group by scenario and year to calculate multi-model ensemble mean and standard deviation
    plot_stats = df_all.groupby(['scenario', 'year'])['heatwave_exp'].agg(['mean', 'std']).reset_index()

    for scen in order:
        if scen not in plot_stats['scenario'].unique(): 
            continue
        
        tmp = plot_stats[plot_stats['scenario'] == scen]
        
        # Plot ensemble mean trend line
        plt.plot(tmp['year'], tmp['mean'], label=scen, 
                 color=color_map[scen], linewidth=1.8)
        
        # Plot uncertainty range (shading represents ±1 standard deviation)
        plt.fill_between(tmp['year'], 
                         tmp['mean'] - tmp['std'], 
                         tmp['mean'] + tmp['std'], 
                         color=color_map[scen], 
                         alpha=0.15)

    # 4. Figure Refinement
    plt.xlim(2015, 2099)
    plt.ylim(2.5, 5.0)
    plt.xlabel('Year', fontsize=10)
    plt.ylabel('Frequency (events/year)', fontsize=10)
    plt.title('Global Heatwave Frequency Trend (2015–2100)', fontsize=12)
    
    # Harmonize legend
    plt.legend(title='Scenario', frameon=True, loc='upper left')
    
    plt.tight_layout()
    # Save as high-resolution PDF for publication/GitHub
    plt.savefig('Figure_1a.pdf', dpi=300)
    print("Successfully generated Figure 1a: Figure_1a.pdf")
    plt.show()

if __name__ == "__main__":
    main()
