from pathlib import Path
import sys

# Ensure project root (parent directory of tests) is on sys.path so tests can import project modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT)) 