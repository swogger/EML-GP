import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from eml_gp_stats import load_all_runs

plt.rcParams['font.family'] = 'serif'

def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "../results"
    print(f"Loading data from {data_dir}...")
    try:
        df = load_all_runs(data_dir)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Filter for target tests: 1.3 (Addition) and 3.2 (Arctan)
    target_tests = ["1.3", "3.2"]
    # Convert to string just in case, test_ids are usually floats like 1.3 or strings like "1.3"
    df["test_id_str"] = df["test_id"].astype(str)
    
    # Sometimes it's exactly "1.3", sometimes it might be "1.30". Try to match cleanly.
    df_filtered = df[df["test_id_str"].isin(target_tests) | df["test_id_str"].str.startswith(tuple(target_tests))].copy()
    
    if df_filtered.empty:
        print(f"No data found for tests {target_tests}.")
        print("Available test IDs:", df["test_id_str"].unique())
        return

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharey=True)
    
    for ax, tid in zip(axes, target_tests):
        sub_df = df_filtered[df_filtered["test_id_str"].str.startswith(tid)]
        if sub_df.empty:
            ax.set_title(f"Test {tid} (No Data)")
            continue
            
        std_nodes = sub_df[sub_df["algorithm"] == "Std-GP"]["nodes"].dropna().values
        eml_nodes = sub_df[sub_df["algorithm"] == "EML-GP"]["nodes"].dropna().values
        
        data_to_plot = [std_nodes, eml_nodes]
        
        if len(std_nodes) == 0 or len(eml_nodes) == 0:
            ax.set_title(f"Test {tid} (Insufficient Data)")
            continue
            
        parts = ax.violinplot(data_to_plot, showmeans=False, showmedians=True)
        
        # Color coding
        parts['bodies'][0].set_facecolor('#1f77b4') # Std-GP
        parts['bodies'][1].set_facecolor('#d62728') # EML-GP
        
        for pc in parts['bodies']:
            pc.set_alpha(0.6)
            
        # Add jittered scatter plot on top of violins to show individual runs
        def add_jitter(data, x_pos, color):
            jitter = np.random.normal(0, 0.04, size=len(data))
            ax.scatter(np.repeat(x_pos, len(data)) + jitter, data, color=color, s=10, alpha=0.5, zorder=3)
            
        add_jitter(std_nodes, 1, '#1f77b4')
        add_jitter(eml_nodes, 2, '#d62728')
            
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['Std-GP', 'EML-GP'])
        
        test_case_name = sub_df['test_case'].iloc[0].split(':')[-1].strip()
        ax.set_title(f"Test {tid}: {test_case_name}")
        if ax == axes[0]:
            ax.set_ylabel("Final Tree Size (Nodes)")
        ax.grid(axis='y', alpha=0.3)
        
        # Use log scale since tree sizes can range from 1 to thousands
        ax.set_yscale('log')

    plt.suptitle("Distribution of Final Tree Sizes: Evidence of Bimodal Failure", fontsize=14, y=1.05)
    plt.tight_layout()
    
    output_path = "Figure_Bimodal_Failure.png"
    plt.savefig(output_path, dpi=1200, bbox_inches="tight", facecolor="white")
    
    pdf_path = "Figure_Bimodal_Failure.pdf"
    plt.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    
    print(f"Saved {output_path} and {pdf_path}")

if __name__ == "__main__":
    main()
