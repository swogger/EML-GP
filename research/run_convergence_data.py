import subprocess
import re
import os
import csv
import sys
import datetime
import concurrent.futures
import resource
from test_suite import TEST_MATRIX, eml_plateau_mult
from seeds import SEEDS

TESTS_TO_COVER   = ['1.1', '1.2', '1.3', '1.4', '2.1', '3.1', '3.2', '3.3', '3.4', '3.5', '4.1', '4.2']
NUM_RUNS         = 30
GENERATIONS_LIST = [100, 200, 500]
POP_SIZE_LIST    = [100, 200, 500]
CPU_TIMEOUT_SEC  = 600  # 10 minutes of CPU time per run


def _set_cpu_limit():
    """Called in the child process before exec — kernel enforces the CPU limit."""
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_TIMEOUT_SEC, CPU_TIMEOUT_SEC))


def run_test_and_log(test_id, algorithm, run_idx, seed, generations, pop_size, output_dir):
    use_eml = (algorithm == 'eml')

    cmd = [
        "python3", "deduce_formula.py",
        "--test_id",      test_id,
        "--generations",  str(generations),
        "--pop_size",     str(pop_size),
        "--seed",         str(seed),
        "--plateau_mult", str(eml_plateau_mult(TEST_MATRIX[test_id]["std_ops"])) if use_eml else "1",
        "--print_interval", "1",
    ]
    if use_eml:
        cmd.append("--use_eml")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        preexec_fn=_set_cpu_limit,
    )

    stdout, stderr = process.communicate()

    gen_pattern = re.compile(
        r"Generation\s+(\d+)\s+-\s+Best Error:\s+([0-9.eE+\-inf]+)"
        r".*?Median Nodes:\s+(\d+)"
    )

    records = []
    for line in stdout.split('\n'):
        m = gen_pattern.search(line)
        if m:
            gen = int(m.group(1))
            try:
                best_fitness = float(m.group(2))
            except ValueError:
                best_fitness = float('inf')
            median_tree_size = int(m.group(3))
            records.append((gen, best_fitness, median_tree_size))

    filename = f"convergence_{test_id}_{algorithm}_{generations}_{pop_size}_{run_idx:02d}.csv"
    filepath = os.path.join(output_dir, filename)

    if not records:
        print(f"[{algorithm.upper()}] Test {test_id} Gen:{generations} Pop:{pop_size} Run {run_idx:02d} — WARNING: no output parsed, skipping write.")
        return

    tmp_path = filepath + ".tmp"
    with open(tmp_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["generation", "best_fitness", "median_tree_size"])
        for r in records:
            w.writerow(r)
    os.replace(tmp_path, filepath)

    print(f"[{algorithm.upper()}] Test {test_id} Gen:{generations} Pop:{pop_size} Run {run_idx:02d} — {len(records)} generations logged.")


def main():
    n_combos = len(GENERATIONS_LIST) * len(POP_SIZE_LIST)
    total_runs = n_combos * len(TESTS_TO_COVER) * 2 * NUM_RUNS
    print(f"\n[{datetime.datetime.now()}] Starting Convergence Data Collection...")
    print(f"Tests: {TESTS_TO_COVER}")
    print(f"Combinations: {len(GENERATIONS_LIST)} x {len(POP_SIZE_LIST)} = {n_combos}")
    print(f"Runs per config: {NUM_RUNS}  |  Total subprocess launches: {total_runs}\n")

    input_dir  = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(input_dir, "convergence_data")
    os.makedirs(output_dir, exist_ok=True)

    combo_idx = 0
    for generations in GENERATIONS_LIST:
        for pop_size in POP_SIZE_LIST:
            combo_idx += 1
            print(f"\n{'='*60}")
            print(f"Combination {combo_idx}/{n_combos}: Generations={generations}, Population={pop_size}")
            print(f"{'='*60}")

            tasks = []
            for tid in TESTS_TO_COVER:
                for run_idx in range(1, NUM_RUNS + 1):
                    seed = SEEDS[run_idx]
                    for algo in ('std', 'eml'):
                        filepath = os.path.join(
                            output_dir,
                            f"convergence_{tid}_{algo}_{generations}_{pop_size}_{run_idx:02d}.csv"
                        )
                        if os.path.exists(filepath):
                            print(f"  SKIP [{algo.upper()}] Test {tid} Gen:{generations} Pop:{pop_size} Run {run_idx:02d} (already on disk)")
                            continue
                        tasks.append((tid, algo, run_idx, seed, generations, pop_size, output_dir))

            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 8) as executor:
                futures = [executor.submit(run_test_and_log, *t) for t in tasks]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"  ERROR in worker: {e}")

            print(f"  --> Combination {combo_idx} done. Ran {len(tasks)} tasks.")

    print("\nData collection finished.")
    print(f"All files saved to {output_dir}")


if __name__ == "__main__":
    main()
