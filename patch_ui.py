import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Sidebar Menu Rebranding
sidebar_old = r'''<li className=\{`sidebar-item \$\{\[\'swing\', \'kavaleri\', \'ninja\'\]\.includes\(activeTab\) \? \'active\' : \'\'\}`\} onClick=\{\(\) => setActiveTab\(\'swing\'\)\}>
              <TrendingUp size=\{18\} />
              Menu IDX
            </li>'''

sidebar_new = '''<li className={`sidebar-item ${['swing', 'kavaleri', 'ninja'].includes(activeTab) ? 'active' : ''}`} onClick={() => setActiveTab('swing')}>
              <TrendingUp size={18} />
              Screener IDX
            </li>'''

content = re.sub(sidebar_old, sidebar_new, content)

# 2. Sub-Navbar Rebranding
content = content.replace("Mode Benteng", "Mode Position")
content = content.replace("Mode Kavaleri", "Mode Swing")
content = content.replace("Mode Ninja", "Mode Scalping")

# 3. Source renaming for composite
content = content.replace("source: 'Benteng'", "source: 'Position'")
content = content.replace("source: 'Kavaleri'", "source: 'Swing'")
content = content.replace("source: 'Ninja'", "source: 'Scalping'")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('App.jsx texts rebranded successfully.')
