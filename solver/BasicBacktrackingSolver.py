import time
from typing import Optional

from solver.BaseCSPSolver import CSPSolver


class BasicBacktrackingSolver(CSPSolver):

    def solve(self, timeout: float = None) -> Optional[str]:
        self.reset_state()
        self.start_time = time.time()
        self.timeout = timeout
        self.timed_out = False

        result = self._backtrack(0)

        self.stats.time_taken = time.time() - self.start_time
        self.stats.solution_found = result is not None and not self.timed_out

        return result

    def _backtrack(self, pos: int) -> Optional[str]:
        if self.timeout and (time.time() - self.start_time > self.timeout):
            self.timed_out = True
            return None

        self.stats.nodes_expanded += 1

        if pos == self.n:
            equation = ''.join([c for c in self.assignment if c is not None])
            if self.validator.is_valid_equation(equation):
                return equation
            return None

        for i in range(self.n):
            if self.available[i]:
                char = self.chars[i]

                if self.validator.is_valid_partial_assignment(self.assignment, pos, char):
                    self.assignment[pos] = char
                    self.available[i] = False

                    result = self._backtrack(pos + 1)
                    if result:
                        return result

                    self.stats.backtracks += 1
                    self.assignment[pos] = None
                    self.available[i] = True

        return None

