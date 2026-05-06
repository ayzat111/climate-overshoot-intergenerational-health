# plot_fig2.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

def main():
    # 1. Load data (Ensuring we use the extended 2200 data for relevant models)
    # Assume 'matrix' is a DataFrame with years 1950-2200 as index and models as columns
    # This matrix should be generated using the updated population weighting logic
    try:
        matrix = pd.read_csv('weighted_hw_days_1950_2200.csv', index_index='year')
    except FileNotFoundError:
        print("Required weighted data not found. Please run the population-weighting script.")
        return

    ensemble_mean = matrix.mean(axis=1)
    ensemble_min = matrix.min(axis=1)
    ensemble_max = matrix.max(axis=1)

    # --- Start Plotting ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), gridspec_kw={'height_ratios': [1, 0.8]})
    sns.set_style('white')

    # --- Panel A: Time Series (1950-2200) ---
    for col in matrix.columns:
        ax1.plot(matrix.index, matrix[col], color='lightgray', lw=0.8, alpha=0.4)
    
    ax1.fill_between(matrix.index, ensemble_min, ensemble_max, color='#d62728', alpha=0.1)
    ax1.plot(ensemble_mean.index, ensemble_mean.values, color='#d62728', lw=2.5, label='Ensemble Mean')
    
    ax1.set_xlim(1950, 2200)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(50))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(10))
    ax1.set_ylabel('Annual Heatwave Days (Days/Person)', fontsize=12)
    ax1.set_title('A. Global Population-Weighted Heatwave Exposure', loc='left', fontweight='bold')
    ax1.legend(frameon=False)

    # --- Panel B: Birth Cohort Comparison ---
    target_cohorts = [1990, 2020, 2050, 2080]
    lifetime_totals = []
    for b_year in target_cohorts:
        # Using the helper function logic
        total = ensemble_mean.loc[b_year : b_year + 74].sum()
        lifetime_totals.append(total)

    labels = [f'{y} Cohort' for y in target_cohorts]
    colors = ['#fee08b', '#fdae61', '#f46d43', '#d53e4f'] # Gradient from yellow to deep red
    
    bars = ax2.barh(labels, lifetime_totals, color=colors, edgecolor='black', height=0.6)
    
    # Add value labels
    for i, val in enumerate(lifetime_totals):
        ax2.text(val + 50, i, f'{int(val)} days', va='center', fontsize=11, fontweight='bold')

    ax2.set_xlabel('Total Lifetime Heatwave Days (0-74 years old)', fontsize=12)
    ax2.set_title('B. Lifetime Exposure by Birth Cohort (SSP5-3.4os)', loc='left', fontweight='bold')
    ax2.set_xlim(2000, max(lifetime_totals) * 1.15)
    
    # Final Touches
    sns.despine()
    plt.tight_layout()
    plt.savefig('Figure_2_Cohort_Exposure.pdf', dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
