import os
import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ubah state tabs
content = content.replace("const [activeTab, setActiveTab] = useState('home');", "const [activeTab, setActiveTab] = useState('swing');")

# 2. Hapus Sidebar Home, Global, Portfolio, News
content = re.sub(r'<li className={`sidebar-item elite-home.*?</li>', '', content, flags=re.DOTALL)
content = re.sub(r'<li className={`sidebar-item premium-glow.*?</li>', '', content, flags=re.DOTALL)
content = re.sub(r'<li className={`sidebar-item.*?Berita dan IPO.*?</li>', '', content, flags=re.DOTALL)
content = re.sub(r'<li className={`sidebar-item.*?Portofolio Robot.*?</li>', '', content, flags=re.DOTALL)
content = re.sub(r'<li className={`sidebar-item.*?Radar Paus.*?</li>', '', content, flags=re.DOTALL)

# 3. Ganti Sidebar Text
content = content.replace("['swing', 'kavaleri', 'ninja'].includes(activeTab) ? 'active' : ''", "['swing', 'intraday'].includes(activeTab) ? 'active' : ''")
content = content.replace("Master Scanner IDX", "Master Trading AI")

# 4. Ganti Tombol Mode
tombol_lama = """
                  <div className="mode-selector" style={{ background: 'rgba(0,0,0,0.3)', padding: '5px', borderRadius: '10px', display: 'flex', gap: '5px', marginBottom: '15px' }}>
                    <button className="btn-scan" onClick={() => setActiveTab('swing')} style={{ background: activeTab === 'swing' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'swing' ? 'black' : 'white', borderRadius: '8px' }}>
                      Mode Position
                    </button>
                    <button className="btn-scan" onClick={() => setActiveTab('kavaleri')} style={{ background: activeTab === 'kavaleri' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'kavaleri' ? 'black' : 'white', borderRadius: '8px' }}>
                      Mode Swing
                    </button>
                    <button className="btn-scan" onClick={() => setActiveTab('ninja')} style={{ background: activeTab === 'ninja' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'ninja' ? 'black' : 'white', borderRadius: '8px' }}>
                      Mode Scalping
                    </button>
                  </div>
"""

tombol_baru = """
                  <div className="mode-selector" style={{ background: 'rgba(0,0,0,0.3)', padding: '5px', borderRadius: '10px', display: 'flex', gap: '5px', marginBottom: '15px' }}>
                    <button className="btn-scan" onClick={() => setActiveTab('intraday')} style={{ flex: 1, background: activeTab === 'intraday' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'intraday' ? 'black' : 'white', borderRadius: '8px', fontWeight: 'bold' }}>
                      ⚡ Intraday Momentum
                    </button>
                    <button className="btn-scan" onClick={() => setActiveTab('swing')} style={{ flex: 1, background: activeTab === 'swing' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'swing' ? 'black' : 'white', borderRadius: '8px', fontWeight: 'bold' }}>
                      📈 Swing Trading
                    </button>
                  </div>
"""
content = content.replace(tombol_lama, tombol_baru)

# 5. Ganti Fetch Function
content = content.replace("fetchSwing(true)", "fetchMasterSwing()")
content = content.replace("fetchNinja(true)", "fetchMasterIntraday()")
content = content.replace("activeTab === 'ninja'", "activeTab === 'intraday'")
content = content.replace("activeTab === 'kavaleri'", "activeTab === 'none'")
content = content.replace("activeTab === 'whale'", "activeTab === 'none'")
content = content.replace("activeTab === 'global'", "activeTab === 'none'")

# Tambahkan fungsi fetch baru
fetch_funcs = """
  const fetchMasterIntraday = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/master/intraday');
      const data = await res.json();
      setNinjaData(data.data || []);
    } catch(err) {
      console.error(err);
    }
    setLoading(false);
  };

  const fetchMasterSwing = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/master/swing');
      const data = await res.json();
      setSwingData(data.data || []);
    } catch(err) {
      console.error(err);
    }
    setLoading(false);
  };
"""

content = content.replace("const fetchSwing = async (isVip = false) => {", fetch_funcs + "\n  const fetchSwing = async (isVip = false) => {")

# Ubah currentData
content = content.replace("const currentData = activeTab === 'swing' ? swingData : activeTab === 'ninja' ? ninjaData : activeTab === 'kavaleri' ? kavaleriData : whaleData;", "const currentData = activeTab === 'swing' ? swingData : activeTab === 'intraday' ? ninjaData : [];")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("App.jsx patched successfully.")
