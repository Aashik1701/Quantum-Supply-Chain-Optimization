"""
Tests for Pareto front computation utilities.
"""

import sys
from pathlib import Path

# Add backend to path
BACKEND_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_ROOT))

from utils.pareto import (
    is_dominated,
    compute_pareto_front,
    compute_hypervolume,
    compute_spacing_metric,
    select_representative_solutions,
    compute_quality_metrics
)


def test_dominance():
    """Test dominance relation between solutions."""
    print("\n=== Testing Dominance ===")
    
    sol_a = {'cost': 100, 'co2': 50, 'time': 10}
    sol_b = {'cost': 90, 'co2': 45, 'time': 9}  # Dominates sol_a
    sol_c = {'cost': 95, 'co2': 55, 'time': 8}  # Neither dominates
    
    # sol_b dominates sol_a
    assert is_dominated(sol_a, sol_b) == True, "sol_b should dominate sol_a"
    print("✓ sol_b dominates sol_a")
    
    # sol_a does not dominate sol_b
    assert is_dominated(sol_b, sol_a) == False, "sol_a should not dominate sol_b"
    print("✓ sol_a does not dominate sol_b")
    
    # Neither dominates the other
    assert is_dominated(sol_a, sol_c) == False, "sol_c should not dominate sol_a"
    assert is_dominated(sol_c, sol_a) == False, "sol_a should not dominate sol_c"
    print("✓ sol_a and sol_c do not dominate each other")
    
    print("✓ All dominance tests passed")


def test_pareto_front_computation():
    """Test Pareto front computation with multiple solutions."""
    print("\n=== Testing Pareto Front Computation ===")
    
    solutions = [
        {'id': '1', 'cost': 100, 'co2': 50, 'time': 10, 'method': 'classical'},
        {'id': '2', 'cost': 90, 'co2': 55, 'time': 12, 'method': 'quantum'},
        {'id': '3', 'cost': 110, 'co2': 45, 'time': 11, 'method': 'hybrid'},
        {'id': '4', 'cost': 95, 'co2': 52, 'time': 9, 'method': 'quantum'},
        {'id': '5', 'cost': 120, 'co2': 60, 'time': 15, 'method': 'classical'},  # Dominated
    ]
    
    pareto, dominated = compute_pareto_front(solutions)
    
    print(f"Total solutions: {len(solutions)}")
    print(f"Pareto front size: {len(pareto)}")
    print(f"Dominated solutions: {len(dominated)}")
    
    # Solution 5 should be dominated (worst in all objectives)
    dominated_ids = [s['id'] for s in dominated]
    assert '5' in dominated_ids, "Solution 5 should be dominated"
    print("✓ Solution 5 correctly identified as dominated")
    
    # Check that all solutions have isDominated flag
    for sol in pareto + dominated:
        assert 'isDominated' in sol, f"Solution {sol['id']} missing isDominated flag"
    print("✓ All solutions have isDominated flag")
    
    # Check that no solution in pareto is dominated
    for sol in pareto:
        assert sol['isDominated'] == False, f"Pareto solution {sol['id']} marked as dominated"
    print("✓ No Pareto solution is marked as dominated")
    
    # Check that all dominated solutions are marked
    for sol in dominated:
        assert sol['isDominated'] == True, f"Dominated solution {sol['id']} not marked"
    print("✓ All dominated solutions are marked")
    
    print("✓ Pareto front computation tests passed")


def test_hypervolume():
    """Test hypervolume calculation for 2D and 3D."""
    print("\n=== Testing Hypervolume ===")
    
    # 2D Pareto front
    pareto_2d = [
        {'cost': 10, 'co2': 20},
        {'cost': 15, 'co2': 15},
        {'cost': 20, 'co2': 10},
    ]
    reference_2d = {'cost': 30, 'co2': 30}
    
    hv_2d = compute_hypervolume(pareto_2d, reference_2d, objectives=['cost', 'co2'])
    print(f"2D Hypervolume: {hv_2d:.2f}")
    assert hv_2d > 0, "2D hypervolume should be positive"
    print("✓ 2D hypervolume computed")
    
    # 3D Pareto front
    pareto_3d = [
        {'cost': 10, 'co2': 20, 'time': 5},
        {'cost': 15, 'co2': 15, 'time': 8},
        {'cost': 20, 'co2': 10, 'time': 10},
    ]
    reference_3d = {'cost': 30, 'co2': 30, 'time': 15}
    
    hv_3d = compute_hypervolume(pareto_3d, reference_3d, objectives=['cost', 'co2', 'time'])
    print(f"3D Hypervolume: {hv_3d:.2f}")
    assert hv_3d > 0, "3D hypervolume should be positive"
    print("✓ 3D hypervolume computed")
    
    print("✓ Hypervolume tests passed")


def test_spacing_metric():
    """Test spacing metric for distribution uniformity."""
    print("\n=== Testing Spacing Metric ===")
    
    # Uniformly distributed Pareto front
    uniform_front = [
        {'cost': 10, 'co2': 30, 'time': 5},
        {'cost': 15, 'co2': 25, 'time': 7},
        {'cost': 20, 'co2': 20, 'time': 9},
        {'cost': 25, 'co2': 15, 'time': 11},
        {'cost': 30, 'co2': 10, 'time': 13},
    ]
    
    spacing_uniform = compute_spacing_metric(uniform_front)
    print(f"Uniform spacing: {spacing_uniform:.4f}")
    
    # Clustered Pareto front
    clustered_front = [
        {'cost': 10, 'co2': 30, 'time': 5},
        {'cost': 11, 'co2': 29, 'time': 5.5},
        {'cost': 12, 'co2': 28, 'time': 6},
        {'cost': 30, 'co2': 10, 'time': 13},
    ]
    
    spacing_clustered = compute_spacing_metric(clustered_front)
    print(f"Clustered spacing: {spacing_clustered:.4f}")
    
    # Uniform should have lower spacing (better)
    assert spacing_uniform < spacing_clustered, "Uniform front should have lower spacing"
    print("✓ Spacing metric correctly distinguishes distribution quality")
    
    print("✓ Spacing metric tests passed")


def test_representative_selection():
    """Test selection of representative solutions."""
    print("\n=== Testing Representative Selection ===")
    
    large_front = [
        {'id': f's{i}', 'cost': 10 + i*2, 'co2': 30 - i*2, 'time': 5 + i}
        for i in range(20)
    ]
    
    representatives = select_representative_solutions(large_front, n=5)
    
    print(f"Selected {len(representatives)} from {len(large_front)} solutions")
    assert len(representatives) == 5, "Should select exactly 5 representatives"
    print("✓ Correct number of representatives selected")
    
    # Check that corner solutions are included
    best_cost = min(large_front, key=lambda x: x['cost'])
    best_co2 = min(large_front, key=lambda x: x['co2'])
    best_time = min(large_front, key=lambda x: x['time'])
    
    assert best_cost in representatives, "Best cost solution should be included"
    assert best_co2 in representatives, "Best CO2 solution should be included"
    assert best_time in representatives, "Best time solution should be included"
    print("✓ Corner solutions included in representatives")
    
    print("✓ Representative selection tests passed")


def test_quality_metrics():
    """Test comprehensive quality metrics computation."""
    print("\n=== Testing Quality Metrics ===")
    
    pareto_front = [
        {'cost': 100, 'co2': 50, 'time': 10},
        {'cost': 90, 'co2': 55, 'time': 12},
        {'cost': 110, 'co2': 45, 'time': 11},
        {'cost': 95, 'co2': 52, 'time': 9},
    ]
    
    reference = {'cost': 150, 'co2': 80, 'time': 20}
    
    metrics = compute_quality_metrics(pareto_front, reference)
    
    print(f"Quality Metrics:")
    print(f"  Size: {metrics['size']}")
    print(f"  Hypervolume: {metrics['hypervolume']:.2f}")
    print(f"  Spacing: {metrics['spacing']:.4f}")
    
    assert metrics['size'] == len(pareto_front), "Size should match front size"
    assert metrics['hypervolume'] > 0, "Hypervolume should be positive"
    assert 'ranges' in metrics, "Should include objective ranges"
    
    # Check ranges
    for obj in ['cost', 'co2', 'time']:
        assert obj in metrics['ranges'], f"Should have range for {obj}"
        assert 'min' in metrics['ranges'][obj], f"Should have min for {obj}"
        assert 'max' in metrics['ranges'][obj], f"Should have max for {obj}"
    
    print("✓ All quality metrics computed correctly")
    print("✓ Quality metrics tests passed")


def test_empty_pareto_front():
    """Test handling of empty Pareto front."""
    print("\n=== Testing Empty Pareto Front ===")
    
    pareto, dominated = compute_pareto_front([])
    assert len(pareto) == 0, "Empty input should yield empty Pareto front"
    assert len(dominated) == 0, "Empty input should yield no dominated solutions"
    print("✓ Empty Pareto front handled correctly")
    
    metrics = compute_quality_metrics([])
    assert metrics['size'] == 0, "Empty front should have size 0"
    assert metrics['hypervolume'] == 0.0, "Empty front should have 0 hypervolume"
    print("✓ Empty front metrics computed correctly")
    
    print("✓ Empty Pareto front tests passed")


def run_all_tests():
    """Run all Pareto utility tests."""
    print("=" * 60)
    print("Running Pareto Utility Tests")
    print("=" * 60)
    
    try:
        test_dominance()
        test_pareto_front_computation()
        test_hypervolume()
        test_spacing_metric()
        test_representative_selection()
        test_quality_metrics()
        test_empty_pareto_front()
        
        print("\n" + "=" * 60)
        print("✅ ALL PARETO TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise


if __name__ == '__main__':
    run_all_tests()
