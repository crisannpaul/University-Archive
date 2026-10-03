def calculate_probability_distribution_naive(board, guesses, flags, row_clues, col_clues):
    """
    prob[r][c] = 
       ((row_clues[r] - hits_in_row[r]) / hidden_in_row[r]) *
       ((col_clues[c] - hits_in_col[c]) / hidden_in_col[c])
    """
    size = len(board)
    
    hits_in_row = [0] * size
    hidden_in_row = [0] * size
    for r in range(size):
        for c in range(size):
            if guesses[r][c] is True:
                hits_in_row[r] += 1
            if guesses[r][c] is None and not flags[r][c]:
                hidden_in_row[r] += 1

    hits_in_col = [0] * size
    hidden_in_col = [0] * size
    for c in range(size):
        for r in range(size):
            if guesses[r][c] is True:
                hits_in_col[c] += 1
            if guesses[r][c] is None and not flags[r][c]:
                hidden_in_col[c] += 1

    prob_map = [[0.0] * size for _ in range(size)]
    for r in range(size):
        for c in range(size):
            if guesses[r][c] is not None or flags[r][c]:
                prob_map[r][c] = 0.0
                continue
            # row/col leftover ships needed
            needed_row = row_clues[r] - hits_in_row[r]
            needed_col = col_clues[c] - hits_in_col[c]
            if hidden_in_row[r] <= 0 or hidden_in_col[c] <= 0:
                prob_map[r][c] = 0.0
            else:
                row_factor = needed_row / float(hidden_in_row[r]) if needed_row > 0 else 0
                col_factor = needed_col / float(hidden_in_col[c]) if needed_col > 0 else 0
                prob_map[r][c] = row_factor * col_factor

    # Apply logical deduction
    # 1. If exactly 2 hidden cells in a row/column and all other cells are flagged/missed
    #    and the clue matches the number of remaining cells, those cells are guaranteed to be ship parts.
    for r in range(size):
        if hidden_in_row[r] == row_clues[r] - hits_in_row[r]:  # All remaining cells in this row must be ships
            for c in range(size):
                if guesses[r][c] is None and not flags[r][c]:
                    prob_map[r][c] = 1.0  # Force these cells to have high probability

    for c in range(size):
        if hidden_in_col[c] == col_clues[c] - hits_in_col[c]:  # All remaining cells in this column must be ships
            for r in range(size):
                if guesses[r][c] is None and not flags[r][c]:
                    prob_map[r][c] = 1.0  # Force these cells to have high probability

    # 2. If the number of hits + hidden cells in a row/column equals the clue, the hidden cells must be ships.
    for r in range(size):
        if hits_in_row[r] + hidden_in_row[r] == row_clues[r]:  # All hidden cells in this row must be ships
            for c in range(size):
                if guesses[r][c] is None and not flags[r][c]:
                    prob_map[r][c] = 1.0

    for c in range(size):
        if hits_in_col[c] + hidden_in_col[c] == col_clues[c]:  # All hidden cells in this column must be ships
            for r in range(size):
                if guesses[r][c] is None and not flags[r][c]:
                    prob_map[r][c] = 1.0

    return prob_map


def ai_move(board, guesses, flags, row_clues, col_clues):
    """    
    1) Flag cells with prob=0.
    2) Shoot cell with highest prob.
    """
    prob_map = calculate_probability_distribution_naive(board, guesses, flags, row_clues, col_clues)
    size = len(board)

    # (1) Look for prob=0 => flag
    for r in range(size):
        for c in range(size):
            if guesses[r][c] is None and not flags[r][c]:
                if prob_map[r][c] == 0.0:
                    return ('flag', r, c)

    # (2) Find highest prob => shoot
    best_prob = 0.0
    best_r, best_c = None, None
    for r in range(size):
        for c in range(size):
            if guesses[r][c] is None and not flags[r][c]:
                if prob_map[r][c] > best_prob:
                    best_prob = prob_map[r][c]
                    best_r, best_c = r, c
    if best_r is not None:
        return ('shoot', best_r, best_c)

    # No valid moves
    return (None, 0, 0)
