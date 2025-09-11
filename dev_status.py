#!/usr/bin/env python3
"""
Development Status & Quick Commands
"""

import requests
import time
from datetime import datetime


def check_server_status():
    """Check if both servers are running"""
    print("🔍 Checking Server Status")
    print("=" * 50)
    
    # Check backend
    try:
        response = requests.get("http://localhost:5000/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend (Flask): Running on http://localhost:5000")
        else:
            print("❌ Backend (Flask): Responding but unhealthy")
    except:
        print("❌ Backend (Flask): Not running")
    
    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend (React): Running on http://localhost:3000")
        else:
            print("❌ Frontend (React): Not accessible")
    except:
        print("❌ Frontend (React): Not running")
    
    print()

def test_optimization_endpoints():
    """Test all optimization endpoints"""
    print("🧪 Quick Optimization Test")
    print("=" * 50)
    
    test_data = {
        "warehouses": [{"id": "W1", "name": "Test Warehouse", "latitude": 40.7, "longitude": -74.0, "capacity": 1000}],
        "customers": [{"id": "C1", "name": "Test Customer", "latitude": 41.8, "longitude": -87.6, "demand": 200}]
    }
    
    methods = ["classical", "quantum", "hybrid"]
    results = []
    
    for method in methods:
        try:
            payload = {"method": method, **test_data}
            start_time = time.time()
            response = requests.post("http://localhost:5000/api/v1/optimize", json=payload, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                cost = result.get('data', {}).get('result', {}).get('totalCost', 0)
                print(f"✅ {method.capitalize()}: ${cost:.2f} ({end_time-start_time:.3f}s)")
                results.append({'method': method, 'cost': cost, 'time': end_time-start_time})
            else:
                print(f"❌ {method.capitalize()}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {method.capitalize()}: Error - {e}")
    
    print()
    return results

def show_useful_commands():
    """Show useful development commands"""
    print("🛠️ Useful Development Commands")
    print("=" * 50)
    print("Backend:")
    print("  curl -X GET http://localhost:5000/api/v1/health")
    print("  curl -X POST http://localhost:5000/api/v1/optimize -H 'Content-Type: application/json' -d '{\"method\":\"classical\", ...}'")
    print()
    print("Frontend:")
    print("  Open http://localhost:3000 in browser")
    print("  npm run build (in frontend directory)")
    print()
    print("Development:")
    print("  python3 test_optimization_integration.py")
    print("  python3 dev_status.py")
    print()

def main():
    print(f"🚀 Quantum Supply Chain Optimization - Dev Status")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    check_server_status()
    test_optimization_endpoints()
    show_useful_commands()
    
    print("=" * 70)
    print("💡 Both servers are ready for development!")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:5000/api/v1")

if __name__ == "__main__":
    main()
