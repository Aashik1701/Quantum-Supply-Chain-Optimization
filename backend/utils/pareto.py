"""
Pareto front computation utilities for multi-objective optimization.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


def is_dominated(solution_a: Dict[str, float], solution_b: Dict[str, float], 
                 objectives: List[str] = ['cost', 'co2', 'time']) -> bool:
    """
    Check if solution_a is dominated by solution_b.
    
    A solution is dominated if another solution is better or equal in all objectives
    and strictly better in at least one objective (for minimization).
    
    Args:
        solution_a: First solution with objective values
        solution_b: Second solution with objective values
        objectives: List of objective keys to compare (all minimization)
        
    Returns:
        True if solution_a is dominated by solution_b
    """
    # Check if b is better or equal in all objectives
    better_or_equal = all(
        solution_b.get(obj, float('inf')) <= solution_a.get(obj, float('inf'))
        for obj in objectives
    )
    
    # Check if b is strictly better in at least one objective
    strictly_better = any(
        solution_b.get(obj, float('inf')) < solution_a.get(obj, float('inf'))
        for obj in objectives
    )
    
    return better_or_equal and strictly_better


def compute_pareto_front(solutions: List[Dict[str, Any]], 
                         objectives: List[str] = ['cost', 'co2', 'time']) -> Tuple[List[Dict], List[Dict]]:
    """
    Compute Pareto front from a list of solutions using non-dominated sorting.
    
    Args:
        solutions: List of solution dictionaries with objective values
        objectives: List of objective keys to consider (all minimization)
        
    Returns:
        Tuple of (pareto_solutions, dominated_solutions) with isDominated flag added
    """
    if not solutions:
        return [], []
    
    # Make copies to avoid modifying originals
    solutions_copy = [dict(s) for s in solutions]
    
    pareto_solutions = []
    dominated_solutions = []
    
    # For each solution, check if it's dominated by any other
    for i, sol_a in enumerate(solutions_copy):
        is_dominated_flag = False
        
        for j, sol_b in enumerate(solutions_copy):
            if i == j:
                continue
            
            if is_dominated(sol_a, sol_b, objectives):
                is_dominated_flag = True
                break
        
        sol_a['isDominated'] = is_dominated_flag
        
        if is_dominated_flag:
            dominated_solutions.append(sol_a)
        else:
            pareto_solutions.append(sol_a)
    
    return pareto_solutions, dominated_solutions


def compute_hypervolume(pareto_front: List[Dict[str, float]], 
                       reference_point: Dict[str, float],
                       objectives: List[str] = ['cost', 'co2', 'time']) -> float:
    """
    Compute hypervolume indicator for Pareto front quality assessment.
    
    Hypervolume measures the volume of objective space dominated by the Pareto front
    relative to a reference point (nadir point).
    
    Args:
        pareto_front: List of non-dominated solutions
        reference_point: Worst acceptable values for each objective
        objectives: List of objective keys
        
    Returns:
        Hypervolume value (higher is better)
    """
    if not pareto_front:
        return 0.0
    
    # Simple 2D hypervolume calculation (can be extended to 3D)
    if len(objectives) == 2:
        obj1, obj2 = objectives[0], objectives[1]
        
        # Sort by first objective
        sorted_front = sorted(pareto_front, key=lambda x: x[obj1])
        
        hypervolume = 0.0
        prev_obj1 = reference_point[obj1]
        
        for solution in sorted_front:
            width = prev_obj1 - solution[obj1]
            height = reference_point[obj2] - solution[obj2]
            hypervolume += width * height
            prev_obj1 = solution[obj1]
        
        return hypervolume
    
    # For 3D, use approximate calculation (sum of dominated boxes)
    elif len(objectives) == 3:
        total_volume = 0.0
        
        for solution in pareto_front:
            # Calculate box volume from solution to reference point
            volume = 1.0
            for obj in objectives:
                diff = reference_point[obj] - solution[obj]
                volume *= max(0, diff)
            total_volume += volume
        
        return total_volume
    
    return 0.0


def compute_spacing_metric(pareto_front: List[Dict[str, float]],
                           objectives: List[str] = ['cost', 'co2', 'time']) -> float:
    """
    Compute spacing metric to assess distribution uniformity of Pareto front.
    
    Lower values indicate more uniform distribution.
    
    Args:
        pareto_front: List of non-dominated solutions
        objectives: List of objective keys
        
    Returns:
        Spacing metric value (lower is better)
    """
    if len(pareto_front) < 2:
        return 0.0
    
    # Normalize objectives
    normalized_front = []
    obj_mins = {obj: min(s[obj] for s in pareto_front) for obj in objectives}
    obj_maxs = {obj: max(s[obj] for s in pareto_front) for obj in objectives}
    
    for solution in pareto_front:
        normalized = {}
        for obj in objectives:
            range_val = obj_maxs[obj] - obj_mins[obj]
            if range_val > 0:
                normalized[obj] = (solution[obj] - obj_mins[obj]) / range_val
            else:
                normalized[obj] = 0.0
        normalized_front.append(normalized)
    
    # Compute distances to nearest neighbor
    distances = []
    for i, sol_a in enumerate(normalized_front):
        min_dist = float('inf')
        for j, sol_b in enumerate(normalized_front):
            if i == j:
                continue
            # Euclidean distance in objective space
            dist = np.sqrt(sum((sol_a[obj] - sol_b[obj])**2 for obj in objectives))
            min_dist = min(min_dist, dist)
        distances.append(min_dist)
    
    # Compute spacing as standard deviation of distances
    mean_dist = np.mean(distances)
    spacing = np.sqrt(np.mean([(d - mean_dist)**2 for d in distances]))
    
    return spacing


def select_representative_solutions(pareto_front: List[Dict[str, Any]],
                                   n: int = 5,
                                   objectives: List[str] = ['cost', 'co2', 'time']) -> List[Dict]:
    """
    Select n representative solutions from Pareto front for visualization.
    
    Selects corner solutions (best in each objective) and uniformly distributed solutions.
    
    Args:
        pareto_front: List of non-dominated solutions
        n: Number of representative solutions to select
        objectives: List of objective keys
        
    Returns:
        List of representative solutions
    """
    if len(pareto_front) <= n:
        return pareto_front
    
    representatives = []
    
    # Add corner solutions (best in each objective)
    for obj in objectives:
        best_solution = min(pareto_front, key=lambda x: x[obj])
        if best_solution not in representatives:
            representatives.append(best_solution)
    
    # Fill remaining slots with uniformly distributed solutions
    remaining_slots = n - len(representatives)
    if remaining_slots > 0:
        remaining_solutions = [s for s in pareto_front if s not in representatives]
        
        # Sort by first objective and select evenly spaced
        sorted_remaining = sorted(remaining_solutions, key=lambda x: x[objectives[0]])
        step = len(sorted_remaining) / (remaining_slots + 1)
        
        for i in range(remaining_slots):
            idx = int((i + 1) * step)
            if idx < len(sorted_remaining):
                representatives.append(sorted_remaining[idx])
    
    return representatives


def compute_quality_metrics(pareto_front: List[Dict[str, float]],
                            reference_point: Dict[str, float] = None,
                            objectives: List[str] = ['cost', 'co2', 'time']) -> Dict[str, Any]:
    """
    Compute comprehensive quality metrics for Pareto front.
    
    Args:
        pareto_front: List of non-dominated solutions
        reference_point: Reference point for hypervolume (optional)
        objectives: List of objective keys
        
    Returns:
        Dictionary with quality metrics
    """
    if not pareto_front:
        return {
            'size': 0,
            'hypervolume': 0.0,
            'spacing': 0.0,
            'ranges': {}
        }
    
    # Compute ranges for each objective
    ranges = {}
    for obj in objectives:
        values = [s[obj] for s in pareto_front]
        ranges[obj] = {
            'min': min(values),
            'max': max(values),
            'mean': np.mean(values),
            'std': np.std(values)
        }
    
    # Compute hypervolume if reference point provided
    hypervolume = 0.0
    if reference_point:
        hypervolume = compute_hypervolume(pareto_front, reference_point, objectives)
    
    # Compute spacing metric
    spacing = compute_spacing_metric(pareto_front, objectives)
    
    return {
        'size': len(pareto_front),
        'hypervolume': hypervolume,
        'spacing': spacing,
        'ranges': ranges
    }
