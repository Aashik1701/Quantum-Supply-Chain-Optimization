# classical_vrp.py
import pandas as pd
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from utils import load_datasets, haversine

# -------------------------
# Load datasets
# -------------------------
factories, warehouses, customers, vehicles = load_datasets()

# Build a combined locations DataFrame (warehouses first, then customers)
locations = pd.concat([warehouses, customers], ignore_index=True)

# Build node id list in the same order as locations
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

# capacities: per vehicle
capacities = vehicles['capacity_units'].astype(int).tolist()
# 👇 Force denominator to 10000 for load reporting
capacity_for_reporting = 10000
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
# RoutingIndexManager and RoutingModel
# -------------------------
manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, starts, ends)
routing = pywrapcp.RoutingModel(manager)

# -------------------------
# Distance callback
# -------------------------
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# -------------------------
# Capacity constraint
# -------------------------
def demand_callback(from_index):
    node = manager.IndexToNode(from_index)
    return demands[node]

demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index, 0, capacities, True, 'Capacity'
)

# -------------------------
# Distance dimension
# -------------------------
routing.AddDimension(
    transit_callback_index,
    0,
    10**9,
    True,
    'Distance'
)

# -------------------------
# Solver parameters
# -------------------------
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.time_limit.seconds = 120
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH

# -------------------------
# Print solution
# -------------------------
def print_solution(manager, routing, solution):
    total_distance = 0
    served_load = 0

    for vehicle_id in range(routing.vehicles()):
        index = routing.Start(vehicle_id)
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

        # add depot at end
        route_plan.append(names[manager.IndexToNode(index)])
        print(f"Vehicle {vehicle_id} | depot_node {manager.IndexToNode(routing.Start(vehicle_id))} ({names[manager.IndexToNode(routing.Start(vehicle_id))]})")
        print(f"  Route: {route_plan}")
        print(f"  Distance (cost units): {route_distance}, Load: {route_load}\n")

        total_distance += route_distance
        served_load += route_load

    print("✅ VRP Solution Found!")
    print(f"Total distance (sum over vehicles): {total_distance}")
    print(f"Total load served: {served_load} / {capacity_for_reporting}")
    print(f"Vehicle utilization: {served_load/capacity_for_reporting*100:.2f}%")

# -------------------------
# Run solver
# -------------------------
if __name__ == "__main__":
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(manager, routing, solution)
    else:
        print("No solution found!")
