import os

path = 'app/api/routes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_ai_xray signature
if 'def get_ai_xray(ticker: str):' in content:
    content = content.replace(
        'def get_ai_xray(ticker: str):',
        'def get_ai_xray(ticker: str, x_gemini_keys: str = Header(None)):\n    if x_gemini_keys:\n        import os\n        os.environ["GEMINI_API_KEYS"] = x_gemini_keys'
    )

# Replace build_idx_universe signature to use x_goapi_keys
if 'def build_idx_universe(background_tasks: BackgroundTasks, x_goapi_key: str = Header(None)):' in content:
    content = content.replace(
        'def build_idx_universe(background_tasks: BackgroundTasks, x_goapi_key: str = Header(None)):',
        'def build_idx_universe(background_tasks: BackgroundTasks, x_goapi_keys: str = Header(None)):\n    if x_goapi_keys:\n        import os\n        os.environ["GOAPI_KEYS"] = x_goapi_keys'
    )

# Replace scan_ninja signature
if 'def scan_ninja(premium: bool = True, x_goapi_key: str = Header(None)):' in content:
    content = content.replace(
        'def scan_ninja(premium: bool = True, x_goapi_key: str = Header(None)):',
        'def scan_ninja(premium: bool = True, x_goapi_keys: str = Header(None)):\n    if x_goapi_keys:\n        import os\n        os.environ["GOAPI_KEYS"] = x_goapi_keys'
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('routes.py patched successfully to use API Key Arrays')
