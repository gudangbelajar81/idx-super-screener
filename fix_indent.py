with open('app/worker/autopilot.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_string = "cursor.execute(\"DELETE FROM idx_signals WHERE mode IN ('position', 'swing')\")\n            \npos_count = 0\n            for res in position_results:"
good_string = "cursor.execute(\"DELETE FROM idx_signals WHERE mode IN ('position', 'swing')\")\n            \n            pos_count = 0\n            for res in position_results:"

content = content.replace(bad_string, good_string)

with open('app/worker/autopilot.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Indentation fixed.')
