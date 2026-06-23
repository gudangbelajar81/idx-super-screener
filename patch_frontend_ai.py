import os

path = 'frontend/src/App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Tambahkan import ReactMarkdown
if "import ReactMarkdown" not in content:
    content = content.replace("import axios from 'axios';", "import axios from 'axios';\nimport ReactMarkdown from 'react-markdown';")

# 2. Tambahkan state untuk AI X-Ray
if "const [aiData, setAiData] = useState(null);" not in content:
    content = content.replace("const [selectedChart, setSelectedChart] = useState(null);", "const [selectedChart, setSelectedChart] = useState(null);\n  const [aiData, setAiData] = useState(null);\n  const [loadingAi, setLoadingAi] = useState(false);")

# 3. Tambahkan fungsi fetchAIXray
FETCH_AI_FUNC = '''
  const fetchAIXray = async (ticker) => {
    setLoadingAi(true);
    setAiData({ ticker, text: "Memanggil Otak AI Gemini untuk X-Ray saham ini..." });
    try {
      const res = await axios.get(`${API_URL}/ai/xray/${ticker}`);
      if (res.data.data) {
        setAiData({ ticker, text: res.data.data });
      } else {
        setAiData({ ticker, text: "Gagal mendapatkan analisis." });
      }
    } catch (err) {
      setAiData({ ticker, text: `Error: ${err.message}` });
    }
    setLoadingAi(false);
  };
'''
if 'const fetchAIXray =' not in content:
    content = content.replace('const handleChartAction = (action) => {', FETCH_AI_FUNC + '\n  const handleChartAction = (action) => {')

# 4. Tambahkan tombol AI X-Ray di dalam card (sebelah tombol chart)
AI_BTN = '''<button className="btn-ai" onClick={(e) => { e.stopPropagation(); fetchAIXray(stock.ticker); }} style={{ flex: 1, padding: '8px', background: 'linear-gradient(135deg, #9b59b6, #8e44ad)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                              🧠 AI X-Ray
                            </button>'''
if '🧠 AI X-Ray' not in content:
    content = content.replace('<button className="btn-chart" onClick={(e) => { e.stopPropagation(); setSelectedChart({ticker: stock.ticker, tp: stock.target_profit, sl: stock.stop_loss}); }}>', AI_BTN + '\n                            <button className="btn-chart" onClick={(e) => { e.stopPropagation(); setSelectedChart({ticker: stock.ticker, tp: stock.target_profit, sl: stock.stop_loss}); }}>')

# 5. Tambahkan Modal AI X-Ray di akhir file (sebelum penutup div className="app-container")
AI_MODAL = '''
      {aiData && (
        <div className="modal-overlay" onClick={() => !loadingAi && setAiData(null)}>
          <div className="modal-content ai-modal" onClick={(e) => e.stopPropagation()} style={{maxWidth: '600px', background: 'rgba(15, 20, 30, 0.95)', border: '1px solid #9b59b6'}}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', borderBottom: '1px solid rgba(155,89,182,0.3)', paddingBottom: '10px' }}>
              <h2 style={{ margin: 0, color: '#9b59b6' }}>🧠 AI X-Ray: {aiData.ticker}</h2>
              <button onClick={() => setAiData(null)} style={{ background: 'none', border: 'none', color: '#ff4757', fontSize: '1.5em', cursor: 'pointer' }}>&times;</button>
            </div>
            
            <div className="ai-result-box" style={{ padding: '15px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', maxHeight: '60vh', overflowY: 'auto', fontSize: '0.95em', lineHeight: '1.6', color: '#ecf0f1' }}>
              {loadingAi ? (
                <div style={{textAlign: 'center', padding: '40px 0'}}>
                  <div className="spinner" style={{width: '40px', height: '40px', border: '4px solid rgba(155,89,182,0.3)', borderTop: '4px solid #9b59b6', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 15px auto'}}></div>
                  <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                  <p style={{color: '#9b59b6', fontWeight: 'bold'}}>{aiData.text}</p>
                </div>
              ) : (
                <div className="markdown-body">
                  <ReactMarkdown>{aiData.text}</ReactMarkdown>
                </div>
              )}
            </div>
            
            <div style={{ marginTop: '15px', textAlign: 'right' }}>
              <button onClick={() => setAiData(null)} style={{ padding: '8px 16px', background: 'rgba(255,255,255,0.1)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Tutup</button>
            </div>
          </div>
        </div>
      )}
'''
if 'className="modal-content ai-modal"' not in content:
    content = content.replace('    </div>\n  );\n}\n\nexport default App;', AI_MODAL + '\n    </div>\n  );\n}\n\nexport default App;')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('App.jsx patched for AI X-Ray')
