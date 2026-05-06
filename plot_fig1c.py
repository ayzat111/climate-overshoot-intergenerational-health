# plot_fig1c.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Configuration and Data Path
CSV_NAME = 'global_intensity_2014-2100_ssp534full.csv'

def main():
    try:
        df = pd.read_csv(CSV_NAME)
    except FileNotFoundError:
        print(f"Error: {CSV_NAME} not found.")
        print("Please ensure the intensity calculation logic has been executed.")
        return

    # 2. Plotting Setup
    sns.set_style('white')
    plt.figure(figsize=(8, 5))
    
    # Consistent color palette
    color_map = {'ssp126': '#2ca02c', 'ssp245': '#ff7f0e', 
                 'ssp585': '#d62728', 'ssp534os': '#000000'}
    order = ['ssp126', 'ssp245', 'ssp585', 'ssp534os']

    # 3. Statistical Aggregation
    plot_stats = (df.groupby(['scenario', 'year'])['intensity']
                    .agg(['mean', 'std'])
                    .reset_index())

    # 4. Visualization
    for scen in order:
        if scen not in plot_stats['scenario'].unique():
            continue
        
        tmp = plot_stats[plot_stats['scenario'] == scen]
        
        # Plot ensemble mean
        plt.plot(tmp['year'], tmp['mean'], label=scen, 
                 color=color_map[scen], linewidth=2)
        
        # Plot uncertainty range (±1 std)
        plt.fill_between(tmp['year'], 
                         tmp['mean'] - tmp['std'], 
                         tmp['mean'] + tmp['std'], 
                         color=color_map[scen], alpha=0.15)

    # 5. Figure Refinement
    plt.title('Global Cumulative Intensity of Heatwaves (2015–2100)', fontsize=12)
    plt.xlabel('Year', fontsize=10)
    plt.ylabel('Intensity (°C·day)', fontsize=10)
    plt.xlim(2015, 2099)
    plt.ylim(0, None)
    
    plt.legend(title='Scenario', frameon=True, loc='upper left')
    plt.tight_layout()
    
    # Save as high-resolution PDF
    plt.savefig('Figure_1c.pdf', dpi=300)
    print("Successfully generated Figure 1c: Figure_1c.pdf")
    plt.show()

if __name__ == "__main__":
    main()
