#!/usr/bin/env python3
"""
Test script for the new optimize dispatcher endpoint
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/v1"

def test_optimize_dispatcher():
    """Test the generic /optimize endpoint with different methods"""
    
    # Sample optimization data
    test_data = {
        "warehouses": [
            {
                "id": "W1",
                "name": "Test Warehouse",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "capacity": 1000,
                "operating_cost": 500
            }
        ],
        "customers": [
            {
                "id": "C1", 
                "name": "Test Customer",
                "latitude": 41.8781,
                "longitude": -87.6298,
                "demand": 200,
                "priority": "high"
            }
        ]
    }
    
    methods = ['classical', 'quantum', 'hybrid']
    
    print("🧪 Testing Optimize Dispatcher Endpoint")
    print("=" * 50)
    
    for method in methods:
        print(f"\n📊 Testing {method} optimization...")
        
        payload = {
            "method": method,
            **test_data
        }
        
        try:
            response = requests.post(f"{BASE_URL}/optimize", json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {method.title()} optimization successful!")
                print(f"   Method: {result.get('method', 'unknown')}")
                print(f"   Total Cost: ${result.get('result', {}).get('total_cost', 0):.2f}")
            else:
                print(f"❌ {method.title()} optimization failed")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error for {method}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error for {method}: {e}")
    
    # Test invalid method
    print(f"\n🚫 Testing invalid method...")
    invalid_payload = {"method": "invalid", **test_data}
    
    try:
        response = requests.post(f"{BASE_URL}/optimize", json=invalid_payload, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            error_data = response.json()
            print(f"✅ Invalid method correctly rejected")
            print(f"   Error code: {error_data.get('error', {}).get('code')}")
            print(f"   Message: {error_data.get('error', {}).get('message')}")
        else:
            print(f"❌ Expected 400 but got {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid method: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Dispatcher test completed!")

if __name__ == "__main__":
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    test_optimize_dispatcher()
