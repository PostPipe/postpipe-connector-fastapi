import sys
import os

# Add the project root to the sys.path to resolve 'app' module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
