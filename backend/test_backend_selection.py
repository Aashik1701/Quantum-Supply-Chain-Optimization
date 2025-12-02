#!/usr/bin/env python3
"""
Test backend selection API and policies
"""

from config.quantum_config import ibm_quantum

def test_backend_selection():
    """Test backend selection with different policies"""
    print("=" * 70)
    print("Testing Backend Selection Policies")
    print("=" * 70)
    
    # Initialize connection
    if not ibm_quantum.initialize():
        print("\n❌ Could not connect to IBM Quantum. Testing local only.")
        return
    
    # Test 1: Get backends info
    print("\n📋 Test 1: Get backends info")
    backends_info = ibm_quantum.get_backends_info()
    print(f"   Simulators: {len(backends_info['simulators'])}")
    print(f"   Devices: {len(backends_info['devices'])}")
    
    if backends_info['simulators']:
        print(f"   Sample simulator: {backends_info['simulators'][0]['name']}")
    if backends_info['devices']:
        print(f"   Sample device: {backends_info['devices'][0]['name']}")
    
    # Test 2: Simulator policy
    print("\n🖥️  Test 2: Select with 'simulator' policy")
    backend_name = ibm_quantum.select_backend(policy='simulator')
    if backend_name:
        print(f"   ✓ Selected: {backend_name}")
    else:
        print("   ⚠️  No simulator available")
    
    # Test 3: Device policy
    print("\n⚛️  Test 3: Select with 'device' policy")
    backend_name = ibm_quantum.select_backend(policy='device')
    if backend_name:
        print(f"   ✓ Selected: {backend_name}")
    else:
        print("   ⚠️  No device available")
    
    # Test 4: Shortest queue policy
    print("\n⏱️  Test 4: Select with 'shortest_queue' policy")
    backend_name = ibm_quantum.select_backend(policy='shortest_queue')
    if backend_name:
        print(f"   ✓ Selected: {backend_name}")
        # Show queue info
        for device in backends_info['devices']:
            if device['name'] == backend_name:
                queue = device.get('pending_jobs', 'N/A')
                print(f"   Queue depth: {queue}")
    else:
        print("   ⚠️  No device available with queue info")
    
    # Test 5: Explicit backend name
    if backends_info['devices']:
        test_backend = backends_info['devices'][0]['name']
        print(f"\n🎯 Test 5: Select explicit backend '{test_backend}'")
        backend_name = ibm_quantum.select_backend(backend_name=test_backend)
        if backend_name:
            print(f"   ✓ Selected: {backend_name}")
        else:
            print(f"   ❌ Failed to select {test_backend}")
    
    print("\n" + "=" * 70)
    print("✅ Backend selection tests completed!")
    print("=" * 70)


def test_backends_endpoint_format():
    """Test the format returned by get_backends_info for API"""
    print("\n" + "=" * 70)
    print("Testing API Response Format")
    print("=" * 70)
    
    backends_info = ibm_quantum.get_backends_info()
    
    print("\n📦 Expected API response structure:")
    print({
        'backends': backends_info,
        'connected': ibm_quantum.service is not None
    })
    
    # Verify structure
    assert 'simulators' in backends_info
    assert 'devices' in backends_info
    assert isinstance(backends_info['simulators'], list)
    assert isinstance(backends_info['devices'], list)
    
    if backends_info['devices']:
        device = backends_info['devices'][0]
        required_fields = ['name', 'qubits', 'operational', 'simulator']
        for field in required_fields:
            assert field in device, f"Missing field: {field}"
        print("\n✓ All required fields present in device info")
    
    print("=" * 70)


if __name__ == "__main__":
    test_backend_selection()
    test_backends_endpoint_format()
