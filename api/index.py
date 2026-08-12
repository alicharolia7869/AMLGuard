import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

_flask_app = create_app()

def app(environ, start_response):
    req_uri = environ.get('REQUEST_URI', '') or environ.get('PATH_INFO', '')
    req_path = req_uri.split('?')[0]
    
    if req_path.startswith('/api/index.py'):
        req_path = req_path[13:]
    elif req_path.startswith('/api'):
        req_path = req_path[4:]
        
    if not req_path:
        req_path = '/'

    environ['PATH_INFO'] = req_path
    environ['SCRIPT_NAME'] = ''
    return _flask_app(environ, start_response)
