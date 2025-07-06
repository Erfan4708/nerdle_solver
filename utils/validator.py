import re

def is_valid_equation(equation: str) -> bool:
    if equation.count('=') != 1:
        return False

    lhs, rhs = equation.split('=')

    if not lhs or not rhs:
        return False

    if not is_syntactically_valid(lhs) or not is_syntactically_valid(rhs):
        return False

    try:
        lhs_val = eval_expr(lhs)
        rhs_val = eval_expr(rhs)
        return abs(lhs_val - rhs_val) < 1e-6
    except Exception:
        return False

def is_syntactically_valid(expr: str) -> bool:
    if expr[0] in '+-*/' or expr[-1] in '+-*/':
        return False

    if re.search(r'[\+\-\*/]{2,}', expr):
        return False

    if re.search(r'/0(?!\d)', expr):
        return False

    return True

def eval_expr(expr: str) -> float:
    allowed_chars = set("0123456789+-*/.")
    if not set(expr).issubset(allowed_chars):
        raise ValueError("Invalid characters in expression.")
    return eval(expr)
