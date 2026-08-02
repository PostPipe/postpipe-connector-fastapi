import sys
import os

# Append the project root to sys.path to ensure 'app' is resolvable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
