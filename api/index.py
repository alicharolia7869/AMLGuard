import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

def app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    
    output = []
    for k, v in sorted(environ.items()):
        output.append(f"{k} = {v}")
        
    return ["\n".join(output).encode('utf-8')]
