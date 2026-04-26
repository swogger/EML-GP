class Node:
    def __init__(self, value, left=None, right=None, is_operator=False):
        self.value = value
        self.left = left
        self.right = right
        self.is_operator = is_operator

    def to_formula(self):
        if self.is_operator:
            if self.value in ['sin', 'cos', 'exp', 'log']:
                left_str = self.left.to_formula() if self.left else ""
                return f"{self.value}({left_str})"
            # assuming binary operators
            left_str = self.left.to_formula() if self.left else ""
            right_str = self.right.to_formula() if self.right else ""
            return f"({left_str} {self.value} {right_str})"
        else:
            return str(self.value)

    def evaluate(self, **kwargs):
        import cmath
        if not self.is_operator:
            if isinstance(self.value, str):
                return complex(kwargs.get(self.value, 0.0)) # variable
            return complex(self.value) # number
        
        left_val = self.left.evaluate(**kwargs) if self.left else 0j
        right_val = self.right.evaluate(**kwargs) if self.right else 0j
        
        if self.value == '+': return left_val + right_val
        if self.value == '-': return left_val - right_val
        if self.value == '*': return left_val * right_val
        if self.value == '/': 
            return left_val / right_val if right_val != 0j else 1.0 + 0j
        if self.value == 'sin':
            try: return cmath.sin(left_val)
            except: return complex(float('inf'), float('inf'))
        if self.value == 'cos':
            try: return cmath.cos(left_val)
            except: return complex(float('inf'), float('inf'))
        if self.value == 'exp':
            try: return cmath.exp(left_val)
            except: return complex(float('inf'), float('inf'))
        if self.value == 'log':
            try: return cmath.log(left_val) if left_val != 0j else complex(float('-inf'), 0)
            except: return complex(float('inf'), float('inf'))
        if self.value == 'eml':
            try:
                return cmath.exp(left_val) - cmath.log(right_val)
            except Exception:
                return complex(float('inf'), float('inf'))
            
        raise ValueError(f"Unknown operator: {self.value}")
        
    def copy(self):
        return Node(
            value=self.value,
            left=self.left.copy() if self.left else None,
            right=self.right.copy() if self.right else None,
            is_operator=self.is_operator
        )
