# EML GP Research Scripts

This directory contains scripts used to conduct, plot, and analyze experiments comparing **Standard GP** (using standard mathematical operators) and **EML-GP** (using the single binary EML operator: `eml(a, b) = exp(a) - ln(b)`).

---

## Script Index

### 1. Core Evolution Scripts

#### `deduce_formula.py`
The primary Genetic Programming script. It runs a single GP evolution trial on a selected target function.
* **Usage**:
  ```bash
  python3 deduce_formula.py [arguments]
  ```
* **Key Arguments**:
  * `--use_eml`: Run EML-GP using only `['eml']` and terminal `1.0`. If omitted, runs Standard GP using test-specific mathematical operators.
  * `--test_id`: Select test case from the test suite (e.g. `1.1`, `1.2`, `1.3`, `3.2`, etc.). If omitted, uses a default target `f(x, y) = (x * y) - 2.0`.
  * `--pop_size`: Number of individuals in the population (default: `500`).
  * `--generations`: Maximum number of generations (default: `100`).
  * `--seed`: Master RNG seed. Derives isolated streams for validation, population, and evolution to ensure fair comparisons.
  * `--mutation_only`: Disable crossover, using 100% mutation (95% subtree, 5% point).
  * `--std_ops`: Comma-separated operator set overriding the per-target set from `test_suite.py` (e.g. `--std_ops '+,-,*,/,exp,log,sin,cos'`). Used by the fixed-primitive-set control; omitted, behaviour is unchanged.
  * `--plateau_mult`: Multiplies early-stopping patience. The study uses the per-test multipliers in `test_suite.py`, each the mean EML K-complexity of that test's Std-GP operator set, which compensates EML-GP for the deeper trees it must assemble.
  * `--print_interval`: Frequency of printing generation metrics (default: `10`).
* **Expected Output**:
  * Real-time generation progress printed to console (best error, validation error, size, formula).
  * Final summary report on convergence, tree size, and SymPy-simplified formula.

#### `compare.py`
Runs a quick concurrent side-by-side comparison of Standard GP and EML-GP on the default target function.
* **Usage**:
  ```bash
  python3 compare.py
  ```
* **Expected Output**:
  * Runs both trials concurrently in a thread pool.
  * Prints a console comparison table comparing: Wall-clock runtime, Generations to perfect convergence, Final validation error, Final tree size, and Simplified formula.

---

### 2. Grid Search Orchestrators

#### `run_matrix.py` / `run_matrix_mutation.py`
Runs the complete grid search experiment across a 3×3 parameter sweep:
* Generations: `[100, 200, 500]`
* Populations: `[100, 200, 500]`
* Runs: `30` independent trials per combination (seeded deterministically from `seeds.py`).
`run_matrix_mutation.py` runs with the `--mutation_only` flag.
* **Usage**:
  ```bash
  python3 run_matrix.py
  # OR
  python3 run_matrix_mutation.py
  ```
* **Expected Output**:
  * Automatically resumes/skips completed trials already on disk.
  * Executes trials in parallel using a CPU-bound thread pool.
  * Outputs detailed files to `results/` (or `results/mutation_only/`):
    * `results_<gen>_<pop>_<run>.csv`: Complete run statistics for all test functions.
    * `summary_<gen>_<pop>_<run>.csv`: Simplified summary of runs.
    * `stats_<gen>_<pop>.csv`: Aggregated means, standard deviations, and convergence rates.

#### `run_convergence_data.py` / `run_convergence_data_mutation.py`
Collects generation-by-generation convergence trajectories (best fitness and median tree size per generation) across the 3×3 grid search.
* **Usage**:
  ```bash
  python3 run_convergence_data.py [target_results_directory]
  # OR
  python3 run_convergence_data_mutation.py [target_results_directory]
  ```
* **Expected Output**:
  * Outputs trajectory files under the directory `convergence_data/`:
    * `convergence_<test>_<algorithm>_<gen>_<pop>_<run>.csv` containing the columns: `generation,best_fitness,median_tree_size`.

---

### 3. Plotting & Visualization

#### `plot_convergence.py`
Aggregates the individual run files under `convergence_data/` and plots their trajectories.
* **Usage**:
  ```bash
  python3 plot_convergence.py <results_data_directory>
  ```
* **Expected Output**:
  * Generates per-test PNG figures under a `figures/` subdirectory within the results directory.
  * Generates two consolidated CSVs in the target directory for downstream statistical analysis:
    * `convergence_plot_data.csv`: Aggregated stats (`median_fitness`, `q1_fitness`, `q3_fitness`, `n_runs` per generation).
    * `convergence_raw_consolidated.csv`: All raw data points across all runs consolidated.

#### `plot_bimodal.py`
Generates a violin plot to visualize the tree size distribution for target tests `1.3` (Addition) and `3.2` (Arctan), illustrating the "bimodal failure" mode of EML-GP.
* **Usage**:
  ```bash
  python3 plot_bimodal.py [results_directory]
  ```
* **Expected Output**:
  * Generates two files:
    * `Figure_Bimodal_Failure.png`: High-resolution PNG.
    * `Figure_Bimodal_Failure.pdf`: Vector PDF format.
* **Note**: the manuscript's Fig. 13 is produced by `make_all_figures.py`, which adds the per-group sample sizes; this script remains the standalone version.

---

### 4. Baseline Comparison Experiments

#### `run_sr_benchmarks.py`
Runs 4 standard symbolic regression benchmarks (Nguyen-1, Nguyen-7, Keijzer-6, Vladislavleva-4) under all four regime combinations: Std-GP and EML-GP, each in Regime A (crossover + mutation) and Regime B (mutation only). 30 seeded runs per configuration (200 generations, population 100).
* **Usage**:
  ```bash
  python3 run_sr_benchmarks.py [output_dir]
  ```
* **Expected Output** (written to `output_dir`, default `sr_benchmark_results/`):
  * `runs/sr_<benchmark>_<algo>_<run>.csv`: Per-run convergence trajectory (`generation`, `best_fitness`, `converged`).
  * `sr_benchmark_results_summary.csv`: Convergence rates and median final MSE for all benchmarks and configurations.
  * `sr_benchmark_convergence_data.csv`: Aggregated median/Q1/Q3 fitness per generation for all configurations.
  * `sr_benchmark_<benchmark>.png`: Convergence plot per benchmark.
* **Notes**:
  * Each run is spawned as an independent subprocess with a 600s CPU-time limit (`RLIMIT_CPU`) enforced by the kernel, so runs are fully isolated from each other.
  * Automatically resumes if interrupted — completed run files on disk are skipped.

#### `run_ssc_baseline.py`
Runs a Semantic Similarity-based Crossover (SSC) baseline experiment (Uy et al., 2011) on 6 representative test functions, comparing SSC against standard crossover and mutation-only variants. Loads existing Regime A and B data from disk for the standard crossover baselines; runs only the new SSC configurations.
* **Usage**:
  ```bash
  python3 run_ssc_baseline.py [output_dir]
  ```
* **Expected Output** (written to `output_dir`, default `ssc_results/`):
  * `runs/ssc_<test>_<algo>_<run>.csv`: Per-run convergence trajectory for SSC configurations.
  * `ssc_results_summary.csv`: Median final MSE comparison across all 5 configurations per test.
  * `ssc_convergence_data.csv`: Aggregated median/Q1/Q3 fitness per generation.
  * `ssc_test_<id>.png`: Convergence plot per test.
* **Notes**:
  * Same subprocess-per-run isolation model as `run_sr_benchmarks.py`.
  * Requires existing convergence data in `results/standard_gp/convergence_data/` and `results/mutation_only/convergence_data/` for the reference cell (200 generations, population 100).

---

### 5. Statistical Analysis

#### `eml_gp_stats.py`
Calculates statistics for a specific grid cell comparison (Default: `200x100`).
* **Usage**:
  ```bash
  python3 eml_gp_stats.py <results_directory> [grid_cell]
  ```
* **Expected Output**:
  * Performs Fisher's exact tests on convergence rates.
  * Performs Mann-Whitney U tests on tree sizes with rank-biserial effect sizes.
  * Applies Holm-Bonferroni correction (α = 0.05).
  * Prints formatted markdown tables and a draft summary paragraph directly to the console.

#### `eml_gp_all.py`
Automates the statistical analysis across all grid cells found in the results directory.
* **Usage**:
  ```bash
  python3 eml_gp_all.py <results_directory>
  ```
* **Expected Output**:
  * Generates `all_cells_analysis.md` inside the results directory, containing full convergence and tree-size tables across all Swept grid cells.

#### `dump_target_k.py`
Computes the EML token count `K` for every study target and SR benchmark by **compiling** the formula into an actual EML tree (via `eml_core.compile`, substituting library witnesses and counting tokens) rather than relying on hand-written estimates. Replaces the hand-tabulated `K` values in Appendix C with compiler-produced upper bounds, numerically verifies each compiled tree against its target, and reports the associated plateau patience multipliers.
* **Usage**:
  ```bash
  python3 dump_target_k.py [--json]
  ```
* **Expected Output**:
  * A formatted table (or `--json` blob) of primitives, study targets, and SR benchmarks, each with `K`, operator count `m = (K-1)/2`, oddness check, patience multiplier, and a numerical `verified` flag (max relative error vs. the reference `cmath` implementation).
  * Flags any tree whose token count is inconsistent with the reported `K`, and prints blocking/diagnostic notes for targets the compiler cannot synthesize.
* **Notes**:
  * Every `K` is an **upper bound** (a construction of that size exists) except where the underlying witness is annotated as proven minimal. `K` is always odd — an EML tree with `m` operators has exactly `2m+1` tokens.
  * Requires the `eml-skill` witness library on the path (resolved automatically relative to this directory).

---

### 6. Utility / Auxiliary Files

#### `eml_simplify.py`
A module containing helpers that convert a GP tree containing `eml` operators into a standard algebraic expression via SymPy.
* **Usage**: Typically imported as:
  ```python
  from eml_simplify import simplify_eml_tree
  ```
* **Note**: Simplification executes in a separate process with a timeout to prevent evolutionary execution hangs.

#### `eml_deduce.py`
A simpler, standalone implementation of EML-only GP that bypasses the general `ga-lib` framework, using `eml-skill`'s types directly.
* **Usage**:
  ```bash
  python3 eml_deduce.py [--pop_size POP_SIZE] [--generations GENS] [--max_depth DEPTH]
  ```

#### `test_suite.py`
Defines the `TEST_MATRIX` for all 12 test functions, data bounds, standard operator sets, and EML plateau patience multipliers.

#### `seeds.py`
Contains the 31 fixed deterministic seeds ensuring experimental replication.

---

### 7. Dense-K Synthetic-Target Experiment (`research/synthetic/`)

A self-contained experiment that isolates the effect of EML complexity `K` on convergence by searching for targets whose `K` is **known by construction**. Every target is an EML tree over `{x, 1}` with exactly `m = (K-1)/2` operators, so expressibility is guaranteed and a 0% convergence result is unambiguously a *search* failure rather than an inexpressibility. The search itself is the main study's EML-GP verbatim (same `ga-lib` operators, ramped init, tournament, elitism, node cap, and plateau rule at the reference cell: pop 100, gen 200, node cap 2000, 600 s timeout), with two deliberate, documented deviations — normalised fitness (nMSE = MSE / Var(target)) and a numpy-vectorised evaluator.

Full provenance, definitions, results-at-a-glance, and caveats live in **[`results/synthetic_dense_k/README.md`](results/synthetic_dense_k/README.md)** and the machine-readable `results/synthetic_dense_k/run_metadata.json`.

Pipeline order: `make_targets.py` → (`make_targets_lowk.py`) → `run_synthetic.py` → `summarize.py` → `calibration.py` / `analysis_ncrit_vs_k.py` / `evaluator_agreement.py`.

#### `eml_synth_core.py`
Core library for the experiment: target parsing/evaluation, the vectorised evaluator, grid and held-out sampling, and a line-for-line transcription of `deduce_formula.py`'s reproduction loop at the reference cell. Documents the two deviations from the main study and provides `check_evaluator_agreement()`. Imported by the other scripts; not run directly.

#### `make_targets.py`
Generates, filters, and structurally measures the pre-registered dense-K targets (13 K levels, 7…31 × 30 targets, plus the force-included rigid, gradient-free reference case, carried in the data under the row key `reviewer_ce`). Acceptance filters run in protocol order (viability → novelty → irreducibility, with an exhaustive minimality audit for K ≤ 11).
* **Usage**: `python3 make_targets.py`
* **Writes** (to `results/synthetic_dense_k/`): `synthetic_targets.csv` (File 2), `synthetic_targets_extra.csv` (diagnostics), `targets.json` (input for the run), `target_generation_log.json` (rejection accounting).

#### `make_targets_lowk.py`
**Post-hoc** extension to K = 3 and K = 5 (outside the pre-registration), used to anchor the logistic fit's upper asymptote and calibrate against `exp(x)`. Spaces are enumerated exhaustively (4 trees at K=3, 16 at K=5). Writes `*_lowk` files kept separate from the contract; do **not** merge into Files 1–2.

#### `run_synthetic.py`
Executes the GP runs: 10 paired seeds × 2 regimes per target at the reference cell. Resumable — completed `(target_id, regime, seed)` triples are read back from the output CSV and skipped.
* **Usage**: `python3 run_synthetic.py`
* **Writes**: `synthetic_runs.csv` (File 1, one row per run).

#### `summarize.py`
Aggregates runs into `synthetic_summary_by_K.csv` (File 3, one row per (K, regime) with Wilson intervals) and assembles `run_metadata.json` (configuration, definitions, provenance including file SHA-1s, and caveats).
* **Usage**: `python3 summarize.py`

#### `calibration.py`
Calibrates the synthetic instrument against the main study's real targets at the pop 100 / G 200 cell — both same-function (`exp(x) = K03_01`, `ln(x) = K07_07`, each re-scored under the main study's absolute MSE ≤ 1e-6 rule) and band-placement. Writes `calibration_same_function.csv` and `calibration_real_targets.csv`.

#### `analysis_ncrit_vs_k.py`
Indicative model comparison of `conv ~ K` vs. `conv ~ n_crit` (deviance / AIC / AUC) plus the within-K test of whether rigidity `α` separates outcomes at fixed K, fitted at both run level (cluster-robust SEs) and target level. Underlies `analysis_scale_vs_rigidity.txt`. Requires `statsmodels`.

#### `evaluator_agreement.py`
Validates the vectorised evaluator against the reference `cmath` evaluator on trees drawn from the GP's own generator, reporting the best fitness among disagreeing trees (`min_nmse_among_disagreements`) to confirm no disagreement can flip a converged outcome. Writes `evaluator_agreement.json`.

---

### 8. Termination and Regime B Analyses (`results/*/`)

Derived tables behind Supplementary Material S1, covering how runs end and how Regime B behaves
across the budget grid:
* `results/standard_gp/termination_generation_analysis.csv`, `results/mutation_only/termination_generation_analysis.csv` — per test × algorithm distribution of first-convergence and failure-termination generations across the 100/200/500 budgets (Supplementary Tables S2 and S3). These establish that convergence rates are invariant to the generation budget because every convergence event occurs by generation 91, and they separate runs that exhausted their budget from runs terminated by the CPU ceiling.
* `results/mutation_only/regimeB_convergence_rates_std.csv`, `results/mutation_only/regimeB_convergence_rates_eml.csv` — Regime B (mutation-only) convergence rates across the full 3×3 grid (Supplementary Tables S4 and S5), documenting where the budget invariance is exact and where it is only approximate.

---

### 9. Fixed-Primitive-Set Control (`research/run_control_fixedset.py`)

Re-runs the Std-GP arm under a single operator set applied uniformly to all twelve targets, to
measure how much of the heterogeneous baseline's advantage comes from per-target operator
selection rather than from search (Section 5.5, Tables 15 and 16).
* **Usage**:
  ```bash
  python3 run_control_fixedset.py [--arms FIX,ABL] [--n_seeds 30] [--workers 6]
  ```
* **Arms**:
  * `FIX` — `{+,-,*,/,exp,log,sin,cos}` on all twelve targets, both regimes. sin and cos are kept so that a zero rate measures search difficulty rather than inexpressibility.
  * `ABL` — `{+,-,*,/,exp,log}` on the two mixed targets (sinh, x^x), removing the matching primitive while adding none, so ablation is separated from dilution.
* **Expected Output**: `results/fixed_set_control/control_runs.csv`, one row per run with arm, operator set, regime, test, seed, final error, node count, status, and CPU and wall time.
* **Notes**:
  * Seed-matched to the main grid at the reference cell (G=200, P=100), so every control run pairs with its main-study counterpart.
  * Resumable — completed `(arm, regime, test, seed)` rows are skipped on restart.
  * Each run is spawned through `_cpu_limit_run.py` under a 600 s **CPU-time** limit.

#### `_cpu_limit_run.py`
Wrapper that runs a command under a hard `RLIMIT_CPU` limit rather than a wall-clock timeout, so
censoring is unaffected by machine load, and reports the CPU actually consumed.
* **Usage**:
  ```bash
  python3 _cpu_limit_run.py <cpu_seconds> <command> [args...]
  ```
* **Expected Output**: the child's stdout, plus `__CPU_SECONDS__=<float>` and `__TERMSIG__=<int>` on stderr.

---

### 10. Manuscript Figures (`research/make_all_figures.py`)

Regenerates every figure in the paper as 400 dpi PNG and vector PDF into `figures/` at the
repository root.
* **Usage**:
  ```bash
  python3 make_all_figures.py
  ```
* **Expected Output**: `figures/Fig01…Fig13`, each as `.png` and `.pdf`. Trajectory panels reuse the aggregation and styling of `plot_convergence.py` so they match the published versions; Figure 12 is delegated to `synthetic/plot_fig12.py`.
* **Notes**: requires the convergence data under `results/standard_gp/convergence_data/` and `results/mutation_only/convergence_data/`, the SSC and benchmark outputs, and the dense-K results.

#### `synthetic/plot_fig12.py`
Renders Figure 12, convergence against target K-complexity for both regimes, with Wilson
intervals and logistic fits. Curves are fitted to the thirteen pre-specified levels only
(K = 7…31); the post-hoc levels K = 3 and 5 are drawn as hollow markers and excluded from the
fit, so the plotted curve and the quoted midpoint are the same estimate.
* **Usage**: `python3 plot_fig12.py`

#### `synthetic/run_budget_sweep.sh`
Repeats the dense-K experiment over the transition band at four and sixteen times the main
generation budget, to bound how far the assembly-reach midpoint K₅₀ moves with search budget
(Supplementary Tables S12 and S13). Runs sequentially and is resumable.
* **Usage**: `bash run_budget_sweep.sh`
* **Expected Output**: `results/synthetic_dense_k/budget_pilot_g800.csv`, `g800_lowk.csv`, `g3200_main.csv`, `g3200_lowk.csv`.
