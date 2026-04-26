import random
from node import Node

def generate_random_tree(max_depth, operators, terminals, variables=None, current_depth=0):
    if variables is None:
        variables = []
        
    # If we reached max depth, must pick a terminal/variable
    if current_depth >= max_depth:
        is_var = random.choice([True, False]) if variables else False
        val = random.choice(variables) if is_var else random.choice(terminals)
        return Node(val, is_operator=False)
        
    # Otherwise, pick operator or terminal (favoring operators at shallow depths)
    # Give a small chance to stop early and pick a leaf node
    if current_depth > 0 and random.random() < 0.1:
        is_var = random.choice([True, False]) if variables else False
        val = random.choice(variables) if is_var else random.choice(terminals)
        return Node(val, is_operator=False)
        
    op = random.choice(operators)
    node = Node(op, is_operator=True)
    node.left = generate_random_tree(max_depth, operators, terminals, variables, current_depth + 1)
    if op not in ['sin', 'cos', 'exp', 'log']:
        node.right = generate_random_tree(max_depth, operators, terminals, variables, current_depth + 1)
    return node
