"""
Classical linear programming solver for supply chain optimization
"""

import numpy as np
from typing import Dict, List, Any
import time

# Classical optimization imports
try:
    from ortools.linear_solver import pywraplp
    import pulp
    ORTOOLS_AVAILABLE = True
    PULP_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    PULP_AVAILABLE = False
    print("Warning: OR-Tools or PuLP not available. Using basic optimization.")


class ClassicalOptimizer:
    """Classical optimization using Linear Programming"""
    
    def __init__(self, solver: str = 'SCIP'):
        self.solver_name = solver
        self.solver = None
        
        if ORTOOLS_AVAILABLE:
            # Use OR-Tools as primary solver
            self.solver = pywraplp.Solver.CreateSolver(solver)
        elif PULP_AVAILABLE:
            # Fallback to PuLP
            self.solver = pulp.LpProblem("SupplyChainOptimization", pulp.LpMinimize)
    
    def optimize(self, warehouses: List[Dict], customers: List[Dict], 
                distance_matrix: np.ndarray, **kwargs) -> Dict[str, Any]:
        """
        Run classical linear programming optimization
        
        Args:
            warehouses: List of warehouse data
            customers: List of customer data
            distance_matrix: Distance matrix between warehouses and customers
            **kwargs: Additional optimization parameters
            
        Returns:
            Optimization result dictionary
        """
        start_time = time.time()
        
        if ORTOOLS_AVAILABLE:
            result = self._optimize_with_ortools(warehouses, customers, distance_matrix)
        elif PULP_AVAILABLE:
            result = self._optimize_with_pulp(warehouses, customers, distance_matrix)
        else:
            result = self._optimize_greedy(warehouses, customers, distance_matrix)
        
        result['optimization_time'] = time.time() - start_time
        result['solver_used'] = self.solver_name
        
        return result
    
    def _optimize_with_ortools(self, warehouses: List[Dict], customers: List[Dict], 
                              distance_matrix: np.ndarray) -> Dict[str, Any]:
        """Optimize using Google OR-Tools"""
        n_warehouses = len(warehouses)
        n_customers = len(customers)
        
        # Create variables: x[i][j] = 1 if warehouse i serves customer j
        x = {}
        for i in range(n_warehouses):
            for j in range(n_customers):
                x[i, j] = self.solver.BoolVar(f'x_{i}_{j}')
        
        # Objective: minimize total cost
        objective_terms = []
        for i in range(n_warehouses):
            for j in range(n_customers):
                cost = distance_matrix[i][j] * 1.0  # Cost per km
                objective_terms.append(cost * x[i, j])
        
        self.solver.Minimize(sum(objective_terms))
        
        # Constraints
        # 1. Each customer must be served by exactly one warehouse
        for j in range(n_customers):
            constraint = self.solver.Constraint(1, 1)
            for i in range(n_warehouses):
                constraint.SetCoefficient(x[i, j], 1)
        
        # 2. Warehouse capacity constraints
        for i in range(n_warehouses):
            capacity = warehouses[i].get('capacity', 1000)
            constraint = self.solver.Constraint(0, capacity)
            for j in range(n_customers):
                demand = customers[j].get('demand', 100)
                constraint.SetCoefficient(x[i, j], demand)
        
        # Solve
        status = self.solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL:
            return self._process_ortools_solution(
                x, warehouses, customers, distance_matrix, n_warehouses, n_customers
            )
        else:
            # Fallback to greedy if no optimal solution
            return self._optimize_greedy(warehouses, customers, distance_matrix)
    
    def _optimize_with_pulp(self, warehouses: List[Dict], customers: List[Dict], 
                           distance_matrix: np.ndarray) -> Dict[str, Any]:
        """Optimize using PuLP"""
        n_warehouses = len(warehouses)
        n_customers = len(customers)
        
        # Create problem
        prob = pulp.LpProblem("SupplyChainOptimization", pulp.LpMinimize)
        
        # Create variables
        x = pulp.LpVariable.dicts("x",
                                 [(i, j) for i in range(n_warehouses) 
                                  for j in range(n_customers)],
                                 cat='Binary')
        
        # Objective function
        prob += pulp.lpSum([distance_matrix[i][j] * 1.0 * x[i, j] 
                           for i in range(n_warehouses) 
                           for j in range(n_customers)])
        
        # Constraints
        # Each customer served exactly once
        for j in range(n_customers):
            prob += pulp.lpSum([x[i, j] for i in range(n_warehouses)]) == 1
        
        # Warehouse capacity constraints
        for i in range(n_warehouses):
            capacity = warehouses[i].get('capacity', 1000)
            prob += pulp.lpSum([customers[j].get('demand', 100) * x[i, j] 
                               for j in range(n_customers)]) <= capacity
        
        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        if prob.status == pulp.LpStatusOptimal:
            return self._process_pulp_solution(
                x, warehouses, customers, distance_matrix, n_warehouses, n_customers
            )
        else:
            return self._optimize_greedy(warehouses, customers, distance_matrix)
    
    def _optimize_greedy(self, warehouses: List[Dict], customers: List[Dict], 
                        distance_matrix: np.ndarray) -> Dict[str, Any]:
        """Simple greedy optimization as fallback"""
        assignments = []
        routes = []
        total_cost = 0
        total_co2 = 0
        total_time = 0
        
        # Track warehouse utilization
        warehouse_used = {w['id']: 0 for w in warehouses}
        
        # Assign each customer to the nearest available warehouse
        for j, customer in enumerate(customers):
            distances = distance_matrix[:, j]
            demand = customer.get('demand', 100)
            
            # Find best available warehouse
            best_warehouse_idx = None
            best_distance = float('inf')
            
            for i, warehouse in enumerate(warehouses):
                if warehouse_used[warehouse['id']] + demand <= warehouse.get('capacity', 1000):
                    if distances[i] < best_distance:
                        best_distance = distances[i]
                        best_warehouse_idx = i
            
            # If no warehouse has capacity, use the nearest one anyway
            if best_warehouse_idx is None:
                best_warehouse_idx = np.argmin(distances)
            
            warehouse = warehouses[best_warehouse_idx]
            warehouse_used[warehouse['id']] += demand
            
            distance = distances[best_warehouse_idx]
            cost = distance * 1.0  # Cost per km
            co2 = distance * 0.4   # CO2 per km
            time_hours = distance / 80  # Speed 80 km/h
            
            assignment = {
                'warehouse_id': warehouse['id'],
                'customer_id': customer['id'],
                'distance_km': distance,
                'cost': cost,
                'co2': co2,
                'delivery_time_hours': time_hours,
                'demand': demand
            }
            assignments.append(assignment)
            
            route = {
                'id': f"{warehouse['id']}-{customer['id']}",
                'warehouse_id': warehouse['id'],
                'customer_id': customer['id'],
                'distance_km': distance,
                'total_cost': cost,
                'total_co2': co2,
                'delivery_time_hours': time_hours
            }
            routes.append(route)
            
            total_cost += cost
            total_co2 += co2
            total_time += time_hours
        
        avg_delivery_time = total_time / len(assignments) if assignments else 0
        
        return {
            'total_cost': total_cost,
            'total_co2': total_co2,
            'avg_delivery_time': avg_delivery_time,
            'routes_used': len(routes),
            'routes': routes,
            'assignments': assignments,
            'iterations': 1,
            'convergence': True,
            'warehouse_utilization': warehouse_used
        }
    
    def _process_ortools_solution(self, x, warehouses: List[Dict], customers: List[Dict], 
                                 distance_matrix: np.ndarray, n_warehouses: int, 
                                 n_customers: int) -> Dict[str, Any]:
        """Process OR-Tools solution"""
        assignments = []
        routes = []
        total_cost = 0
        total_co2 = 0
        total_time = 0
        
        for i in range(n_warehouses):
            for j in range(n_customers):
                if x[i, j].solution_value() > 0.5:  # Binary variable is 1
                    warehouse = warehouses[i]
                    customer = customers[j]
                    distance = distance_matrix[i][j]
                    cost = distance * 1.0
                    co2 = distance * 0.4
                    time_hours = distance / 80
                    
                    assignment = {
                        'warehouse_id': warehouse['id'],
                        'customer_id': customer['id'],
                        'distance_km': distance,
                        'cost': cost,
                        'co2': co2,
                        'delivery_time_hours': time_hours,
                        'demand': customer.get('demand', 100)
                    }
                    assignments.append(assignment)
                    
                    route = {
                        'id': f"{warehouse['id']}-{customer['id']}",
                        'warehouse_id': warehouse['id'],
                        'customer_id': customer['id'],
                        'distance_km': distance,
                        'total_cost': cost,
                        'total_co2': co2,
                        'delivery_time_hours': time_hours
                    }
                    routes.append(route)
                    
                    total_cost += cost
                    total_co2 += co2
                    total_time += time_hours
        
        avg_delivery_time = total_time / len(assignments) if assignments else 0
        
        return {
            'total_cost': total_cost,
            'total_co2': total_co2,
            'avg_delivery_time': avg_delivery_time,
            'routes_used': len(routes),
            'routes': routes,
            'assignments': assignments,
            'iterations': self.solver.iterations(),
            'convergence': True,
            'optimal_value': self.solver.Objective().Value()
        }
    
    def _process_pulp_solution(self, x, warehouses: List[Dict], customers: List[Dict], 
                              distance_matrix: np.ndarray, n_warehouses: int, 
                              n_customers: int) -> Dict[str, Any]:
        """Process PuLP solution"""
        assignments = []
        routes = []
        total_cost = 0
        total_co2 = 0
        total_time = 0
        
        for i in range(n_warehouses):
            for j in range(n_customers):
                if pulp.value(x[i, j]) > 0.5:  # Binary variable is 1
                    warehouse = warehouses[i]
                    customer = customers[j]
                    distance = distance_matrix[i][j]
                    cost = distance * 1.0
                    co2 = distance * 0.4
                    time_hours = distance / 80
                    
                    assignment = {
                        'warehouse_id': warehouse['id'],
                        'customer_id': customer['id'],
                        'distance_km': distance,
                        'cost': cost,
                        'co2': co2,
                        'delivery_time_hours': time_hours,
                        'demand': customer.get('demand', 100)
                    }
                    assignments.append(assignment)
                    
                    route = {
                        'id': f"{warehouse['id']}-{customer['id']}",
                        'warehouse_id': warehouse['id'],
                        'customer_id': customer['id'],
                        'distance_km': distance,
                        'total_cost': cost,
                        'total_co2': co2,
                        'delivery_time_hours': time_hours
                    }
                    routes.append(route)
                    
                    total_cost += cost
                    total_co2 += co2
                    total_time += time_hours
        
        avg_delivery_time = total_time / len(assignments) if assignments else 0
        
        return {
            'total_cost': total_cost,
            'total_co2': total_co2,
            'avg_delivery_time': avg_delivery_time,
            'routes_used': len(routes),
            'routes': routes,
            'assignments': assignments,
            'iterations': 1,
            'convergence': True
        }
