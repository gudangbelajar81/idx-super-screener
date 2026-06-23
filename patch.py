import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Live Radar State
content = content.replace("const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });", "const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });\n  const [liveRadar, setLiveRadar] = useState(false);")

# 2. Add Live Radar Effect
effect_code = '''
  // Live Radar Effect (Auto Scan every 3 mins for Scalping)
  useEffect(() => {
    let radarTimer;
    if (liveRadar && activeTab === 'ninja') {
      radarTimer = setInterval(() => {
        console.log('Live Radar: Auto-scanning Scalping VIP...');
        fetchNinja(true);
      }, 180000);
    }
    return () => clearInterval(radarTimer);
  }, [liveRadar, activeTab]);

  const currentData = activeTab === 'swing' ? swingData : activeTab === 'ninja' ? ninjaData : activeTab === 'kavaleri' ? kavaleriData : whaleData;
'''
content = content.replace("const currentData = activeTab === 'swing' ? swingData : activeTab === 'ninja' ? ninjaData : activeTab === 'kavaleri' ? kavaleriData : whaleData;", effect_code)

# 3. Rename Sidebar
content = content.replace("<span>Benteng Swing</span>", "<span>Mode Position (Invest)</span>")
content = content.replace("<span>Kavaleri Liquidity</span>", "<span>Mode Swing (Trend)</span>")
content = content.replace("<span>Ninja Scalping</span>", "<span>Mode Scalping (Intraday)</span>")

# 4. Rename Sub-navbar buttons
content = content.replace(">Mode Benteng<", ">Mode Position<")
content = content.replace(">Mode Kavaleri<", ">Mode Swing<")
content = content.replace(">Mode Ninja<", ">Mode Scalping<")

# 5. Add Live Radar Toggle UI
radar_ui = '''<div style={{display:'flex', gap:'10px', alignItems: 'center'}}>
                  {activeTab === 'ninja' && (
                    <label style={{
                      display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer',
                      background: liveRadar ? 'rgba(255, 71, 87, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                      padding: '8px 12px', borderRadius: '8px', border: liveRadar ? '1px solid #ff4757' : '1px solid transparent',
                      color: liveRadar ? '#ff4757' : 'white', fontWeight: 'bold'
                    }}>
                      <input 
                        type="checkbox" 
                        checked={liveRadar} 
                        onChange={(e) => setLiveRadar(e.target.checked)} 
                        style={{ display: 'none' }}
                      />
                      <div className={`radar-dot ${liveRadar ? 'pulsing' : ''}`} style={{ width: 10, height: 10, borderRadius: '50%', background: liveRadar ? '#ff4757' : '#555' }}></div>
                      Live Radar
                    </label>
                  )}
                  <button className="btn-scan" onClick={handleScan} disabled={loading} style={{background: 'var(--color-green)', color: 'black'}}>'''

content = content.replace("""<div style={{display:'flex', gap:'10px'}}>
                  <button className="btn-scan" onClick={handleScan} disabled={loading} style={{background: 'var(--color-green)', color: 'black'}}>""", radar_ui)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('App.jsx patched successfully.')
