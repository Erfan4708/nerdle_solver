from typing import List, Optional


class EquationValidator:
    @staticmethod
    def is_valid_equation(equation: str) -> bool:
        try:
            if equation.count('=') != 1:
                return False

            left, right = equation.split('=')

            if not left or not right:
                return False

            if not (left[0].isdigit() and left[-1].isdigit() and
                    right[0].isdigit() and right[-1].isdigit()):
                return False

            operators = {'+', '-', '*', '/'}
            for i in range(len(equation) - 1):
                if equation[i] in operators and equation[i + 1] in operators:
                    return False

            left_val = eval(left)
            right_val = eval(right)

            return abs(left_val - right_val) < 1e-10
        except:
            return False

    @staticmethod
    def is_valid_partial_assignment(assignment: List[Optional[str]], pos: int, char: str) -> bool:
        n = len(assignment)

        if pos == 0 and not char.isdigit():
            return False

        if pos == n - 1 and not char.isdigit():
            return False

        if pos > 0 and assignment[pos - 1] is not None:
            prev_char = assignment[pos - 1]
            if prev_char in {'+', '-', '*', '/', '='} and not char.isdigit():
                return False
            if prev_char in {'+', '-', '*', '/', '='} and char in {'+', '-', '*', '/', '='}:
                return False

        if pos < n - 1 and assignment[pos + 1] is not None:
            next_char = assignment[pos + 1]
            if next_char in {'+', '-', '*', '/', '='} and not char.isdigit():
                return False
            if char in {'+', '-', '*', '/', '='} and next_char in {'+', '-', '*', '/', '='}:
                return False

        return True
