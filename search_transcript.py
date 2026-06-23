import json
import os

path = r'C:\Users\Administrator\.gemini\antigravity\brain\3e0d8b07-45a9-4ef4-8582-97c570b78c3e\.system_generated\logs\transcript.jsonl'
with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if content and 'apikey router' in content.lower():
                print(f"Step {data.get('step_index')}: {content[:1000]}...")
                print("-" * 50)
            elif content and 'router' in content.lower() and 'master' in content.lower():
                print(f"Step {data.get('step_index')}: {content[:1000]}...")
                print("-" * 50)
        except:
            pass
