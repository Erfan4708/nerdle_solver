from solver.backtracking import solve_with_backtracking


def main():
    chars = ['2', '7', '2', '2', '4', '5', '4', '+', '-', '=']
    result = solve_with_backtracking(chars)
    if result:
        print(result)
    else:
        print("Not found!")


if __name__ == "__main__":
    main()
