import pygame
import sys
import time
import random
from board_generation import generate_battleship_armada
from naive_solver import calculate_probability_distribution_naive, ai_move
from backtracking_solver import solve_with_backtracking

########################################
# 1) USER-SELECTED SIZE & FLEET
########################################

ARMADAS = {
    5: [
        (3,1),  # 1 ship of length 3
        (2,2),  # 2 ships of length 2
        (1,2),  # 2 ships of length 1
    ],
    6: [
        (3,2),  # 2 ship of length 3
        (2,2),  # 2 ships of length 2
    ],
    7: [
        (4,1),
        (3,1),
        (2,2),
        (1,3),
    ],
    8: [
        (4,1),
        (3,2),
        (2,3),
        (1,3),
    ],
    10: [
        (4,1),  # 1 battleship (4 squares)
        (3,2),  # 2 cruisers (3 squares)
        (2,3),  # 3 destroyers (2 squares)
        (1,4),  # 4 submarines (1 square)
    ]
}

def choose_board_size():
    """Prompt user to pick 5, 6, 7, or 10."""
    while True:
        choice = input("Choose board size (5, 6, 7, 8 or 10): ").strip()
        if choice in ("5", "6", "7", "8", "10"):
            return int(choice)
        print("Invalid choice. Enter 5, 6, 7, 8 or 10.")

########################################
# 2) BATTLESHIP GAME CLASS
########################################

BLACK=(0,0,0); RED=(255,0,0); GRAY=(128,128,128)
GREEN=(0,200,0); BLUE=(0,0,255); WHITE=(255,255,255)

CELL_SIZE=40
MARGIN=100
FONT_SIZE=24

class BattleshipGame:
    def __init__(self, size):
        self.size = size
        # pick the fleet for this size
        self.fleet = ARMADAS[size]
        
        # generate board
        while True:
            try:
                self.board = generate_battleship_armada(size, self.fleet)
                break
            except RuntimeError:
                continue
        
        # guesses
        self.guesses = [[None]*size for _ in range(size)]
        self.flags   = [[False]*size for _ in range(size)]
        
        # row/col clues
        self.row_clues = [ sum(self.board[r][c]==1 for c in range(size)) for r in range(size)]
        self.col_clues = [ sum(self.board[r][c]==1 for r in range(size)) for c in range(size)]

        self.total_ships = sum(self.row_clues)
        self.hits_found=0
        self.hits=0
        self.misses=0
        self.game_over=False

        self.prob_map = self.refresh_probability_map()

    def refresh_probability_map(self):
        self.prob_map = calculate_probability_distribution_naive(
            self.board, self.guesses, self.flags, self.row_clues, self.col_clues
        )

    def handle_left_click(self,mx,my):
        col = (mx - MARGIN)//CELL_SIZE
        row = (my - MARGIN)//CELL_SIZE
        if 0<=row<self.size and 0<=col<self.size:
            if not self.game_over:
                if self.guesses[row][col] is None and not self.flags[row][col]:
                    if self.board[row][col]==1:
                        self.guesses[row][col]=True
                        self.hits_found+=1
                        self.hits+=1
                        if self.hits_found==self.total_ships:
                            self.game_over=True
                    else:
                        self.guesses[row][col]=False
                        self.misses+=1

    def handle_right_click(self,mx,my):
        col=(mx - MARGIN)//CELL_SIZE
        row=(my - MARGIN)//CELL_SIZE
        if 0<=row<self.size and 0<=col<self.size:
            if not self.game_over:
                if self.guesses[row][col] is None:
                    self.flags[row][col] = not self.flags[row][col]

    def handle_alg_shoot(self,row,col):
        if 0<=row<self.size and 0<=col<self.size:
            if not self.game_over:
                if self.guesses[row][col] is None and not self.flags[row][col]:
                    if self.board[row][col]==1:
                        self.guesses[row][col]=True
                        self.hits_found+=1
                        self.hits+=1
                        if self.hits_found==self.total_ships:
                            self.game_over=True
                    else:
                        self.guesses[row][col]=False
                        self.misses+=1

    def handle_alg_flag(self,row,col):
        if 0<=row<self.size and 0<=col<self.size:
            if not self.game_over:
                if self.guesses[row][col] is None:
                    self.flags[row][col] = not self.flags[row][col]

    def color_of_cell(self,r,c):
        guess_state=self.guesses[r][c]
        hidden_state=self.board[r][c]
        if not self.game_over:
            if guess_state is None:
                return BLACK
            else:
                return RED if guess_state else GRAY
        else:
            # reveal
            if guess_state is True:
                return RED
            elif guess_state is False:
                return GRAY
            else:
                return GREEN if hidden_state==1 else BLUE

    def draw(self,screen,font):
        screen.fill(WHITE)
        small_font=pygame.font.SysFont(None,16)

        for r in range(self.size):
            for c in range(self.size):
                x=MARGIN+c*CELL_SIZE
                y=MARGIN+r*CELL_SIZE
                color=self.color_of_cell(r,c)
                pygame.draw.rect(screen,color,(x,y,CELL_SIZE,CELL_SIZE))
                pygame.draw.rect(screen,WHITE,(x,y,CELL_SIZE,CELL_SIZE),1)

                # flagged?
                if (self.guesses[r][c] is None and
                    self.flags[r][c] and
                    not self.game_over):
                    text_surf=font.render("X",True,WHITE)
                    text_rect=text_surf.get_rect(center=(x+CELL_SIZE//2,y+CELL_SIZE//2))
                    screen.blit(text_surf,text_rect)

                # show probability
                if hasattr(self,'prob_map'):
                    if (self.guesses[r][c] is None and 
                        not self.flags[r][c] and
                        not self.game_over):
                        val=self.prob_map[r][c]
                        txt=f"{val:.2f}"
                        surf=small_font.render(txt,True,WHITE)
                        rect=surf.get_rect(center=(x+CELL_SIZE//2,y+CELL_SIZE//2))
                        screen.blit(surf,rect)

        # row clues
        for r in range(self.size):
            clue=str(self.row_clues[r])
            surf=font.render(clue,True,BLACK)
            rect=surf.get_rect(right=MARGIN-10,
                               centery=MARGIN+r*CELL_SIZE+CELL_SIZE//2)
            screen.blit(surf,rect)

        # col clues
        for c in range(self.size):
            clue=str(self.col_clues[c])
            surf=font.render(clue,True,BLACK)
            rect=surf.get_rect(centerx=MARGIN+c*CELL_SIZE+CELL_SIZE//2,
                               bottom=MARGIN-10)
            screen.blit(surf,rect)

        # hits/misses
        status=f"Hits: {self.hits}   Misses: {self.misses}"
        st_surf=font.render(status,True,BLACK)
        screen.blit(st_surf,(10,10))

        # game over?
        if self.game_over:
            msg="YOU WIN! All ships found."
            msg_surf=font.render(msg,True,BLACK)
            screen.blit(msg_surf,(10,40))

    def solve_step(self):
        """
        Perform a single backtracking step and apply forced hits/misses.
        Forced misses are now flagged instead of being marked as misses.
        """
        known_hits = set()
        known_misses = set()

        # Gather known hits and misses
        for r in range(self.size):
            for c in range(self.size):
                if self.guesses[r][c] is True:
                    known_hits.add((r, c))
                elif self.guesses[r][c] is False:
                    known_misses.add((r, c))

        # Solve with backtracking to find all solutions
        solutions = solve_with_backtracking(
            self.row_clues, self.col_clues, known_hits, known_misses, self.size, self.fleet
        )

        if not solutions:
            print("No valid solutions found with current constraints.")
            return

        # Build occupancy counts for each cell based on all solutions
        occ_count = [[0] * self.size for _ in range(self.size)]
        for solution in solutions:
            for r in range(self.size):
                for c in range(self.size):
                    if solution[r][c] == 1:
                        occ_count[r][c] += 1

        # Identify forced hits and forced misses
        total_solutions = len(solutions)
        forced_hits = []
        forced_misses = []

        for r in range(self.size):
            for c in range(self.size):
                if self.guesses[r][c] is None:
                    if occ_count[r][c] == total_solutions:
                        forced_hits.append((r, c))  # Always a ship
                    elif occ_count[r][c] == 0:
                        forced_misses.append((r, c))  # Never a ship10

        # Apply forced hits
        for (r, c) in forced_hits:
            if self.guesses[r][c] is None:
                self.guesses[r][c] = True
                self.hits_found += 1
                self.hits += 1
                if self.hits_found == self.total_ships:
                    self.game_over = True

        # Flag forced misses
        for (r, c) in forced_misses:
            if self.guesses[r][c] is None and not self.flags[r][c]:
                self.flags[r][c] = True

        # Debug output
        print(f"Forced hits: {forced_hits}")
        print(f"Flags for forced misses: {forced_misses}")

########################################
# 3) MAIN LOOP
########################################

def main():
    pygame.init()
    font = pygame.font.SysFont(None, FONT_SIZE)

    chosen_size = choose_board_size()
    board_size_px = CELL_SIZE * chosen_size
    window_width = MARGIN + board_size_px + MARGIN
    window_height = MARGIN + board_size_px + MARGIN

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption(f"Battleship {chosen_size}x{chosen_size}")

    clock = pygame.time.Clock()
    game = BattleshipGame(chosen_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Press 'n' for AI to make a move
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    move, row, col = ai_move(game.board, game.guesses, game.flags, game.row_clues, game.col_clues)
                    if move == 'flag':
                        game.handle_alg_flag(row, col)
                    elif move == 'shoot':
                        game.handle_alg_shoot(row, col)
                    elif not move:
                        print("No AI move found.")
                
                # Press 's' to trigger backtracking solver
                if event.key == pygame.K_s:
                    game.solve_step()

            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    game.handle_left_click(mx, my)
                elif event.button == 3:
                    game.handle_right_click(mx, my)

        game.refresh_probability_map()
        game.draw(screen, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()

