import re

path = 'frontend/src/App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Hapus duplicate import
content = content.replace("import { useState, useEffect } from 'react';\n\nconst ApiKeysDashboard", "const ApiKeysDashboard")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("App.jsx fixed duplicate imports")
