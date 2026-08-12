import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

_flask_app = create_app()

def app(environ, start_response):
    # Extract real browser URL path from Vercel edge header
    real_path = environ.get('HTTP_X_FORWARDED_URI') or environ.get('HTTP_X_MATCHED_PATH') or environ.get('PATH_INFO', '/')
    real_path = real_path.split('?')[0]
    
    if not real_path or real_path.startswith('/api/index') or real_path == '/api':
        real_path = '/'
        
    environ['PATH_INFO'] = real_path
    environ['SCRIPT_NAME'] = ''
    return _flask_app(environ, start_response)
