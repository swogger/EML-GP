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
  * `--plateau_mult`: Multiplies early stopping patience (recommended: `--plateau_mult 3` for EML-GP to allow for slower structural convergence).
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

---

### 4. Statistical Analysis

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

---

### 5. Utility / Auxiliary Files

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
