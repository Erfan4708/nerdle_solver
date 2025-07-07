import time
from typing import List, Optional, Dict, Set

from solver.BaseCSPSolver import CSPSolver


class OptimizedCSPSolver(CSPSolver):

    def __init__(self, chars: List[str]):
        super().__init__(chars)
        self.use_ac2 = True
        self.use_forward_checking = True
        self.use_mrv = True
        self.use_lcv = True

    def solve(self, timeout: float = None) -> Optional[str]:
        self.reset_state()
        self.start_time = time.time()
        self.timeout = timeout
        self.timed_out = False

        if self.use_ac2:
            if not self._initial_constraint_propagation():
                self.stats.time_taken = time.time() - self.start_time
                return None

        result = self._backtrack()

        self.stats.time_taken = time.time() - self.start_time
        self.stats.solution_found = result is not None and not self.timed_out

        return result

    def _initial_constraint_propagation(self) -> bool:
        for pos in range(self.n):
            valid_chars = set()
            for char in self.domains[pos]:
                if self._can_place_char_at_position(pos, char):
                    valid_chars.add(char)

            if not valid_chars:
                return False

            if len(valid_chars) < len(self.domains[pos]):
                self.domains[pos] = valid_chars
                self.stats.domain_reductions += 1

        return True

    def _can_place_char_at_position(self, pos: int, char: str) -> bool:
        if pos == 0 and not char.isdigit():
            return False
        if pos == self.n - 1 and not char.isdigit():
            return False

        if char == '=' and (pos == 0 or pos == self.n - 1):
            return False

        return True

    def _backtrack(self) -> Optional[str]:
        if self.timeout and (time.time() - self.start_time > self.timeout):
            self.timed_out = True
            return None

        self.stats.nodes_expanded += 1

        if all(self.assignment[i] is not None for i in range(self.n)):
            equation = ''.join([c for c in self.assignment if c is not None])
            if self.validator.is_valid_equation(equation):
                return equation
            return None

        pos = self._select_variable()
        if pos == -1:
            return None

        ordered_values = self._order_domain_values(pos)

        for char in ordered_values:
            char_idx = self._find_available_char_index(char)
            if char_idx == -1:
                continue

            if not self.validator.is_valid_partial_assignment(self.assignment, pos, char):
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
        if not self.use_mrv:
            for i in range(self.n):
                if self.assignment[i] is None:
                    return i
            return -1

        unassigned = [i for i in range(self.n) if self.assignment[i] is None]
        if not unassigned:
            return -1

        def get_real_domain_size(position):
            count = 0
            for char in self.domains[position]:
                if (self._find_available_char_index(char) != -1 and
                        self.validator.is_valid_partial_assignment(self.assignment, position, char)):
                    count += 1
            return count

        min_domain_size = float('inf')
        best_pos = -1

        for pos in unassigned:
            domain_size = get_real_domain_size(pos)
            if domain_size < min_domain_size:
                min_domain_size = domain_size
                best_pos = pos

        return best_pos

    def _order_domain_values(self, pos: int) -> List[str]:
        if not self.use_lcv:
            return [char for char in self.domains[pos]
                    if self._find_available_char_index(char) != -1]

        valid_values = []
        for char in self.domains[pos]:
            if (self._find_available_char_index(char) != -1 and
                    self.validator.is_valid_partial_assignment(self.assignment, pos, char)):
                remaining_choices = self._count_remaining_choices(pos, char)
                valid_values.append((char, remaining_choices))

        valid_values.sort(key=lambda x: x[1], reverse=True)
        return [char for char, _ in valid_values]

    def _count_remaining_choices(self, pos: int, char: str) -> int:
        char_idx = self._find_available_char_index(char)
        if char_idx == -1:
            return 0

        old_assignment = self.assignment[pos]
        old_available = self.available[char_idx]

        self.assignment[pos] = char
        self.available[char_idx] = False

        total_choices = 0
        for other_pos in range(self.n):
            if self.assignment[other_pos] is None and other_pos != pos:
                for other_char in self.domains[other_pos]:
                    if (self._find_available_char_index(other_char) != -1 and
                            self.validator.is_valid_partial_assignment(self.assignment, other_pos, other_char)):
                        total_choices += 1

        self.assignment[pos] = old_assignment
        self.available[char_idx] = old_available

        return total_choices

    def _propagate_constraints(self) -> bool:
        if self.use_forward_checking:
            if not self._forward_check():
                return False

        if self.use_ac2:
            if not self._arc_consistency_check():
                return False

        return True

    def _forward_check(self) -> bool:
        self.stats.forward_checks += 1
        for future_pos in range(self.n):
            if self.assignment[future_pos] is None:
                valid_chars = set()

                for char in self.domains[future_pos]:
                    if (self._find_available_char_index(char) != -1 and
                            self.validator.is_valid_partial_assignment(self.assignment, future_pos, char)):
                        valid_chars.add(char)

                if not valid_chars:
                    return False

                if len(valid_chars) < len(self.domains[future_pos]):
                    self.domains[future_pos] = valid_chars
                    self.stats.domain_reductions += 1

        return True

    def _arc_consistency_check(self) -> bool:
        self.stats.arc_consistency_calls += 1
        for pos in range(self.n):
            if self.assignment[pos] is None:
                valid_chars = set()

                for char in self.domains[pos]:
                    if (self._find_available_char_index(char) != -1 and
                            self.validator.is_valid_partial_assignment(self.assignment, pos, char)):
                        valid_chars.add(char)

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
        return {i: self.domains[i].copy() for i in range(self.n)}

    def _restore_domains(self, saved_domains: Dict[int, Set[str]]):
        for i, domain in saved_domains.items():
            self.domains[i] = domain.copy()
