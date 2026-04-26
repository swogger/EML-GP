import subprocess
import time
import re
import os

def run_experiment(name, command):
    print(f"Starting {name}...")
    start_time = time.time()
    
    # Run the process
    process = subprocess.Popen(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1, # line buffered
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    generations_to_perfect = None
    final_error = None
    final_size = None
    formula = None
    
    # Read output line by line in real-time
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
            
        if line:
            line = line.strip()
            if "Generation" in line and "Best Error" in line:
                match = re.search(r"Generation (\d+) - Best Error: ([0-9.]+) - Size.*?: (\d+)", line)
                if match:
                    gen = int(match.group(1))
                    error = float(match.group(2))
                    size = int(match.group(3))
                    
                    final_error = error
                    final_size = size
                    
                    if error <= 1e-6 and generations_to_perfect is None:
                        generations_to_perfect = gen
                        
                    # Print progress every 5 generations to show it's working
                    if gen % 5 == 0 or gen == 0:
                        print(f"[{name}] Generation {gen:02d} | Error: {error:.6f} | Size: {size}")
                        
            if "Best Formula:" in line or "Best EML RPN Formula:" in line:
                formula = line.split("Result = ")[-1] if "Result = " in line else line.split(": ")[-1]
                
    stderr = process.stderr.read()
    end_time = time.time()
    
    runtime = end_time - start_time
    
    return {
        "name": name,
        "runtime_sec": runtime,
        "generations_to_perfect": generations_to_perfect if generations_to_perfect is not None else ">100",
        "final_error": final_error,
        "final_size": final_size,
        "formula": formula,
        "status": "Success" if process.returncode == 0 else f"Failed (Exit Code {process.returncode})\n{stderr}"
    }

def main():
    print("Running Standard GP and EML GP in parallel. This will take a moment...\n")
    
    import concurrent.futures
    
    commands = {
        "Standard Operators (+, -, *, /)": ["python3", "deduce_formula.py"],
        "EML Operator (eml)": ["python3", "deduce_formula.py", "--use_eml"]
    }
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_name = {
            executor.submit(run_experiment, name, cmd): name 
            for name, cmd in commands.items()
        }
        
        for future in concurrent.futures.as_completed(future_to_name):
            results.append(future.result())
            
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    
    for res in results:
        print(f"\n[{res['name']}]")
        if res['status'] != "Success":
            print(f"Error: {res['status']}")
            continue
            
        print(f"  Wall-clock Time : {res['runtime_sec']:.2f} seconds")
        print(f"  Gens to Perfect : {res['generations_to_perfect']}")
        print(f"  Final Error     : {res['final_error']:.6f}")
        print(f"  Final Tree Size : {res['final_size']} nodes")
        print(f"  Deduced Formula : {res['formula']}")
        
    print("\n" + "="*60)
    print("CONCLUSION METRICS:")
    print(" - Speed (Wall-clock Time): Lower is better (computational efficiency)")
    print(" - Speed (Gens to Perfect): Lower is better (search efficiency)")
    print(" - Parsimony (Tree Size):   Lower is better (less bloat)")
    print("="*60)

if __name__ == "__main__":
    main()
