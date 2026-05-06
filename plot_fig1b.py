# plot_fig1b.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data
CSV_NAME = 'hw_days_global_mean_2014-2100_ssp534full.csv'

def main():
    try:
        df_global = pd.read_csv(CSV_NAME)
    except FileNotFoundError:
        print(f"Error: {CSV_NAME} not found. Please run the calculation logic first.")
        return

    df_global['year'] = df_global['year'].astype(int)

    # 2. Plotting Setup
    plt.figure(figsize=(8, 5))
    sns.set_style('white')
    
    # Consistent color palette with Fig 1a
    palette = {'ssp126': '#2ca02c', 'ssp245': '#ff7f0e', 
               'ssp585': '#d62728', 'ssp534os': '#000000'}
    order = ['ssp126', 'ssp245', 'ssp585', 'ssp534os']

    # 3. Calculate Statistics
    plot_stats = (df_global.groupby(['scenario', 'year'])['hw_days']
                           .agg(['mean', 'std'])
                           .reset_index())

    # 4. Visualization
    for scen in order:
        if scen not in plot_stats['scenario'].unique(): continue
        tmp = plot_stats[plot_stats['scenario'] == scen]
        
        plt.plot(tmp['year'], tmp['mean'], label=scen, 
                 color=palette[scen], linewidth=1.8)
        
        plt.fill_between(tmp['year'], 
                         tmp['mean'] - tmp['std'], 
                         tmp['mean'] + tmp['std'], 
                         color=palette[scen], alpha=0.15)

    # 5. Refinement
    plt.title('Global Annual Heatwave Duration (2015–2100)')
    plt.ylabel('Total Heatwave Days (days)')
    plt.xlabel('Year')
    plt.xlim(2015, 2099)
    plt.ylim(0, None)  # Duration usually starts from 0
    
    # Legend ordering
    handles, labels = plt.gca().get_legend_handles_labels()
    hdl_dict = dict(zip(labels, handles))
    plt.legend([hdl_dict[l] for l in order], order, 
               title='Scenario', frameon=True)

    plt.tight_layout()
    plt.savefig('Figure_1b.pdf', dpi=300)
    print("Figure 1b saved successfully.")
    plt.show()

if __name__ == "__main__":
    main()
