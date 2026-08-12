import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

_flask_app = create_app()

class VercelPathFix:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req_uri = environ.get('REQUEST_URI', '')
        path = environ.get('PATH_INFO', '')
        
        if req_uri and req_uri.startswith('/'):
            environ['PATH_INFO'] = req_uri.split('?')[0]
        elif path.startswith('/api/index.py'):
            environ['PATH_INFO'] = path[13:] or '/'
        elif path.startswith('/api'):
            environ['PATH_INFO'] = path[4:] or '/'
            
        environ['SCRIPT_NAME'] = ''
        return self.app(environ, start_response)

app = VercelPathFix(_flask_app)
