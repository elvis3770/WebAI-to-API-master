"""
Start WebAI-to-API server (Windows-compatible, no emoji issues)
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run the server
from src.run import *

if __name__ == "__main__":
    print("="*70)
    print("  WebAI-to-API Server Starting (Cookie Mode)")
    print("="*70)
    print()
    
    # The rest of the startup will be handled by run.py
    # but with proper encoding
