#!/usr/bin/env python3
"""
Test runner for the supply chain optimization backend
"""

import sys
import subprocess
import os


def run_tests(test_type="all", verbose=False):
    """Run tests based on type"""
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add specific test markers
    if test_type == "smoke":
        cmd.extend(["-m", "smoke"])
    elif test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    elif test_type == "optimization":
        cmd.extend(["-m", "optimization"])
    elif test_type == "data":
        cmd.extend(["-m", "data"])
    elif test_type != "all":
        print(f"Unknown test type: {test_type}")
        return 1
    
    # Add coverage if requested
    if "--coverage" in sys.argv:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Install with: pip install pytest")
        return 1


def main():
    """Main test runner"""
    
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <test_type> [options]")
        print("Test types: all, smoke, unit, integration, api, optimization, data")
        print("Options: --verbose, --coverage")
        return 1
    
    test_type = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print(f"Running {test_type} tests...")
    
    return run_tests(test_type, verbose)


if __name__ == "__main__":
    sys.exit(main())
