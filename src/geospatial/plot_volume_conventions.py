"""
Visualization of Geometric Column Volume vs. Ice-Equivalent Volume
Generates a publication-grade comparative bar chart and firn-air sensitivity diagram.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set matplotlib cache directory to local folder to avoid sandbox warnings
os.environ['MPLCONFIGDIR'] = 'antarctic-ice-volume-prediction/data/processed/.matplotlib'

def generate_comparison_chart():
    csv_path = "antarctic-ice-volume-prediction/data/processed/bedmap3_basin_volumes_geometric_and_ice_equivalent.csv"
    fig_dir = "antarctic-ice-volume-prediction/reports/figures"
    os.makedirs(fig_dir, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    basins_df = df[df['Basin'] != 'Peninsula Total']
    total_row = df[df['Basin'] == 'Peninsula Total'].iloc[0]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    # -------------------------------------------------------------
    # Subplot 1: Geometric Volume vs Ice-Equivalent Volume by Basin
    # -------------------------------------------------------------
    x = np.arange(len(basins_df['Basin']))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, basins_df['Corr_Vol_Geom_km3'], width, 
                    label='Geometric Column Vol ($V_{geom}$)', color='#2b5c8f', edgecolor='black', linewidth=0.8)
    rects2 = ax1.bar(x + width/2, basins_df['Corr_Vol_Ice_Eq_km3'], width, 
                    label='Solid-Ice Equivalent Vol ($V_{ice\_eq}$)', color='#56b4e9', edgecolor='black', linewidth=0.8)
    
    # Add values on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f"{h:,.0f}",
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1b3a5b')
                    
    for rect in rects2:
        h = rect.get_height()
        ax1.annotate(f"{h:,.0f}",
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0072b2')

    ax1.set_ylabel("Grounded Ice Volume ($\mathrm{km^3}$)", fontsize=11, fontweight='bold')
    ax1.set_title("Grounded Ice Volume by Basin (Bedmap3)\nGeometric Column vs. Solid-Ice Equivalent", fontsize=12, fontweight='bold', pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"Basin {b}\n({'Graham Land' if b=='I-Ipp' else 'Palmer W' if b=='Hp-I' else 'Palmer E'})" for b in basins_df['Basin']], fontsize=10)
    ax1.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    ax1.grid(axis='y', linestyle=':', alpha=0.6)
    ax1.set_ylim(0, 115000)

    # -------------------------------------------------------------
    # Subplot 2: Firn Air Volume and Relative Reduction
    # -------------------------------------------------------------
    categories = list(basins_df['Basin']) + ['Peninsula Total']
    firn_vols = list(basins_df['Firn_Air_Vol_km3']) + [total_row['Firn_Air_Vol_km3']]
    pct_red = list(basins_df['Firn_Volume_Reduction_%']) + [total_row['Firn_Volume_Reduction_%']]
    
    x2 = np.arange(len(categories))
    color_list = ['#e69f00', '#d55e00', '#cc79a7', '#009e73']
    
    bars = ax2.bar(x2, firn_vols, width=0.5, color=color_list, edgecolor='black', linewidth=0.8)
    
    for i, bar in enumerate(bars):
        h = bar.get_height()
        ax2.annotate(f"{h:,.1f} $\mathrm{{km^3}}$\n(-{pct_red[i]:.2f}%)",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax2.set_ylabel("Firn Air Volume ($\mathrm{km^3}$)", fontsize=11, fontweight='bold')
    ax2.set_title("Trapped Firn Air Volume & Relative Reduction\n$V_{firn} = V_{geom} - V_{ice\_eq}$", fontsize=12, fontweight='bold', pad=12)
    ax2.set_xticks(x2)
    ax2.set_xticklabels([f"{c}\n({pct_red[i]:.1f}% vol)" for i, c in enumerate(categories)], fontsize=9)
    ax2.grid(axis='y', linestyle=':', alpha=0.6)
    ax2.set_ylim(0, 4300)

    plt.tight_layout()
    out_png = os.path.join(fig_dir, "chart_ice_equivalent_vs_geometric_volume.png")
    fig.savefig(out_png, dpi=300)
    plt.close(fig)
    print(f"Chart successfully saved to {out_png}")

if __name__ == "__main__":
    generate_comparison_chart()

