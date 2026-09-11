import time
from typing import List, Optional, Dict, Set

from solver.BaseCSPSolver import CSPSolver


class OptimizedCSPSolver(CSPSolver):
    """Backtracking with the usual CSP improvements: MRV, LCV and constraint propagation.

    The individual techniques can be switched off to see what each one contributes.
    """

    def __init__(self, chars: List[str]):
        super().__init__(chars)
        self.use_ac2 = True
        self.use_forward_checking = True
        self.use_mrv = True
        self.use_lcv = True

    def solve(self, timeout: Optional[float] = None) -> Optional[str]:
        self._start_solve(timeout)

        if self.use_ac2 and not self._initial_constraint_propagation():
            self.stats.time_taken = time.time() - self.start_time
            return None

        result = self._backtrack()

        self.stats.time_taken = time.time() - self.start_time
        self.stats.solution_found = result is not None and not self.timed_out

        return result

    def _initial_constraint_propagation(self) -> bool:
        """Apply the position constraints once, before the search starts."""
        self.stats.arc_consistency_calls += 1

        for pos in range(self.n):
            valid_chars = {char for char in self.domains[pos]
                           if self._can_place_char_at_position(pos, char)}

            if not valid_chars:
                return False

            if len(valid_chars) < len(self.domains[pos]):
                self.domains[pos] = valid_chars
                self.stats.domain_reductions += 1

        return True

    def _can_place_char_at_position(self, pos: int, char: str) -> bool:
        """Constraint that depends on the position alone: an equation starts and ends
        with a digit."""
        if pos == 0 or pos == self.n - 1:
            return char.isdigit()
        return True

    def _backtrack(self) -> Optional[str]:
        if self._is_timed_out():
            return None

        self.stats.nodes_expanded += 1

        if None not in self.assignment:
            equation = ''.join(self.assignment)
            return equation if self.validator.is_valid_equation(equation) else None

        pos = self._select_variable()
        if pos == -1:
            return None

        for char in self._order_domain_values(pos):
            char_idx = self._find_available_char_index(char)
            if char_idx == -1:
                continue

            old_domains = self._save_domains()
            old_available = self.available.copy()

            self.assignment[pos] = char
            self.available[char_idx] = False

            if self._propagate_constraints():
                result = self._backtrack()
                if result:
                    return result

            self.stats.backtracks += 1
            self.assignment[pos] = None
            self.available = old_available
            self._restore_domains(old_domains)

        return None

    def _select_variable(self) -> int:
        """Pick the next position to fill, preferring the most constrained one (MRV)."""
        unassigned = [pos for pos in range(self.n) if self.assignment[pos] is None]
        if not unassigned:
            return -1

        if not self.use_mrv:
            return unassigned[0]

        return min(unassigned, key=lambda pos: len(self._candidates(pos)))

    def _order_domain_values(self, pos: int) -> List[str]:
        """Order the values for a position, least constraining first (LCV).

        The candidates are sorted first so that a run does not depend on the iteration
        order of the domain set, which keeps the benchmark numbers reproducible.
        """
        candidates = sorted(self._candidates(pos))

        if not self.use_lcv:
            return candidates

        return sorted(candidates, key=lambda char: self._count_remaining_choices(pos, char),
                      reverse=True)

    def _candidates(self, pos: int) -> List[str]:
        """The characters that are still free and allowed at `pos`."""
        return [char for char in self.domains[pos]
                if self._find_available_char_index(char) != -1 and
                self.validator.is_valid_partial_assignment(self.assignment, pos, char)]

    def _count_remaining_choices(self, pos: int, char: str) -> int:
        """Count the values left for the other positions if `char` were placed at `pos`."""
        char_idx = self._find_available_char_index(char)
        if char_idx == -1:
            return 0

        old_assignment = self.assignment[pos]
        old_available = self.available[char_idx]

        self.assignment[pos] = char
        self.available[char_idx] = False

        total_choices = sum(len(self._candidates(other_pos))
                            for other_pos in range(self.n)
                            if other_pos != pos and self.assignment[other_pos] is None)

        self.assignment[pos] = old_assignment
        self.available[char_idx] = old_available

        return total_choices

    def _propagate_constraints(self) -> bool:
        """Prune the domains of the unassigned positions after an assignment.

        Forward checking and arc consistency come down to the same pass in this model:
        every constraint links a position to its neighbours only, so once the values
        that no longer fit have been dropped the remaining domains are already arc
        consistent and a second pass cannot remove anything. The pass therefore runs
        once here, and arc consistency does its own useful work as preprocessing in
        _initial_constraint_propagation().
        """
        if self.use_forward_checking:
            self.stats.forward_checks += 1
            return self._prune_domains()

        if self.use_ac2:
            self.stats.arc_consistency_calls += 1
            return self._prune_domains()

        return True

    def _prune_domains(self) -> bool:
        """Narrow every unassigned domain to its remaining candidates.

        Returns False on a domain wipeout, meaning some position has no value left and
        the current partial assignment cannot be extended.
        """
        for pos in range(self.n):
            if self.assignment[pos] is not None:
                continue

            valid_chars = set(self._candidates(pos))

            if not valid_chars:
                return False

            if len(valid_chars) < len(self.domains[pos]):
                self.domains[pos] = valid_chars
                self.stats.domain_reductions += 1

        return True

    def _find_available_char_index(self, char: str) -> int:
        for i in range(self.n):
            if self.available[i] and self.chars[i] == char:
                return i
        return -1

    def _save_domains(self) -> Dict[int, Set[str]]:
        return {pos: self.domains[pos].copy() for pos in range(self.n)}

    def _restore_domains(self, saved_domains: Dict[int, Set[str]]):
        for pos, domain in saved_domains.items():
            self.domains[pos] = domain.copy()
