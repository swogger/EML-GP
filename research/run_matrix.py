import subprocess
import time
import re
import os
import csv
import datetime
from test_suite import TEST_MATRIX

MAX_GENERATIONS = 200
POPULATION_SIZE = 500

def run_test(test_id, use_eml, generations=MAX_GENERATIONS, pop_size=POPULATION_SIZE):
    cmd = ["python3", "deduce_formula.py", "--test_id", test_id, "--generations", str(generations), "--pop_size", str(pop_size)]
    if use_eml:
        cmd.append("--use_eml")
        
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    stdout, stderr = process.communicate()
    
    # Parse final results
    final_error = None
    final_size = None
    best_gen = generations
    lowest_error = float('inf')
    formula = "None"
    
    for line in stdout.split('\n'):
        if "Best Formula: Result =" in line:
            formula = line.split("Result = ")[1].strip()
            
        if "Generation" in line and "Best Error" in line:
            match = re.search(r"Generation (\d+) - Best Error: ([0-9.]+) - Size.*?: (\d+)", line)
            if match:
                gen = int(match.group(1))
                error = float(match.group(2))
                size = int(match.group(3))
                
                final_error = error
                final_size = size
                
                if error < lowest_error:
                    lowest_error = error
                    best_gen = gen
                    
    return final_error, final_size, best_gen, formula

import concurrent.futures

def run_single_eval(test_id, name, use_eml, generations, pop_size=POPULATION_SIZE):
    print(f"[{test_id}] Starting {'EML GP' if use_eml else 'Standard GP'}...")
    err, size, gen, form = run_test(test_id, use_eml, generations, pop_size)
    
    err_str = f"{err:.6f}" if err is not None else "FAIL"
    print(f"[{test_id}] Finished {'EML GP' if use_eml else 'Standard GP'} | Error: {err_str} | Size: {size}")
    return {
        "test_id": test_id,
        "use_eml": use_eml,
        "err": err,
        "size": size,
        "gen": gen,
        "form": form
    }

def main():
    while True:
        print(f"\n[{datetime.datetime.now()}] Starting new Test Matrix cycle IN PARALLEL across all CPU cores...\n")
        results_dict = {}
        
        futures = []
        # Using ThreadPoolExecutor because run_test spawns independent subprocesses
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 8) as executor:
            for test_id in sorted(TEST_MATRIX.keys()):
                test = TEST_MATRIX[test_id]
                results_dict[test_id] = {
                    "id": test_id, 
                    "name": test["name"]
                }
                
                futures.append(executor.submit(run_single_eval, test_id, test["name"], False, MAX_GENERATIONS, POPULATION_SIZE))
                futures.append(executor.submit(run_single_eval, test_id, test["name"], True, MAX_GENERATIONS, POPULATION_SIZE))
                
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                tid = res["test_id"]
                if res["use_eml"]:
                    results_dict[tid]["eml_err"] = res["err"]
                    results_dict[tid]["eml_size"] = res["size"]
                    results_dict[tid]["eml_gen"] = res["gen"]
                    results_dict[tid]["eml_form"] = res["form"]
                else:
                    results_dict[tid]["std_err"] = res["err"]
                    results_dict[tid]["std_size"] = res["size"]
                    results_dict[tid]["std_gen"] = res["gen"]
                    results_dict[tid]["std_form"] = res["form"]

        # Flatten back to list
        results = [results_dict[tid] for tid in sorted(results_dict.keys())]
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
        # Write Markdown
        md = "# EML vs Standard GP Benchmark Matrix\n\n"
        md += "| Test ID | Test Case | Std Error | EML Error | Std Size | EML Size | Std Gens | EML Gens |\n"
        md += "|---|---|---|---|---|---|---|---|\n"
        
        for r in results:
            std_e = f"{r['std_err']:.6f}" if r['std_err'] is not None else "FAIL"
            eml_e = f"{r['eml_err']:.6f}" if r['eml_err'] is not None else "FAIL"
            md += f"| {r['id']} | {r['name']} | {std_e} | {eml_e} | {r['std_size']} | {r['eml_size']} | {r['std_gen']} | {r['eml_gen']} |\n"
            
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"matrix_results_{timestamp}.md"), "w") as f:
            f.write(md)
            
        # Write summary.csv
        summary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"summary_{timestamp}.csv")
        with open(summary_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Test ID", "Test Case", "Std Error", "EML Error", "Std Size", "EML Size", "Std Gens", "EML Gens"])
            for r in results:
                std_e = f"{r['std_err']:.6f}" if r['std_err'] is not None else "FAIL"
                eml_e = f"{r['eml_err']:.6f}" if r['eml_err'] is not None else "FAIL"
                writer.writerow([r['id'], r['name'], std_e, eml_e, r['std_size'], r['eml_size'], r['std_gen'], r['eml_gen']])
                
        # Write results.csv
        results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"results_{timestamp}.csv")
        with open(results_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Test ID", "Test Case", "Std Error", "EML Error", "Std Size", "EML Size", "Std Gens", "EML Gens", "Std Formula", "EML Formula"])
            for r in results:
                std_e = f"{r['std_err']:.6f}" if r['std_err'] is not None else "FAIL"
                eml_e = f"{r['eml_err']:.6f}" if r['eml_err'] is not None else "FAIL"
                writer.writerow([r['id'], r['name'], std_e, eml_e, r['std_size'], r['eml_size'], r['std_gen'], r['eml_gen'], r['std_form'], r['eml_form']])
                
        print(f"\nDone! Results saved to summary_{timestamp}.csv and results_{timestamp}.csv")
        print("Sleeping for 5 seconds before starting next cycle...\n")
        time.sleep(5)

if __name__ == "__main__":
    main()
