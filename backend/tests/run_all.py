"""
Master Test Runner for Phase 2 Production Validation.
Runs pytest suites for unit, contract, and integration tests with UTF-8 support.
"""
import subprocess
import sys
import os

# Configure UTF-8 encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_venv_candidates = [
    os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe"),
    os.path.join(BACKEND_DIR, "..", ".venv", "Scripts", "python.exe"),
]
VENV_PYTHON = next((p for p in _venv_candidates if os.path.exists(p)), sys.executable)



def run_tests():
    python_exec = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    print("=" * 75)
    print("FINANCE ADVISOR — PHASE 2 MASTER TEST SUITE")
    print(f"Runner Python: {python_exec}")
    print("=" * 75)

    cmd = [
        python_exec,
        "-m",
        "pytest",
        "tests",
        "-v",
        "--tb=short",
    ]

    result = subprocess.run(cmd, cwd=BACKEND_DIR)
    print("=" * 75)
    return result.returncode


if __name__ == "__main__":
    code = run_tests()
    sys.exit(code)
