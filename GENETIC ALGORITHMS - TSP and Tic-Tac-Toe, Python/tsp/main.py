import tsplib95 as tsp
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from tsp_solvers import greedy_solver
from genetic_tsp import genetic_solver

tsp_problems_dir = 'tsplib-master'
plots_dir = 'tsp_plots'  # Directory to save all plots
results_dir = 'tsp_results'  # Directory to save results

class TSPProblem:
    def __init__(self, name:str, graph:tsp.models.StandardProblem, optimal_len:int):
        self.name = name
        self.graph = graph
        self.optimal_len = optimal_len
        
def init_tsp_problems(dimension_limit) -> list[TSPProblem]:
    with open(file=f'{tsp_problems_dir}/solutions') as solutions_file:
        temp = {}
        for line in solutions_file.readlines():
            problem_name = line.split(':')[0].strip()
            problem_optimal_len = line.split(':')[1].strip().removesuffix('(CEIL_2D)')
            temp[problem_name] = problem_optimal_len

    problems = []
    for file in os.listdir(tsp_problems_dir):
        if file.endswith('.tsp'):
            problem = tsp.load(f'{tsp_problems_dir}/{file}')
            if problem.dimension < dimension_limit:
                try:
                    if problem.edge_weight_type in ('EUC_2D'):
                        problems.append(TSPProblem(file.strip('.tsp'), problem, int(temp[file.strip('.tsp')])))
                except KeyError:
                    pass

    return problems

def save_results_to_file(results, filename):
    """Save results to a text file"""
    with open(filename, 'w') as f:
        for key, value in results.items():
            if isinstance(value, dict):
                f.write(f"{key}:\n")
                for k, v in value.items():
                    f.write(f"  {k}: {v}\n")
            else:
                f.write(f"{key}: {value}\n")
        f.write("\n")

def select_diverse_problems(problems, num_problems=10):
    """
    Select a diverse set of problems with different sizes
    
    Args:
        problems: List of TSP problems
        num_problems: Number of problems to select
        
    Returns:
        selected_problems: List of selected problems
    """
    # Sort problems by size
    sorted_problems = sorted(problems, key=lambda p: p.graph.dimension)
    
    # If we have fewer problems than requested, return all of them
    if len(sorted_problems) <= num_problems:
        return sorted_problems
    
    # Otherwise, select problems of different sizes
    step = len(sorted_problems) / num_problems
    selected_indices = [int(i * step) for i in range(num_problems)]
    
    # Ensure we include the smallest and largest problems
    if 0 not in selected_indices:
        selected_indices[0] = 0
    if len(sorted_problems) - 1 not in selected_indices:
        selected_indices[-1] = len(sorted_problems) - 1
    
    selected_problems = [sorted_problems[i] for i in selected_indices]
    
    return selected_problems

def run_ga_on_problem(problem, population_size=200, generations=300, 
                     mutation_rate=0.01, elite_size=40, tournament_size=10):
    """
    Run genetic algorithm on a single problem and create detailed visualization
    
    Args:
        problem: TSP problem instance
        population_size: Size of the population
        generations: Maximum number of generations
        mutation_rate: Probability of mutation
        elite_size: Number of elite individuals to keep
        tournament_size: Number of individuals in tournament selection
    """
    print(f"\nSolving problem: {problem.name} ({problem.graph.dimension} cities)")
    
    # Get greedy solution
    greedy_start = time.time()
    greedy_tour, greedy_distance = greedy_solver(problem)
    greedy_time = time.time() - greedy_start
    greedy_gap = (greedy_distance - problem.optimal_len) / problem.optimal_len * 100
    
    # Run genetic algorithm
    ga_start = time.time()
    tour, tour_distance, ga = genetic_solver(
        problem, 
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        elite_size=elite_size,
        tournament_size=tournament_size,
        plot_progress=False  # We'll create our own enhanced plots
    )
    ga_time = time.time() - ga_start
    
    # Calculate gap from optimal
    ga_gap = (tour_distance - problem.optimal_len) / problem.optimal_len * 100
    improvement = greedy_gap - ga_gap
    
    # Print results
    print(f"Genetic algorithm tour length: {tour_distance:.2f}")
    print(f"Greedy tour length: {greedy_distance:.2f}")
    print(f"Optimal length: {problem.optimal_len}")
    print(f"Genetic algorithm gap from optimal: {ga_gap:.2f}%")
    print(f"Greedy gap from optimal: {greedy_gap:.2f}%")
    print(f"Improvement over greedy: {improvement:.2f}%")
    print(f"Genetic algorithm time: {ga_time:.2f} seconds")
    print(f"Greedy time: {greedy_time:.2f} seconds")
    
    # Create enhanced fitness evolution plot
    plt.figure(figsize=(12, 6))
    
    generations_run = len(ga.best_distance_history)
    generation_numbers = range(1, generations_run + 1)
    
    # Plot genetic algorithm progress
    plt.plot(generation_numbers, ga.best_distance_history, 'b-', label='Best GA Solution', linewidth=2)
    plt.plot(generation_numbers, ga.avg_distance_history, 'b--', label='Average GA Solution', alpha=0.7)
    
    # Add horizontal lines for greedy and optimal
    plt.axhline(y=greedy_distance, color='r', linestyle='-', label=f'Greedy Solution: {greedy_distance:.2f}')
    plt.axhline(y=problem.optimal_len, color='g', linestyle='-', label=f'Optimal Solution: {problem.optimal_len}')
    
    # Annotate final GA solution
    plt.annotate(f'Final GA: {tour_distance:.2f}', 
                xy=(generations_run, tour_distance),
                xytext=(generations_run - (generations_run * 0.2), tour_distance * 1.05),
                arrowprops=dict(facecolor='blue', shrink=0.05))
    
    plt.title(f'GA Progress for {problem.name} ({problem.graph.dimension} cities)')
    plt.xlabel('Generation')
    plt.ylabel('Tour Distance')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Save plot
    plt.savefig(os.path.join(plots_dir, f"{problem.name}_progress_enhanced.png"))
    plt.close()
    
    # Create tour visualization if coordinates are available
    if hasattr(problem.graph, 'node_coords'):
        plt.figure(figsize=(10, 8))
        
        # Get coordinates for all nodes
        coords = {}
        for node in problem.graph.get_nodes():
            coords[node] = problem.graph.node_coords[node]
        
        # Extract tour coordinates
        x_coords = [coords[node][0] for node in tour]
        y_coords = [coords[node][1] for node in tour]
        
        # Plot cities
        plt.scatter([coords[node][0] for node in problem.graph.get_nodes()],
                    [coords[node][1] for node in problem.graph.get_nodes()],
                    c='blue', s=30)
        
        # Plot tour
        plt.plot(x_coords, y_coords, 'r-', alpha=0.7)
        
        # Mark start/end
        plt.scatter(x_coords[0], y_coords[0], c='green', s=100, marker='*', label='Start/End')
        
        # Add solution quality information
        plt.title(f"GA Tour for {problem.name} ({problem.graph.dimension} cities)")
        plt.figtext(0.5, 0.01, f"Length: {tour_distance:.2f} (Gap: {ga_gap:.2f}%, Optimal: {problem.optimal_len})", 
                  ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        # Save plot
        tour_plot_path = os.path.join(plots_dir, f"{problem.name}_tour.png")
        plt.savefig(tour_plot_path)
        plt.close()
    
    return {
        'name': problem.name,
        'cities': problem.graph.dimension,
        'ga_tour_length': tour_distance,
        'greedy_tour_length': greedy_distance,
        'optimal_length': problem.optimal_len,
        'ga_gap': ga_gap,
        'greedy_gap': greedy_gap,
        'improvement': improvement,
        'ga_time': ga_time,
        'greedy_time': greedy_time,
        'generations_run': generations_run
    }

if __name__ == "__main__":
    # Create required directories
    for directory in [plots_dir, results_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Load problems
    problems = init_tsp_problems(dimension_limit=500)
    print(f"Loaded {len(problems)} problems")
    
    # Select diverse problems to test
    selected_problems = select_diverse_problems(problems, num_problems=10)
    print(f"\nSelected {len(selected_problems)} diverse problems:")
    for p in selected_problems:
        print(f"  - {p.name} ({p.graph.dimension} cities)")
    
    # Hardcoded GA parameters
    ga_params = {
        'population_size': 800,  
        'generations': 300,
        'mutation_rate': 0.01,
        'elite_size': 80, 
        'tournament_size': 40
    }
    
    print(f"\nUsing GA parameters: {ga_params}")
    
    # Run GA on each problem
    results = []
    for problem in selected_problems:
        result = run_ga_on_problem(
            problem, 
            population_size=ga_params['population_size'],
            generations=ga_params['generations'],
            mutation_rate=ga_params['mutation_rate'],
            elite_size=ga_params['elite_size'],
            tournament_size=ga_params['tournament_size']
        )
        results.append(result)
    
    # Calculate summary statistics
    ga_gaps = [r['ga_gap'] for r in results]
    greedy_gaps = [r['greedy_gap'] for r in results]
    improvements = [r['improvement'] for r in results]
    
    summary = {
        'num_problems': len(results),
        'ga_avg_gap': np.mean(ga_gaps),
        'ga_median_gap': np.median(ga_gaps),
        'ga_min_gap': min(ga_gaps),
        'ga_max_gap': max(ga_gaps),
        'greedy_avg_gap': np.mean(greedy_gaps),
        'avg_improvement': np.mean(improvements),
        'parameters': ga_params
    }
    
    # Print summary
    print("\nFinal summary:")
    print(f"Number of problems: {summary['num_problems']}")
    print(f"Genetic Algorithm - Average gap: {summary['ga_avg_gap']:.2f}%")
    print(f"Genetic Algorithm - Median gap: {summary['ga_median_gap']:.2f}%")
    print(f"Genetic Algorithm - Min gap: {summary['ga_min_gap']:.2f}%")
    print(f"Genetic Algorithm - Max gap: {summary['ga_max_gap']:.2f}%")
    print(f"Greedy Algorithm - Average gap: {summary['greedy_avg_gap']:.2f}%")
    print(f"Average improvement over greedy: {summary['avg_improvement']:.2f}%")
    
    # Save detailed results
    save_results_to_file(
        summary,
        os.path.join(results_dir, 'final_results_summary.txt')
    )
    
    # Create summary plots
    
    # Plot gap comparison
    plt.figure(figsize=(12, 6))
    
    # Sort results by number of cities for better visualization
    sorted_results = sorted(results, key=lambda x: x['cities'])
    problem_names = [r['name'] for r in sorted_results]
    problem_sizes = [r['cities'] for r in sorted_results]
    ga_gaps_sorted = [r['ga_gap'] for r in sorted_results]
    greedy_gaps_sorted = [r['greedy_gap'] for r in sorted_results]
    
    x = np.arange(len(problem_names))
    width = 0.35
    
    plt.bar(x - width/2, ga_gaps_sorted, width, label='Genetic Algorithm')
    plt.bar(x + width/2, greedy_gaps_sorted, width, label='Greedy Algorithm')
    
    plt.xlabel('Problem')
    plt.ylabel('Gap from Optimal (%)')
    plt.title('GA vs Greedy - Gap from Optimal Solution')
    plt.xticks(x, problem_names, rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'gap_comparison.png'))
    plt.close()
    
    # Plot improvement by problem size
    plt.figure(figsize=(12, 6))
    improvements_sorted = [r['improvement'] for r in sorted_results]
    
    plt.scatter(problem_sizes, improvements_sorted, s=100, alpha=0.7)
    for i, txt in enumerate(problem_names):
        plt.annotate(txt, (problem_sizes[i], improvements_sorted[i]), 
                    xytext=(5, 5), textcoords='offset points')
    
    plt.xlabel('Problem Size (cities)')
    plt.ylabel('Improvement over Greedy (%)')
    plt.title('GA Improvement over Greedy by Problem Size')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'improvement_by_size.png'))
    plt.close()
    
    print(f"Results saved to {results_dir}")
    print(f"Plots saved to {plots_dir}")