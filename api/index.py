import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

app = create_app()

class VercelWSGIHandler:
    def __init__(self, flask_app):
        self.flask_app = flask_app

    def __call__(self, environ, start_response):
        # Extract actual edge requested URL path from Vercel headers
        forwarded = environ.get('HTTP_X_FORWARDED_URI') or environ.get('HTTP_X_MATCHED_PATH')
        if forwarded:
            path = forwarded.split('?')[0]
        else:
            path = environ.get('PATH_INFO', '/')
            if path.startswith('/api/index.py'):
                path = path[13:]
            elif path.startswith('/api/index'):
                path = path[10:]
            elif path.startswith('/api'):
                path = path[4:]
                
        if not path or path == '':
            path = '/'
            
        environ['PATH_INFO'] = path
        environ['SCRIPT_NAME'] = ''
        return self.flask_app(environ, start_response)

app.wsgi_app = VercelWSGIHandler(app.wsgi_app)
