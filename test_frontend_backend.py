#!/usr/bin/env python3
"""
Test Frontend-Backend Communication
Tests all optimization methods with sample data
"""

import requests
import json
import sys

BASE_URL = 'http://127.0.0.1:5000/api/v1'

# Sample data
TEST_DATA = {
    "warehouses": [
        {"id": "W1", "name": "Warehouse Sao Paulo", "latitude": -23.5505, "longitude": -46.6333, "capacity": 2461},
        {"id": "W3", "name": "Warehouse New York", "latitude": 40.7128, "longitude": -74.006, "capacity": 2809},
        {"id": "W7", "name": "Warehouse Mumbai", "latitude": 19.076, "longitude": 72.8777, "capacity": 2529}
    ],
    "customers": [
        {"id": "C1", "name": "Customer Mumbai", "latitude": 19.076, "longitude": 72.8777, "demand": 152},
        {"id": "C2", "name": "Customer Berlin", "latitude": 52.52, "longitude": 13.405, "demand": 114},
        {"id": "C4", "name": "Customer New York", "latitude": 40.7128, "longitude": -74.006, "demand": 56},
        {"id": "C5", "name": "Customer Shanghai", "latitude": 31.2304, "longitude": 121.4737, "demand": 133},
        {"id": "C6", "name": "Customer Sydney", "latitude": -33.8688, "longitude": 151.2093, "demand": 110}
    ],
    "routes": []
}


def test_health():
    """Test API health endpoint"""
    print("🔍 Testing API Health...")
    try:
        resp = requests.get(f'{BASE_URL}/health', timeout=5)
        if resp.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        return False


def test_classical_optimization():
    """Test classical optimization"""
    print("\n🔍 Testing Classical Optimization...")
    payload = {
        "method": "classical",
        "parameters": {},
        "data": TEST_DATA
    }
    
    try:
        resp = requests.post(f'{BASE_URL}/optimize', json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            data = result.get('data', {}).get('result', {})
            print("✅ Classical Optimization successful")
            print(f"   Total Cost: ${data.get('totalCost', 0):.2f}")
            print(f"   Total CO2: {data.get('totalCo2', 0):.2f} kg")
            print(f"   Routes: {data.get('routesUsed', 0)}")
            print(f"   Assignments: {len(data.get('assignments', []))}")
            return True
        else:
            print(f"❌ Classical optimization failed: {resp.status_code}")
            print(f"   Response: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_validation():
    """Test data validation endpoint"""
    print("\n🔍 Testing Data Validation...")
    try:
        resp = requests.post(f'{BASE_URL}/data/validate', json=TEST_DATA, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            data = result.get('data', {})
            print(f"✅ Validation successful")
            print(f"   Valid: {data.get('valid', False)}")
            print(f"   Errors: {len(data.get('errors', []))}")
            print(f"   Warnings: {len(data.get('warnings', []))}")
            return True
        else:
            print(f"❌ Validation failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_dashboard():
    """Test dashboard data endpoint"""
    print("\n🔍 Testing Dashboard Endpoint...")
    try:
        resp = requests.get(f'{BASE_URL}/dashboard', timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            data = result.get('data', {})
            print("✅ Dashboard endpoint working")
            print(f"   Jobs: {len(data.get('recentJobs', []))}")
            print(f"   Metrics available: {list(data.get('metrics', {}).keys())}")
            return True
        else:
            print(f"❌ Dashboard failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Frontend-Backend Communication Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Data Validation", test_validation),
        ("Classical Optimization", test_classical_optimization),
        ("Dashboard", test_dashboard)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Frontend and Backend are communicating properly.")
        print("\n📝 Next Steps:")
        print("   1. Open browser: http://localhost:3000")
        print("   2. Navigate to Optimization page")
        print("   3. Upload data or use sample data")
        print("   4. Run optimization and view results")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
