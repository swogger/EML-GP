import subprocess
import re
import os
import csv
import sys
import datetime
import statistics
import concurrent.futures
from test_suite import TEST_MATRIX, eml_plateau_mult
from seeds import SEEDS

csv.field_size_limit(sys.maxsize)

GENERATIONS_LIST     = [100, 200, 500]
POPULATION_SIZE_LIST = [100, 200, 500]
NUM_RUNS             = 30          # must be <= len(SEEDS) - 1


def run_test(test_id, use_eml, generations, pop_size, seed):
    cmd = [
        "python3", "deduce_formula.py",
        "--test_id",      test_id,
        "--generations",  str(generations),
        "--pop_size",     str(pop_size),
        "--seed",         str(seed),
        "--plateau_mult", str(eml_plateau_mult(TEST_MATRIX[test_id]["std_ops"])) if use_eml else "1",
        "--mutation_only",
    ]
    if use_eml:
        cmd.append("--use_eml")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    try:
        stdout, stderr = process.communicate(timeout=600)  # 10 min hard ceiling per trial
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        return None, None, generations, "TIMEOUT", "TIMEOUT"

    final_error   = None
    final_nodes   = None
    best_gen      = generations
    lowest_error  = float('inf')
    formula       = "None"
    status        = "BUDGET EXHAUSTED"

    for line in stdout.split('\n'):
        if "Best Formula: Result =" in line:
            formula = line.split("Result = ")[1].strip()

        if line.startswith("Node count:"):
            m = re.search(r"Node count:\s*(\d+)", line)
            if m:
                final_nodes = int(m.group(1))

        if "Final MSE:" in line:
            m = re.search(r"Final MSE:\s*([0-9.eE+\-]+)", line)
            if m:
                try:
                    final_error = float(m.group(1))
                except ValueError:
                    pass

        if "Status:" in line:
            if "CONVERGED" in line:
                status = "CONVERGED"

        # Per-generation line:
        # "Generation 010 - Best Error: 0.001234 - Val Error: 0.001100 - Nodes:    37 - ..."
        if "Generation" in line and "Best Error" in line:
            m = re.search(
                r"Generation\s+(\d+)\s+-\s+Best Error:\s+([0-9.eE+\-inf]+)"
                r"\s+-\s+Val Error:\s+([0-9.eE+\-inf]+)"
                r"\s+-\s+Nodes:\s+(\d+)",
                line
            )
            if m:
                gen = int(m.group(1))
                try:
                    err = float(m.group(2))
                except ValueError:
                    err = float('inf')
                nodes = int(m.group(4))
                final_nodes = nodes
                if err < lowest_error:
                    lowest_error = err
                    best_gen     = gen

    return final_error, final_nodes, best_gen, formula, status


def run_single_eval(test_id, name, use_eml, generations, pop_size, seed):
    err, nodes, gen, form, status = run_test(test_id, use_eml, generations, pop_size, seed)
    return {
        "test_id": test_id,
        "use_eml": use_eml,
        "err":     err,
        "nodes":   nodes,
        "gen":     gen,
        "form":    form,
        "status":  status,
    }


def main():
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "mutation_only"))
    os.makedirs(results_dir, exist_ok=True)

    assert NUM_RUNS <= len(SEEDS) - 1, "Not enough seeds for NUM_RUNS"

    n_combos = len(GENERATIONS_LIST) * len(POPULATION_SIZE_LIST)
    print(f"\n[{datetime.datetime.now()}] Starting Grid Search...")
    print(f"Combinations: {len(GENERATIONS_LIST)} x {len(POPULATION_SIZE_LIST)} = {n_combos}")
    print(f"Runs per combination: {NUM_RUNS}  |  Seeds: deterministic from seeds.py")
    total_procs = n_combos * NUM_RUNS * len(TEST_MATRIX) * 2
    print(f"Total subprocess launches: {total_procs}\n")

    combo_idx = 0
    for gen in GENERATIONS_LIST:
        for pop in POPULATION_SIZE_LIST:
            combo_idx += 1
            print(f"\n{'='*60}")
            print(f"Combination {combo_idx}/{n_combos}: Generations={gen}, Population={pop}")
            print(f"{'='*60}")

            stats_data = {
                tid: {
                    "std_errs": [], "std_nodes": [], "std_gens": [],
                    "eml_errs": [], "eml_nodes": [], "eml_gens": [],
                    "std_converged": 0, "eml_converged": 0,
                }
                for tid in TEST_MATRIX
            }

            for run_idx in range(1, NUM_RUNS + 1):
                seed = SEEDS[run_idx]
                results_path = os.path.join(results_dir, f"results_{gen}_{pop}_{run_idx}.csv")

                # --- Resume: load from disk if this run already completed ---
                if os.path.exists(results_path):
                    print(f"  [Gen:{gen} Pop:{pop}] Run {run_idx}/{NUM_RUNS}  SKIPPED (already on disk)")
                    with open(results_path, newline="") as f:
                        for row in csv.DictReader(f):
                            tid = row["Test ID"]
                            if tid not in stats_data:
                                continue
                            for mode, prefix in (("std", "Std"), ("eml", "EML")):
                                err_str = row[f"{prefix} Error"]
                                if err_str != "FAIL":
                                    try:
                                        err = float(err_str)
                                        nodes = int(row[f"{prefix} Nodes"] or 0)
                                        gen_val = int(row[f"{prefix} Gens"] or 0)
                                        stats_data[tid][f"{mode}_errs"].append(err)
                                        stats_data[tid][f"{mode}_nodes"].append(nodes)
                                        stats_data[tid][f"{mode}_gens"].append(gen_val)
                                    except (ValueError, KeyError):
                                        pass
                                if row.get(f"{prefix} Status") == "CONVERGED":
                                    stats_data[tid][f"{mode}_converged"] += 1
                    continue

                # --- Normal run ---
                print(f"  [Gen:{gen} Pop:{pop}] Run {run_idx}/{NUM_RUNS}  seed={seed}...  [{datetime.datetime.now().strftime('%H:%M:%S')}]")

                results_dict = {}

                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=os.cpu_count() or 8
                ) as executor:
                    futures = {}
                    for tid in sorted(TEST_MATRIX):
                        results_dict[tid] = {"id": tid, "name": TEST_MATRIX[tid]["name"]}
                        f_std = executor.submit(
                            run_single_eval, tid, TEST_MATRIX[tid]["name"], False, gen, pop, seed
                        )
                        f_eml = executor.submit(
                            run_single_eval, tid, TEST_MATRIX[tid]["name"], True,  gen, pop, seed
                        )
                        futures[f_std] = ("std", tid)
                        futures[f_eml] = ("eml", tid)

                    for future in concurrent.futures.as_completed(futures):
                        mode, tid = futures[future]
                        res = future.result()
                        if mode == "eml":
                            results_dict[tid]["eml_err"]    = res["err"]
                            results_dict[tid]["eml_nodes"]  = res["nodes"]
                            results_dict[tid]["eml_gen"]    = res["gen"]
                            results_dict[tid]["eml_form"]   = res["form"]
                            results_dict[tid]["eml_status"] = res["status"]
                            if res["err"] is not None:
                                stats_data[tid]["eml_errs"].append(res["err"])
                                stats_data[tid]["eml_nodes"].append(res["nodes"] or 0)
                                stats_data[tid]["eml_gens"].append(res["gen"])
                            if res["status"] == "CONVERGED":
                                stats_data[tid]["eml_converged"] += 1
                        else:
                            results_dict[tid]["std_err"]    = res["err"]
                            results_dict[tid]["std_nodes"]  = res["nodes"]
                            results_dict[tid]["std_gen"]    = res["gen"]
                            results_dict[tid]["std_form"]   = res["form"]
                            results_dict[tid]["std_status"] = res["status"]
                            if res["err"] is not None:
                                stats_data[tid]["std_errs"].append(res["err"])
                                stats_data[tid]["std_nodes"].append(res["nodes"] or 0)
                                stats_data[tid]["std_gens"].append(res["gen"])
                            if res["status"] == "CONVERGED":
                                stats_data[tid]["std_converged"] += 1

                results = [results_dict[tid] for tid in sorted(results_dict)]

                # Per-run summary CSV
                summary_path = os.path.join(results_dir, f"summary_{gen}_{pop}_{run_idx}.csv")
                with open(summary_path, "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow([
                        "Test ID", "Test Case",
                        "Std Error",  "EML Error",
                        "Std Nodes",  "EML Nodes",
                        "Std Gens",   "EML Gens",
                        "Std Status", "EML Status",
                    ])
                    for r in results:
                        std_e = f"{r['std_err']:.6f}" if r.get('std_err') is not None else "FAIL"
                        eml_e = f"{r['eml_err']:.6f}" if r.get('eml_err') is not None else "FAIL"
                        w.writerow([
                            r['id'], r['name'],
                            std_e, eml_e,
                            r.get('std_nodes', ''), r.get('eml_nodes', ''),
                            r.get('std_gen',   ''), r.get('eml_gen',   ''),
                            r.get('std_status',''), r.get('eml_status',''),
                        ])

                # Per-run detailed CSV — written atomically via temp file so a
                # partial write (e.g. from a crash) never leaves a valid-looking file.
                tmp_path = results_path + ".tmp"
                with open(tmp_path, "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow([
                        "Test ID", "Test Case",
                        "Std Error",   "EML Error",
                        "Std Nodes",   "EML Nodes",
                        "Std Gens",    "EML Gens",
                        "Std Status",  "EML Status",
                        "Std Formula", "EML Formula",
                    ])
                    for r in results:
                        std_e = f"{r['std_err']:.6f}" if r.get('std_err') is not None else "FAIL"
                        eml_e = f"{r['eml_err']:.6f}" if r.get('eml_err') is not None else "FAIL"
                        w.writerow([
                            r['id'], r['name'],
                            std_e, eml_e,
                            r.get('std_nodes',  ''), r.get('eml_nodes',  ''),
                            r.get('std_gen',    ''), r.get('eml_gen',    ''),
                            r.get('std_status', ''), r.get('eml_status', ''),
                            r.get('std_form',   ''), r.get('eml_form',   ''),
                        ])
                os.replace(tmp_path, results_path)

            # Per-combination statistics CSV
            print(f"  --> Statistics for Combination {combo_idx} (Gen:{gen}, Pop:{pop})...")
            stats_path = os.path.join(results_dir, f"stats_{gen}_{pop}.csv")
            with open(stats_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow([
                    "Test ID", "Test Case",
                    "Std Mean Err", "Std StdDev Err",
                    "EML Mean Err", "EML StdDev Err",
                    "Std Med Nodes", "EML Med Nodes",
                    "Std Converge Rate", "EML Converge Rate",
                ])
                for tid in sorted(TEST_MATRIX):
                    name = TEST_MATRIX[tid]["name"]
                    s    = stats_data[tid]

                    std_m  = f"{statistics.mean(s['std_errs']):.6f}"  if s['std_errs']           else "FAIL"
                    std_sd = f"{statistics.stdev(s['std_errs']):.6f}" if len(s['std_errs']) > 1  else ("0.000000" if s['std_errs'] else "FAIL")
                    std_sz = statistics.median(s['std_nodes'])         if s['std_nodes']           else "FAIL"
                    std_cr = f"{s['std_converged'] / NUM_RUNS:.3f}"

                    eml_m  = f"{statistics.mean(s['eml_errs']):.6f}"  if s['eml_errs']           else "FAIL"
                    eml_sd = f"{statistics.stdev(s['eml_errs']):.6f}" if len(s['eml_errs']) > 1  else ("0.000000" if s['eml_errs'] else "FAIL")
                    eml_sz = statistics.median(s['eml_nodes'])         if s['eml_nodes']           else "FAIL"
                    eml_cr = f"{s['eml_converged'] / NUM_RUNS:.3f}"

                    w.writerow([
                        tid, name,
                        std_m, std_sd, eml_m, eml_sd,
                        std_sz, eml_sz,
                        std_cr, eml_cr,
                    ])

    print("\n" + "="*60)
    print("Grid Search Complete!")
    print("stats_{gen}_{pop}.csv — mean/stdev error, median nodes, convergence rate")
    print("="*60)


if __name__ == "__main__":
    main()
