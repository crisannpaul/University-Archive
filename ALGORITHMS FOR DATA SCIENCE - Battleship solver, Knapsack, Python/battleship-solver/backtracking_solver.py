def solve_with_backtracking(row_clues, col_clues, known_hits, known_misses, board_size, fleet):
    solutions = []

    # Initialize the board and constraints
    board = [[0] * board_size for _ in range(board_size)]
    required_row = row_clues[:]
    required_col = col_clues[:]

    # Apply known hits and misses
    for r, c in known_hits:
        board[r][c] = 1
        required_row[r] -= 1
        required_col[c] -= 1
    for r, c in known_misses:
        board[r][c] = 0

    # Begin backtracking
    ships_to_place = [length for length, count in fleet for _ in range(count)]
    backtrack_place_ships(board, required_row, required_col, ships_to_place, 0, solutions)

    return solutions


def backtrack_place_ships(board, required_row, required_col, ships_to_place, index, solutions):
    # Base case: All ships have been placed
    if index == len(ships_to_place):
        if all(x == 0 for x in required_row) and all(x == 0 for x in required_col):
            solutions.append([row[:] for row in board])  # Add a deep copy of the solution
        return

    ship_length = ships_to_place[index]

    # Try placing the ship at every valid position
    for r in range(len(board)):
        for c in range(len(board)):
            for orientation in ('H', 'V'):
                if can_place_ship_partial(board, r, c, ship_length, orientation, required_row, required_col):
                    # Place the ship
                    place_ship_temp(board, r, c, ship_length, orientation, 1)
                    update_constraints(required_row, required_col, r, c, ship_length, orientation, -1)

                    # Recur to place the next ship
                    backtrack_place_ships(board, required_row, required_col, ships_to_place, index + 1, solutions)

                    # Backtrack: Remove the ship
                    update_constraints(required_row, required_col, r, c, ship_length, orientation, 1)
                    place_ship_temp(board, r, c, ship_length, orientation, 0)


def can_place_ship_partial(board, row, col, length, orientation, required_row, required_col):
    if orientation == 'H':
        if col + length > len(board):  # Check bounds
            return False
        for c in range(col, col + length):
            if board[row][c] != 0 or not is_cell_free(board, row, c):  # Check overlap/adjacency
                return False
        if required_row[row] < length:  # Check row constraint
            return False
        for c in range(col, col + length):
            if required_col[c] < 1:  # Check column constraints
                return False
    else:  # Vertical
        if row + length > len(board):  # Check bounds
            return False
        for r in range(row, row + length):
            if board[r][col] != 0 or not is_cell_free(board, r, col):  # Check overlap/adjacency
                return False
        if required_col[col] < length:  # Check column constraint
            return False
        for r in range(row, row + length):
            if required_row[r] < 1:  # Check row constraints
                return False

    return True


def is_cell_free(board, r, c):
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            rr, cc = r + dr, c + dc
            if 0 <= rr < len(board) and 0 <= cc < len(board[0]):
                if board[rr][cc] == 1:  # Adjacent cell occupied
                    return False
    return True


def place_ship_temp(board, row, col, length, orientation, value):
    if orientation == 'H':
        for c in range(col, col + length):
            board[row][c] = value
    else:
        for r in range(row, row + length):
            board[r][col] = value


def update_constraints(required_row, required_col, row, col, length, orientation, delta):
    if orientation == 'H':
        required_row[row] += delta * length
        for c in range(col, col + length):
            required_col[c] += delta
    else:
        required_col[col] += delta * length
        for r in range(row, row + length):
            required_row[r] += delta
