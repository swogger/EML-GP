import sys
import os
import argparse
import random
import cmath

# Ensure we can import the ga-lib modules from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ga-lib')))
from population import evolve
from generator import generate_random_tree
from node import Node

def count_nodes(tree):
    """Count the total number of nodes in our custom tree."""
    if not tree.is_operator:
        return 1
    left_count = count_nodes(tree.left) if tree.left else 0
    right_count = count_nodes(tree.right) if tree.right else 0
    return 1 + left_count + right_count

from test_suite import TEST_MATRIX

def main():
    parser = argparse.ArgumentParser(description="Deduce formula using standard GP")
    parser.add_argument("--pop_size", type=int, default=500, help="Population size")
    parser.add_argument("--generations", type=int, default=100, help="Number of generations")
    parser.add_argument("--max_depth", type=int, default=4, help="Maximum initial tree depth")
    parser.add_argument("--use_eml", action="store_true", help="Use the EML operator instead of standard math operators")
    parser.add_argument("--test_id", type=str, default=None, help="Test ID from the Test Matrix (e.g. '1.1')")
    
    args = parser.parse_args()
    
    # Defaults
    variables = ['x', 'y']
    data_range = (-10.0, 10.0)
    target_func = lambda x, y: (x * y) - 2.0
    std_ops = ['+', '-', '*', '/']
    
    if args.test_id and args.test_id in TEST_MATRIX:
        test = TEST_MATRIX[args.test_id]
        variables = test["vars"]
        data_range = test["range"]
        target_func = test["func"]
        std_ops = test["std_ops"]
        print(f"Loaded Test {args.test_id}: {test['name']}")
    
    terminals = [1.0]
    
    if args.use_eml:
        operators = ['eml']
        print("Initializing GP population with only EML operator...")
    else:
        operators = std_ops
        print(f"Initializing GP population with standard operators: {operators}...")
        
    population = [generate_random_tree(args.max_depth, operators, terminals, variables) for _ in range(args.pop_size)]
    
    def fitness_function(tree, batch_inputs):
        error = 0.0
        valid_evals = 0
        try:
            for inputs in batch_inputs:
                kwargs = {var: val for var, val in zip(variables, inputs)}
                pred = tree.evaluate(**kwargs)
                expected = target_func(*inputs)
                diff = abs(pred - expected)
                if cmath.isnan(diff) or cmath.isinf(diff):
                    error += 1000.0
                else:
                    error += diff ** 2
                valid_evals += 1
                
            mse = error / valid_evals if valid_evals > 0 else float('inf')
            
            # Penalize size
            if mse < 1e-5:
                return mse + (count_nodes(tree) * 0.0001)
            return mse
        except Exception:
            return float('inf')

    for gen in range(args.generations):
        # Generate new random batch
        batch_inputs = [[random.uniform(data_range[0], data_range[1]) for _ in variables] for _ in range(20)]
        
        fitness_scores = [(ind, fitness_function(ind, batch_inputs)) for ind in population]
        fitness_scores.sort(key=lambda item: item[1])
        
        best_tree, best_fitness = fitness_scores[0]
        actual_error = fitness_function(best_tree, batch_inputs)
        display_error = actual_error if actual_error >= 1e-5 else actual_error - (count_nodes(best_tree) * 0.0001)
        
        # Only print occasionally to reduce log spam if running automatically
        if gen % 10 == 0 or gen == args.generations - 1:
            print(f"Generation {gen:03d} - Best Error: {display_error:.6f} - Size: {count_nodes(best_tree)} - Formula: {best_tree.to_formula()}")
        
        if display_error <= 1e-6 and gen % 10 != 0: # Print if perfect
            # Only print once to avoid spam
            pass
            
        from evolution import crossover, mutate
        new_pop = [best_tree.copy()]
        while len(new_pop) < args.pop_size:
            tournament = random.sample(fitness_scores, k=3)
            tournament.sort(key=lambda x: x[1])
            parent1 = tournament[0][0]
            
            if random.random() < 0.7 and len(new_pop) < args.pop_size - 1:
                tournament2 = random.sample(fitness_scores, k=3)
                tournament2.sort(key=lambda x: x[1])
                parent2 = tournament2[0][0]
                child1, child2 = crossover(parent1, parent2)
                new_pop.extend([child1, child2])
            else:
                new_pop.append(parent1.copy())
                
        for i in range(1, len(new_pop)):
            if random.random() < 0.2:
                new_pop[i] = mutate(new_pop[i], operators, terminals, variables, args.max_depth)
                
        population = new_pop[:args.pop_size]
        
    print("\n===============================")
    print("Standard GP Evolution complete.")
    print(f"Best Formula: Result = {best_tree.to_formula()}")
    print(f"Node count (operators & leaves): {count_nodes(best_tree)}")

if __name__ == "__main__":
    main()
