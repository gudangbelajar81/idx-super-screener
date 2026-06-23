import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

old_buttons = """                  <div style={{ display: 'flex', gap: '10px', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px' }}>
                    <button className="btn-scan" onClick={() => setActiveTab('swing')} style={{ background: activeTab === 'swing' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'swing' ? 'black' : 'white', borderRadius: '8px' }}>
                      Mode Position
                    </button>
                    <button className="btn-scan" onClick={() => setActiveTab('kavaleri')} style={{ background: activeTab === 'none' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'none' ? 'black' : 'white', borderRadius: '8px' }}>
                      Mode Swing
                    </button>
                    <button className="btn-scan" onClick={() => setActiveTab('ninja')} style={{ background: activeTab === 'intraday' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'intraday' ? 'black' : 'white', borderRadius: '8px' }}>
                      Mode Scalping
                    </button>
                  </div>"""

new_buttons = """                  <div style={{ display: 'flex', gap: '10px', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px' }}>
                    <button className="btn-scan" onClick={() => setActiveTab('intraday')} style={{ flex: 1, background: activeTab === 'intraday' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'intraday' ? 'black' : 'white', borderRadius: '8px', fontWeight: 'bold' }}>
                      ⚡ Intraday Momentum
                    </button>
                    <button className="btn-scan" onClick={() => setActiveTab('swing')} style={{ flex: 1, background: activeTab === 'swing' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'swing' ? 'black' : 'white', borderRadius: '8px', fontWeight: 'bold' }}>
                      📈 Swing Trading
                    </button>
                  </div>"""

if old_buttons in text:
    text = text.replace(old_buttons, new_buttons)
    with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Buttons patched successfully")
else:
    print("Buttons block not found!")
