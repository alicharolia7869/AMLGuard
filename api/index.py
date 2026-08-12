import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

_flask_app = create_app()

def app(environ, start_response):
    # Retrieve raw requested path from Vercel headers or PATH_INFO
    raw_url = environ.get('HTTP_X_FORWARDED_URI') or environ.get('HTTP_X_MATCHED_PATH') or environ.get('PATH_INFO', '/')
    raw_url = raw_url.split('?')[0]

    # Strip Vercel serverless rewrite prefixes cleanly
    for prefix in ['/api/index.py', '/api/index', '/api']:
        if raw_url.startswith(prefix):
            raw_url = raw_url[len(prefix):]
            break

    if not raw_url or raw_url == '':
        raw_url = '/'

    environ['PATH_INFO'] = raw_url
    environ['SCRIPT_NAME'] = ''
    return _flask_app(environ, start_response)
