from typing import List, Optional

DIGITS = frozenset('0123456789')
OPERATORS = frozenset('+-*/')
SYMBOLS = OPERATORS | {'='}

# Equations are compared as floating point numbers because '/' is a true division.
TOLERANCE = 1e-10


class EquationValidator:
    @staticmethod
    def is_valid_equation(equation: str) -> bool:
        """Check that a complete equation is both syntactically and mathematically correct."""
        if equation.count('=') != 1:
            return False

        left, right = equation.split('=')

        if not left or not right:
            return False

        if not (left[0].isdigit() and left[-1].isdigit() and
                right[0].isdigit() and right[-1].isdigit()):
            return False

        for char, next_char in zip(equation, equation[1:]):
            if char in OPERATORS and next_char in OPERATORS:
                return False

        left_value = evaluate(left)
        right_value = evaluate(right)

        if left_value is None or right_value is None:
            return False

        return abs(left_value - right_value) < TOLERANCE

    @staticmethod
    def is_valid_partial_assignment(assignment: List[Optional[str]], pos: int, char: str) -> bool:
        """Check that placing `char` at `pos` does not already break the syntax rules.

        Only the neighbours of `pos` are looked at, so this stays cheap enough to call
        on every candidate value during the search.
        """
        n = len(assignment)

        # An equation always starts and ends with a digit.
        if (pos == 0 or pos == n - 1) and not char.isdigit():
            return False

        # Operators and '=' must be surrounded by digits, so two of them cannot be adjacent.
        if pos > 0 and assignment[pos - 1] in SYMBOLS and not char.isdigit():
            return False

        if pos < n - 1 and assignment[pos + 1] in SYMBOLS and not char.isdigit():
            return False

        return True


def evaluate(expression: str) -> Optional[float]:
    """Evaluate an expression of non-negative integers joined by + - * /.

    Returns None when the expression is malformed, has a number with a leading zero,
    or divides by zero. This is a hand written evaluator rather than a call to eval()
    so that a string built from the puzzle input can never be executed as code.
    """
    tokens = tokenize(expression)
    if tokens is None:
        return None

    # Apply * and / first, then add up the terms that are left.
    terms = [tokens[0]]
    operators = []

    for i in range(1, len(tokens), 2):
        operator, value = tokens[i], tokens[i + 1]

        if operator == '*':
            terms[-1] *= value
        elif operator == '/':
            if value == 0:
                return None
            terms[-1] /= value
        else:
            operators.append(operator)
            terms.append(value)

    result = terms[0]
    for operator, term in zip(operators, terms[1:]):
        result = result + term if operator == '+' else result - term

    return result


def tokenize(expression: str) -> Optional[List]:
    """Split an expression into alternating numbers and operators, or None if malformed."""
    tokens = []
    number = ''

    for char in expression:
        if char in DIGITS:
            number += char
        elif char in OPERATORS and number:
            tokens.append(number)
            tokens.append(char)
            number = ''
        else:
            return None

    if not number:
        return None

    tokens.append(number)

    # Numbers may not have a leading zero, which is also how Nerdle reads them.
    for i in range(0, len(tokens), 2):
        if len(tokens[i]) > 1 and tokens[i][0] == '0':
            return None
        tokens[i] = int(tokens[i])

    return tokens
