import os

path = 'app/worker/autopilot.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('risk_reward_ratio FLOAT,', 'risk_reward_ratio FLOAT, edge_data TEXT,')
content = content.replace('analysis["risk_reward_ratio"]', 'analysis["risk_reward_ratio"], str(analysis.get("edge_data", "{}"))')
content = content.replace('expected_return, target_profit, stop_loss, risk_reward_ratio', 'expected_return, target_profit, stop_loss, risk_reward_ratio, edge_data')
content = content.replace('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s', '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('autopilot.py updated')
