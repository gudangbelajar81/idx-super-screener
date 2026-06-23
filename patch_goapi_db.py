import os

path1 = 'app/services/engines/goapi_engine.py'
with open(path1, 'r', encoding='utf-8') as f:
    content1 = f.read()

content1 = content1.replace(
    'def get_goapi_router():\n    """Mengambil instance router untuk GoAPI setiap kali dipanggil, agar env selalu terupdate"""\n    raw_keys = os.getenv("GOAPI_KEYS", os.getenv("GOAPI_KEY", DEFAULT_GOAPI_KEY))\n    return APIKeyRouter(raw_keys)',
    'def get_goapi_router():\n    return APIKeyRouter("GoAPI")'
)
content1 = content1.replace('current_key = router.get_key()', 'current_key, _ = router.get_key()')

with open(path1, 'w', encoding='utf-8') as f:
    f.write(content1)
print("goapi_engine.py patched")


path2 = 'app/services/engines/universe_engine.py'
with open(path2, 'r', encoding='utf-8') as f:
    content2 = f.read()

content2 = content2.replace(
    'raw_keys = os.getenv("GOAPI_KEYS", os.getenv("GOAPI_KEY", goapi_key or ""))\n    goapi_router = APIKeyRouter(raw_keys)',
    'goapi_router = APIKeyRouter("GoAPI")'
)
content2 = content2.replace('current_key = goapi_router.get_key()', 'current_key, _ = goapi_router.get_key()')

with open(path2, 'w', encoding='utf-8') as f:
    f.write(content2)
print("universe_engine.py patched")
