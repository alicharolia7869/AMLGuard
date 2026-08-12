import sys
import os
from flask import make_response

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app import create_app
    app = create_app()
except Exception as err:
    import traceback
    err_tb = traceback.format_exc()
    print(f"Vercel Initialization Error: {err_tb}", file=sys.stderr)
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def vercel_init_error(path):
        return f"<h2>Vercel Serverless Error</h2><pre>{err_tb}</pre>", 500

