import os
import sys

# Make `api/` importable (matches how Flask loads api/index.py).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
os.environ.setdefault("DRONE_TYPE", "sim")
