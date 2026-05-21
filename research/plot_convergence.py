"""
Generate convergence curves for all (generations, pop_size) combinations,
comparing Std-GP and EML-GP best-fitness trajectories per generation.

Reads all `convergence_<test>_<algorithm>_<gen>_<pop>_<run>.csv` files in a
directory and produces one set of per-test figures per (gen, pop) combination,
saved into a single folder named `figures/`. It also generates consolidated
CSV files for the plotted data points and raw data in the input directory.

Usage:
    python plot_convergence.py <data_directory>

Example:
    python plot_convergence.py ./convergence_data
"""

import sys
import os
import re
import glob
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = ['Arial']

# Filename pattern: convergence_<testid>_<algo>_<gen>_<pop>_<run>.csv
FILENAME_PATTERN = re.compile(
    r"convergence_(\d+[._]\d+)_(std|eml)_(\d+)_(\d+)_(\d+)\.csv$",
    re.IGNORECASE,
)

TEST_LABELS = {
    "1_1": "Test 1.1 — exp(x)",
    "1_2": "Test 1.2 — ln(x)",
    "1_3": "Test 1.3 — Addition",
    "1_4": "Test 1.4 — exp composite",
    "2_1": "Test 2.1 — sin(x)+cos(x)",
    "3_1": "Test 3.1 — sinh(x)",
    "3_2": "Test 3.2 — arctan(x)",
    "3_3": "Test 3.3",
    "3_4": "Test 3.4",
    "3_5": "Test 3.5 — Polynomial",
    "4_1": "Test 4.1",
    "4_2": "Test 4.2",
}

PANEL_ORDER = ["1_1", "1_2", "1_3", "1_4", "2_1", "3_1", "3_2", "3_3", "3_4", "3_5", "4_1", "4_2"]

ALGO_COLORS = {"std": "#1f77b4", "eml": "#d62728"}
ALGO_LABELS = {"std": "Std-GP", "eml": "EML-GP"}


def parse_filename(path):
    match = FILENAME_PATTERN.search(os.path.basename(path))
    if not match:
        return None
    test_id, algo, generations, pop_size, run = match.groups()
    test_id = test_id.replace('.', '_')
    return test_id, algo.lower(), int(generations), int(pop_size), int(run)


def load_runs(data_dir):
    """Load all convergence CSVs, grouped by (generations, pop_size) combo."""
    files = sorted(glob.glob(os.path.join(data_dir, "convergence_*.csv")))
    if not files:
        raise FileNotFoundError(f"No convergence_*.csv files in {data_dir}")

    # combo -> list of (test_id, algo, run, df)
    combos = defaultdict(list)
    skipped = 0
    for path in files:
        meta = parse_filename(path)
        if meta is None:
            print(f"Skipping unrecognized filename: {os.path.basename(path)}")
            skipped += 1
            continue
        test_id, algo, generations, pop_size, run = meta
        df = pd.read_csv(path)
        combos[(generations, pop_size)].append((test_id, algo, run, df))

    print(f"Loaded {sum(len(v) for v in combos.values())} files across {len(combos)} combo(s). Skipped {skipped}.")
    return combos


def aggregate_panel(runs, test_id, algo):
    """Compute median, Q1, Q3 best_fitness per generation across runs."""
    matching = [df for tid, a, _, df in runs if tid == test_id and a == algo]
    if not matching:
        return None

    max_gen = max(df["generation"].max() for df in matching)

    aligned = pd.DataFrame(index=np.arange(max_gen + 1))
    for i, df in enumerate(matching):
        s = df.set_index("generation")["best_fitness"]
        s = s.reindex(np.arange(max_gen + 1)).ffill()
        aligned[i] = s

    return {
        "generations": aligned.index,
        "median": aligned.median(axis=1),
        "q1": aligned.quantile(0.25, axis=1),
        "q3": aligned.quantile(0.75, axis=1),
        "n_runs": len(matching),
    }


def save_consolidated_data(data_dir, combos):
    """Generate consolidated CSVs of both the plotted statistics and all raw run data."""
    print("\n--- Generating Consolidated CSV Files ---")
    plot_data_rows = []
    raw_dfs = []

    for (generations, pop_size), runs in sorted(combos.items()):
        available_tests = set(tid for tid, _, _, _ in runs)
        for test_id in PANEL_ORDER:
            if test_id not in available_tests:
                continue

            std_data = aggregate_panel(runs, test_id, "std")
            eml_data = aggregate_panel(runs, test_id, "eml")

            # Collect plot (aggregated) data
            for algo_data, algo_name in [(std_data, "std"), (eml_data, "eml")]:
                if algo_data is not None:
                    for g, med, q1, q3 in zip(
                        algo_data["generations"],
                        algo_data["median"],
                        algo_data["q1"],
                        algo_data["q3"]
                    ):
                        plot_data_rows.append({
                            "test_id": test_id,
                            "generations_config": generations,
                            "pop_size": pop_size,
                            "algorithm": algo_name,
                            "generation": g,
                            "median_fitness": med,
                            "q1_fitness": q1,
                            "q3_fitness": q3,
                            "n_runs": algo_data["n_runs"]
                        })

        # Collect raw data efficiently
        for test_id, algo, run, df in runs:
            df_copy = df.copy()
            df_copy["test_id"] = test_id
            df_copy["generations_config"] = generations
            df_copy["pop_size"] = pop_size
            df_copy["algorithm"] = algo
            df_copy["run"] = run
            raw_dfs.append(df_copy)

    # Save to CSV files
    if plot_data_rows:
        plot_df = pd.DataFrame(plot_data_rows)
        plot_csv_path = os.path.join(data_dir, "convergence_plot_data.csv")
        plot_df.to_csv(plot_csv_path, index=False)
        print(f"Saved consolidated plot statistics to: {plot_csv_path}")

    if raw_dfs:
        raw_df = pd.concat(raw_dfs, ignore_index=True)
        # Reorder and filter columns
        cols = ["test_id", "generations_config", "pop_size", "algorithm", "run", "generation", "best_fitness"]
        raw_df = raw_df[cols]
        raw_csv_path = os.path.join(data_dir, "convergence_raw_consolidated.csv")
        raw_df.to_csv(raw_csv_path, index=False)
        print(f"Saved consolidated raw runs data to: {raw_csv_path}")


def plot_panel(ax, std_data, eml_data, test_label, generations, pop_size):
    for algo_data, algo_name in [(std_data, "std"), (eml_data, "eml")]:
        if algo_data is None:
            continue
        color = ALGO_COLORS[algo_name]
        label = f"{ALGO_LABELS[algo_name]} (n={algo_data['n_runs']})"

        median_safe = algo_data["median"].clip(lower=1e-10)
        q1_safe = algo_data["q1"].clip(lower=1e-10)
        q3_safe = algo_data["q3"].clip(lower=1e-10)

        linestyle = ":" if algo_name == "eml" else "-"
        ax.plot(algo_data["generations"], median_safe, color=color,
                linewidth=1.6, linestyle=linestyle, label=label)
        ax.fill_between(algo_data["generations"], q1_safe, q3_safe,
                        color=color, alpha=0.15)

    ax.set_yscale("log")
    ax.set_title(f"{test_label}\n(Generations: {generations}, Population: {pop_size})", fontsize=10)
    ax.set_xlabel("Generation", fontsize=8)
    ax.set_ylabel("MSE", fontsize=8)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.5)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc="upper right", framealpha=0.9)


def make_figures(data_dir):
    combos = load_runs(data_dir)
    save_consolidated_data(data_dir, combos)

    out_dir = os.path.join(data_dir, "figures")
    os.makedirs(out_dir, exist_ok=True)

    for (generations, pop_size), runs in sorted(combos.items()):
        print(f"\n--- Gen:{generations} Pop:{pop_size} → {out_dir} ---")

        available_tests = set(tid for tid, _, _, _ in runs)

        for test_id in PANEL_ORDER:
            if test_id not in available_tests:
                print(f"  Skipping {test_id} (no data)")
                continue

            fig, ax = plt.subplots(figsize=(6, 4))
            std_data = aggregate_panel(runs, test_id, "std")
            eml_data = aggregate_panel(runs, test_id, "eml")
            plot_panel(ax, std_data, eml_data, TEST_LABELS[test_id], generations, pop_size)

            fig_name = os.path.join(out_dir, f"convergence_{test_id}_tests_{generations}_{pop_size}.png")
            plt.savefig(fig_name, dpi=1200, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            print(f"  Saved {fig_name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    make_figures(sys.argv[1])
