import random
import numpy as np
import time
import matplotlib.pyplot as plt
from tsp_solvers import greedy_solver


class GeneticTSP:
    def __init__(self, problem, population_size=100, elite_size=20, 
                 mutation_rate=0.01, tournament_size=5):
        """
        Initialize the genetic algorithm solver
        
        Args:
            problem: TSP problem instance
            population_size: Size of the population
            elite_size: Number of elite individuals to keep
            mutation_rate: Probability of mutation
            tournament_size: Number of individuals in tournament selection
        """
        self.problem = problem
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.population = []
        self.nodes = list(problem.graph.get_nodes())
        
        # History of best fitness for plotting
        self.best_distance_history = []
        self.avg_distance_history = []
        
        # Cache of distances between cities for faster calculation
        self.distance_cache = {}
        for i in self.nodes:
            for j in self.nodes:
                if i != j:
                    self.distance_cache[(i, j)] = problem.graph.get_weight(i, j)
    
    def get_distance(self, city1, city2):
        """Get distance between two cities using cache"""
        return self.distance_cache.get((city1, city2), 
                                     self.problem.graph.get_weight(city1, city2))
    
    def calculate_tour_distance(self, tour):
        """Calculate the total distance of a tour"""
        if len(tour) <= 1:
            return 0
            
        total_distance = 0
        for i in range(len(tour) - 1):
            total_distance += self.get_distance(tour[i], tour[i+1])
            
        # Add distance back to starting city if not already included
        if tour[0] != tour[-1]:
            total_distance += self.get_distance(tour[-1], tour[0])
            
        return total_distance
    
    def create_initial_population(self):
        """Create an initial population of random tours"""
        population = []
        
        # Add one greedy solution for a good starting point
        greedy_tour, _ = greedy_solver(self.problem)
        population.append(greedy_tour[:-1])  # Remove the duplicate start city
        
        # Generate random permutations for the rest
        for _ in range(self.population_size - 1):
            # Random permutation of cities
            tour = self.nodes.copy()
            random.shuffle(tour)
            population.append(tour)
            
        self.population = population
        return population
    
    def rank_population(self):
        """Rank population by fitness (shorter tours are better)"""
        # Calculate distances
        population_distances = [(tour, self.calculate_tour_distance(tour)) 
                               for tour in self.population]
        
        # Sort by distance (ascending)
        population_distances.sort(key=lambda x: x[1])
        
        # Return sorted population and distances
        return [item[0] for item in population_distances], [item[1] for item in population_distances]
    
    def selection(self, ranked_population, ranked_distances):
        """Select parents using tournament selection"""
        selection_results = []
        
        # Elitism - keep best individuals
        selection_results.extend(ranked_population[:self.elite_size])
        
        # Tournament selection for the rest
        while len(selection_results) < self.population_size:
            # Select random individuals for tournament
            tournament = random.sample(list(enumerate(ranked_population)), self.tournament_size)
            
            # Find the best individual in the tournament
            tournament_fitness = [(i, ranked_distances[i]) for i, _ in tournament]
            winner_idx = min(tournament_fitness, key=lambda x: x[1])[0]
            
            # Add the winner to selection
            selection_results.append(ranked_population[winner_idx])
        
        return selection_results
    
    def ordered_crossover(self, parent1, parent2):
        """
        Ordered Crossover (OX) for TSP
        Preserves the relative order of cities from both parents
        """
        # Create empty child
        child = [None] * len(parent1)
        
        # Choose random start/end positions for parent1 segment
        start, end = sorted(random.sample(range(len(parent1)), 2))
        
        # Copy segment from parent1
        child[start:end+1] = parent1[start:end+1]
        
        # Fill remaining positions with cities from parent2 in order
        parent2_idx = 0
        child_idx = (end + 1) % len(child)
        
        while None in child:
            # Find next city in parent2 that's not already in the child
            while parent2[parent2_idx] in child:
                parent2_idx = (parent2_idx + 1) % len(parent2)
            
            # Add this city to the child
            child[child_idx] = parent2[parent2_idx]
            
            # Move to next positions
            parent2_idx = (parent2_idx + 1) % len(parent2)
            child_idx = (child_idx + 1) % len(child)
            
        return child
    
    def swap_mutation(self, tour):
        """Swap mutation - randomly swap two cities"""
        for i in range(len(tour)):
            # Apply mutation with specified probability
            if random.random() < self.mutation_rate:
                # Choose a random position different from i
                j = i
                while j == i:
                    j = random.randint(0, len(tour) - 1)
                
                # Swap cities
                tour[i], tour[j] = tour[j], tour[i]
        
        return tour
    
    def inversion_mutation(self, tour):
        """Inversion mutation - reverse a random subsection of the tour"""
        if random.random() < self.mutation_rate:
            # Choose random start/end positions
            start, end = sorted(random.sample(range(len(tour)), 2))
            
            # Reverse the subsection
            tour[start:end+1] = reversed(tour[start:end+1])
            
        return tour
    
    def breed_population(self, mating_pool):
        """Create a new generation through crossover and mutation"""
        children = []
        
        # Keep elite individuals without changes
        children.extend(mating_pool[:self.elite_size])
        
        # Create children from random pairs
        for i in range(self.elite_size, self.population_size):
            parent1 = random.choice(mating_pool)
            parent2 = random.choice(mating_pool)
            
            # Create child through crossover
            child = self.ordered_crossover(parent1, parent2)
            
            # Apply mutations
            child = self.swap_mutation(child)
            child = self.inversion_mutation(child)
            
            children.append(child)
            
        return children
    
    def evolve(self, generations=500, print_interval=50, early_stop=50):
        """
        Main evolution loop
        
        Args:
            generations: Maximum number of generations
            print_interval: How often to print progress
            early_stop: Stop if no improvement for this many generations
        
        Returns:
            best_tour: Best tour found
            best_distance: Length of the best tour
        """
        # Create initial population
        self.create_initial_population()
        
        # Track best solution and generations without improvement
        overall_best_tour = None
        overall_best_distance = float('inf')
        generations_no_improvement = 0
        
        start_time = time.time()
        
        # Main evolution loop
        for generation in range(generations):
            # Rank population
            ranked_population, ranked_distances = self.rank_population()
            
            # Get generation statistics
            best_distance = ranked_distances[0]
            avg_distance = sum(ranked_distances) / len(ranked_distances)
            
            # Track history for plotting
            self.best_distance_history.append(best_distance)
            self.avg_distance_history.append(avg_distance)
            
            # Update overall best
            if best_distance < overall_best_distance:
                overall_best_distance = best_distance
                overall_best_tour = ranked_population[0].copy()
                generations_no_improvement = 0
            else:
                generations_no_improvement += 1
            
            # Print progress
            if generation % print_interval == 0 or generation == generations - 1:
                elapsed = time.time() - start_time
                print(f"Generation {generation}: Best distance = {best_distance:.2f}, "
                      f"Avg distance = {avg_distance:.2f}, "
                      f"Time elapsed = {elapsed:.2f}s")
            
            # Check early stopping
            if generations_no_improvement >= early_stop:
                print(f"No improvement for {early_stop} generations. Stopping early at generation {generation}.")
                break
            
            # Select parents
            mating_pool = self.selection(ranked_population, ranked_distances)
            
            # Create next generation
            self.population = self.breed_population(mating_pool)
        
        # Ensure the best tour is a cycle (add starting city at the end if needed)
        if overall_best_tour and overall_best_tour[0] != overall_best_tour[-1]:
            overall_best_tour.append(overall_best_tour[0])
            
        # Recalculate best distance to ensure it's accurate
        if overall_best_tour:
            overall_best_distance = self.calculate_tour_distance(overall_best_tour)
        
        return overall_best_tour, overall_best_distance
    
    def plot_progress(self, save_path=None, show_greedy=True, show_optimal=True):
        """
        Plot the progress of evolution
        
        Args:
            save_path: Path to save the plot (if None, plot is displayed)
            show_greedy: Whether to show the greedy solution line
            show_optimal: Whether to show the optimal solution line
        """
        plt.figure(figsize=(12, 6))
        
        generations = range(1, len(self.best_distance_history) + 1)
        
        # Plot GA progress
        plt.plot(generations, self.best_distance_history, 'b-', label='Best Distance')
        plt.plot(generations, self.avg_distance_history, 'r-', label='Average Distance', alpha=0.7)
        
        # Add greedy and optimal solution lines if requested
        if show_greedy or show_optimal:
            if show_greedy:
                _, greedy_distance = greedy_solver(self.problem)
                plt.axhline(y=greedy_distance, color='g', linestyle='--', 
                           label=f'Greedy Solution: {greedy_distance:.2f}')
            
            if show_optimal and hasattr(self.problem, 'optimal_len'):
                plt.axhline(y=self.problem.optimal_len, color='r', linestyle='--', 
                           label=f'Optimal Solution: {self.problem.optimal_len}')
        
        plt.title(f'GA Progress for {self.problem.name} ({len(self.nodes)} cities)')
        plt.xlabel('Generation')
        plt.ylabel('Tour Distance')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()


def genetic_solver(problem, population_size=100, generations=500, mutation_rate=0.01, 
                  elite_size=20, tournament_size=5, print_interval=50, early_stop=50,
                  plot_progress=True, plot_dir='plots'):
    """
    Solve TSP using genetic algorithm
    
    Args:
        problem: TSP problem instance
        population_size: Size of the population
        generations: Maximum number of generations
        mutation_rate: Probability of mutation
        elite_size: Number of elite individuals to keep
        tournament_size: Number of individuals in tournament selection
        print_interval: How often to print progress
        early_stop: Stop if no improvement for this many generations
        plot_progress: Whether to plot progress
        plot_dir: Directory to save plots to
        
    Returns:
        best_tour: Best tour found
        best_distance: Length of the best tour
        ga: The genetic algorithm object for further analysis
    """
    import os
    
    # Create genetic algorithm instance
    ga = GeneticTSP(problem, population_size, elite_size, mutation_rate, tournament_size)
    
    # Run evolution
    best_tour, best_distance = ga.evolve(generations, print_interval, early_stop)
    
    # Plot progress
    if plot_progress:
        # Create plot directory if it doesn't exist
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
            
        # Save plot
        plot_path = os.path.join(plot_dir, f"{problem.name}_progress.png")
        ga.plot_progress(save_path=plot_path, show_greedy=True, show_optimal=True)
        print(f"Progress plot saved to {plot_path}")
    
    return best_tour, best_distance, ga