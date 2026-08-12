import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

app = create_app()

@app.errorhandler(404)
def custom_404(e):
    from flask import request
    return f"DEBUG 404: request.path={request.path} | request.url={request.url} | PATH_INFO={request.environ.get('PATH_INFO')} | RAW_URI={request.environ.get('RAW_URI')} | HTTP_X_FORWARDED_URI={request.environ.get('HTTP_X_FORWARDED_URI')}", 404
