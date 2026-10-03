import random
import copy
import time
import pickle  # For saving/loading AI

# Constants
POPULATION_SIZE = 50  # Reduced population size
NUM_GENERATIONS = 10   # Fewer generations
TOURNAMENT_SIZE = 5   
MUTATION_RATE = 0.05   
GAMES_PER_EVALUATION = 40  # Fewer games for faster evaluation

class TicTacToe:
    """A Tic-Tac-Toe game board and logic"""
    
    def __init__(self):
        # Initialize empty 3x3 board (0 = empty, 1 = X, 2 = O)
        self.board = [0] * 9
        self.current_player = 1  # X goes first
        self.winner = None
        self.game_over = False
    
    def make_move(self, position):
        """Make a move on the board"""
        if self.game_over or self.board[position] != 0:
            return False
        
        self.board[position] = self.current_player
        
        # Check for win
        if self.check_win(self.current_player):
            self.winner = self.current_player
            self.game_over = True
            return True
        
        # Check for draw
        if 0 not in self.board:
            self.game_over = True
            return True
        
        # Switch player
        self.current_player = 3 - self.current_player  # Toggles between 1 and 2
        return True
    
    def check_win(self, player):
        """Check if the specified player has won"""
        # Check rows
        for i in range(0, 9, 3):
            if self.board[i] == self.board[i+1] == self.board[i+2] == player:
                return True
        
        # Check columns
        for i in range(3):
            if self.board[i] == self.board[i+3] == self.board[i+6] == player:
                return True
        
        # Check diagonals
        if self.board[0] == self.board[4] == self.board[8] == player:
            return True
        if self.board[2] == self.board[4] == self.board[6] == player:
            return True
        
        return False
    
    def get_legal_moves(self):
        """Return a list of legal move positions"""
        if self.game_over:
            return []
        return [i for i, val in enumerate(self.board) if val == 0]
    
    def print_board(self):
        """Print the current state of the board"""
        symbols = {0: ' ', 1: 'X', 2: 'O'}
        print("-------------")
        for i in range(0, 9, 3):
            print(f"| {symbols[self.board[i]]} | {symbols[self.board[i+1]]} | {symbols[self.board[i+2]]} |")
            print("-------------")


class GeneticPlayer:
    """A genetic algorithm-based Tic-Tac-Toe player"""
    
    def __init__(self, chromosome=None):
        # Chromosome represents weights for each board position and pattern
        # We'll use a simple approach: each empty position gets a weight,
        # and we choose the position with the highest weight
        if chromosome is None:
            # Initialize with random weights
            self.chromosome = [random.uniform(-1, 1) for _ in range(4 * 3**9)]
        else:
            self.chromosome = chromosome
        
        self.fitness = 0
    
    def get_move(self, game, player_num):
        """Choose the next move based on the chromosome"""
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return None
        
        # Simple position-based strategy:
        # Convert board state to a feature vector and calculate weights
        scores = {}
        for move in legal_moves:
            # Create a temporary board with this move
            temp_game = copy.deepcopy(game)
            temp_game.make_move(move)
            
            # Calculate a score for this move based on features
            scores[move] = self.evaluate_position(temp_game, player_num)
        
        # Choose the move with the highest score
        return max(scores, key=scores.get)
    
    def evaluate_position(self, game, player_num):
        """Evaluate a board position using features encoded in the chromosome"""
        # We'll use four simple features:
        # 1. Number of rows/cols/diags with only our pieces
        # 2. Number of rows/cols/diags with only opponent pieces
        # 3. Center control
        # 4. Corner control
        
        features = []
        opponent = 3 - player_num
        
        # Count our potential winning lines
        our_lines = 0
        opponent_lines = 0
        
        # Check rows
        for i in range(0, 9, 3):
            row = game.board[i:i+3]
            if opponent not in row and player_num in row:
                our_lines += 1
            if player_num not in row and opponent in row:
                opponent_lines += 1
        
        # Check columns
        for i in range(3):
            col = [game.board[i], game.board[i+3], game.board[i+6]]
            if opponent not in col and player_num in col:
                our_lines += 1
            if player_num not in col and opponent in col:
                opponent_lines += 1
        
        # Check diagonals
        diag1 = [game.board[0], game.board[4], game.board[8]]
        diag2 = [game.board[2], game.board[4], game.board[6]]
        if opponent not in diag1 and player_num in diag1:
            our_lines += 1
        if player_num not in diag1 and opponent in diag1:
            opponent_lines += 1
        if opponent not in diag2 and player_num in diag2:
            our_lines += 1
        if player_num not in diag2 and opponent in diag2:
            opponent_lines += 1
        
        # Center control (position 4 is the center)
        center_control = 1 if game.board[4] == player_num else 0
        
        # Corner control (positions 0, 2, 6, 8 are corners)
        corners = [game.board[0], game.board[2], game.board[6], game.board[8]]
        corner_control = sum(1 for c in corners if c == player_num)
        
        # Combine features
        features = [our_lines, -opponent_lines, center_control, corner_control]
        
        # Get the chromosome section for this board state
        board_state_index = 0
        for i, val in enumerate(game.board):
            board_state_index += val * (3 ** i)
        
        chromosome_section = self.chromosome[board_state_index*4:(board_state_index+1)*4]
        
        # Calculate weighted sum
        score = sum(f * w for f, w in zip(features, chromosome_section))
        return score
    
    def calculate_fitness(self, num_games=GAMES_PER_EVALUATION):
        """Calculate fitness by playing against multiple strategies"""
        # Play against random player
        random_score = self.play_against_random(num_games)
        
        # Play against simple heuristic player
        heuristic_score = self.play_against_heuristic(num_games)
        
        # Skip minimax - it's too slow for training
        minimax_score = self.play_against_minimax(num_games // 2)
        
        self.fitness = random_score + heuristic_score + minimax_score
        return self.fitness
    
    def play_against_random(self, num_games):
        """Play against a random player and return the score"""
        score = 0
        for _ in range(num_games):
            game = TicTacToe()
            # Alternate who goes first
            player_num = random.choice([1, 2])
            
            while not game.game_over:
                if game.current_player == player_num:
                    # Our turn
                    move = self.get_move(game, player_num)
                    game.make_move(move)
                else:
                    # Random player's turn
                    legal_moves = game.get_legal_moves()
                    if legal_moves:
                        move = random.choice(legal_moves)
                        game.make_move(move)
            
            # Score: +2 for win, +1 for draw, 0 for loss
            if game.winner == player_num:
                score += 2
            elif game.winner is None:
                score += 1
        
        return score
    
    def play_against_heuristic(self, num_games):
        """Play against a simple heuristic player and return the score"""
        score = 0
        for _ in range(num_games):
            game = TicTacToe()
            # Alternate who goes first
            player_num = random.choice([1, 2])
            
            while not game.game_over:
                if game.current_player == player_num:
                    # Our turn
                    move = self.get_move(game, player_num)
                    game.make_move(move)
                else:
                    # Heuristic player's turn (simple but not random)
                    move = self.heuristic_move(game, 3 - player_num)
                    game.make_move(move)
            
            # Score: +3 for win, +1 for draw, 0 for loss (harder opponent)
            if game.winner == player_num:
                score += 3
            elif game.winner is None:
                score += 1
        
        return score
        
    def play_against_minimax(self, num_games):
        """Play against a minimax player with limited depth"""
        score = 0
        for _ in range(num_games):
            game = TicTacToe()
            # Alternate who goes first
            player_num = random.choice([1, 2])
            
            while not game.game_over:
                if game.current_player == player_num:
                    # Our turn
                    move = self.get_move(game, player_num)
                    game.make_move(move)
                else:
                    # Minimax player's turn
                    move = self.minimax_move(game, 3 - player_num)
                    game.make_move(move)
            
            # Score: +5 for win, +2 for draw, 0 for loss (hardest opponent)
            if game.winner == player_num:
                score += 5
            elif game.winner is None:
                score += 2
        
        return score
    
    def minimax_move(self, game, player_num):
        """Use minimax algorithm to find the best move (with limited depth for efficiency)"""
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return None
            
        best_score = float('-inf')
        best_move = legal_moves[0]
        
        # Try each move
        for move in legal_moves:
            # Make a copy of the game
            new_game = copy.deepcopy(game)
            new_game.make_move(move)
            
            # Use minimax to evaluate this move
            score = self.minimax(new_game, 3, False, player_num)  # Limited depth of 3
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move
    
    def minimax(self, game, depth, is_maximizing, player_num):
        """Minimax algorithm with limited depth"""
        opponent = 3 - player_num
        
        # Terminal conditions
        if game.winner == player_num:
            return 10
        elif game.winner == opponent:
            return -10
        elif 0 not in game.board or depth == 0:  # Draw or max depth reached
            return 0
            
        if is_maximizing:
            best_score = float('-inf')
            for move in game.get_legal_moves():
                new_game = copy.deepcopy(game)
                new_game.current_player = player_num
                new_game.make_move(move)
                score = self.minimax(new_game, depth - 1, False, player_num)
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for move in game.get_legal_moves():
                new_game = copy.deepcopy(game)
                new_game.current_player = opponent
                new_game.make_move(move)
                score = self.minimax(new_game, depth - 1, True, player_num)
                best_score = min(score, best_score)
            return best_score
    
    def heuristic_move(self, game, player_num):
        """Simple heuristic for playing Tic-Tac-Toe"""
        board = game.board
        opponent = 3 - player_num
        
        # Check if we can win in the next move
        for i in game.get_legal_moves():
            board[i] = player_num
            if game.check_win(player_num):
                board[i] = 0  # Restore the board
                return i
            board[i] = 0  # Restore the board
        
        # Check if the opponent can win in their next move and block them
        for i in game.get_legal_moves():
            board[i] = opponent
            if game.check_win(opponent):
                board[i] = 0  # Restore the board
                return i
            board[i] = 0  # Restore the board
        
        # Take center if available
        if board[4] == 0:
            return 4
        
        # Take a corner if available
        corners = [0, 2, 6, 8]
        available_corners = [c for c in corners if board[c] == 0]
        if available_corners:
            return random.choice(available_corners)
        
        # Take what's available
        return random.choice(game.get_legal_moves())
    
    def mate(self, partner):
        """Create a child through crossover and mutation"""
        # Single-point crossover
        crossover_point = random.randint(1, len(self.chromosome) - 1)
        child_chromosome = self.chromosome[:crossover_point] + partner.chromosome[crossover_point:]
        
        # Mutation
        for i in range(len(child_chromosome)):
            if random.random() < MUTATION_RATE:
                child_chromosome[i] += random.uniform(-0.2, 0.2)
                # Ensure values stay in a reasonable range
                child_chromosome[i] = max(-1, min(1, child_chromosome[i]))
        
        return GeneticPlayer(child_chromosome)


def run_genetic_algorithm():
    """Run the genetic algorithm to evolve Tic-Tac-Toe players"""
    # Initialize population
    population = [GeneticPlayer() for _ in range(POPULATION_SIZE)]
    best_ever = None
    best_ever_fitness = 0
    last_improvement = 0
    
    for generation in range(NUM_GENERATIONS):
        start_time = time.time()
        print(f"Generation {generation+1}/{NUM_GENERATIONS}...")
        
        # Calculate fitness for each individual
        for i, individual in enumerate(population):
            if (i + 1) % 20 == 0:  # Report less frequently
                print(f"  Evaluating individual {i+1}/{POPULATION_SIZE}...")
            
            individual.calculate_fitness()
        
        # Sort by fitness (higher is better)
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Track best ever individual
        if population[0].fitness > best_ever_fitness:
            best_ever = copy.deepcopy(population[0])
            best_ever_fitness = population[0].fitness
            last_improvement = generation
            print(f"  New best fitness: {best_ever_fitness}")
            
            # Save the best player whenever we find a better one
            with open('best_tictactoe_ai.pkl', 'wb') as f:
                pickle.dump(best_ever, f)
            print("  Best player saved to 'best_tictactoe_ai.pkl'")
        
        # Print stats
        best_fitness = population[0].fitness
        avg_fitness = sum(ind.fitness for ind in population) / POPULATION_SIZE
        print(f"  Current best fitness: {best_fitness}")
        print(f"  All-time best fitness: {best_ever_fitness}")
        print(f"  Average fitness: {avg_fitness:.2f}")
        print(f"  Generation completed in {time.time() - start_time:.2f} seconds")
        
        # Visualize the best player's strategy (only every 5 generations to reduce output)
        if generation % 5 == 0 or generation == NUM_GENERATIONS - 1:
            visualize_strategy(population[0], generation+1)
        
        # Stop early if no improvement for many generations
        if generation - last_improvement > 10:  # Reduced from 15
            print(f"  No improvement for 10 generations. Stopping early.")
            break
        
        # Create new generation
        new_population = []
        
        # Elitism: keep the top performers
        elitism_count = max(2, POPULATION_SIZE // 20)  # At least 2, typically 5% of population
        new_population.extend(population[:elitism_count])
        
        # Add the all-time best individual to preserve good solutions
        if best_ever is not None:
            new_population.append(best_ever)
        
        # Fill the rest of the population with children
        while len(new_population) < POPULATION_SIZE:
            # Tournament selection
            parent1 = max(random.sample(population, TOURNAMENT_SIZE), key=lambda x: x.fitness)
            parent2 = max(random.sample(population, TOURNAMENT_SIZE), key=lambda x: x.fitness)
            
            # Create child
            child = parent1.mate(parent2)
            new_population.append(child)
        
        # Replace old population
        population = new_population
    
    # Return best individual
    return best_ever


def load_ai(filename='best_tictactoe_ai.pkl'):
    """Load a previously saved AI"""
    try:
        with open(filename, 'rb') as f:
            ai = pickle.load(f)
        print(f"Successfully loaded AI from {filename}")
        return ai
    except FileNotFoundError:
        print(f"File {filename} not found. Please train an AI first.")
        return None
    except Exception as e:
        print(f"Error loading AI: {e}")
        return None
    
    # Return best individual
    return population[0]


def visualize_strategy(ai_player, generation):
    """Visualize the strategy of the best player in each generation"""
    print("\n  Strategy Visualization for Generation", generation)
    print("  " + "-" * 50)
    
    # Test key board states and show what move the AI would make
    test_boards = [
        # Opening moves
        [0, 0, 0, 0, 0, 0, 0, 0, 0],  # Empty board
        [0, 0, 0, 0, 2, 0, 0, 0, 0],  # Opponent in center
        [2, 0, 0, 0, 0, 0, 0, 0, 0],  # Opponent in corner
        
        # Defensive scenarios
        [2, 2, 0, 0, 1, 0, 0, 0, 0],  # Block horizontal threat (0-1-2)
        [2, 0, 0, 2, 0, 0, 0, 0, 1],  # Block vertical threat (0-3-6)
        [2, 0, 0, 0, 2, 0, 1, 0, 0],  # Block diagonal threat (0-4-8)
        
        # Offensive scenarios
        [1, 1, 0, 0, 2, 0, 0, 0, 0],  # Complete horizontal for win (0-1-2)
        [1, 0, 0, 0, 1, 2, 0, 0, 0],  # Complete diagonal for win (0-4-8)
        
        # Complex scenarios
        [1, 0, 0, 0, 1, 0, 2, 0, 0],  # Create a fork (two ways to win)
        [1, 0, 0, 0, 2, 0, 1, 0, 0]   # Block opponent's fork
    ]

    scenarios = [
        "Empty board (first move)",
        "Opponent starts in center",
        "Opponent starts in corner",
        
        "Block horizontal threat (positions 0-1-2)",
        "Block vertical threat (positions 0-3-6)",
        "Block diagonal threat (positions 0-4-8)",
        
        "Complete horizontal for win (positions 0-1-2)",
        "Complete diagonal for win (positions 0-4-8)",
        
        "Create a fork (diagonal with center)",
        "Block opponent's fork"
    ]
    
    for i, board in enumerate(test_boards):
        game = TicTacToe()
        game.board = board.copy()
        game.current_player = 1  # AI plays as X
        
        # Find AI's move
        move = ai_player.get_move(game, 1)
        
        # Create a visual representation of the board and move
        symbols = {0: ' ', 1: 'X', 2: 'O'}
        
        # Make a copy and show the AI's next move with a '*'
        visual_board = [symbols[cell] for cell in board]
        if visual_board[move] == ' ':
            visual_board[move] = '*'
        
        # Display the board with AI's choice
        print(f"\n  Scenario {i+1}: {scenarios[i]}")
        print("  -------------")
        for j in range(0, 9, 3):
            print(f"  | {visual_board[j]} | {visual_board[j+1]} | {visual_board[j+2]} |")
            print("  -------------")
        print(f"  AI chooses position {move}")
        
        # Get top features that influenced this decision
        if i == 0:  # Only show features for the first scenario to avoid clutter
            scores = {}
            for pos in range(9):
                if board[pos] == 0:  # If position is empty
                    temp_game = copy.deepcopy(game)
                    temp_game.board[pos] = 1  # Try this move
                    
                    features = []
                    # Count our potential winning lines
                    our_lines = 0
                    opponent_lines = 0
                    
                    # Check rows
                    for row in range(0, 9, 3):
                        row_vals = temp_game.board[row:row+3]
                        if 2 not in row_vals and 1 in row_vals:
                            our_lines += 1
                        if 1 not in row_vals and 2 in row_vals:
                            opponent_lines += 1
                    
                    # Check columns
                    for col in range(3):
                        col_vals = [temp_game.board[col], temp_game.board[col+3], temp_game.board[col+6]]
                        if 2 not in col_vals and 1 in col_vals:
                            our_lines += 1
                        if 1 not in col_vals and 2 in col_vals:
                            opponent_lines += 1
                    
                    # Check diagonals
                    diag1 = [temp_game.board[0], temp_game.board[4], temp_game.board[8]]
                    diag2 = [temp_game.board[2], temp_game.board[4], temp_game.board[6]]
                    if 2 not in diag1 and 1 in diag1:
                        our_lines += 1
                    if 1 not in diag1 and 2 in diag1:
                        opponent_lines += 1
                    if 2 not in diag2 and 1 in diag2:
                        our_lines += 1
                    if 1 not in diag2 and 2 in diag2:
                        opponent_lines += 1
                    
                    # Center and corner control
                    center_control = 1 if pos == 4 else 0
                    corner_control = 1 if pos in [0, 2, 6, 8] else 0
                    
                    scores[pos] = (our_lines, -opponent_lines, center_control, corner_control)
            
            print("\n  Feature importance for first move (our_lines, -opp_lines, center, corners):")
            print(f"  Selected move ({move}): {scores[move]}")
    
    print("\n  " + "-" * 50)


def play_against_evolved(ai_player):
    """Let a human play against the evolved AI"""
    game = TicTacToe()
    
    # Decide who goes first
    human_player = int(input("Do you want to be player 1 (X) or 2 (O)? "))
    ai_player_num = 3 - human_player
    
    print("\nGame starts!")
    print("Use numbers 0-8 to make your move (0 is top-left, 8 is bottom-right)")
    
    while not game.game_over:
        game.print_board()
        
        if game.current_player == human_player:
            # Human's turn
            while True:
                try:
                    move = int(input(f"Your move (player {human_player}): "))
                    if move < 0 or move > 8:
                        print("Invalid move! Please enter a number between 0 and 8.")
                        continue
                    if game.board[move] != 0:
                        print("That position is already taken! Try again.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number!")
            
            game.make_move(move)
        else:
            # AI's turn
            print(f"AI (player {ai_player_num}) is thinking...")
            move = ai_player.get_move(game, ai_player_num)
            print(f"AI chooses position {move}")
            game.make_move(move)
    
    # Game over
    game.print_board()
    if game.winner == human_player:
        print("Congratulations! You won!")
    elif game.winner == ai_player_num:
        print("The AI won! Better luck next time.")
    else:
        print("It's a draw!")


if __name__ == "__main__":
    choice = input("Do you want to (t)rain a new AI or (p)lay against a saved one? (t/p): ").lower()
    
    if choice.startswith('t'):
        print("Training new Tic-Tac-Toe AI...")
        best_player = run_genetic_algorithm()
        print("\nTraining complete!")
        print("Best player saved to 'best_tictactoe_ai.pkl'")
        
        play_again = True
        while play_again:
            play_against_evolved(best_player)
            again = input("\nDo you want to play again? (y/n): ").lower()
            play_again = again.startswith('y')
            
    elif choice.startswith('p'):
        best_player = load_ai()
        if best_player:
            # Display AI's strategy before playing
            visualize_strategy(best_player, "Loaded AI")
            
            play_again = True
            while play_again:
                play_against_evolved(best_player)
                again = input("\nDo you want to play again? (y/n): ").lower()
                play_again = again.startswith('y')
    else:
        print("Invalid choice. Please run the program again and choose 't' or 'p'.")