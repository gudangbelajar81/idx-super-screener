import os

path = 'frontend/src/App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Tambahkan state untuk geminiKeys
if "const [geminiKeys, setGeminiKeys] = useState" not in content:
    content = content.replace(
        "const [goapiKey, setGoapiKey] = useState(localStorage.getItem('GOAPI_KEY') || \"\");",
        "const [goapiKeys, setGoapiKeys] = useState(localStorage.getItem('GOAPI_KEYS') || \"\");\n  const [geminiKeys, setGeminiKeys] = useState(localStorage.getItem('GEMINI_KEYS') || \"\");"
    )
    content = content.replace("const [goapiKey, setGoapiKey]", "// replaced") # To avoid duplicates if ran multiple times

# 2. Update axios headers
content = content.replace("if (goapiKey) axios.defaults.headers.common['X-GoAPI-Key'] = goapiKey;", "if (goapiKeys) axios.defaults.headers.common['X-GoAPI-Keys'] = goapiKeys;\n    if (geminiKeys) axios.defaults.headers.common['X-Gemini-Keys'] = geminiKeys;")

# 3. Update localStorage
content = content.replace("localStorage.setItem('GOAPI_KEY', goapiKey);", "localStorage.setItem('GOAPI_KEYS', goapiKeys);\n    localStorage.setItem('GEMINI_KEYS', geminiKeys);")
content = content.replace("}, [serverKey, goapiKey]);", "}, [serverKey, goapiKeys, geminiKeys]);")

# 4. Update UI di Settings Modal
OLD_SETTINGS_UI = '''<label style={{ display: 'block', marginBottom: 6, fontSize: 13, color: 'var(--color-blue)' }}>Kunci Provider (GoAPI VIP)</label>
              <input type="password" value={goapiKey} onChange={e => setGoapiKey(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="Masukkan Kunci GoAPI" />'''

NEW_SETTINGS_UI = '''<label style={{ display: 'block', marginBottom: 6, fontSize: 13, color: 'var(--color-blue)' }}>Kunci Provider (GoAPI VIP - Pisahkan dengan koma)</label>
              <input type="password" value={goapiKeys} onChange={e => setGoapiKeys(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="key1,key2,key3..." />
              
              <label style={{ display: 'block', marginTop: 15, marginBottom: 6, fontSize: 13, color: '#9b59b6' }}>Kunci AI X-Ray (Gemini - Pisahkan dengan koma)</label>
              <input type="password" value={geminiKeys} onChange={e => setGeminiKeys(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="key1,key2,key3..." />
'''

if 'Kunci AI X-Ray (Gemini' not in content:
    content = content.replace(OLD_SETTINGS_UI, NEW_SETTINGS_UI)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("App.jsx updated with Pusat API Key Rotator UI")
