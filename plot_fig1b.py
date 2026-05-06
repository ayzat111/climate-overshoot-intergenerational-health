# plot_fig1b.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Configuration and Data Path
# This script expects the processed CSV output from the analysis pipeline
CSV_NAME = 'hw_days_global_mean_2014-2100_ssp534full.csv'

def main():
    # Load the processed global mean heatwave duration data
    try:
        df_global = pd.read_csv(CSV_NAME)
    except FileNotFoundError:
        print(f"Error: {CSV_NAME} not found.")
        print("Please ensure the calculation logic in functions.py has been executed ")
        print("to generate the necessary intermediate CSV files.")
        return

    # Ensure year is treated as integer for cleaner plotting
    df_global['year'] = df_global['year'].astype(int)

    # 2. Plotting Setup
    plt.figure(figsize=(8, 5))
    sns.set_style('white')
    
    # Define a consistent color palette for CMIP6 scenarios
    # SSP126: Green, SSP245: Orange, SSP585: Red, SSP534os: Black
    palette = {'ssp126': '#2ca02c', 'ssp245': '#ff7f0e', 
               'ssp585': '#d62728', 'ssp534os': '#000000'}
    order = ['ssp126', 'ssp245', 'ssp585', 'ssp534os']

    # 3. Statistical Aggregation
    # Group by scenario and year to calculate multi-model ensemble mean and standard deviation
    plot_stats = (df_global.groupby(['scenario', 'year'])['hw_days']
                           .agg(['mean', 'std'])
                           .reset_index())

    # 4. Data Visualization
    for scen in order:
        if scen not in plot_stats['scenario'].unique():
            continue
            
        tmp = plot_stats[plot_stats['scenario'] == scen]
        
        # Plot ensemble mean trend line
        plt.plot(tmp['year'], tmp['mean'], label=scen, 
                 color=palette[scen], linewidth=1.8)
        
        # Plot uncertainty range (shading represents ±1 standard deviation)
        plt.fill_between(tmp['year'], 
                         tmp['mean'] - tmp['std'], 
                         tmp['mean'] + tmp['std'], 
                         color=palette[scen], alpha=0.15)

    # 5. Figure Refinement and Aesthetics
    plt.title('Global Annual Heatwave Duration (2015–2100)', fontsize=12)
    plt.ylabel('Total Heatwave Days (days)', fontsize=10)
    plt.xlabel('Year', fontsize=10)
    
    # Set axis limits to match the study period
    plt.xlim(2015, 2099)
    plt.ylim(0, None)  # Duration naturally starts from zero
    
    # Harmonize legend order with the plotting sequence
    handles, labels = plt.gca().get_legend_handles_labels()
    hdl_dict = dict(zip(labels, handles))
    plt.legend([hdl_dict[l] for l in order], order, 
               title='Scenario', frameon=True, loc='upper left')

    plt.tight_layout()
    
    # Save as high-resolution PDF for publication-quality output
    plt.savefig('Figure_1b.pdf', dpi=300)
    print("Successfully generated Figure 1b: Figure_1b.pdf")
    plt.show()

if __name__ == "__main__":
    main()
