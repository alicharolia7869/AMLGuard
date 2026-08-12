import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

app = create_app()

@app.route('/debug-env')
def debug_env():
    from flask import request
    return {
        'path': request.path,
        'script_root': request.script_root,
        'url': request.url,
        'headers': dict(request.headers)
    }
