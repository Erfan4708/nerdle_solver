from typing import List, Dict

from tabulate import tabulate

from solver.BasicBacktrackingSolver import BasicBacktrackingSolver
from solver.OptimizedCSPSolver import OptimizedCSPSolver


class NerdleCSPBenchmark:
    def __init__(self):
        self.results = []

    def run_comparison(self, chars: List[str], runs: int = 1) -> Dict:
        """Run comparison between basic and advanced solvers."""
        print(f"Comparing solvers for input: {chars}")
        print("=" * 50)

        basic_solver = BasicBacktrackingSolver(chars)
        basic_results = []

        for _ in range(runs):
            solution = basic_solver.solve(60)
            stats = basic_solver.get_stats()
            basic_results.append({
                'solution': solution,
                'stats': stats,
                'timed_out': basic_solver.timed_out,
            })

        advanced_solver = OptimizedCSPSolver(chars)
        advanced_results = []

        for _ in range(runs):
            solution = advanced_solver.solve(60)
            stats = advanced_solver.get_stats()
            advanced_results.append({
                'solution': solution,
                'stats': stats,
                'timed_out': advanced_solver.timed_out,
            })

        comparison = self._analyze_results(basic_results, advanced_results)

        return {
            'input': chars,
            'basic_results': basic_results,
            'advanced_results': advanced_results,
            'comparison': comparison
        }

    @staticmethod
    def _analyze_results(basic_results: List, advanced_results: List) -> Dict:
        """Analyze and compare results from both solvers."""
        basic_stats = basic_results[0]['stats']
        advanced_stats = advanced_results[0]['stats']

        return {
            'basic_solver': {
                'time': basic_stats.time_taken,
                'nodes_expanded': basic_stats.nodes_expanded,
                'backtracks': basic_stats.backtracks,
                'solution_found': basic_stats.solution_found
            },
            'advanced_solver': {
                'time': advanced_stats.time_taken,
                'nodes_expanded': advanced_stats.nodes_expanded,
                'backtracks': advanced_stats.backtracks,
                'forward_checks': advanced_stats.forward_checks,
                'arc_consistency_calls': advanced_stats.arc_consistency_calls,
                'domain_reductions': advanced_stats.domain_reductions,
                'solution_found': advanced_stats.solution_found
            },
            'improvements': {
                'time_ratio': basic_stats.time_taken / max(advanced_stats.time_taken, 0.0001),
                'nodes_ratio': basic_stats.nodes_expanded / max(advanced_stats.nodes_expanded, 1),
                'backtracks_ratio': basic_stats.backtracks / max(advanced_stats.backtracks, 1)
            }
        }

    @staticmethod
    def print_table_report(comparison_result: Dict):
        """Print detailed tabular report comparing both solvers."""
        print("\n Detailed Solver Comparison Report")
        print("=" * 60)

        input_chars = comparison_result['input']
        print(f"Input: {input_chars}\n")

        basic_result = comparison_result['basic_results'][0]
        advanced_result = comparison_result['advanced_results'][0]
        basic = comparison_result['comparison']['basic_solver']
        advanced = comparison_result['comparison']['advanced_solver']
        improvements = comparison_result['comparison']['improvements']

        solver_table = [
            ["Solver", "Result", "Time (s)", "Nodes", "Backtracks", "Found", "Fwd Checks", "AC-2 Calls",
             "Domain Reductions", "Timed Out"],
            ["Basic",
             basic_result['solution'] or "None",
             f"{basic['time']:.4f}",
             basic['nodes_expanded'],
             basic['backtracks'],
             "Yes" if basic['solution_found'] else "No",
             "-", "-", "-",
             "Yes" if basic_result['timed_out'] else "No"],
            ["Advanced",
             advanced_result['solution'] or "None",
             f"{advanced['time']:.4f}",
             advanced['nodes_expanded'],
             advanced['backtracks'],
             "Yes" if advanced['solution_found'] else "No",
             advanced['forward_checks'],
             advanced['arc_consistency_calls'],
             advanced['domain_reductions'],
             "Yes" if advanced_result['timed_out'] else "No"]
        ]
        print(tabulate(solver_table, headers="firstrow", tablefmt="fancy_grid"))

        # Table for improvements
        improvement_table = [
            ["Metric", "Improvement (x)"],
            ["Time", f"{improvements['time_ratio']:.2f}x"],
            ["Nodes", f"{improvements['nodes_ratio']:.2f}x"],
            ["Backtracks", f"{improvements['backtracks_ratio']:.2f}x"]
        ]
        print("\n Improvements:")
        print(tabulate(improvement_table, headers="firstrow", tablefmt="github"))

