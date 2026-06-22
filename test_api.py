import urllib.request
import json
import time

endpoints = [
    '/docs', 
    '/api/scan/swing', 
    '/api/scan/ninja', 
    '/api/macro'
]
base_url = 'https://idx-super-screener-production.up.railway.app'

for e in endpoints:
    print(f"Menguji {e} ...")
    try:
        t0 = time.time()
        req = urllib.request.Request(base_url + e, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=30)
        t1 = time.time()
        
        status = res.status
        size = len(res.read())
        print(f"  [OK] Status: {status} | Size: {size} bytes | Waktu: {t1-t0:.2f}s")
    except Exception as exc:
        print(f"  [ERROR] {exc}")
