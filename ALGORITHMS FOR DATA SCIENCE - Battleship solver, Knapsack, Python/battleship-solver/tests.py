import time
import random
from board_generation import generate_battleship_armada
from naive_solver import calculate_probability_distribution_naive, ai_move
from backtracking_solver import solve_with_backtracking

# Armada configurations for testing
ARMADAS = {
    4: [(3, 1), (2, 1)],
    5: [(3, 1), (2, 2)],
    6: [(3, 2), (2, 2)],
    7: [(4, 1), (3, 1), (2, 2)],
    8: [(4, 1), (3, 1), (2, 3)],
    9: [(4, 1), (3, 2), (2, 3)],
    10: [(4, 1), (3, 2), (2, 3), (1, 4)],
}

def test_naive_solver(grid_size, trials=100):
    """
    Test the naive solver for accuracy and execution time.
    """
    fleet = ARMADAS[grid_size]
    total_hits = 0
    total_misses = 0
    total_time = 0

    for _ in range(trials):
        board = generate_battleship_armada(grid_size, fleet)
        guesses = [[None] * grid_size for _ in range(grid_size)]
        flags = [[False] * grid_size for _ in range(grid_size)]
        row_clues = [sum(row) for row in board]
        col_clues = [sum(board[r][c] for r in range(grid_size)) for c in range(grid_size)]

        hits = 0
        misses = 0
        start_time = time.time()

        while hits < sum(row_clues):
            move, r, c = ai_move(board, guesses, flags, row_clues, col_clues)
            if move == 'shoot':
                if board[r][c] == 1:
                    guesses[r][c] = True
                    hits += 1
                else:
                    guesses[r][c] = False
                    misses += 1
            elif move == 'flag':
                flags[r][c] = True
            else:
                break

        total_time += time.time() - start_time
        total_hits += hits
        total_misses += misses

    accuracy = total_hits / (total_hits + total_misses) * 100
    avg_time = total_time / trials

    return accuracy, avg_time

def test_backtracking_solver(grid_size, trials=100):
    """
    Test the backtracking solver for execution time.
    """
    fleet = ARMADAS[grid_size]
    total_time = 0

    for _ in range(trials):
        while True:
            try:
                board = generate_battleship_armada(grid_size, fleet)
                break
            except RuntimeError:
                continue
        row_clues = [sum(row) for row in board]
        col_clues = [sum(board[r][c] for r in range(grid_size)) for c in range(grid_size)]
        known_hits = set()
        known_misses = set()

        start_time = time.time()
        solve_with_backtracking(row_clues, col_clues, known_hits, known_misses, grid_size, fleet)
        total_time += time.time() - start_time

    avg_time = total_time / trials

    return avg_time

def plot_results():
    """
    Generate results and plot graphs for naive solver and backtracking solver.
    """
    import matplotlib.pyplot as plt

    grid_sizes = range(4, 11)
    naive_accuracies = []
    naive_times = []
    backtracking_times = []

    for size in grid_sizes:
        print(f"Testing grid size {size}...")

        # Test naive solver
        avg_naive_accuracy, avg_naive_time = test_naive_solver(size)
        naive_accuracies.append(avg_naive_accuracy)
        naive_times.append(avg_naive_time)

        # Test backtracking solver, exclude size 10
        if size < 10:
            avg_backtracking_time = test_backtracking_solver(size)
            backtracking_times.append(avg_backtracking_time)

    # Plot Naive Solver Accuracy
    plt.figure()
    plt.plot(grid_sizes, naive_accuracies, marker='o')
    plt.title("Naive Solver Accuracy")
    plt.xlabel("Grid Size")
    plt.ylabel("Accuracy (%)")
    plt.grid(True)
    plt.savefig("naive_solver_accuracy.png")
    plt.close()

    # Plot Naive Solver Execution Time
    plt.figure()
    plt.plot(grid_sizes, naive_times, marker='o')
    plt.title("Naive Solver Execution Time")
    plt.xlabel("Grid Size")
    plt.ylabel("Time (s)")
    plt.grid(True)
    plt.savefig("naive_solver_execution_time.png")
    plt.close()

    # Plot Backtracking Solver Execution Time (Exclude Grid Size 10)
    plt.figure()
    plt.plot(range(4, 10), backtracking_times, marker='o')
    plt.title("Backtracking Solver Execution Time")
    plt.xlabel("Grid Size")
    plt.ylabel("Time (s)")
    plt.grid(True)
    plt.savefig("backtracking_solver_execution_time.png")
    plt.close()

if __name__ == "__main__":
    plot_results()
