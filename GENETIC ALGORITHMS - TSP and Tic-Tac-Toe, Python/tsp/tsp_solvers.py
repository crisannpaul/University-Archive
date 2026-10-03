import time
import matplotlib.pyplot as plt
import numpy as np

def greedy_solver(problem):
    """
    Implements a simple greedy algorithm for TSP:
    1. Start at the first city
    2. Repeatedly visit the nearest unvisited city
    3. Return to the starting city
    """
    nodes = list(problem.graph.get_nodes())
    
    # Start from the first node
    start_node = nodes[0]
    current = start_node
    tour = [current]
    unvisited = set(nodes)
    unvisited.remove(current)
    
    # Greedy selection of nearest unvisited city
    while unvisited:
        # Find nearest unvisited city
        next_city = min(unvisited, key=lambda city: problem.graph.get_weight(current, city))
        tour.append(next_city)
        unvisited.remove(next_city)
        current = next_city
    
    # Complete the tour by returning to start
    tour.append(start_node)
    
    # Calculate tour length
    tour_length = 0
    for i in range(len(tour) - 1):
        tour_length += problem.graph.get_weight(tour[i], tour[i+1])
    
    return tour, tour_length

def optimal_tsp_solver(problem, time_limit=60):
    """
    Branch and Bound algorithm to find the optimal TSP solution.
    """
    start_time = time.time()
    
    nodes = list(problem.graph.get_nodes())
    n = len(nodes)
    
    if n > 15:
        print(f"Warning: Optimal solving for {n} cities may take a very long time.")
    
    # Initialize with the best known solution as the greedy solution
    greedy_tour, best_length = greedy_solver(problem)
    best_tour = greedy_tour.copy()
    
    # Calculate distance matrix for faster access
    dist_matrix = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                dist_matrix[(i, j)] = problem.graph.get_weight(i, j)
    
    # Function to calculate lower bound for a partial tour
    def calculate_lower_bound(current_path, unvisited):
        # Current path length
        current_length = 0
        for i in range(len(current_path) - 1):
            current_length += dist_matrix[(current_path[i], current_path[i+1])]
        
        # Minimum cost to include each unvisited city
        min_to_connect = 0
        for city in unvisited:
            # Find two shortest edges from this city
            if len(current_path) > 0:
                # Connection to the current path
                min_to_current = min(dist_matrix[(city, current_path[-1])], 
                                    dist_matrix[(current_path[0], city)])
                min_to_connect += min_to_current
            
            # Plus minimum edge to any other unvisited city
            if len(unvisited) > 1:
                other_cities = [c for c in unvisited if c != city]
                min_edge = min(dist_matrix[(city, c)] for c in other_cities)
                min_to_connect += min_edge / 2  # Divide by 2 to avoid double counting
        
        return current_length + min_to_connect
    
    # Branch and bound function
    def branch_and_bound(current_path, unvisited, current_length):
        nonlocal best_tour, best_length
        
        # Check time limit
        if time.time() - start_time > time_limit:
            return
        
        # If all cities are visited, complete the tour
        if not unvisited:
            # Add return to start
            complete_length = current_length + dist_matrix[(current_path[-1], current_path[0])]
            
            # Update best tour if better
            if complete_length < best_length:
                current_path.append(current_path[0])  # Complete the cycle
                best_tour = current_path.copy()
                best_length = complete_length
                print(f"New best tour found: {best_length:.2f}")
            return
        
        # Calculate lower bound
        lower_bound = calculate_lower_bound(current_path, unvisited)
        
        # Prune if this path can't be better than the current best
        if lower_bound >= best_length:
            return
        
        # Try each unvisited city as the next step
        for next_city in sorted(unvisited, key=lambda c: dist_matrix[(current_path[-1], c)]):
            # Add city to path
            new_path = current_path.copy()
            new_path.append(next_city)
            
            # Calculate new length
            new_length = current_length + dist_matrix[(current_path[-1], next_city)]
            
            # Skip if already worse than best
            if new_length >= best_length:
                continue
                
            # Continue exploration
            new_unvisited = unvisited.copy()
            new_unvisited.remove(next_city)
            branch_and_bound(new_path, new_unvisited, new_length)
    
    # Start with first city
    start_node = nodes[0]
    initial_path = [start_node]
    remaining = set(nodes)
    remaining.remove(start_node)
    
    # Start branch and bound
    try:
        branch_and_bound(initial_path, remaining, 0)
    except KeyboardInterrupt:
        print("Search interrupted by user.")
    
    # Check if time limit reached
    if time.time() - start_time >= time_limit:
        print(f"Time limit of {time_limit} seconds reached. Returning best solution found.")
    
    return best_tour, best_length

def visualize_tour(problem, tour, title_prefix="Tour"):
    """
    Visualize a TSP tour
    """
    if not hasattr(problem.graph, 'node_coords'):
        print("Cannot visualize - problem doesn't have coordinates")
        return
    
    # Get coordinates for all nodes
    coords = {}
    for node in problem.graph.get_nodes():
        coords[node] = problem.graph.node_coords[node]
    
    # Extract tour coordinates
    x_coords = [coords[node][0] for node in tour]
    y_coords = [coords[node][1] for node in tour]
    
    plt.figure(figsize=(10, 8))
    
    # Plot cities
    plt.scatter([coords[node][0] for node in problem.graph.get_nodes()],
                [coords[node][1] for node in problem.graph.get_nodes()],
                c='blue', s=30)
    
    # Plot tour
    plt.plot(x_coords, y_coords, 'r-', alpha=0.7)
    
    # Mark start/end
    plt.scatter(x_coords[0], y_coords[0], c='green', s=100, marker='*', label='Start/End')
    
    plt.title(f"{title_prefix} for {problem.name} ({problem.graph.dimension} cities)")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

def test_greedy_solver(problems, max_problems=5):
    """
    Test the greedy solver on a set of TSP problems
    """
    results = []
    
    # Limit number of test problems
    test_problems = problems[:min(max_problems, len(problems))]
    
    for problem in test_problems:
        print(f"\nTesting problem: {problem.name} ({problem.graph.dimension} cities)")
        
        # Time the solver
        start_time = time.time()
        tour, tour_length = greedy_solver(problem)
        elapsed_time = time.time() - start_time
        
        # Calculate gap from optimal
        gap = (tour_length - problem.optimal_len) / problem.optimal_len * 100
        
        print(f"Tour length: {tour_length:.2f}")
        print(f"Optimal length: {problem.optimal_len}")
        print(f"Gap from optimal: {gap:.2f}%")
        print(f"Time taken: {elapsed_time:.3f} seconds")
        
        # Store results
        results.append({
            'name': problem.name,
            'cities': problem.graph.dimension,
            'tour_length': tour_length,
            'optimal_length': problem.optimal_len,
            'gap': gap,
            'time': elapsed_time
        })
        
        # Visualize the tour if problem has coordinates
        if hasattr(problem.graph, 'node_coords'):
            visualize_tour(problem, tour, "Greedy Tour")
    
    return results

def test_optimal_solver(problems, max_problems=3, max_cities=12, time_limit=120):
    """
    Test the optimal TSP solver on a set of small TSP problems
    """
    # Filter for appropriately sized problems
    small_problems = [p for p in problems if p.graph.dimension <= max_cities]
    
    if not small_problems:
        print(f"No problems found with ≤ {max_cities} cities. Try increasing max_cities.")
        return []
    
    # Limit number of problems
    test_problems = small_problems[:min(max_problems, len(small_problems))]
    
    results = []
    
    for problem in test_problems:
        print(f"\nTesting optimal solver on: {problem.name} ({problem.graph.dimension} cities)")
        print(f"Time limit: {time_limit} seconds")
        
        # Time the solver
        start_time = time.time()
        tour, tour_length = optimal_tsp_solver(problem, time_limit=time_limit)
        elapsed_time = time.time() - start_time
        
        # Calculate gap from known optimal
        gap = (tour_length - problem.optimal_len) / problem.optimal_len * 100
        
        print(f"Tour length: {tour_length:.2f}")
        print(f"Known optimal length: {problem.optimal_len}")
        print(f"Gap from optimal: {gap:.6f}%")
        print(f"Time taken: {elapsed_time:.3f} seconds")
        
        # Flag if the solution is truly optimal
        is_optimal = abs(gap) < 1e-5  # Allow for small floating point differences
        print(f"Found optimal solution: {'Yes' if is_optimal else 'No'}")
        
        # Store results
        results.append({
            'name': problem.name,
            'cities': problem.graph.dimension,
            'tour_length': tour_length,
            'optimal_length': problem.optimal_len,
            'gap': gap,
            'time': elapsed_time,
            'is_optimal': is_optimal
        })
        
        # Visualize the tour if coordinates are available
        if hasattr(problem.graph, 'node_coords'):
            visualize_tour(problem, tour, "Optimal Tour")
    
    # Compare with greedy for the same problems
    print("\nComparison with greedy solver:")
    for problem in test_problems:
        greedy_tour, greedy_length = greedy_solver(problem)
        greedy_gap = (greedy_length - problem.optimal_len) / problem.optimal_len * 100
        
        # Find the corresponding optimal result
        optimal_result = next(r for r in results if r['name'] == problem.name)
        
        print(f"\n{problem.name} ({problem.graph.dimension} cities):")
        print(f"Greedy: {greedy_length:.2f} (gap: {greedy_gap:.2f}%)")
        print(f"Optimal: {optimal_result['tour_length']:.2f} (gap: {optimal_result['gap']:.6f}%)")
        print(f"Improvement: {greedy_gap - optimal_result['gap']:.2f}%")
    
    return results