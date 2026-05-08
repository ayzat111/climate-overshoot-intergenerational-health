# plot_fig5.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from functions import fit_response_curve

def main():
    # --- 1. Path Configuration ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'processed_data')
    SAVE_DIR = os.path.join(BASE_DIR, 'global_analysis')
    
    # --- 2. Panel A: Multi-SSP Impact Curve ---
    scenarios = {
        'SSP1-2.6':  {'file': 'warming_exposure_ssp126.csv', 'color': '#2E8B57'},
        'SSP2-4.5':  {'file': 'warming_exposure_ssp245.csv', 'color': '#FFA500'},
        'SSP5-8.5':  {'file': 'warming_exposure_ssp585.csv', 'color': '#FF0000'},
        'SSP5-3.4os': {'file': 'warming_exposure_ssp534os.csv', 'color': '#3498db'}
    }

    fig = plt.figure(figsize=(16, 12), facecolor='white', dpi=300)
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

    ax_a = fig.add_subplot(gs[0, 0])
    all_dfs = []
    for name, cfg in scenarios.items():
        path = os.path.join(DATA_DIR, cfg['file'])
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Normalize SSP5-8.5 if needed as per user logic
            if df['hw_days'].max() > 500: df['hw_days'] /= 7490.6 
            ax_a.scatter(df['warming'], df['hw_days'], color=cfg['color'], s=15, alpha=0.2, label=name)
            all_dfs.append(df)

    # Fit multi-model response trend
    if all_dfs:
        full_df = pd.concat(all_dfs)
        p_trend = fit_response_curve(full_df['warming'], full_df['hw_days'])
        x_fit = np.linspace(0.5, 4.5, 100)
        ax_a.plot(x_fit, p_trend(x_fit), color='black', lw=2.5, label='Response Trend', zorder=10)

    ax_a.set_title('a) Heatwave Exposure vs. Global Warming', loc='left', fontweight='bold')
    ax_a.set_xlabel('GMST relative to 1850-1900 (°C)')
    ax_a.set_ylabel('Annual Heatwave Exposure (Days/Person)')
    ax_a.legend(frameon=False, loc='upper left')

    # --- 3. Panel B & C: AR6 C2 Scenario Projection ---
    # Load AR6 GMST data
    ar6_path = os.path.join(BASE_DIR, 'AR6_Scenario_Datasets', 'GMST.csv')
    ar6_df = pd.read_csv(ar6_path)
    ar6_world = ar6_df[ar6_df['region'] == 'World'].copy()
    ar6_summary = ar6_world.groupby('year')['value'].agg(['median', 'min', 'max']).reset_index()

    # Panel B: Warming Trajectory (Vertical)
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.fill_betweenx(ar6_summary['year'], ar6_summary['min'], ar6_summary['max'], color='#2C7FB8', alpha=0.2)
    ax_b.plot(ar6_summary['median'], ar6_summary['year'], color='#2C7FB8', lw=2, label='AR6 C2 Trajectory')
    ax_b.set_ylim(2020, 2100)
    ax_b.set_xlim(0.5, 4.5)
    ax_b.set_title('b) AR6 C2 Warming Pathway', loc='left', fontweight='bold')
    ax_b.set_xlabel('GMST Change (°C)')
    ax_b.set_ylabel('Year')

    # Panel C: Projected Annual Exposure
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.fill_between(ar6_summary['year'], p_trend(ar6_summary['min']), p_trend(ar6_summary['max']), color='#D7301F', alpha=0.2)
    ax_c.plot(ar6_summary['year'], p_trend(ar6_summary['median']), color='#D7301F', lw=2, label='Projected Exposure')
    ax_c.set_title('c) Projected Annual Exposure (AR6 C2)', loc='left', fontweight='bold')
    ax_c.set_xlabel('Year')
    ax_c.set_ylabel('Days/Person')

    # --- 4. Panel D: Cohort Comparison (Pyramid style) ---
    cohort_data = {
        'Birth_Year': [1960, 1970, 1980, 1990, 2000, 2010, 2020],
        'Days': [2199.64, 2483.43, 2777.45, 3033.27, 3258.54, 3391.90, 3485.62],
        'Risk': [507.72, 580.81, 627.57, 645.53, 649.86, 644.26, 630.49]
    }
    cd = pd.DataFrame(cohort_data)
    
    ax_d_left = fig.add_subplot(gs[1, 1])
    ax_d_right = ax_d_left.twiny()
    
    y_pos = cd['Birth_Year']
    ax_d_left.barh(y_pos, cd['Days'], height=6, color='#4575b4', alpha=0.8)
    ax_d_right.barh(y_pos, cd['Risk'], height=6, color='#d73027', alpha=0.8)
    
    ax_d_left.invert_xaxis()
    ax_d_left.set_xlabel('← Lifetime Days', color='#4575b4', fontweight='bold')
    ax_d_right.set_xlabel('Weighted Risk →', color='#d73027', fontweight='bold')
    ax_d_left.set_yticks(y_pos)
    ax_d_left.set_yticklabels(y_pos.astype(int))
    ax_d_left.set_title('d) Cohort Life-course Comparison', loc='left', pad=25, fontweight='bold')

    # --- 5. Save ---
    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, 'Figure_5_Impact_and_Projection.pdf'), bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
