with open('app/api/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

autopilot_route = '''
@router.post("/api/trigger-autopilot")
def trigger_autopilot(api_key: str = Depends(verify_api_key)):
    try:
        from app.worker.autopilot import run_eod_autopilot
        run_eod_autopilot()
        return {"message": "Autopilot Triggered successfully!"}
    except Exception as e:
        return {"message": f"Error triggering autopilot: {e}"}
'''

if 'trigger-autopilot' not in content:
    content += '\n' + autopilot_route

with open('app/api/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added trigger-autopilot route.')
