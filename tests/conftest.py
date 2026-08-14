"""
Pytest configuration: make `src.*` importable when running `pytest` from
the project root (same sys.path concern as src/ui/app.py under Streamlit).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))