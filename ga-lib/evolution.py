import random
from node import Node
from generator import generate_random_tree

def get_random_node(tree):
    """Returns a random node from the tree and its parent."""
    nodes = []
    def traverse(node, parent=None, is_left=None):
        if node is not None:
            nodes.append((node, parent, is_left))
            traverse(node.left, node, True)
            traverse(node.right, node, False)
    traverse(tree)
    return random.choice(nodes) if nodes else (None, None, None)

def crossover(tree1, tree2):
    """Swaps random subtrees between two trees."""
    new_tree1 = tree1.copy()
    new_tree2 = tree2.copy()
    
    node1, parent1, is_left1 = get_random_node(new_tree1)
    node2, parent2, is_left2 = get_random_node(new_tree2)
    
    if node1 is None or node2 is None:
        return new_tree1, new_tree2
        
    if parent1 is None:
        new_tree1 = node2.copy()
    elif is_left1:
        parent1.left = node2.copy()
    else:
        parent1.right = node2.copy()
        
    if parent2 is None:
        new_tree2 = node1.copy()
    elif is_left2:
        parent2.left = node1.copy()
    else:
        parent2.right = node1.copy()
        
    return new_tree1, new_tree2

def mutate(tree, operators, terminals, variables=None, max_depth=2):
    """Replaces a random subtree with a new random tree."""
    new_tree = tree.copy()
    node, parent, is_left = get_random_node(new_tree)
    
    if node is None:
        return generate_random_tree(max_depth, operators, terminals, variables)
        
    new_subtree = generate_random_tree(max_depth, operators, terminals, variables)
    
    if parent is None:
        return new_subtree
    elif is_left:
        parent.left = new_subtree
    else:
        parent.right = new_subtree
        
    return new_tree
