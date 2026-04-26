import sys
import os
import random
import cmath
import argparse

# Add eml-skill to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../eml-skill/eml-skill/skills/_shared')))
from eml_core.eml import EmlNode, Leaf, evaluate, to_rpn, k_tokens

def generate_random_tree(max_depth, current_depth=0):
    """Generates a random EML tree."""
    if current_depth >= max_depth:
        return Leaf(random.choice(["1", "x", "y"]))
        
    if current_depth > 0 and random.random() < 0.1:
        return Leaf(random.choice(["1", "x", "y"]))
        
    a = generate_random_tree(max_depth, current_depth + 1)
    b = generate_random_tree(max_depth, current_depth + 1)
    return EmlNode(a, b)

def get_all_nodes(tree):
    """Returns a list of all nodes in the tree for random selection."""
    nodes = []
    def traverse(n):
        nodes.append(n)
        if isinstance(n, EmlNode):
            traverse(n.a)
            traverse(n.b)
    traverse(tree)
    return nodes

def replace_node(tree, target_node, new_node):
    """Returns a new tree with target_node replaced by new_node (handles immutability)."""
    if tree is target_node:
        return new_node
    if isinstance(tree, Leaf):
        return tree
    
    new_a = replace_node(tree.a, target_node, new_node)
    new_b = replace_node(tree.b, target_node, new_node)
    
    if new_a is tree.a and new_b is tree.b:
        return tree
    return EmlNode(new_a, new_b)

def crossover(tree1, tree2):
    """Swaps random subtrees to create two new trees."""
    node1 = random.choice(get_all_nodes(tree1))
    node2 = random.choice(get_all_nodes(tree2))
    
    new_tree1 = replace_node(tree1, node1, node2)
    new_tree2 = replace_node(tree2, node2, node1)
    return new_tree1, new_tree2

def mutate(tree, max_depth=3):
    """Replaces a random subtree with a new random one."""
    target_node = random.choice(get_all_nodes(tree))
    new_subtree = generate_random_tree(max_depth)
    return replace_node(tree, target_node, new_subtree)

def target_function(x, y):
    """The function we want to deduce: (A * B) - 2.0 (mapped to x, y)"""
    return (x * y) - 2.0

def main():
    parser = argparse.ArgumentParser(description="Deduce formula using EML operator")
    parser.add_argument("--pop_size", type=int, default=500, help="Population size")
    parser.add_argument("--generations", type=int, default=100, help="Number of generations")
    parser.add_argument("--max_depth", type=int, default=4, help="Maximum initial tree depth")
    
    args = parser.parse_args()
    
    print("Initializing EML population...")
    population = [generate_random_tree(args.max_depth) for _ in range(args.pop_size)]
    
    for gen in range(args.generations):
        batch_inputs = [(random.uniform(-10, 10)+0j, random.uniform(-10, 10)+0j) for _ in range(20)]
        
        fitness_scores = []
        for tree in population:
            error = 0.0
            valid_evals = 0
            for x, y in batch_inputs:
                expected = target_function(x, y)
                try:
                    pred = evaluate(tree, x, y)
                    diff = abs(pred - expected)
                    if cmath.isnan(diff) or cmath.isinf(diff):
                        error += 1000.0
                    else:
                        error += diff ** 2
                    valid_evals += 1
                except Exception:
                    error += 1000.0
            
            mse = error / len(batch_inputs) if valid_evals > 0 else float('inf')
            
            # Penalize by tree size if we are close to perfect so we find the minimal tree
            if mse < 1e-5:
                mse += k_tokens(tree) * 0.0001
                
            fitness_scores.append((tree, mse))
            
        fitness_scores.sort(key=lambda item: item[1])
        best_tree, best_fitness = fitness_scores[0]
        
        # Recover display error
        display_error = best_fitness if best_fitness >= 1e-5 else best_fitness - (k_tokens(best_tree) * 0.0001)
        
        print(f"Generation {gen} - Best Error: {display_error:.6f} - Size (K): {k_tokens(best_tree)} - RPN: {to_rpn(best_tree)}")
        
        if display_error <= 1e-6:
            print("Perfect solution found! Evolving to minimize size...")
            
        new_pop = [best_tree] # Elitism
        
        while len(new_pop) < args.pop_size:
            tournament = random.sample(fitness_scores, k=3)
            tournament.sort(key=lambda item: item[1])
            parent1 = tournament[0][0]
            
            if random.random() < 0.7 and len(new_pop) < args.pop_size - 1:
                tournament2 = random.sample(fitness_scores, k=3)
                tournament2.sort(key=lambda item: item[1])
                parent2 = tournament2[0][0]
                
                child1, child2 = crossover(parent1, parent2)
                new_pop.extend([child1, child2])
            else:
                new_pop.append(parent1)
                
        for i in range(1, len(new_pop)):
            if random.random() < 0.2:
                new_pop[i] = mutate(new_pop[i], args.max_depth)
                
        population = new_pop[:args.pop_size]
        
    print("\n===============================")
    print("EML Evolution complete.")
    print(f"Best EML RPN Formula: {to_rpn(best_tree)}")
    print(f"Node count (K tokens): {k_tokens(best_tree)}")

if __name__ == "__main__":
    main()
