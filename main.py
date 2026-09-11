"""Run both solvers over a set of sample inputs and print the comparison tables."""

from solver.NerdleCSPBenchmark import NerdleCSPBenchmark

TIMEOUT_SECONDS = 30.0

# Every input is the multiset of characters that has to be rearranged into a valid
# equation. Writing them as strings keeps them readable; the order is not part of the
# puzzle, but it does decide the order in which the solvers try the characters.
SAMPLE_INPUTS = [
    # Short equations, solved almost immediately by both solvers.
    "1+2=3",
    "2*3=6",
    "8/2=4",
    "0/1=0",

    # Two digit numbers.
    "10-5=5",
    "15+3=18",
    "12+34=46",
    "99-11=88",
    "96/8=12",

    # Longer inputs, and inputs with several operators.
    "1000-1=999",
    "7777/77=111",
    "1+2+3+4+5=15",
    "9/3+2*2-1=4",
    "3+5*2-8/4+6=7",

    # A shuffled input, so the answer is not simply the characters in the order given.
    "2722454+-=",

    # No valid equation exists for these, so the whole search space is explored.
    "2++3--4==5",
    "1+2=3=4",
    "+1*2+3=7",
]


def main():
    benchmark = NerdleCSPBenchmark()

    for sample in SAMPLE_INPUTS:
        try:
            result = benchmark.run_comparison(list(sample), TIMEOUT_SECONDS)
            benchmark.print_table_report(result)
        except Exception as error:
            print(f"Error while solving {sample}: {error}")

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
