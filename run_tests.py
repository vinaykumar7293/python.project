"""
Test Runner for Customer Feedback Summary
Executes all unit tests and prints formatted test coverage.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 65)
    print(f" TOTAL TESTS RUN : {result.testsRun}")
    print(f" SUCCESSFUL      : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" FAILURES        : {len(result.failures)}")
    print(f" ERRORS          : {len(result.errors)}")
    print("=" * 65)

    if result.wasSuccessful():
        print(" [✓] ALL UNIT TESTS PASSED WITH 100% SUCCESS!")
        return 0
    else:
        print(" [!] SOME TESTS FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
