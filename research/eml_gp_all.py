"""
Run statistical analysis on every grid cell in the dataset.

Outputs:
  - Console summary: count of significant differences per cell
  - all_cells_analysis.md : full markdown file with all 18 tables 
    (one convergence + one tree-size table per cell), 
    suitable for direct inclusion as Supplementary Material

Usage:
    python run_all_cells.py <data_directory>

Example:
    python run_all_cells.py ../results
"""

import sys
import os
import io
import contextlib

# Import functions from the main analysis module
from eml_gp_stats import (
    load_all_runs,
    compare_convergence,
    compare_tree_size,
    apply_holm,
    make_convergence_table,
    make_tree_size_table,
)


def analyze_cell(df, gens, pop):
    """Run both statistical comparisons for a single grid cell."""
    cell = df[(df["gens"] == gens) & (df["pop"] == pop)]
    if cell.empty:
        return None, None, None
    
    test_ids = sorted(cell["test_id"].unique())
    
    conv_results = []
    for tid in test_ids:
        sub = cell[cell["test_id"] == tid]
        std = sub[sub["algorithm"] == "Std-GP"]["converged"]
        eml = sub[sub["algorithm"] == "EML-GP"]["converged"]
        conv_results.append(compare_convergence(std, eml))
    conv_results = apply_holm(conv_results)
    
    size_results = []
    for tid in test_ids:
        sub = cell[cell["test_id"] == tid]
        std = sub[sub["algorithm"] == "Std-GP"]["nodes"]
        eml = sub[sub["algorithm"] == "EML-GP"]["nodes"]
        size_results.append(compare_tree_size(std, eml))
    size_results = apply_holm(size_results)
    
    return test_ids, conv_results, size_results


def count_significant(results):
    return sum(1 for r in results if r.get("significant", False))


def main(data_dir):
    print(f"Loading from: {data_dir}")
    df = load_all_runs(data_dir)
    print(f"Loaded {len(df)} rows from {df['run'].nunique()} unique run IDs")
    
    cells = sorted(df.groupby(["gens", "pop"]).groups.keys())
    print(f"Found {len(cells)} grid cells: {cells}\n")
    
    # Console summary
    print(f"{'Grid cell':<12} {'n':<6} {'Conv. sig.':<12} {'Tree-size sig.':<15}")
    print("-" * 50)
    
    out_lines = [
        "# Supplementary Material S1: Per-Cell Statistical Analyses",
        "",
        "Statistical comparisons of EML-GP vs Std-GP at every grid cell. "
        "Convergence rates compared with Fisher's exact test; tree sizes with "
        "Mann-Whitney U test. All p-values Holm-Bonferroni corrected across "
        "the 12 target functions per cell (α = 0.05).",
        "",
        "## Summary across all cells",
        "",
        "| Grid cell (Gens × Pop) | n per algorithm per test | Convergence: significant tests | Tree size: significant tests |",
        "|---------------|--------------------------|-------------------------|----------------------|",
    ]
    
    detailed_sections = []
    
    for gens, pop in cells:
        test_ids, conv, size = analyze_cell(df, gens, pop)
        if test_ids is None:
            continue
        n_runs = df[(df["gens"] == gens) & (df["pop"] == pop) & 
                    (df["algorithm"] == "Std-GP")].groupby("test_id").size().median()
        n_runs = int(n_runs) if not (n_runs != n_runs) else 0  # NaN check
        
        n_conv_sig = count_significant(conv)
        n_size_sig = count_significant(size)
        
        cell_label = f"{gens}×{pop}"
        print(f"{cell_label:<12} {n_runs:<6} {n_conv_sig}/{len(conv):<10} {n_size_sig}/{len(size)}")
        
        out_lines.append(
            f"| {cell_label} | {n_runs} | {n_conv_sig}/{len(conv)} | {n_size_sig}/{len(size)} |"
        )
        
        # Detailed tables for this cell
        section = [
            "",
            f"## Grid cell {cell_label}",
            "",
            make_convergence_table(test_ids, conv, label=cell_label),
            "",
            make_tree_size_table(test_ids, size, label=cell_label),
        ]
        detailed_sections.extend(section)
    
    out_lines.extend(detailed_sections)
    
    output_path = "all_cells_analysis.md"
    with open(output_path, "w") as f:
        f.write("\n".join(out_lines))
    
    print(f"\nFull report written to: {output_path}")
    print("Paste it directly into your supplementary material.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])