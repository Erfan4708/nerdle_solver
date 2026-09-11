import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Set

from solver.EquationValidator import EquationValidator


@dataclass
class CSPStats:
    nodes_expanded: int = 0
    backtracks: int = 0
    forward_checks: int = 0
    arc_consistency_calls: int = 0
    domain_reductions: int = 0
    time_taken: float = 0.0
    solution_found: bool = False

    def reset(self):
        self.nodes_expanded = 0
        self.backtracks = 0
        self.forward_checks = 0
        self.arc_consistency_calls = 0
        self.domain_reductions = 0
        self.time_taken = 0.0
        self.solution_found = False


class CSPSolver(ABC):
    """Shared state for the solvers.

    The CSP has one variable per position in the equation, the domain of every
    variable is the set of input characters, and each character may be used only as
    often as it appears in the input. `available` tracks which of the input characters
    have not been placed yet.
    """

    def __init__(self, chars: List[str]):
        self.chars = chars
        self.n = len(chars)
        self.stats = CSPStats()
        self.validator = EquationValidator()

        self.assignment: List[Optional[str]] = [None] * self.n
        self.available: List[bool] = [True] * self.n
        self.domains: Dict[int, Set[str]] = {}

        self.start_time = None
        self.timeout = None
        self.timed_out = False

        self._initialize_domains()

    def _initialize_domains(self):
        for pos in range(self.n):
            self.domains[pos] = set(self.chars)

    def reset_state(self):
        self.assignment = [None] * self.n
        self.available = [True] * self.n
        self.domains = {}
        self._initialize_domains()
        self.stats.reset()

    def _start_solve(self, timeout: Optional[float]):
        self.reset_state()
        self.start_time = time.time()
        self.timeout = timeout
        self.timed_out = False

    def _is_timed_out(self) -> bool:
        """Report whether the time budget is used up, remembering it once it is."""
        if self.timeout is not None and time.time() - self.start_time > self.timeout:
            self.timed_out = True
            return True
        return False

    @abstractmethod
    def solve(self, timeout: Optional[float] = None) -> Optional[str]:
        """Return an equation using every input character once, or None if there is none."""

    def get_stats(self) -> CSPStats:
        return self.stats
