# solver/hybrid_integration.py
"""
Hybrid integration: merge classical baseline routing with quantum assignment.

Writes outputs/hybrid.json at project root /outputs/.

Robust imports so it works when run as:
  python3 -m solver.hybrid_integration
or
  python3 solver/hybrid_integration.py
"""
import os
import sys
import json
import math
from pathlib import Path

# Ensure project root is on sys.path so local utils is importable
THIS = Path(__file__).resolve()
PROJECT_ROOT = THIS.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Try import utils from project root; fallback to solver.utils if moved
try:
    from utils import load_datasets, haversine
except Exception:
    from solver.utils import load_datasets, haversine

import pandas as pd

# OR-Tools is only used for heavier routing. We do a simple greedy NN here.
# If OR-Tools is available and you want to replace greedy with VRP, you can.
# from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def load_json_if_exists(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def safe_read_outputs():
    out_dir = PROJECT_ROOT / "outputs"
    baseline_path = out_dir / "baseline.json"
    quantum_path = out_dir / "quantum_assignment.json"
    baseline = load_json_if_exists(str(baseline_path))
    quantum = load_json_if_exists(str(quantum_path))
    return baseline, quantum

def build_baseline_assignment(baseline):
    """
    Normalise baseline into a dict: customer_id -> warehouse_id
    Accepts several baseline file schemas.
    """
    assign = {}
    if not baseline:
        return assign

    # Try common shapes
    # 1) baseline may have 'routes' list with dicts containing 'depot_node' and 'route' (our classical_vrp_export)
    if "routes" in baseline:
        for route in baseline.get("routes", []):
            depot = route.get("depot_node") or route.get("start_depot") or route.get("depot")
            for node in route.get("route", []):
                if isinstance(node, str) and node.upper().startswith("C"):
                    assign[node] = depot
        return assign

    # 2) baseline may have 'vehicles' with start depot + route list
    if "vehicles" in baseline:
        for v in baseline.get("vehicles", []):
            depot = v.get("depot_node") or v.get("start_depot") or v.get("depot")
            # route might be a list of IDs
            for node in v.get("route", []):
                if isinstance(node, str) and node.upper().startswith("C"):
                    assign[node] = depot
        return assign

    # 3) fallback: if baseline contains a mapping directly
    if isinstance(baseline, dict):
        # try to find any mapping-like keys
        if "assignment" in baseline and isinstance(baseline["assignment"], dict):
            return baseline["assignment"].copy()
    return assign

def route_for_warehouse(warehouse_id, warehouse_loc, customer_rows):
    """
    Simple nearest-neighbor route starting/ending at warehouse.
    warehouse_loc: pd.Series with lat/lon columns
    customer_rows: pd.DataFrame of customers assigned to this warehouse (may be empty)
    Returns dict: {warehouse_id, route (list of ids), distance}
    """
    nodes = []
    # node 0 is warehouse
    nodes.append((str(warehouse_id), float(warehouse_loc["lat"]), float(warehouse_loc["lon"])))
    # subsequent nodes are customers: keep order as list
    cust_ids = []
    for _, r in customer_rows.iterrows():
        cid = str(r["customer_id"])
        cust_ids.append(cid)
        nodes.append((cid, float(r["lat"]), float(r["lon"])))

    n = len(nodes)
    if n == 1:
        # no customers
        return {"warehouse_id": warehouse_id, "route": [warehouse_id, warehouse_id], "distance": 0}

    # build distance matrix (integers)
    dist = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i][j] = 0
            else:
                dist[i][j] = int(haversine(nodes[i][1], nodes[i][2], nodes[j][1], nodes[j][2]))

    # greedy nearest neighbor from node 0
    visited = [False] * n
    visited[0] = True
    current = 0
    route_indices = [0]
    while True:
        next_idx = None
        next_d = None
        for j in range(1, n):
            if not visited[j]:
                if next_idx is None or dist[current][j] < next_d:
                    next_idx = j
                    next_d = dist[current][j]
        if next_idx is None:
            break
        visited[next_idx] = True
        route_indices.append(next_idx)
        current = next_idx
    # return to depot
    route_indices.append(0)

    # compute route distance
    total_d = 0
    for a, b in zip(route_indices[:-1], route_indices[1:]):
        total_d += dist[a][b]

    # convert route indices to ids in same ID format as nodes
    route_ids = []
    for idx in route_indices:
        route_ids.append(nodes[idx][0])

    return {"warehouse_id": warehouse_id, "route": route_ids, "distance": int(total_d)}

def repair_capacity(merged_assign, customers_df, warehouses_df):
    """
    Attempt to repair violations where load_by_wh > storage_capacity by reassigning smallest-demand customers
    to nearest feasible warehouses.
    This is greedy and not optimal but works for a PoC.
    """
    # build demand and capacity maps
    demand_map = {str(r["customer_id"]): int(r["demand_units"]) for _, r in customers_df.iterrows()}
    cap_map = {str(r["warehouse_id"]): int(r["storage_capacity"]) for _, r in warehouses_df.iterrows()}

    # init load_by_wh
    load_by_wh = {}
    for c, w in merged_assign.items():
        load_by_wh[w] = load_by_wh.get(w, 0) + demand_map.get(c, 0)

    # coordinate lookup for distance calc
    wh_coords = {str(r["warehouse_id"]): (float(r["lat"]), float(r["lon"])) for _, r in warehouses_df.iterrows()}
    cust_coords = {str(r["customer_id"]): (float(r["lat"]), float(r["lon"])) for _, r in customers_df.iterrows()}

    changed_any = True
    iteration = 0
    while True:
        iteration += 1
        overfull = [w for w, l in load_by_wh.items() if l > cap_map.get(w, 0)]
        if not overfull or iteration > 100:
            break
        for w in overfull:
            # customers assigned to w
            assigned = [c for c, wh in merged_assign.items() if wh == w]
            # sort by demand ascending (we try to move small ones first)
            assigned.sort(key=lambda x: demand_map.get(x, 0))
            moved = False
            for c in assigned:
                # create list of candidate warehouses (excluding current) sorted by distance to customer
                cust_lat, cust_lon = cust_coords.get(c, (None, None))
                if cust_lat is None:
                    continue
                candidates = sorted(
                    [str(r["warehouse_id"]) for _, r in warehouses_df.iterrows() if str(r["warehouse_id"]) != w],
                    key=lambda wh: haversine(wh_coords[w][0], wh_coords[w][1], wh_coords[wh][0], wh_coords[wh][1])
                )
                for wh in candidates:
                    new_load = load_by_wh.get(wh, 0) + demand_map.get(c, 0)
                    if new_load <= cap_map.get(wh, 0):
                        # reassign
                        merged_assign[c] = wh
                        load_by_wh[w] -= demand_map.get(c, 0)
                        load_by_wh[wh] = load_by_wh.get(wh, 0) + demand_map.get(c, 0)
                        moved = True
                        changed_any = True
                        break
                if moved:
                    break
            if not moved:
                # couldn't move any from this warehouse - leave it and move to next to avoid infinite loop
                continue
        if not changed_any:
            break
    return merged_assign

def main():
    out_dir = PROJECT_ROOT / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    baseline, qassign = safe_read_outputs()

    # load datasets
    factories_df, warehouses_df, customers_df, vehicles_df = load_datasets()

    baseline_assign = build_baseline_assignment(baseline)

    # qassign may be None or of shape {"assignment": {customer: warehouse, ...}}
    quantum_map = {}
    if qassign and isinstance(qassign, dict):
        if "assignment" in qassign and isinstance(qassign["assignment"], dict):
            quantum_map = {str(k): str(v) for k, v in qassign["assignment"].items()}
        else:
            # maybe qassign is directly a mapping
            if all(isinstance(v, str) for v in qassign.keys()):
                quantum_map = {str(k): str(v) for k, v in qassign.items()}

    # merged assignment: baseline + quantum override
    merged_assign = baseline_assign.copy()
    merged_assign.update(quantum_map)

    # Ensure all customers have an assignment: if not assigned, give nearest warehouse
    all_customer_ids = [str(r["customer_id"]) for _, r in customers_df.iterrows()]
    wh_coords = {str(r["warehouse_id"]): (float(r["lat"]), float(r["lon"])) for _, r in warehouses_df.iterrows()}
    cust_coords = {str(r["customer_id"]): (float(r["lat"]), float(r["lon"])) for _, r in customers_df.iterrows()}
    for c in all_customer_ids:
        if c not in merged_assign:
            # assign to nearest warehouse
            lat, lon = cust_coords[c]
            nearest_wh = min(wh_coords.keys(), key=lambda wh: haversine(lat, lon, wh_coords[wh][0], wh_coords[wh][1]))
            merged_assign[c] = nearest_wh

    # capacity repair
    merged_assign = repair_capacity(merged_assign, customers_df, warehouses_df)

    # per-warehouse customer lists
    wh_customers = {}
    for c, w in merged_assign.items():
        wh_customers.setdefault(w, []).append(c)

    # build hybrid routes
    hybrid_out = {"vehicles": [], "total_distance": 0, "total_load": 0}
    for w, cust_list in wh_customers.items():
        # find warehouse row
        wh_row = warehouses_df[warehouses_df["warehouse_id"].astype(str) == str(w)]
        if wh_row.shape[0] == 0:
            # skip unknown warehouse (shouldn't happen)
            continue
        wh_row = wh_row.iloc[0]
        cust_rows = customers_df[customers_df["customer_id"].astype(str).isin(cust_list)]
        route_info = route_for_warehouse(w, wh_row, cust_rows)
        hybrid_out["vehicles"].append(route_info)
        hybrid_out["total_distance"] += int(route_info.get("distance", 0))
        hybrid_out["total_load"] += int(cust_rows["demand_units"].astype(int).sum() if cust_rows.size else 0)

    output_path = out_dir / "hybrid.json"
    with open(output_path, "w") as f:
        json.dump(hybrid_out, f, indent=2)

    print(f"Hybrid solution saved to {output_path}")
    return hybrid_out

if __name__ == "__main__":
    main()
