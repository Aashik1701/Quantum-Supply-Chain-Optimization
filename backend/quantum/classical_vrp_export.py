# core/classical_vrp_export.py
"""
Robust classical VRP exporter.
Works when run as:
  python3 core/classical_vrp_export.py
or as module:
  python3 -m core.classical_vrp_export

It ensures the project root is on sys.path so imports like `import utils`
resolve to the local utils.py (avoiding conflicts with a system 'utils' package).
"""

import os
import sys
import json
import pandas as pd
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# -------------------------
# Ensure project root is on sys.path so local modules import reliably
# -------------------------
# This file lives at PROJECT_ROOT/core/classical_vrp_export.py
THIS_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(THIS_FILE))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now import local utils (project-root utils.py)
try:
    # prefer local module
    from utils import load_datasets, haversine
except Exception as e:
    # fallback to core.utils if you moved utils into core/
    try:
        from core.utils import load_datasets, haversine
    except Exception:
        raise ImportError(f"Couldn't import local utils.py (tried project-root utils and core.utils). Error: {e}")

# -------------------------
# Load datasets
# -------------------------
factories, warehouses, customers, vehicles = load_datasets()

# Build combined locations (warehouses first, then customers)
locations = pd.concat([warehouses, customers], ignore_index=True)

# Node id list (names)
names = []
names.extend(warehouses['warehouse_id'].astype(str).tolist())
names.extend(customers['customer_id'].astype(str).tolist())

# -------------------------
# Build distance matrix
# -------------------------
n = len(locations)
distance_matrix = [[0] * n for _ in range(n)]
for i in range(n):
    for j in range(n):
        distance_matrix[i][j] = int(haversine(
            locations.iloc[i]['lat'], locations.iloc[i]['lon'],
            locations.iloc[j]['lat'], locations.iloc[j]['lon']
        ))

# -------------------------
# Demands and capacities
# -------------------------
demands = [0] * len(warehouses) + customers['demand_units'].astype(int).tolist()
total_demand = sum(demands)

capacities = vehicles['capacity_units'].astype(int).tolist()
capacity_for_reporting = 10000  # user requested denominator
total_capacity = sum(capacities)

print(f"Num nodes: {n} (warehouses: {len(warehouses)}, customers: {len(customers)})")
print(f"Total customer demand: {total_demand}")
print(f"Vehicle capacities: {capacities}  (total {total_capacity})")

# -------------------------
# Multi-depot setup
# -------------------------
depots = list(range(len(warehouses)))
num_vehicles = len(vehicles)

starts = [depots[i % len(depots)] for i in range(num_vehicles)]
ends = starts.copy()

print(f"Depots (node indices): {depots}")
print(f"Vehicle starts (node indices): {starts}")

# -------------------------
# Routing model
# -------------------------
manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, starts, ends)
routing = pywrapcp.RoutingModel(manager)

# Distance callback
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Capacity constraint
def demand_callback(from_index):
    node = manager.IndexToNode(from_index)
    return demands[node]

demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index, 0, capacities, True, 'Capacity'
)

# Distance dimension (to measure route lengths)
routing.AddDimension(
    transit_callback_index,
    0,
    10**9,
    True,
    'Distance'
)

# Solver parameters
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.time_limit.seconds = 120
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH

# -------------------------
# Solution printing + JSON assembly
# -------------------------
def print_solution(manager, routing, solution):
    total_distance = 0
    served_load = 0
    all_routes = []

    for vehicle_id in range(routing.vehicles()):
        index = routing.Start(vehicle_id)
        # skip unused vehicles
        if routing.IsEnd(solution.Value(routing.NextVar(index))):
            continue

        route_distance = 0
        route_load = 0
        route_plan = []

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            if node_index < len(demands):
                route_load += demands[node_index]
            route_plan.append(names[node_index])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

        # append final depot
        route_plan.append(names[manager.IndexToNode(index)])

        print(f"Vehicle {vehicle_id} | depot_node {manager.IndexToNode(routing.Start(vehicle_id))} ({names[manager.IndexToNode(routing.Start(vehicle_id))]})")
        print(f"  Route: {route_plan}")
        print(f"  Distance (cost units): {route_distance}, Load: {route_load}\n")

        total_distance += route_distance
        served_load += route_load
        all_routes.append({
            "vehicle_id": int(vehicle_id),
            "depot_node": names[manager.IndexToNode(routing.Start(vehicle_id))],
            "route": route_plan,
            "distance": int(route_distance),
            "load": int(route_load)
        })

    print("✅ VRP Solution Found!")
    print(f"Total distance (sum over vehicles): {total_distance}")
    print(f"Total load served: {served_load} / {capacity_for_reporting}")
    print(f"Vehicle utilization: {served_load/capacity_for_reporting*100:.2f}%")

    return all_routes, int(total_distance), int(served_load)

# -------------------------
# Run & export to project-root outputs/
# -------------------------
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)
OUTPUT_BASELINE = os.path.join(OUTPUTS_DIR, "baseline.json")

if __name__ == "__main__":
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        routes, tot_dist, tot_load = print_solution(manager, routing, solution)

        output_data = {
            "num_nodes": n,
            "vehicle_capacities": capacities,
            "routes": routes,
            "total_distance": tot_dist,
            "total_load": tot_load
        }

        with open(OUTPUT_BASELINE, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"✅ Baseline solution saved to {OUTPUT_BASELINE}")
    else:
        print("No solution found!")
