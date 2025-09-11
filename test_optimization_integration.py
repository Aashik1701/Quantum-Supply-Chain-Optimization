#!/usr/bin/env python3
"""
Integration test for the optimize dispatcher endpoint
Tests all optimization methods through the new unified endpoint
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/v1"

def test_dispatcher_integration():
    """Test complete optimization workflow"""
    
    print("🧪 Testing Optimize Dispatcher Integration")
    print("=" * 60)
    
    # Test data with proper validation structure
    test_data = {
        "warehouses": [
            {
                "id": "W1",
                "name": "New York Hub",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "capacity": 1000,
                "operating_cost": 500
            },
            {
                "id": "W2", 
                "name": "Chicago Center",
                "latitude": 41.8781,
                "longitude": -87.6298,
                "capacity": 800,
                "operating_cost": 400
            }
        ],
        "customers": [
            {
                "id": "C1",
                "name": "Boston Store",
                "latitude": 42.3601,
                "longitude": -71.0589,
                "demand": 300,
                "priority": "high"
            },
            {
                "id": "C2",
                "name": "Miami Outlet", 
                "latitude": 25.7617,
                "longitude": -80.1918,
                "demand": 250,
                "priority": "medium"
            }
        ]
    }
    
    methods = ["classical", "quantum", "hybrid"]
    results = {}
    
    for method in methods:
        print(f"\n📊 Testing {method.upper()} optimization...")
        
        payload = {
            "method": method,
            **test_data
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/optimize", json=payload, timeout=30)
            elapsed = time.time() - start_time
            
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {elapsed:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract key metrics
                result_data = result.get('data', {}).get('result', {})
                total_cost = result_data.get('totalCost', 0)
                total_co2 = result_data.get('totalCo2', 0)
                routes_used = result_data.get('routesUsed', 0)
                
                print(f"   ✅ Success!")
                print(f"   Total Cost: ${total_cost:.2f}")
                print(f"   Total CO2: {total_co2:.2f} kg")
                print(f"   Routes: {routes_used}")
                
                results[method] = {
                    'cost': total_cost,
                    'co2': total_co2,
                    'routes': routes_used,
                    'time': elapsed
                }
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                error_data = response.json()
                print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown')}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 30s")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary comparison
    if results:
        print(f"\n📈 OPTIMIZATION COMPARISON")
        print("-" * 60)
        print(f"{'Method':<10} {'Cost ($)':<12} {'CO2 (kg)':<12} {'Routes':<8} {'Time (s)':<10}")
        print("-" * 60)
        
        for method, data in results.items():
            print(f"{method.capitalize():<10} ${data['cost']:<11.2f} {data['co2']:<11.2f} {data['routes']:<8} {data['time']:<10.2f}")
    
    # Test error handling
    print(f"\n🚫 Testing Error Handling...")
    
    # Invalid method
    try:
        response = requests.post(f"{BASE_URL}/optimize", 
            json={"method": "invalid", **test_data}, timeout=5)
        if response.status_code == 400:
            error = response.json()
            print(f"   ✅ Invalid method correctly rejected")
            print(f"   Error Code: {error.get('error', {}).get('code')}")
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid method: {e}")
    
    # Missing data
    try:
        response = requests.post(f"{BASE_URL}/optimize", 
            json={"method": "classical"}, timeout=5)
        if response.status_code == 400:
            print(f"   ✅ Missing data correctly rejected")
        else:
            print(f"   ❌ Expected 400 for missing data, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing missing data: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Integration test completed!")
    
    return len(results) == 3  # Success if all 3 methods worked

if __name__ == "__main__":
    success = test_dispatcher_integration()
    exit(0 if success else 1)
