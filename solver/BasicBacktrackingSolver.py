import time
from typing import Optional

from solver.BaseCSPSolver import CSPSolver


class BasicBacktrackingSolver(CSPSolver):
    """Plain backtracking: fill the positions left to right, in input character order.

    It is the baseline the optimized solver is measured against, so it deliberately
    uses no heuristics and no constraint propagation.
    """

    def solve(self, timeout: Optional[float] = None) -> Optional[str]:
        self._start_solve(timeout)

        result = self._backtrack(0)

        self.stats.time_taken = time.time() - self.start_time
        self.stats.solution_found = result is not None and not self.timed_out

        return result

    def _backtrack(self, pos: int) -> Optional[str]:
        if self._is_timed_out():
            return None

        self.stats.nodes_expanded += 1

        if pos == self.n:
            equation = ''.join(self.assignment)
            return equation if self.validator.is_valid_equation(equation) else None

        for i in range(self.n):
            if not self.available[i]:
                continue

            char = self.chars[i]
            if not self.validator.is_valid_partial_assignment(self.assignment, pos, char):
                continue

            self.assignment[pos] = char
            self.available[i] = False

            result = self._backtrack(pos + 1)
            if result:
                return result

            self.stats.backtracks += 1
            self.assignment[pos] = None
            self.available[i] = True

        return None
