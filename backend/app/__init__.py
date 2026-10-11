"""
Finance Advisor Application Package.
"""
import sys
from pathlib import Path

# Ensure backend root directory is on sys.path so internal app.* imports resolve from anywhere
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

__version__ = "1.0.0"

