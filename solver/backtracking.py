from typing import List, Optional
from utils.validator import is_valid_equation

def solve_with_backtracking(chars: List[str]) -> Optional[str]:
    n = len(chars)
    assignment: List[Optional[str]] = [None] * n
    available: List[bool] = [True] * n

    def backtrack(next_pos: int) -> Optional[str]:
        if next_pos == n:
            last_char = assignment[-1]
            if last_char is None or not last_char.isdigit():
                return None
            equation = ''.join([c for c in assignment if c is not None])
            if is_valid_equation(equation):
                return equation
            return None

        for i in range(n):
            if available[i]:
                c = chars[i]
                if next_pos == 0:
                    if not c.isdigit():
                        continue
                else:
                    prev_c = assignment[next_pos - 1]
                    if prev_c is None or not prev_c.isdigit():
                        if c in {'+', '-', '*', '/', '='}:
                            continue
                assignment[next_pos] = c
                available[i] = False
                result = backtrack(next_pos + 1)
                if result:
                    return result
                available[i] = True
                assignment[next_pos] = None

        return None

    return backtrack(0)
