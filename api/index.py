import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app import create_app
    app = create_app()
except Exception as e:
    import traceback
    err_msg = traceback.format_exc()
    print("Vercel App Initialization Traceback:\n", err_msg)
    
    from flask import Flask
    app = Flask(__name__)
    @app.route('/<path:path>')
    @app.route('/')
    def fallback(path=''):
        return f"<h2>Vercel Startup Diagnostic Error</h2><pre>{err_msg}</pre>", 500
