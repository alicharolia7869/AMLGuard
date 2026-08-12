import sys
import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

base_app = create_app()

# Dispatch Vercel serverless function paths (/api/index.py, /api/index, /api) directly to Flask app
app = DispatcherMiddleware(
    base_app,
    {
        '/api/index.py': base_app,
        '/api/index': base_app,
        '/api': base_app
    }
)
