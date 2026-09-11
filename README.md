# Nerdle Solver

A constraint satisfaction solver for the equation puzzle [Nerdle](https://nerdlegame.com/).
Given a bag of characters, it rearranges them into a valid mathematical equation, and
compares a plain backtracking search against one that uses the standard CSP heuristics.

The project was written to explore how much difference variable ordering, value ordering
and constraint propagation actually make on a concrete problem, so both solvers are kept
side by side and every run reports how much work each of them did.

## Problem

The input is a multiset of characters: digits `0`-`9`, the operators `+`, `-`, `*`, `/`,
and one `=`. The task is to arrange **all** of them into an equation that is:

1. syntactically correct - it starts and ends with a digit, operators are surrounded by
   digits, and there is exactly one `=`
2. mathematically correct - both sides evaluate to the same value, respecting operator
   precedence
3. built from every input character exactly once

Multi-digit numbers are allowed; numbers may not have a leading zero.

**Example**

```
Input:  ['2', '7', '2', '2', '4', '5', '4', '+', '-', '=']
Output: 27+22-45=4
```

## Features

- Two interchangeable solvers behind a shared base class
  - `BasicBacktrackingSolver` - left-to-right backtracking with no heuristics, used as
    the baseline
  - `OptimizedCSPSolver` - adds MRV, LCV, constraint propagation and a preprocessing pass
- Per-solver statistics: nodes expanded, backtracks, propagation passes, domain
  reductions, time taken
- Each optimization can be switched off individually (`use_mrv`, `use_lcv`,
  `use_forward_checking`, `use_ac2`) to see what it contributes
- A timeout, so a hard instance ends in a reported timeout instead of hanging
- A benchmark runner that prints both solvers side by side as a table

## Tech Stack

- Python 3.7+ (standard library: `abc`, `dataclasses`, `typing`, `time`)
- [tabulate](https://pypi.org/project/tabulate/) for the comparison tables

No other dependencies, no configuration files and no external services.

## Project Structure

```
main.py                        Entry point: runs the sample inputs through the benchmark
requirements.txt               The single dependency
solver/
  BaseCSPSolver.py             CSPSolver base class and the CSPStats dataclass
  EquationValidator.py         Syntax checks and the arithmetic evaluator
  BasicBacktrackingSolver.py   Baseline search
  OptimizedCSPSolver.py        Search with MRV, LCV and constraint propagation
  NerdleCSPBenchmark.py        Runs both solvers and prints the comparison
```

## Getting Started

**Prerequisites:** Python 3.7 or newer.

```bash
git clone https://github.com/Erfan4708/nerdle_solver.git
cd nerdle_solver

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Run the demo:

```bash
python main.py
```

It solves the sample inputs listed in `main.py` and prints a table per input. The whole
run takes a couple of seconds.

## Usage

To solve a single input directly:

```python
from solver.OptimizedCSPSolver import OptimizedCSPSolver

solver = OptimizedCSPSolver(list("2722454+-="))
solution = solver.solve(timeout=30)     # '24+25-47=2', or None

stats = solver.get_stats()
print(solution, stats.nodes_expanded, stats.time_taken)
```

`solve()` returns the first equation it finds, or `None` if the input has no solution or
the timeout ran out (`solver.timed_out` tells the two apart). A solver instance can be
reused; `solve()` resets its state each time.

To compare both solvers on one input:

```python
from solver.NerdleCSPBenchmark import NerdleCSPBenchmark

benchmark = NerdleCSPBenchmark()
benchmark.print_table_report(benchmark.run_comparison(list("2722454+-=")))
```

## Configuration

There are no environment variables or secrets. The things worth changing live in the code:

- `TIMEOUT_SECONDS` and `SAMPLE_INPUTS` in `main.py`
- `DEFAULT_TIMEOUT` in `solver/NerdleCSPBenchmark.py`
- the `use_mrv` / `use_lcv` / `use_forward_checking` / `use_ac2` flags on
  `OptimizedCSPSolver`

## How It Works

### CSP formulation

- **Variables** - one per position in the equation, `0` to `n-1`
- **Domains** - the set of input characters, narrowed as the search proceeds
- **Constraints**
  - each input character is used exactly once, tracked by the `available` list, so
    duplicates in the input stay usable the right number of times
  - the first and last positions are digits, and no two operators are adjacent
  - the finished string must evaluate to a true equation

The syntax constraints are local, involving only a position and its neighbours, so they
can be checked cheaply on every candidate value. The arithmetic constraint involves every
variable at once, so it is only checked on a complete assignment.

### Optimizations

- **MRV (minimum remaining values)** - fill the position with the fewest candidates first,
  so dead ends surface early.
- **LCV (least constraining value)** - try the character that leaves the most options open
  for the remaining positions first.
- **Constraint propagation** - after each assignment, drop the values that no longer fit
  from the unassigned domains; if a domain empties, backtrack immediately.
- **Preprocessing** - before the search starts, remove non-digits from the first and last
  position.

Forward checking and arc consistency were originally written as two separate passes, but
in this model they do the same thing: every constraint links a position to its neighbours
only, so once the values that no longer fit have been removed the remaining domains are
already arc consistent, and a second pass can never remove anything. They now share one
implementation (`_prune_domains`) that runs once per assignment, and arc consistency does
its distinct work in the preprocessing pass. The `use_forward_checking` and `use_ac2`
flags still select between them.

### What the comparison shows

On the sample inputs the optimized solver explores far fewer nodes - roughly 10x fewer on
the shuffled 10-character input, and about 38x fewer when proving that an input has no
solution at all - but it is often **slower in wall-clock time**, because MRV and LCV
recompute the candidate sets for every unassigned position at every node. The pruning is
real; the per-node bookkeeping is what eats the gain. On larger inputs that cost grows
faster than the saving, and the optimized solver can time out where the baseline does not.

Two caveats worth knowing when reading the numbers:

- Most sample inputs are written as an already valid equation with its characters in
  order. The baseline fills positions left to right in input order, so it stumbles onto
  the answer almost immediately on those. The shuffled input and the unsolvable ones are
  the more honest comparisons.
- Node counts used to vary between runs, because iteration order over a set of strings
  differs per process. Candidate values are sorted before ordering now, so runs are
  reproducible.

## Testing

There is no automated test suite. The solvers are exercised through `python main.py`,
which includes solvable inputs of several sizes and three inputs with no valid equation,
so the search has to fail exhaustively.

## Limitations and Possible Improvements

- Division is floating point, and the two sides are compared with a `1e-10` tolerance.
  Real Nerdle requires every intermediate result to be a whole number; this solver does
  not enforce that.
- Only the first solution is returned. There is no way to enumerate all of them.
- The `=` is treated as just another symbol during the search. Restricting how many `=`
  signs may be placed while assigning, rather than only checking it at the end, would
  prune a lot.
- The arithmetic constraint is only checked on a complete assignment. Reasoning about a
  partial equation, for example bounding what the remaining characters could still
  produce, would cut the search far more than the syntax rules do.
- MRV and LCV recompute candidate sets from scratch at every node. Maintaining them
  incrementally is the obvious fix for the wall-clock gap described above.
- A real test suite, starting with the equation validator, would be the first thing to add.
