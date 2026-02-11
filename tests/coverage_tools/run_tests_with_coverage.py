#!/usr/bin/env python3
"""
Test Runner with Coverage

Runs all tests and generates coverage report.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_file(test_file):
    """Run a single test file."""
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Test timed out"
    except Exception as e:
        return False, "", str(e)


def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("RUNNING ALL TESTS")
    print("=" * 70)
    print()
    
    # Find all test files
    tests_dir = project_root / 'tests'
    test_files = list(tests_dir.glob('test_*.py'))
    
    # Exclude certain test files
    exclude_files = {'test_image_display.py'}  # Demo files
    test_files = [f for f in test_files if f.name not in exclude_files]
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    print()
    
    # Run each test
    results = []
    for test_file in test_files:
        print(f"Running {test_file.name}...")
        success, stdout, stderr = run_test_file(test_file)
        results.append((test_file.name, success))
        
        if not success:
            print(f"  ❌ FAILED")
            if stderr:
                print(f"  Error: {stderr[:200]}")
        else:
            print(f"  ✅ PASSED")
    
    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
