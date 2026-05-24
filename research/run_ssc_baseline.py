"""
Semantic Similarity-based Crossover (SSC) Baseline Experiment
==============================================================
Runs 4 configurations on 6 representative tests:
  - std_std : Std-GP  + standard crossover  (loaded from existing Regime A data)
  - std_ssc : Std-GP  + SSC                 (new runs)
  - eml_std : EML-GP  + standard crossover  (loaded from existing Regime A data)
  - eml_ssc : EML-GP  + SSC                 (new runs)
  - eml_mut : EML-GP  + mutation only       (loaded from existing Regime B data)

SSC (Uy et al., 2011): instead of picking crossover points uniformly at random,
sample N_CANDIDATES pairs and pick the pair whose subtree outputs are most similar
on a small set of fitness cases drawn from the training domain.

Usage:
    python run_ssc_baseline.py [output_dir]

Output:
    <output_dir>/ssc_results_summary.csv
    <output_dir>/ssc_convergence_data.csv
    <output_dir>/ssc_test_<id>.png  (one per test)
"""

import sys
import os
import csv
import math
import cmath
import random
import signal
import time
import datetime
import resource
import subprocess
import glob

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Path setup — mirror deduce_formula.py
# ---------------------------------------------------------------------------
_RESEARCH_DIR = os.path.dirname(os.path.abspath(__file__))
_GALIB_DIR    = os.path.abspath(os.path.join(_RESEARCH_DIR, "../ga-lib"))
sys.path.insert(0, _GALIB_DIR)

from generator import generate_ramped_population
from evolution  import mutate, point_mutate
from test_suite import TEST_MATRIX, eml_plateau_mult
from seeds      import SEEDS

# ---------------------------------------------------------------------------
# Experiment configuration
# ---------------------------------------------------------------------------
TESTS_TO_RUN   = ["1.1", "1.2", "1.3", "2.1", "3.2", "3.3"]
GENERATIONS    = 200
POP_SIZE       = 100
NUM_RUNS       = 30
CPU_TIMEOUT    = 600   # seconds of CPU time per run

# SSC parameters (Uy et al. 2011)
N_CANDIDATES   = 10    # candidate crossover points sampled per parent
N_SEMANTIC_PTS = 20    # fitness cases used to evaluate subtree similarity
SSC_THRESHOLD  = 1e6   # fall back to random crossover if best MSE exceeds this

# Budget (must match deduce_formula.py)
MAX_NODES = 2_000
MAX_DEPTH = math.ceil(math.log2(MAX_NODES + 1)) - 1  # 10
BATCH_SIZE      = 75
VALIDATION_SIZE = 200

# Existing data locations
_RESULTS_ROOT = os.path.abspath(os.path.join(_RESEARCH_DIR, "../results"))
REGIME_A_DIR  = os.path.join(_RESULTS_ROOT, "standard_gp", "convergence_data")
REGIME_B_DIR  = os.path.join(_RESULTS_ROOT, "mutation_only", "convergence_data")

plt.rcParams["font.family"] = ["Arial"]

ALGO_STYLES = {
    "std_std": {"color": "#1f77b4", "ls": "-",    "lw": 1.4, "label": "Std-GP (standard xover)"},
    "std_ssc": {"color": "#1f77b4", "ls": "--",   "lw": 1.4, "label": "Std-GP + SSC"},
    "eml_std": {"color": "#d62728", "ls": ":",    "lw": 1.4, "label": "EML-GP (standard xover)"},
    "eml_ssc": {"color": "#d62728", "ls": "--",   "lw": 1.4, "label": "EML-GP + SSC"},
    "eml_mut": {"color": "#d62728", "ls": "-.",   "lw": 1.4, "label": "EML-GP (mutation only)"},
}


# ---------------------------------------------------------------------------
# Helper: node count (mirrors deduce_formula.py)
# ---------------------------------------------------------------------------
def count_nodes(tree):
    if tree is None:
        return 0
    if not tree.is_operator:
        return 1
    return 1 + count_nodes(tree.left) + count_nodes(tree.right)


# ---------------------------------------------------------------------------
# SSC crossover
# ---------------------------------------------------------------------------
def _eval_subtree(node, variables, inputs):
    """Evaluate a subtree on a list of input dicts, return output vector."""
    out = []
    for kwargs in inputs:
        try:
            v = node.evaluate(**kwargs)
            out.append(abs(v))
        except Exception:
            out.append(float("inf"))
    return out


def _subtree_mse(vec_a, vec_b):
    """Mean squared difference between two subtree output vectors."""
    total = 0.0
    for a, b in zip(vec_a, vec_b):
        d = a - b
        if math.isnan(d) or math.isinf(d):
            total += 1000.0
        else:
            total += d * d
    return total / len(vec_a) if vec_a else float("inf")


def _all_nodes(tree):
    """Return list of all (node, parent, is_left) tuples in the tree."""
    result = []
    def traverse(node, parent=None, is_left=None):
        if node is not None:
            result.append((node, parent, is_left))
            traverse(node.left, node, True)
            traverse(node.right, node, False)
    traverse(tree)
    return result


def ssc_crossover(tree1, tree2, variables, semantic_inputs, max_nodes=MAX_NODES, rng=None):
    """
    SSC: sample N_CANDIDATES crossover points in each parent, pick the pair
    whose subtree outputs are most similar on semantic_inputs.  Fall back to
    a random crossover point if the best similarity exceeds SSC_THRESHOLD.
    """
    if rng is None:
        rng = random

    new_tree1 = tree1.copy()
    new_tree2 = tree2.copy()

    nodes1 = _all_nodes(new_tree1)
    nodes2 = _all_nodes(new_tree2)

    if not nodes1 or not nodes2:
        return new_tree1, new_tree2

    # Sample candidate points
    cands1 = rng.choices(nodes1, k=min(N_CANDIDATES, len(nodes1)))
    cands2 = rng.choices(nodes2, k=min(N_CANDIDATES, len(nodes2)))

    # Pre-compute semantic vectors for all candidates
    vecs1 = [_eval_subtree(n, variables, semantic_inputs) for n, _, _ in cands1]
    vecs2 = [_eval_subtree(n, variables, semantic_inputs) for n, _, _ in cands2]

    # Find the pair with smallest semantic distance
    best_mse  = float("inf")
    best_i, best_j = 0, 0
    for i, v1 in enumerate(vecs1):
        for j, v2 in enumerate(vecs2):
            m = _subtree_mse(v1, v2)
            if m < best_mse:
                best_mse = m
                best_i, best_j = i, j

    # Fall back to random if no semantically similar pair found
    if best_mse > SSC_THRESHOLD:
        best_i = rng.randrange(len(cands1))
        best_j = rng.randrange(len(cands2))

    node1, parent1, is_left1 = cands1[best_i]
    node2, parent2, is_left2 = cands2[best_j]

    # Perform the swap
    swap1 = node2.copy()
    swap2 = node1.copy()

    if parent1 is None:
        new_tree1 = swap1
    elif is_left1:
        parent1.left = swap1
    else:
        parent1.right = swap1

    if parent2 is None:
        new_tree2 = swap2
    elif is_left2:
        parent2.left = swap2
    else:
        parent2.right = swap2

    # Enforce MAX_NODES
    if count_nodes(new_tree1) > max_nodes:
        new_tree1 = tree1.copy()
    if count_nodes(new_tree2) > max_nodes:
        new_tree2 = tree2.copy()

    return new_tree1, new_tree2


# ---------------------------------------------------------------------------
# Single-run GP with SSC
# ---------------------------------------------------------------------------
def run_ssc(test_id, use_eml, seed, generations=GENERATIONS, pop_size=POP_SIZE):
    """
    Run one GP experiment (SSC crossover) and return per-generation records.
    Returns list of (generation, best_fitness) tuples.
    """
    test        = TEST_MATRIX[test_id]
    variables   = test["vars"]
    data_range  = test["range"]
    target_func = test["func"]
    std_ops     = test["std_ops"]

    # Three isolated RNG streams (same design as deduce_formula.py)
    master = seed
    _m     = random.Random(master)
    val_seed = _m.randint(0, 2**31 - 1)
    pop_seed = _m.randint(0, 2**31 - 1)
    evo_seed = _m.randint(0, 2**31 - 1)

    val_rng = random.Random(val_seed)
    pop_rng = random.Random(pop_seed)
    evo_rng = random.Random(evo_seed)

    # Monkey-patch global random (mirrors deduce_formula.py)
    import random as _rm
    _rm.choice  = evo_rng.choice
    _rm.random  = evo_rng.random
    _rm.sample  = evo_rng.sample
    _rm.uniform = evo_rng.uniform
    _rm.seed    = lambda *a, **kw: None

    terminals = [1.0]
    operators = ["eml"] if use_eml else std_ops

    plateau_mult = eml_plateau_mult(std_ops) if use_eml else 1
    plateau_gens = max(50, generations // 10) * plateau_mult

    val_inputs = [
        [val_rng.uniform(data_range[0], data_range[1]) for _ in variables]
        for _ in range(VALIDATION_SIZE)
    ]

    # Initialise population with pop_rng
    _rm.choice  = pop_rng.choice
    _rm.random  = pop_rng.random
    _rm.sample  = pop_rng.sample
    _rm.uniform = pop_rng.uniform

    population = generate_ramped_population(pop_size, MAX_DEPTH, operators, terminals, variables)

    _rm.choice  = evo_rng.choice
    _rm.random  = evo_rng.random
    _rm.sample  = evo_rng.sample
    _rm.uniform = evo_rng.uniform

    mut_depth = max(2, round(math.sqrt(MAX_DEPTH)))
    use_point_mutate = len(operators) > 1 or not all(op == "eml" for op in operators)

    def _mse(tree, inputs):
        if count_nodes(tree) > MAX_NODES:
            return float("inf")
        error = 0.0
        valid = 0
        try:
            for inp in inputs:
                kwargs   = {var: val for var, val in zip(variables, inp)}
                pred     = tree.evaluate(**kwargs)
                expected = target_func(*inp)
                diff     = abs(pred - expected)
                if cmath.isnan(diff) or cmath.isinf(diff):
                    error += 1000.0
                else:
                    error += diff ** 2
                valid += 1
            return error / valid if valid > 0 else float("inf")
        except Exception:
            return float("inf")

    def training_fitness(tree, batch):
        mse = _mse(tree, batch)
        if mse < 1e-5:
            return mse + count_nodes(tree) * 0.0001
        return mse

    def validation_error(tree):
        return _mse(tree, val_inputs)

    best_tree       = None
    best_val_error  = float("inf")
    gens_no_improve = 0
    records         = []

    for gen in range(generations):
        batch = [
            [evo_rng.uniform(data_range[0], data_range[1]) for _ in variables]
            for _ in range(BATCH_SIZE)
        ]

        # Semantic evaluation inputs for SSC (fresh sample each generation)
        sem_raw = [
            [evo_rng.uniform(data_range[0], data_range[1]) for _ in variables]
            for _ in range(N_SEMANTIC_PTS)
        ]
        semantic_inputs = [{var: val for var, val in zip(variables, inp)} for inp in sem_raw]

        fitness_scores = [(ind, training_fitness(ind, batch)) for ind in population]
        fitness_scores.sort(key=lambda x: x[1])

        gen_best = fitness_scores[0][0]
        gen_val  = validation_error(gen_best)

        if gen_val < best_val_error:
            best_val_error  = gen_val
            best_tree       = gen_best
            gens_no_improve = 0
        else:
            gens_no_improve += 1

        records.append((gen, best_val_error))

        if best_val_error <= 1e-6:
            break
        if gens_no_improve >= plateau_gens:
            break

        # Reproduction
        new_pop = [best_tree.copy()]

        while len(new_pop) < pop_size:
            t1 = evo_rng.sample(fitness_scores, k=5)
            t1.sort(key=lambda x: x[1])
            parent1 = t1[0][0]

            if evo_rng.random() < 0.75 and len(new_pop) < pop_size - 1:
                t2 = evo_rng.sample(fitness_scores, k=5)
                t2.sort(key=lambda x: x[1])
                parent2 = t2[0][0]
                child1, child2 = ssc_crossover(
                    parent1, parent2, variables, semantic_inputs, MAX_NODES, evo_rng
                )
                new_pop.extend([child1, child2])
            else:
                new_pop.append(parent1.copy())

        for i in range(1, len(new_pop)):
            if evo_rng.random() < 0.20:
                cand = mutate(new_pop[i], operators, terminals, variables,
                              mut_depth, absolute_max_depth=MAX_DEPTH)
                new_pop[i] = cand if count_nodes(cand) <= MAX_NODES else new_pop[i]
            elif use_point_mutate and evo_rng.random() < 0.05:
                new_pop[i] = point_mutate(new_pop[i], operators, terminals, variables)

        population = new_pop[:pop_size]

    return records


# ---------------------------------------------------------------------------
# Single-task entry point (invoked as a subprocess)
# ---------------------------------------------------------------------------
def _set_cpu_limit():
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_TIMEOUT, CPU_TIMEOUT))


def run_ssc_task(test_id, use_eml, run_idx, seed, output_dir):
    """Execute one SSC run and write its CSV. Called inside a fresh subprocess."""
    algo = "eml_ssc" if use_eml else "std_ssc"
    filename = f"ssc_{test_id}_{algo}_{run_idx:02d}.csv"
    filepath = os.path.join(output_dir, filename)

    records = run_ssc(test_id, use_eml, seed)

    if not records:
        print(f"  WARNING: {algo} Test {test_id} Run {run_idx:02d} produced no records")
        return

    tmp = filepath + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["generation", "best_fitness"])
        w.writerows(records)
    os.replace(tmp, filepath)

    print(f"  [{algo.upper()}] Test {test_id} Run {run_idx:02d} — {len(records)} gens")


def _load_ssc_runs(ssc_dir, test_id, algo_token):
    """Load SSC run CSVs written by run_ssc_task."""
    pattern = os.path.join(ssc_dir, f"ssc_{test_id}_{algo_token}_*.csv")
    files = sorted(glob.glob(pattern))
    dfs = []
    for path in files:
        try:
            dfs.append(pd.read_csv(path))
        except Exception:
            pass
    return dfs


# ---------------------------------------------------------------------------
# Aggregate runs into median/q1/q3 series
# ---------------------------------------------------------------------------
def aggregate(dfs, fitness_col="best_fitness"):
    """Return dict with generations, median, q1, q3, n_runs."""
    if not dfs:
        return None
    max_gen = max(df["generation"].max() for df in dfs)
    aligned = pd.DataFrame(index=np.arange(max_gen + 1))
    for i, df in enumerate(dfs):
        s = df.set_index("generation")[fitness_col]
        s = s.reindex(np.arange(max_gen + 1)).ffill()
        aligned[i] = s
    return {
        "generations": aligned.index.values,
        "median": aligned.median(axis=1).values,
        "q1":     aligned.quantile(0.25, axis=1).values,
        "q3":     aligned.quantile(0.75, axis=1).values,
        "n_runs": len(dfs),
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_test(test_id, series_dict, out_path):
    """
    series_dict: { algo_key -> aggregate_result_or_None }
    algo_key in ALGO_STYLES keys.
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for key, data in series_dict.items():
        if data is None:
            continue
        style = ALGO_STYLES[key]
        med = np.clip(data["median"], 1e-10, None)
        q1  = np.clip(data["q1"],    1e-10, None)
        q3  = np.clip(data["q3"],    1e-10, None)
        ax.plot(data["generations"], med,
                color=style["color"], ls=style["ls"], lw=style["lw"],
                label=f"{style['label']} (n={data['n_runs']})")
        ax.fill_between(data["generations"], q1, q3,
                        color=style["color"], alpha=0.10)

    test_name = TEST_MATRIX[test_id]["name"]
    ax.set_yscale("log")
    ax.set_title(f"Test {test_id}: {test_name}", fontsize=10)
    ax.set_xlabel("Generation", fontsize=9)
    ax.set_ylabel("MSE", fontsize=9)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.5)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc="upper right", framealpha=0.9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Saved {out_path}")


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def median_final_mse(data):
    if data is None:
        return float("nan")
    return float(np.median(data["median"][-1:]))


def write_summary(test_ids, all_series, out_path):
    rows = []
    for tid in test_ids:
        s = all_series[tid]
        rows.append({
            "test_id":              tid,
            "test_name":            TEST_MATRIX[tid]["name"],
            "std_std_median_mse":   median_final_mse(s.get("std_std")),
            "std_ssc_median_mse":   median_final_mse(s.get("std_ssc")),
            "eml_std_median_mse":   median_final_mse(s.get("eml_std")),
            "eml_ssc_median_mse":   median_final_mse(s.get("eml_ssc")),
            "eml_mut_median_mse":   median_final_mse(s.get("eml_mut")),
            "ssc_improves_eml":     _ssc_direction(s.get("eml_std"), s.get("eml_ssc")),
        })
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    print(f"Saved summary → {out_path}")
    return df


def _ssc_direction(std_data, ssc_data):
    a = median_final_mse(std_data)
    b = median_final_mse(ssc_data)
    if math.isnan(a) or math.isnan(b):
        return "N/A"
    if b < a:
        return f"BETTER  ({a:.4g} → {b:.4g})"
    if b > a:
        return f"WORSE   ({a:.4g} → {b:.4g})"
    return f"SAME    ({a:.4g})"


# ---------------------------------------------------------------------------
# Write consolidated convergence CSV
# ---------------------------------------------------------------------------
def write_convergence_csv(test_ids, all_series, out_path):
    rows = []
    for tid in test_ids:
        for algo_key, data in all_series[tid].items():
            if data is None:
                continue
            for g, med, q1, q3 in zip(
                data["generations"], data["median"], data["q1"], data["q3"]
            ):
                rows.append({
                    "test_id":            tid,
                    "generations_config": GENERATIONS,
                    "pop_size":           POP_SIZE,
                    "algorithm":          algo_key,
                    "generation":         g,
                    "median_fitness":     med,
                    "q1_fitness":         q1,
                    "q3_fitness":         q3,
                    "n_runs":             data["n_runs"],
                })
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"Saved convergence data → {out_path}")


# ---------------------------------------------------------------------------
# Subprocess orchestrator
# ---------------------------------------------------------------------------
def _run_tasks_parallel(tasks):
    """
    Spawn one subprocess per task.  Each process gets a fresh RLIMIT_CPU budget
    via preexec_fn, so timeouts are fully independent of one another.
    tasks: list of (test_id, use_eml, run_idx, seed, output_dir)
    """
    script = os.path.abspath(__file__)
    max_workers = os.cpu_count() or 4
    pending = list(tasks)
    active  = {}   # proc -> (test_id, use_eml, run_idx)

    while pending or active:
        while pending and len(active) < max_workers:
            test_id, use_eml, run_idx, seed, output_dir = pending.pop(0)
            cmd = [
                sys.executable, script,
                "--run-task", test_id, str(int(use_eml)), str(run_idx), str(seed), output_dir,
            ]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=_set_cpu_limit,
            )
            active[proc] = (test_id, use_eml, run_idx)

        finished = []
        for proc in list(active):
            ret = proc.poll()
            if ret is not None:
                out, _ = proc.communicate()
                test_id, use_eml, run_idx = active.pop(proc)
                for line in out.splitlines():
                    if line.strip():
                        print(f"  {line}")
                if ret in (-signal.SIGXCPU, -signal.SIGKILL):
                    algo = "eml_ssc" if use_eml else "std_ssc"
                    print(f"  TIMEOUT {algo} Test {test_id} Run {run_idx:02d}: CPU limit exceeded")
                elif ret != 0:
                    algo = "eml_ssc" if use_eml else "std_ssc"
                    print(f"  ERROR {algo} Test {test_id} Run {run_idx:02d}: exit code {ret}")
                finished.append(proc)

        if not finished:
            time.sleep(0.1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    output_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(_RESEARCH_DIR, "ssc_results")
    ssc_runs_dir = os.path.join(output_dir, "runs")
    os.makedirs(ssc_runs_dir, exist_ok=True)

    print(f"\n[{datetime.datetime.now()}] SSC Baseline Experiment")
    print(f"Tests: {TESTS_TO_RUN}")
    print(f"Generations: {GENERATIONS}, Population: {POP_SIZE}, Runs: {NUM_RUNS}")
    print(f"SSC candidates: {N_CANDIDATES}, Semantic pts: {N_SEMANTIC_PTS}")
    print(f"Output: {output_dir}\n")

    # ------------------------------------------------------------------
    # Phase 1: run SSC experiments
    # ------------------------------------------------------------------
    total_tasks = len(TESTS_TO_RUN) * 2 * NUM_RUNS
    print(f"Launching {total_tasks} SSC runs (std_ssc + eml_ssc × {NUM_RUNS} runs × {len(TESTS_TO_RUN)} tests)...\n")

    tasks = []
    for test_id in TESTS_TO_RUN:
        for run_idx in range(1, NUM_RUNS + 1):
            seed = SEEDS[run_idx]
            for use_eml in (False, True):
                algo = "eml_ssc" if use_eml else "std_ssc"
                fp = os.path.join(ssc_runs_dir, f"ssc_{test_id}_{algo}_{run_idx:02d}.csv")
                if not os.path.exists(fp):
                    tasks.append((test_id, use_eml, run_idx, seed, ssc_runs_dir))

    if tasks:
        _run_tasks_parallel(tasks)
    else:
        print("  All SSC runs already on disk — skipping execution.\n")

    # ------------------------------------------------------------------
    # Phase 2: load all data and build aggregate series
    # ------------------------------------------------------------------
    print("\nLoading and aggregating all runs...")

    # For Regime A we pick the reference cell: 200 generations, 100 population.
    # The filename pattern uses gen=200, pop=100.
    REF_GEN = 200
    REF_POP = 100

    def _regime_a(test_id, algo_token):
        """Load Regime A runs for specific gen/pop combo."""
        pat = os.path.join(REGIME_A_DIR, f"convergence_{test_id}_{algo_token}_{REF_GEN}_{REF_POP}_*.csv")
        files = sorted(glob.glob(pat))
        dfs = []
        for path in files:
            try:
                dfs.append(pd.read_csv(path))
            except Exception:
                pass
        return dfs

    def _regime_b(test_id, algo_token):
        pat = os.path.join(REGIME_B_DIR, f"convergence_{test_id}_{algo_token}_{REF_GEN}_{REF_POP}_*.csv")
        files = sorted(glob.glob(pat))
        dfs = []
        for path in files:
            try:
                dfs.append(pd.read_csv(path))
            except Exception:
                pass
        return dfs

    all_series = {}
    for test_id in TESTS_TO_RUN:
        std_std_dfs = _regime_a(test_id, "std")
        eml_std_dfs = _regime_a(test_id, "eml")
        eml_mut_dfs = _regime_b(test_id, "eml")
        std_ssc_dfs = _load_ssc_runs(ssc_runs_dir, test_id, "std_ssc")
        eml_ssc_dfs = _load_ssc_runs(ssc_runs_dir, test_id, "eml_ssc")

        for label, dfs in [
            ("std_std", std_std_dfs), ("eml_std", eml_std_dfs),
            ("eml_mut", eml_mut_dfs), ("std_ssc", std_ssc_dfs), ("eml_ssc", eml_ssc_dfs),
        ]:
            n = len(dfs)
            status = f"{n} runs" if n > 0 else "NO DATA"
            print(f"  Test {test_id} {label:8s}: {status}")

        all_series[test_id] = {
            "std_std": aggregate(std_std_dfs),
            "eml_std": aggregate(eml_std_dfs),
            "eml_mut": aggregate(eml_mut_dfs),
            "std_ssc": aggregate(std_ssc_dfs),
            "eml_ssc": aggregate(eml_ssc_dfs),
        }

    # ------------------------------------------------------------------
    # Phase 3: plots
    # ------------------------------------------------------------------
    print("\nGenerating plots...")
    for test_id in TESTS_TO_RUN:
        safe_id = test_id.replace(".", "_")
        out_png = os.path.join(output_dir, f"ssc_test_{safe_id}.png")
        plot_test(test_id, all_series[test_id], out_png)

    # ------------------------------------------------------------------
    # Phase 4: summary table + convergence CSV
    # ------------------------------------------------------------------
    summary_df = write_summary(
        TESTS_TO_RUN, all_series,
        os.path.join(output_dir, "ssc_results_summary.csv")
    )
    write_convergence_csv(
        TESTS_TO_RUN, all_series,
        os.path.join(output_dir, "ssc_convergence_data.csv")
    )

    print("\n--- Results Summary ---")
    print(summary_df.to_string(index=False))
    print(f"\n[{datetime.datetime.now()}] Done.")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--run-task":
        # Called by the orchestrator: run one task and exit.
        # argv: script --run-task test_id use_eml run_idx seed output_dir
        _, _, test_id, use_eml_str, run_idx, seed, output_dir = sys.argv
        run_ssc_task(test_id, bool(int(use_eml_str)), int(run_idx), int(seed), output_dir)
    else:
        main()
