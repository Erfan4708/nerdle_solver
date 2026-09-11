from typing import Dict, List

from tabulate import tabulate

from solver.BaseCSPSolver import CSPSolver
from solver.BasicBacktrackingSolver import BasicBacktrackingSolver
from solver.OptimizedCSPSolver import OptimizedCSPSolver

DEFAULT_TIMEOUT = 60.0


class NerdleCSPBenchmark:
    """Runs both solvers on the same input and reports how they compare."""

    @staticmethod
    def run_comparison(chars: List[str], timeout: float = DEFAULT_TIMEOUT) -> Dict:
        return {
            'input': chars,
            'basic': NerdleCSPBenchmark._run(BasicBacktrackingSolver(chars), timeout),
            'advanced': NerdleCSPBenchmark._run(OptimizedCSPSolver(chars), timeout),
        }

    @staticmethod
    def _run(solver: CSPSolver, timeout: float) -> Dict:
        solution = solver.solve(timeout)
        return {
            'solution': solution,
            'stats': solver.get_stats(),
            'timed_out': solver.timed_out,
        }

    @staticmethod
    def print_table_report(result: Dict):
        """Print the two solvers side by side, followed by the ratios between them."""
        basic, advanced = result['basic'], result['advanced']
        basic_stats, advanced_stats = basic['stats'], advanced['stats']

        print("Solver comparison")
        print("=" * 60)
        print(f"Input: {''.join(result['input'])}\n")

        solver_table = [
            ["Solver", "Result", "Time (s)", "Nodes", "Backtracks", "Found", "Fwd Checks",
             "AC-2 Calls", "Domain Reductions", "Timed Out"],
            ["Basic",
             basic['solution'] or "None",
             f"{basic_stats.time_taken:.4f}",
             basic_stats.nodes_expanded,
             basic_stats.backtracks,
             "Yes" if basic_stats.solution_found else "No",
             "-", "-", "-",
             "Yes" if basic['timed_out'] else "No"],
            ["Advanced",
             advanced['solution'] or "None",
             f"{advanced_stats.time_taken:.4f}",
             advanced_stats.nodes_expanded,
             advanced_stats.backtracks,
             "Yes" if advanced_stats.solution_found else "No",
             advanced_stats.forward_checks,
             advanced_stats.arc_consistency_calls,
             advanced_stats.domain_reductions,
             "Yes" if advanced['timed_out'] else "No"],
        ]
        print(tabulate(solver_table, headers="firstrow", tablefmt="grid"))

        ratio_table = [
            ["Metric", "Basic / Advanced"],
            ["Time", f"{basic_stats.time_taken / max(advanced_stats.time_taken, 1e-4):.2f}x"],
            ["Nodes", f"{basic_stats.nodes_expanded / max(advanced_stats.nodes_expanded, 1):.2f}x"],
            ["Backtracks", f"{basic_stats.backtracks / max(advanced_stats.backtracks, 1):.2f}x"],
        ]
        print("\nRatios (above 1 means the advanced solver did less work):")
        print(tabulate(ratio_table, headers="firstrow", tablefmt="github"))
