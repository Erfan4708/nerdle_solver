
## 1. Introduction

This project implements a solution to the mathematical equation puzzle "Nerdle" using **Constraint Satisfaction Problem (CSP)** techniques. The goal is to construct a valid mathematical equation using all given characters exactly once.

### Problem Description

Given a set of characters including:
- Digits (0-9)
- Mathematical operators: `+`, `-`, `*`, `/`, `=`
- Possibly duplicate characters

The task is to arrange these characters to form a valid mathematical equation where:
1. Each character is used exactly once
2. The equation is syntactically correct
3. The equation is mathematically correct (both sides of `=` evaluate to the same value)
4. Standard mathematical operator precedence is respected
5. Multi-digit numbers are allowed
6. There is exactly one `=` symbol

### Example

**Input:** `['2', '7', '2', '2', '4', '5', '4', '+', '-', '=']`

**Valid Solution:** `"22+54-4=72"`

## 2. CSP Formulation

### 2.1 Variables
- Each position in the equation string is a variable
- Variables are indexed from 0 to n-1 (where n is the number of characters)

### 2.2 Domain
- Each variable can take any value from the given character set
- Domain reduces as characters are assigned (each character used exactly once)

### 2.3 Constraints
1. **Uniqueness Constraint**: Each character must be used exactly once
2. **Syntax Constraints**: 
   - First and last positions must be digits
   - No consecutive operators
   - Operators must be surrounded by digits
3. **Mathematical Constraint**: The equation must evaluate correctly

## 3. Implementation Architecture

### 3.1 Core Classes

#### `CSPStats`
Tracks performance metrics:
- `nodes_expanded`: Number of search nodes explored
- `backtracks`: Number of backtracking operations
- `forward_checks`: Number of forward checking operations
- `arc_consistency_calls`: Number of arc consistency applications
- `domain_reductions`: Number of domain pruning operations
- `time_taken`: Total solving time
- `solution_found`: Whether a solution was found

#### `EquationValidator`
Validates equations and partial assignments:
- `is_valid_equation(equation)`: Checks if complete equation is valid
- `is_valid_partial_assignment(assignment, pos, char)`: Validates partial assignment

#### `CSPSolver` (Abstract Base Class)
Base class for all solvers with common functionality:
- State management
- Domain initialization
- Abstract solve method

### 3.2 Solver Implementations

#### `BasicBacktrackingSolver`
Simple backtracking implementation:
- Sequential variable ordering
- No heuristics or constraint propagation
- Baseline for comparison

#### `OptimizedCSPSolver`
Advanced solver with CSP optimization techniques:
- MRV (Minimum Remaining Values) heuristic
- LCV (Least Constraining Value) heuristic
- Forward Checking
- Arc Consistency (AC-2)
- Constraint propagation

## 4. Optimization Techniques

### 4.1 Variable Ordering: MRV (Minimum Remaining Values)

**Purpose:** Select the variable with the smallest domain size first.

**Rationale:** Variables with fewer options are more likely to fail fast, reducing search space.

**Implementation:**
```python
def _select_variable(self) -> int:
    unassigned = [i for i in range(self.n) if self.assignment[i] is None]
    if not unassigned:
        return -1
    
    # Select variable with minimum valid domain size
    min_domain_size = float('inf')
    best_pos = -1
    
    for pos in unassigned:
        domain_size = get_real_domain_size(pos)
        if domain_size < min_domain_size:
            min_domain_size = domain_size
            best_pos = pos
    
    return best_pos
```

### 4.2 Value Ordering: LCV (Least Constraining Value)

**Purpose:** Choose values that leave the most options for other variables.

**Rationale:** Preserve flexibility for future assignments by selecting less constraining values first.

**Implementation:**
```python
def _order_domain_values(self, pos: int) -> List[str]:
    valid_values = []
    for char in self.domains[pos]:
        if is_valid_assignment(pos, char):
            remaining_choices = self._count_remaining_choices(pos, char)
            valid_values.append((char, remaining_choices))
    
    # Sort by most remaining choices first
    valid_values.sort(key=lambda x: x[1], reverse=True)
    return [char for char, _ in valid_values]
```

### 4.3 Forward Checking

**Purpose:** After assigning a value, check if it makes future assignments impossible.

**Process:**
1. Assign value to variable
2. Update domains of unassigned variables
3. Remove values that would create conflicts
4. If any domain becomes empty, backtrack immediately

**Implementation:**
```python
def _forward_check(self, pos: int) -> bool:
    for future_pos in range(self.n):
        if self.assignment[future_pos] is None:
            valid_chars = set()
            
            for char in self.domains[future_pos]:
                if is_valid_for_position(future_pos, char):
                    valid_chars.add(char)
            
            if not valid_chars:
                return False  # Domain wipeout
            
            self.domains[future_pos] = valid_chars
    
    return True
```

### 4.4 Arc Consistency (AC-2)

**Purpose:** Ensure that for every value in a variable's domain, there exists a compatible value in related variables' domains.

**When Applied:**
1. As preprocessing before search
2. After each assignment during search

**Implementation:**
```python
def _arc_consistency_check(self) -> bool:
    for pos in range(self.n):
        if self.assignment[pos] is None:
            valid_chars = set()
            
            for char in self.domains[pos]:
                if is_valid_and_supported(pos, char):
                    valid_chars.add(char)
            
            if not valid_chars:
                return False
            
            self.domains[pos] = valid_chars
    
    return True
```

## 5. Algorithm Flow

### 5.1 Basic Backtracking Algorithm

```
1. If all variables assigned:
   - Check if equation is valid
   - Return solution if valid
2. Select next variable (position)
3. For each character in domain:
   - If assignment is valid:
     - Assign character
     - Recursively solve
     - If solution found, return it
     - Otherwise, backtrack
4. Return failure
```

### 5.2 Optimized Algorithm

```
1. Preprocessing:
   - Apply initial constraint propagation
   - Reduce domains based on position constraints
2. Search:
   - If all variables assigned, validate equation
   - Select variable using MRV heuristic
   - Order values using LCV heuristic
   - For each value:
     - If assignment is valid:
       - Assign value
       - Apply forward checking
       - Apply arc consistency
       - If domains remain consistent:
         - Recursively solve
       - Backtrack if needed
3. Return solution or failure
```

## 6. Performance Analysis

### 6.1 Key Metrics

1. **Time Complexity:** 
   - Basic: O(n! × validation_cost)
   - Optimized: Significantly reduced through pruning

2. **Space Complexity:** O(n × domain_size)

3. **Practical Performance:**
   - Measured by nodes expanded
   - Backtracking operations
   - Domain reduction effectiveness

### 6.2 Expected Improvements

The optimized solver should show:
- Fewer nodes expanded (due to better variable/value ordering)
- More efficient pruning (forward checking + arc consistency)
- Faster time to solution or failure detection
- Better scaling with problem size

## 7. Usage Example

```python
# Initialize solvers
basic_solver = BasicBacktrackingSolver(chars)
optimized_solver = OptimizedCSPSolver(chars)

# Solve with timeout
solution1 = basic_solver.solve(timeout=30)
solution2 = optimized_solver.solve(timeout=30)

# Compare performance
basic_stats = basic_solver.get_stats()
optimized_stats = optimized_solver.get_stats()

print(f"Basic solver: {basic_stats.time_taken:.4f}s, {basic_stats.nodes_expanded} nodes")
print(f"Optimized solver: {optimized_stats.time_taken:.4f}s, {optimized_stats.nodes_expanded} nodes")
```

## 8. Test Cases

### 8.1 Simple Case
**Input:** `['2', '7', '2', '2', '4', '5', '4', '+', '-', '=']`  
**Expected:** `"22+54-4=72"` or equivalent

### 8.2 Complex Case
**Input:** `['0', '2', '3', '2', '3', '4', '1', '0', '6', '9', '3', '*', '/', '*', '+', '=']`  
**Expected:** `"24/2*33=30*10+96"` or equivalent

### 8.3 Edge Cases
- Minimal equation: `['1', '=', '1']`
- No solution cases
- Multiple valid solutions

## 9. Implementation Notes

### 9.1 Key Design Decisions

1. **Validation Strategy:** Separate validator class for modularity
2. **Domain Representation:** Sets for efficient membership testing
3. **State Management:** Explicit backup/restore for backtracking
4. **Timeout Handling:** Prevents infinite loops on hard instances

### 9.2 Performance Optimizations

1. **Efficient Domain Operations:** Use sets for O(1) lookup
2. **Lazy Evaluation:** Only compute necessary constraint checks
3. **Early Termination:** Stop as soon as solution is found
4. **Memory Management:** Reuse data structures where possible

## 10. Limitations and Future Work

### 10.1 Current Limitations

1. **Division by Zero:** Not explicitly handled in validation
2. **Floating Point Precision:** Limited to 1e-10 tolerance
3. **Memory Usage:** Could be optimized for very large instances

### 10.2 Future Improvements

1. **Better Heuristics:** Domain-specific variable/value ordering
2. **Constraint Learning:** Remember and reuse conflict information
3. **Parallel Search:** Explore multiple branches simultaneously
4. **Preprocessing:** More sophisticated initial constraint propagation

## 11. Conclusion

This implementation demonstrates the power of CSP techniques for solving combinatorial problems. The optimized solver should significantly outperform the basic backtracking approach by:

- Reducing search space through intelligent variable/value ordering
- Detecting failures early through constraint propagation
- Maintaining consistency through forward checking and arc consistency

The modular design allows for easy experimentation with different optimization techniques and provides a solid foundation for further research in constraint satisfaction.
