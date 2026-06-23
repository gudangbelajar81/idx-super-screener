import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

replacements = {
    'dY"^ Buka Grafik': '📈 Buka Grafik',
    'dYO? Global Markets': '🌍 Global Markets',
    'dY"3 Cards': '💳 Cards',
    'dY", Table': '📊 Table',
    's Refresh Data Lokal': '⚡ Refresh Data Lokal',
    'â\xad\x90 Tampilkan Hanya Elite Target': '⭐ Tampilkan Hanya Elite Target',
    'â\xad\x90 Sembunyikan Elite Target': '⭐ Sembunyikan Elite Target'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
