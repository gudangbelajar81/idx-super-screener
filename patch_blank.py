import re

path = 'frontend/src/App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Hapus sisa-sisa goapiKey yang bikin blank
content = re.sub(
    r'<label.*?Kunci Provider \(GoAPI VIP\).*?</label>\s*<input.*?value=\{goapiKey\}.*?/>',
    '''<label style={{ display: 'block', marginBottom: 6, fontSize: 13, color: 'var(--color-blue)' }}>Kunci Provider (GoAPI VIP - Pisahkan dengan koma)</label>
              <input type="password" value={goapiKeys} onChange={e => setGoapiKeys(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="key1,key2,key3..." />
              
              <label style={{ display: 'block', marginTop: 15, marginBottom: 6, fontSize: 13, color: '#9b59b6' }}>Kunci AI X-Ray (Gemini - Pisahkan dengan koma)</label>
              <input type="password" value={geminiKeys} onChange={e => setGeminiKeys(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="key1,key2,key3..." />''',
    content,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('App.jsx fixed')
