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

    @abstractmethod
    def solve(self) -> Optional[str]:
        pass

    def get_stats(self) -> CSPStats:
        return self.stats
