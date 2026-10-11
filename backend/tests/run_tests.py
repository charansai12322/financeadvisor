"""
Master Test Runner for Finance Advisor Backend Audit.
Discovers and executes all static, unit, live integration, and contract tests.
Outputs structured summary metrics conforming to Phase 1 validation standards.
"""
import unittest
import sys
import os

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def run_suite():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.dirname(__file__), pattern="test_*.py")

    print("=" * 70)
    print("FINANCE ADVISOR - PHASE 1 FORENSIC AUDIT TEST SUITE")
    print("=" * 70)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("TEST EXECUTION SUMMARY:")
    print("=" * 70)
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped

    print(f"Total Tests Run: {total_tests}")
    print(f"Passed:          {passed}")
    print(f"Failed:          {failures}")
    print(f"Errors:          {errors}")
    print(f"Skipped/Blocked: {skipped}")

    if skipped > 0:
        print("\nBlocked / Skipped Test Details:")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")

    if failures > 0 or errors > 0:
        print("\nFailures / Errors:")
        for test, trace in result.failures + result.errors:
            print(f"  - {test}:")
            lines = [l for l in trace.splitlines() if l.strip()]
            if lines:
                print(f"    {lines[-1]}")

    print("=" * 70)
    return result


if __name__ == "__main__":
    result = run_suite()
    sys.exit(0 if (len(result.failures) == 0 and len(result.errors) == 0) else 1)
