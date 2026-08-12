import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

_flask_app = create_app()

def handler(environ, start_response):
    # Extract original requested URL path from Vercel headers
    raw_path = environ.get('HTTP_X_MATCHED_PATH', '') or environ.get('REQUEST_URI', '') or environ.get('PATH_INFO', '')
    raw_path = raw_path.split('?')[0]
    
    if raw_path.startswith('/api/index.py'):
        raw_path = raw_path[13:] or '/'
    elif raw_path.startswith('/api'):
        raw_path = raw_path[4:] or '/'
        
    if not raw_path:
        raw_path = '/'

    environ['PATH_INFO'] = raw_path
    environ['SCRIPT_NAME'] = ''
    
    return _flask_app(environ, start_response)

app = handler
