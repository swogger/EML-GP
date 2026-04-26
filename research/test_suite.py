import cmath

def safe_exp(x):
    try: return cmath.exp(x)
    except: return complex(float('inf'), float('inf'))

def safe_log(x):
    try: return cmath.log(x) if x != 0j else complex(float('-inf'), 0)
    except: return complex(float('inf'), float('inf'))

def safe_sin(x):
    try: return cmath.sin(x)
    except: return complex(float('inf'), float('inf'))

def safe_cos(x):
    try: return cmath.cos(x)
    except: return complex(float('inf'), float('inf'))
    
def safe_sinh(x):
    try: return cmath.sinh(x)
    except: return complex(float('inf'), float('inf'))
    
def safe_arctan(x):
    # cmath.atan is arctan
    try: return cmath.atan(x)
    except: return complex(float('inf'), float('inf'))

def target_1_1(x):
    return safe_exp(x)

def target_1_2(x):
    return safe_log(x)

def target_1_3(x1, x2):
    return x1 + x2
    
def target_2_1(x):
    return (x**3) - (2*(x**2)) + x

def target_2_2(x):
    return safe_sin(x) + safe_cos(x)
    
def target_3_1(x):
    return safe_sinh(x)
    
def target_3_2(x):
    return safe_arctan(x)
    
def target_3_3(x):
    try: return x**x
    except: return complex(float('inf'), float('inf'))
    
def target_3_4(x):
    # 1 / (1 + exp(-x))
    try: return 1.0 / (1.0 + safe_exp(-x))
    except: return complex(float('inf'), float('inf'))

def target_4_1(x):
    # exp(sin(x)) + log(x^2 + 1)
    return safe_exp(safe_sin(x)) + safe_log((x**2) + 1.0)

def target_4_2(x1, x2):
    # sin(x1 * exp(x2)) - cos(log(x1^2 + x2^2 + 0.1))
    return safe_sin(x1 * safe_exp(x2)) - safe_cos(safe_log((x1**2) + (x2**2) + 0.1))

TEST_MATRIX = {
    "1.1": {
        "name": "Phase 1: f(x) = exp(x)",
        "func": target_1_1,
        "vars": ["x"],
        "range": (-3.0, 3.0),
        "std_ops": ['+', '-', '*', '/', 'exp']
    },
    "1.2": {
        "name": "Phase 1: f(x) = ln(x)",
        "func": target_1_2,
        "vars": ["x"],
        "range": (0.1, 5.0),
        "std_ops": ['+', '-', '*', '/', 'log']
    },
    "1.3": {
        "name": "Phase 1: f(x1, x2) = x1 + x2",
        "func": target_1_3,
        "vars": ["x1", "x2"],
        "range": (-5.0, 5.0),
        "std_ops": ['+', '-', '*', '/']
    },
    "2.1": {
        "name": "Phase 2: f(x) = x^3 - 2x^2 + x",
        "func": target_2_1,
        "vars": ["x"],
        "range": (-5.0, 5.0),
        "std_ops": ['+', '-', '*', '/']
    },
    "2.2": {
        "name": "Phase 2: f(x) = sin(x) + cos(x)",
        "func": target_2_2,
        "vars": ["x"],
        "range": (-3.14159, 3.14159), # -pi to pi
        "std_ops": ['+', '-', '*', '/', 'sin', 'cos']
    },
    "3.1": {
        "name": "Phase 3: f(x) = sinh(x)",
        "func": target_3_1,
        "vars": ["x"],
        "range": (-3.0, 3.0),
        "std_ops": ['+', '-', '*', '/', 'exp', 'log']
    },
    "3.2": {
        "name": "Phase 3: f(x) = arctan(x)",
        "func": target_3_2,
        "vars": ["x"],
        "range": (-10.0, 10.0),
        "std_ops": ['+', '-', '*', '/', 'exp', 'log']
    },
    "3.3": {
        "name": "Phase 3: f(x) = x^x",
        "func": target_3_3,
        "vars": ["x"],
        "range": (0.1, 3.0),
        "std_ops": ['+', '-', '*', '/', 'exp', 'log']
    },
    "3.4": {
        "name": "Phase 3: f(x) = 1 / (1 + exp(-x))",
        "func": target_3_4,
        "vars": ["x"],
        "range": (-5.0, 5.0),
        "std_ops": ['+', '-', '*', '/', 'exp', 'log']
    },
    "4.1": {
        "name": "Phase 4: f(x) = exp(sin(x)) + ln(x^2 + 1)",
        "func": target_4_1,
        "vars": ["x"],
        "range": (-3.0, 3.0),
        "std_ops": ['+', '-', '*', '/', 'exp', 'log', 'sin', 'cos']
    },
    "4.2": {
        "name": "Phase 4: f(x1, x2) = sin(x1 * exp(x2)) - cos(ln(x1^2 + x2^2 + 0.1))",
        "func": target_4_2,
        "vars": ["x1", "x2"],
        "range": (-2.0, 2.0),
        "std_ops": ['+', '-', '*', '/', 'exp', 'log', 'sin', 'cos']
    }
}
