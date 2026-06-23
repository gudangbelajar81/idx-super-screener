import re

path = 'frontend/src/App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Kita akan mencari block mulai dari 🔐 Brankas Kunci API sampai sebelum Daftar Pantauan
# Atau lebih spesifik:
old_block_pattern = r'<h3.*?Brankas Kunci API \(Pribadi\).*?</h3>.*?<label.*?Kunci Provider.*?<input.*?/>.*?<label.*?Kunci AI X-Ray.*?<input.*?/>'

if re.search(old_block_pattern, content, flags=re.DOTALL):
    content = re.sub(
        old_block_pattern,
        '<ApiKeysDashboard />',
        content,
        flags=re.DOTALL
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Berhasil me-replace UI lama dengan <ApiKeysDashboard />")
else:
    print("Pattern UI lama tidak ditemukan!")

# Tapi tunggu, kotak "Brankas Kunci API (Pribadi)" mungkin ada di dalam div tersendiri.
# Mari kita lihat apakah kita bisa me-replace satu div penuh.
