import sys
import os

# Add root directory to sys.path for Vercel Serverless
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

app = create_app()

@app.route('/api/index.py/<path:subpath>', methods=['GET', 'POST'])
@app.route('/api/index/<path:subpath>', methods=['GET', 'POST'])
@app.route('/api/index.py', methods=['GET', 'POST'])
@app.route('/api/index', methods=['GET', 'POST'])
def vercel_catch_all(subpath=''):
    from flask import redirect, url_for, session
    clean_subpath = subpath.strip('/')
    if not clean_subpath:
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Dispatch to target view function dynamically
    for endpoint, func in app.view_functions.items():
        if endpoint == clean_subpath or endpoint.endswith(f".{clean_subpath}"):
            return func()

    return redirect(url_for('auth.login'))
