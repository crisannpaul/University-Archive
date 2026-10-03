import random

def is_cell_free(board, r, c):
    if board[r][c] == 1:
        return False
    rows = len(board)
    cols = len(board[0])
    for dr in [-1,0,1]:
        for dc in [-1,0,1]:
            rr = r+dr
            cc = c+dc
            if 0 <= rr < rows and 0 <= cc < cols:
                if board[rr][cc] == 1:
                    return False
    return True

def can_place_ship(board, row, col, length, orientation):
    size = len(board)
    if orientation=='H':
        if col+length>size:
            return False
        for c in range(col,col+length):
            if not is_cell_free(board,row,c):
                return False
    else:
        if row+length>size:
            return False
        for r in range(row,row+length):
            if not is_cell_free(board,r,col):
                return False
    return True

def place_ship(board, row, col, length, orientation):
    if orientation=='H':
        for c in range(col,col+length):
            board[row][c] = 1
    else:
        for r in range(row,row+length):
            board[r][col] = 1

def generate_battleship_armada(size, fleet):
    board = [[0]*size for _ in range(size)]
    for ship_length, count in fleet:
        for _ in range(count):
            placed = False
            attempts = 0
            while not placed and attempts<2000:
                attempts+=1
                orientation = random.choice(['H','V'])
                row = random.randint(0,size-1)
                col = random.randint(0,size-1)
                if can_place_ship(board,row,col,ship_length,orientation):
                    place_ship(board,row,col,ship_length,orientation)
                    placed=True
            if not placed:
                raise RuntimeError(f"Could not place a ship of length {ship_length}")
    return board