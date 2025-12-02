"""
IBM Quantum Platform Configuration
Connect to IBM Quantum for real quantum hardware and cloud simulators
"""

import os
from typing import Optional, Any

from qiskit_ibm_runtime import QiskitRuntimeService


class IBMQuantumConfig:
    """IBM Quantum Platform configuration and connection manager (Runtime API)"""

    def __init__(self):
        self.service: Optional[QiskitRuntimeService] = None
        self.token = os.environ.get('IBM_QUANTUM_TOKEN')
        # Public/free accounts use channel 'ibm_quantum'
        self.channel = os.environ.get('IBM_QUANTUM_CHANNEL', 'ibm_quantum')
        # Optional: account instance string, e.g. 'ibm-q/open/main'
        self.instance = os.environ.get('IBM_QUANTUM_INSTANCE')

    def initialize(self) -> bool:
        """
        Initialize connection to IBM Quantum Platform using Runtime Service

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.token:
            print("ERROR: IBM_QUANTUM_TOKEN not found in environment")
            print("Get your token from: https://quantum-computing.ibm.com/")
            return False

        try:
            # Attempt with configured channel first
            def _connect_with_channel(channel: str):
                if self.instance:
                    return QiskitRuntimeService(channel=channel, token=self.token, instance=self.instance)
                return QiskitRuntimeService(channel=channel, token=self.token)

            try:
                self.service = _connect_with_channel(self.channel)
                print("✓ Connected to IBM Quantum Runtime")
                print(f"  Channel: {self.channel}")
                if self.instance:
                    print(f"  Instance: {self.instance}")
                return True
            except Exception as primary_err:
                # Fallback: try the alternate channel automatically
                alt_channel = 'ibm_cloud' if self.channel == 'ibm_quantum' else 'ibm_quantum'
                print(f"⚠️  Primary channel '{self.channel}' failed, trying '{alt_channel}'...")
                try:
                    self.service = _connect_with_channel(alt_channel)
                    self.channel = alt_channel
                    print("✓ Connected to IBM Quantum Runtime")
                    print(f"  Channel: {self.channel}")
                    if self.instance:
                        print(f"  Instance: {self.instance}")
                    return True
                except Exception as alt_err:
                    print(f"ERROR: Failed to initialize IBM Quantum Runtime: {primary_err}")
                    print(f"ERROR: Alternate channel '{alt_channel}' also failed: {alt_err}")
                    return False

        except Exception as e:
            print(f"ERROR: Unexpected initialization error: {e}")
            return False

    def get_backend(self, backend_name: str = 'ibmq_qasm_simulator') -> Optional[Any]:
        """
        Get a specific IBM Quantum backend

        Args:
            backend_name: Name of the backend
                - Simulators: 'ibmq_qasm_simulator'
                - Real hardware: 'ibm_manila', 'ibm_quito', 'ibm_nairobi', etc.

        Returns:
            Backend instance or None if not available
        """
        if not self.service and not self.initialize():
            return None

        try:
            backend = self.service.backend(backend_name)

            # Print backend info
            config = backend.configuration()
            status = backend.status()

            print(f"\n📡 Backend: {backend_name}")
            print(f"   Qubits: {config.num_qubits if hasattr(config, 'num_qubits') else config.n_qubits}")
            print(f"   Simulator: {getattr(config, 'simulator', False)}")
            print(f"   Operational: {getattr(status, 'operational', True)}")

            # Show queue info if available
            pending = getattr(status, 'pending_jobs', None)
            if pending is not None and not getattr(config, 'simulator', False):
                print(f"   Queue: {pending} jobs")

            return backend

        except Exception as e:
            print(f"ERROR: Failed to get backend '{backend_name}': {e}")
            return None

    def get_backends_info(self):
        """Get structured information about all available backends"""
        if not self.service and not self.initialize():
            return {'simulators': [], 'devices': []}

        try:
            backends = self.service.backends()
        except Exception as e:
            print(f"ERROR: Could not list backends: {e}")
            return {'simulators': [], 'devices': []}

        simulators = []
        real_devices = []

        for backend in backends:
            try:
                config = backend.configuration()
                status = backend.status()
                info = {
                    'name': backend.name,
                    'qubits': getattr(config, 'num_qubits', getattr(config, 'n_qubits', '?')),
                    'operational': getattr(status, 'operational', True),
                    'simulator': getattr(config, 'simulator', False),
                    'pending_jobs': getattr(status, 'pending_jobs', None)
                }
                (simulators if info['simulator'] else real_devices).append(info)
            except Exception:
                continue

        return {'simulators': simulators, 'devices': real_devices}

    def list_available_backends(self):
        """Print all available backends (for CLI/debug)"""
        backends_info = self.get_backends_info()
        
        print("\n📋 Available IBM Quantum Backends:\n")
        
        print("🖥️  SIMULATORS:")
        for sim in backends_info['simulators']:
            status = "✓" if sim['operational'] else "✗"
            print(f"  {status} {sim['name']:<30} | {sim['qubits']:>3} qubits")

        print("\n⚛️  QUANTUM HARDWARE:")
        for device in backends_info['devices']:
            status = "✓" if device['operational'] else "✗"
            queue = f"({device['pending_jobs']} in queue)" if device['pending_jobs'] is not None else ""
            print(f"  {status} {device['name']:<30} | {device['qubits']:>3} qubits {queue}")
    
    def select_backend(self, policy: str = 'simulator', backend_name: Optional[str] = None) -> Optional[str]:
        """Select backend based on policy.
        
        Args:
            policy: 'simulator', 'device', or 'shortest_queue'
            backend_name: Optional specific backend name to use
            
        Returns:
            Backend name or None if not available
        """
        if backend_name:
            # Explicit backend requested
            try:
                backend = self.get_backend(backend_name)
                return backend_name if backend else None
            except Exception:
                return None
        
        backends_info = self.get_backends_info()
        
        if policy == 'simulator':
            # Prefer any operational simulator
            for sim in backends_info['simulators']:
                if sim['operational']:
                    return sim['name']
            # Fallback to first device if no simulator
            for device in backends_info['devices']:
                if device['operational']:
                    return device['name']
        
        elif policy == 'device':
            # Use first operational device
            for device in backends_info['devices']:
                if device['operational']:
                    return device['name']
        
        elif policy == 'shortest_queue':
            # Find device with shortest queue
            operational_devices = [
                d for d in backends_info['devices'] 
                if d['operational'] and d['pending_jobs'] is not None
            ]
            if operational_devices:
                shortest = min(operational_devices, key=lambda d: d['pending_jobs'])
                return shortest['name']
            # Fallback to any operational device
            for device in backends_info['devices']:
                if device['operational']:
                    return device['name']
        
        return None


# Global instance
ibm_quantum = IBMQuantumConfig()


def get_ibm_backend(backend_name: str = 'ibmq_qasm_simulator'):
    """
    Convenience function to get IBM backend

    Usage:
        backend = get_ibm_backend('ibmq_qasm_simulator')
        backend = get_ibm_backend('ibm_manila')  # Real hardware
    """
    return ibm_quantum.get_backend(backend_name)


def test_ibm_connection():
    """Test IBM Quantum connection and list backends"""
    print("=" * 60)
    print("Testing IBM Quantum Platform Connection")
    print("=" * 60)

    if ibm_quantum.initialize():
        ibm_quantum.list_available_backends()
        return True
    else:
        print("\n❌ Failed to connect to IBM Quantum Platform")
        print("\nSetup instructions:")
        print("1. Get API token from: https://quantum-computing.ibm.com/")
        print("2. Add to .env file: IBM_QUANTUM_TOKEN=your_token_here")
        print("3. Restart the application")
        return False


if __name__ == "__main__":
    # Test connection when run directly
    test_ibm_connection()
