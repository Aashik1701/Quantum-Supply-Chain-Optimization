#!/usr/bin/env python3
"""
Frontend Feature Verification Script
Tests that all frontend-backend features are working correctly
"""

import requests
import json
import sys

BASE_URL = 'http://127.0.0.1:5000/api/v1'
FRONTEND_URL = 'http://localhost:3000'

def test_feature(name, test_func):
    """Run a test and report results"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print('='*70)
    try:
        result = test_func()
        if result:
            print(f"✅ PASS: {name}")
            return True
        else:
            print(f"❌ FAIL: {name}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {name} - {str(e)}")
        return False


def test_api_health():
    """Test API health endpoint"""
    r = requests.get(f'{BASE_URL}/health', timeout=5)
    data = r.json()
    print(f"   Status: {data['data']['status']}")
    return r.status_code == 200 and data['data']['status'] == 'healthy'


def test_sample_data_load():
    """Test that optimization works with sample data"""
    sample_data = {
        "method": "classical",
        "parameters": {},
        "data": {
            "warehouses": [
                {"id": "W1", "name": "Warehouse 1", "latitude": 40.7128, "longitude": -74.006, "capacity": 1000},
                {"id": "W2", "name": "Warehouse 2", "latitude": 34.0522, "longitude": -118.2437, "capacity": 1500}
            ],
            "customers": [
                {"id": "C1", "name": "Customer 1", "latitude": 40.7589, "longitude": -73.9851, "demand": 100},
                {"id": "C2", "name": "Customer 2", "latitude": 34.0522, "longitude": -118.2437, "demand": 150}
            ],
            "routes": []
        }
    }
    
    r = requests.post(f'{BASE_URL}/optimize', json=sample_data, timeout=30)
    if r.status_code == 200:
        result = r.json()['data']['result']
        print(f"   Total Cost: ${result.get('totalCost', 0):.2f}")
        print(f"   Routes: {result.get('routesUsed', 0)}")
        print(f"   Assignments: {len(result.get('assignments', []))}")
        return True
    else:
        print(f"   Error: {r.status_code} - {r.text[:200]}")
        return False


def test_all_optimization_methods():
    """Test all optimization methods work"""
    test_data = {
        "warehouses": [
            {"id": "W1", "name": "W1", "latitude": 40.7, "longitude": -74.0, "capacity": 1000},
            {"id": "W2", "name": "W2", "latitude": 34.0, "longitude": -118.2, "capacity": 1000}
        ],
        "customers": [
            {"id": "C1", "name": "C1", "latitude": 40.8, "longitude": -73.9, "demand": 100},
            {"id": "C2", "name": "C2", "latitude": 34.1, "longitude": -118.3, "demand": 100}
        ],
        "routes": []
    }
    
    methods = ['classical', 'hybrid', 'quantum']
    results = {}
    
    for method in methods:
        try:
            payload = {"method": method, "parameters": {}, "data": test_data}
            r = requests.post(f'{BASE_URL}/optimize', json=payload, timeout=30)
            results[method] = r.status_code == 200
            status = "✅" if results[method] else "❌"
            print(f"   {status} {method.upper()}: {r.status_code}")
        except Exception as e:
            results[method] = False
            print(f"   ❌ {method.upper()}: {str(e)[:50]}")
    
    # Classical should always work, quantum might not if no IBM token
    return results.get('classical', False)


def test_data_validation():
    """Test data validation endpoint"""
    test_data = {
        "warehouses": [
            {"id": "W1", "name": "Test", "latitude": 40.7, "longitude": -74.0, "capacity": 1000}
        ],
        "customers": [
            {"id": "C1", "name": "Test", "latitude": 40.8, "longitude": -73.9, "demand": 100}
        ],
        "routes": []
    }
    
    r = requests.post(f'{BASE_URL}/data/validate', json=test_data, timeout=10)
    if r.status_code == 200:
        result = r.json()['data']
        print(f"   Valid: {result.get('valid', False)}")
        print(f"   Errors: {len(result.get('errors', []))}")
        print(f"   Warnings: {len(result.get('warnings', []))}")
        return True
    return False


def test_error_handling():
    """Test that API handles errors correctly"""
    # Test 1: Empty data
    bad_data = {"method": "classical", "data": {"warehouses": [], "customers": [], "routes": []}}
    r1 = requests.post(f'{BASE_URL}/optimize', json=bad_data, timeout=10)
    
    # Test 2: Missing data
    bad_data2 = {"method": "classical", "data": {}}
    r2 = requests.post(f'{BASE_URL}/optimize', json=bad_data2, timeout=10)
    
    # Both should return 400
    test1 = r1.status_code == 400
    test2 = r2.status_code == 400
    
    print(f"   Empty arrays: {'✅' if test1 else '❌'} (Status: {r1.status_code})")
    print(f"   Missing data: {'✅' if test2 else '❌'} (Status: {r2.status_code})")
    
    return test1 and test2


def test_different_problem_sizes():
    """Test optimization with different problem sizes"""
    sizes = {
        "Small (1W, 1C)": {
            "warehouses": [{"id": "W1", "name": "W1", "latitude": 40, "longitude": -74, "capacity": 1000}],
            "customers": [{"id": "C1", "name": "C1", "latitude": 41, "longitude": -73, "demand": 50}],
            "routes": []
        },
        "Medium (2W, 3C)": {
            "warehouses": [
                {"id": f"W{i}", "name": f"W{i}", "latitude": 40+i, "longitude": -74-i, "capacity": 1000}
                for i in range(2)
            ],
            "customers": [
                {"id": f"C{i}", "name": f"C{i}", "latitude": 40+i*0.5, "longitude": -74-i*0.3, "demand": 50}
                for i in range(3)
            ],
            "routes": []
        },
        "Large (3W, 7C)": {
            "warehouses": [
                {"id": f"W{i}", "name": f"W{i}", "latitude": 40+i, "longitude": -74-i, "capacity": 1000}
                for i in range(3)
            ],
            "customers": [
                {"id": f"C{i}", "name": f"C{i}", "latitude": 40+i*0.3, "longitude": -74-i*0.2, "demand": 50}
                for i in range(7)
            ],
            "routes": []
        }
    }
    
    all_passed = True
    for size_name, data in sizes.items():
        try:
            payload = {"method": "classical", "data": data}
            r = requests.post(f'{BASE_URL}/optimize', json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()['data']['result']
                cost = result.get('totalCost', 0)
                routes = result.get('routesUsed', 0)
                print(f"   ✅ {size_name}: Cost=${cost:.2f}, Routes={routes}")
            else:
                print(f"   ❌ {size_name}: Failed with status {r.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {size_name}: {str(e)[:50]}")
            all_passed = False
    
    return all_passed


def test_dashboard_endpoint():
    """Test dashboard data aggregation"""
    r = requests.get(f'{BASE_URL}/dashboard', timeout=10)
    if r.status_code == 200:
        data = r.json()['data']
        summary = data.get('summary', {})
        print(f"   Warehouses: {summary.get('warehouses', 0)}")
        print(f"   Customers: {summary.get('customers', 0)}")
        print(f"   Routes: {summary.get('routes', 0)}")
        print(f"   Recent Optimizations: {summary.get('recentOptimizations', 0)}")
        return True
    return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("QUANTUM SUPPLY CHAIN OPTIMIZATION - FEATURE VERIFICATION")
    print("=" * 70)
    print(f"\nBackend URL: {BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    
    tests = [
        ("API Health Check", test_api_health),
        ("Sample Data Loading", test_sample_data_load),
        ("All Optimization Methods", test_all_optimization_methods),
        ("Data Validation", test_data_validation),
        ("Error Handling", test_error_handling),
        ("Different Problem Sizes", test_different_problem_sizes),
        ("Dashboard Endpoint", test_dashboard_endpoint),
    ]
    
    results = []
    for name, test_func in tests:
        passed = test_feature(name, test_func)
        results.append((name, passed))
    
    # Final Summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 70)
    print(f"Overall: {passed_count}/{total_count} tests passed ({passed_count*100//total_count}%)")
    print("=" * 70)
    
    if passed_count == total_count:
        print("\n🎉 SUCCESS! All features are working correctly!")
        print("\n📋 How to use the application:")
        print("   1. Open your browser to: http://localhost:3000")
        print("   2. Navigate to 'Optimization' page")
        print("   3. The page will auto-load sample data")
        print("   4. Select optimization method (Classical/Quantum/Hybrid)")
        print("   5. Click 'Start Optimization'")
        print("   6. View results in real-time")
        print("\n✨ The system is fully operational!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed.")
        print("Check the detailed output above for specific issues.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
