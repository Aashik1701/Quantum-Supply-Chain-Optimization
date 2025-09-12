# data_utils.py
"""
Utility functions for the quantum supply chain optimization algorithms.
This file provides data loading and distance calculation functions.
"""

import os
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def load_datasets():
    """
    Load all datasets from the data directory.
    Returns: factories, warehouses, customers, vehicles
    """
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(backend_dir)
    data_dir = os.path.join(project_root, 'data')
    
    # Load datasets
    try:
        # Try csvdata directory first (new format)
        csvdata_dir = os.path.join(data_dir, 'csvdata')
        if os.path.exists(csvdata_dir):
            warehouses = pd.read_csv(
                os.path.join(csvdata_dir, 'warehouses.csv'))
            customers = pd.read_csv(
                os.path.join(csvdata_dir, 'customers.csv'))
        else:
            # Fallback to data directory
            warehouses = pd.read_csv(
                os.path.join(data_dir, 'warehouses.csv'))
            customers = pd.read_csv(
                os.path.join(data_dir, 'customers.csv'))
        
        # Load other files from data directory
        factories = pd.read_csv(os.path.join(data_dir, 'factories.csv'))
        vehicles = pd.read_csv(os.path.join(data_dir, 'vehicles.csv'))
        
        # Normalize column names for consistency
        # Warehouses
        if 'warehouse_id' in warehouses.columns:
            warehouses['warehouse_id'] = warehouses['warehouse_id']
        elif 'id' in warehouses.columns:
            warehouses['warehouse_id'] = warehouses['id']
            
        if 'storage_capacity' in warehouses.columns:
            warehouses['capacity'] = warehouses['storage_capacity']
        elif ('capacity' not in warehouses.columns and
              'storage_capacity' in warehouses.columns):
            warehouses['capacity'] = warehouses['storage_capacity']
            
        # Normalize lat/lon columns for warehouses
        if 'latitude' in warehouses.columns:
            warehouses['lat'] = warehouses['latitude']
        if 'longitude' in warehouses.columns:
            warehouses['lon'] = warehouses['longitude']

        # Customers
        if 'customer_id' in customers.columns:
            customers['customer_id'] = customers['customer_id']
        elif 'id' in customers.columns:
            customers['customer_id'] = customers['id']

        if 'demand' in customers.columns:
            customers['demand_units'] = customers['demand']
        elif ('demand_units' not in customers.columns and
              'demand' in customers.columns):
            customers['demand_units'] = customers['demand']
            
        # Normalize lat/lon columns for customers
        if 'latitude' in customers.columns:
            customers['lat'] = customers['latitude']
        if 'longitude' in customers.columns:
            customers['lon'] = customers['longitude']

        print(f"Loaded {len(factories)} factories, "
              f"{len(warehouses)} warehouses, "
              f"{len(customers)} customers, {len(vehicles)} vehicles")
        return factories, warehouses, customers, vehicles
        
    except Exception as e:
        print(f"Error loading datasets: {e}")
        # Return empty DataFrames with expected columns
        factories = pd.DataFrame(columns=[
            'factory_id', 'country', 'city', 'lat', 'lon',
            'daily_production_capacity'
        ])
        warehouses = pd.DataFrame(columns=[
            'warehouse_id', 'name', 'city', 'country', 'lat', 'lon',
            'capacity'
        ])
        customers = pd.DataFrame(columns=[
            'customer_id', 'name', 'city', 'country', 'latitude',
            'longitude', 'demand_units'
        ])
        vehicles = pd.DataFrame(columns=[
            'vehicle_id', 'mode', 'capacity_units', 'cost_per_km_usd',
            'co2_g_per_km', 'speed_kmph'
        ])
        return factories, warehouses, customers, vehicles


def calculate_distance_matrix(locations1, locations2=None):
    """
    Calculate distance matrix between two sets of locations.
    If locations2 is None, calculate distance matrix within locations1.
    """
    if locations2 is None:
        locations2 = locations1
    
    n1 = len(locations1)
    n2 = len(locations2)
    
    distance_matrix = np.zeros((n1, n2))
    
    for i in range(n1):
        for j in range(n2):
            lat1, lon1 = locations1.iloc[i]['lat'], locations1.iloc[i]['lon']
            lat2, lon2 = locations2.iloc[j]['lat'], locations2.iloc[j]['lon']
            distance_matrix[i][j] = haversine(lat1, lon1, lat2, lon2)
    
    return distance_matrix


if __name__ == "__main__":
    # Test the functions
    factories, warehouses, customers, vehicles = load_datasets()
    print("Datasets loaded successfully!")
    print(f"Warehouses shape: {warehouses.shape}")
    print(f"Customers shape: {customers.shape}")
    print(f"Vehicles shape: {vehicles.shape}")
    print(f"Factories shape: {factories.shape}")
