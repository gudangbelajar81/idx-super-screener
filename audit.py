import re
import os

frontend_file = 'frontend/src/App.jsx'
backend_file = 'app/api/routes.py'

print("=== FRONTEND API CALLS ===")
with open(frontend_file, 'r', encoding='utf-8') as f:
    content = f.read()
    
    # find all axios.get, axios.post, etc.
    axios_calls = re.findall(r'axios\.(get|post|put|delete)\(\s*`\$\{API_BASE\}([^`\?]+)', content)
    for method, path in set(axios_calls):
        print(f"{method.upper():<6} {path}")

print("\n=== BACKEND ROUTES ===")
with open(backend_file, 'r', encoding='utf-8') as f:
    content = f.read()
    
    routes = re.findall(r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']', content)
    for method, path in set(routes):
        print(f"{method.upper():<6} /api{path}")

