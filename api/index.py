import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

_flask_app = create_app()

def app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    
    # Strip Vercel serverless script prefix
    for prefix in ['/api/index.py', '/api/index', '/api']:
        if path.startswith(prefix):
            path = path[len(prefix):]
            break

    # Flask route matcher requires '/' when path is empty
    if not path or path == '':
        path = '/'

    environ['PATH_INFO'] = path
    environ['SCRIPT_NAME'] = ''
    return _flask_app(environ, start_response)
