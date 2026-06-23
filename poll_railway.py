import urllib.request
import urllib.error
import time

ninja_req = urllib.request.Request(
    'https://idx-super-screener-production.up.railway.app/api/sensus/ninja',
    method='POST',
    headers={'X-API-Key': 'KunciRahasiaBos88'}
)

auto_req = urllib.request.Request(
    'https://idx-super-screener-production.up.railway.app/api/trigger-autopilot',
    method='POST',
    headers={'X-API-Key': 'KunciRahasiaBos88'}
)

print('Waiting for Railway server to come back online (max 5 mins)...')
server_up = False
for _ in range(30):
    try:
        with urllib.request.urlopen(ninja_req, timeout=30) as response:
            res = response.read().decode('utf-8')
            print('Sensus Ninja Success:', res)
            server_up = True
            break
    except urllib.error.HTTPError as e:
        print(f'HTTP Error: {e.code} - Waiting...')
    except urllib.error.URLError as e:
        print(f'URL Error: {e.reason} - Waiting...')
    except Exception as e:
        print(f'Unknown Error: {e} - Waiting...')
    time.sleep(10)

if server_up:
    print('Triggering Autopilot EOD (Swing & Position)...')
    try:
        with urllib.request.urlopen(auto_req, timeout=120) as response:
            res = response.read().decode('utf-8')
            print('Autopilot Success:', res)
    except Exception as e:
        print('Autopilot Error:', e)
else:
    print('Server did not come back online in time.')
