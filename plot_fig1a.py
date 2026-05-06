# plot_fig1a.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from functions import identify_heatwave, global_mean, make_ssp534os_full

# 1. 加载数据
CSV_NAME = 'heatwave_exposure_2014-2100_ssp534full.csv'

def main():
    try:
        df_all = pd.read_csv(CSV_NAME)
    except FileNotFoundError:
        print(f"Error: {CSV_NAME} not found. Please run the calculation logic first.")
        return

    # 2. 绘图设置
    sns.set_style('white')
    plt.figure(figsize=(8, 5))
    
    color_map = {'ssp126': 'green', 'ssp245': 'orange', 'ssp585': 'red', 'ssp534os': 'black'}
    order = ['ssp126', 'ssp245', 'ssp585', 'ssp534os']

    # 3. 统计并绘图
    plot_stats = df_all.groupby(['scenario', 'year'])['heatwave_exp'].agg(['mean', 'std']).reset_index()

    for scen in order:
        if scen not in plot_stats['scenario'].unique(): continue
        tmp = plot_stats[plot_stats['scenario'] == scen]
        plt.plot(tmp['year'], tmp['mean'], label=scen, color=color_map[scen], linewidth=1.8)
        plt.fill_between(tmp['year'], tmp['mean'] - tmp['std'], tmp['mean'] + tmp['std'], 
                         color=color_map[scen], alpha=0.15)

    # 4. 细节修饰
    plt.xlim(2015, 2099)
    plt.ylim(2.5, 5.0)
    plt.xlabel('Year')
    plt.ylabel('Frequency (events)')
    plt.title('Global Heatwave Frequency Trend (2015–2100)')
    plt.legend(title='Scenario')
    
    plt.tight_layout()
    plt.savefig('Figure_1a.pdf', dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
