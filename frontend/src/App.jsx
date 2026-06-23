import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { LayoutDashboard, TrendingUp, Zap, Activity, Settings, Bell, Search, BarChart2, Trash2, Plus, Globe } from 'lucide-react';
import ChartModal from './ChartModal';
import XRayModal from './XRayModal';
import InstitutionalRadar from './InstitutionalRadar';
import TradingChart from './components/TradingChart';
import CalculatorModal from './CalculatorModal';
import './index.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';


const renderEdgeData = (stock) => {
    try {
        if (!stock.edge_data || stock.edge_data === '{}' || stock.edge_data === 'null') return null;
        let edge = typeof stock.edge_data === 'string' ? JSON.parse(stock.edge_data) : stock.edge_data;
        if (!edge || !edge.tp1_prob) return null;
        
        return (
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px', marginTop: '10px', marginBottom: '10px' }}>
                <div style={{ fontSize: '0.85em', color: '#f1c40f', marginBottom: '5px', fontWeight: 'bold' }}>
                    🎯 Historical Probability (7 Years)
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px', fontSize: '0.85em' }}>
                    <div style={{ color: '#2ed573' }}>🟢 TP1 (+5%): {edge.tp1_prob}%</div>
                    <div style={{ color: '#eccc68' }}>🟡 TP2 (+8%): {edge.tp2_prob}%</div>
                    <div style={{ color: '#ffa502' }}>🟠 TP3 (+12%): {edge.tp3_prob}%</div>
                    <div style={{ color: '#ff4757' }}>🔴 TP4 (+15%): {edge.tp4_prob}%</div>
                </div>
                <div style={{ fontSize: '0.8em', color: '#dfe4ea', marginTop: '8px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '5px' }}>
                    <strong>Plan:</strong> Kunci BEP di +5%, Buntuti EMA-20 di +10%
                </div>
            </div>
        );
    } catch (e) {
        return null;
    }
}


const ApiKeysDashboard = () => {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState('Gemini');
  const [name, setName] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('');

  const fetchKeys = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/keys`);
      if (res.data.status === 'success') {
        setKeys(res.data.data);
      }
    } catch (e) {
      console.error('Failed to fetch keys', e);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleAdd = async () => {
    if (!name) {
      alert("Harap isi 'Nama Akun' terlebih dahulu! Bebas saja, misal 'Utama' atau 'Cadangan'.");
      return;
    }
    if (!apiKey) {
      alert("Harap masukkan API Key!");
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/keys`, { provider, name, api_key: apiKey, base_url: baseUrl });
      setName('');
      setApiKey('');
      setBaseUrl('');
      fetchKeys();
    } catch (e) {
      alert(e.response?.data?.detail || 'Gagal menambahkan kunci');
    }
    setLoading(false);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Hapus kunci ini?')) return;
    try {
      await axios.delete(`${API_BASE}/api/keys/${id}`);
      fetchKeys();
    } catch (e) {
      console.error(e);
    }
  };

  const handleReset = async (id) => {
    try {
      await axios.put(`${API_BASE}/api/keys/${id}/reset`);
      fetchKeys();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ background: 'var(--bg-card)', padding: 20, borderRadius: 12, marginTop: 20, border: '1px solid var(--border-subtle)' }}>
      <h3 style={{ margin: '0 0 15px 0', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 24 }}>🗝️</span> Pusat API Key (Omni-Gateway)
      </h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 15, marginBottom: 20 }}>
        <div>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: 'var(--color-blue)' }}>Provider</label>
          <select value={provider} onChange={e => setProvider(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }}>
            <option value="Gemini">Gemini</option>
            <option value="GoAPI">GoAPI</option>
            <option value="OpenAI">OpenAI</option>
            <option value="Groq">Groq</option>
            <option value="KieAI">Kie AI</option>
            <option value="Custom">Custom / Lainnya</option>
          </select>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: 'var(--color-blue)' }}>Nama Akun (Bebas)</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="Misal: Akun Susi" />
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: 'var(--color-blue)' }}>API Key</label>
          <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="Masukkan Kunci Rahasia" />
        </div>
        
        {['Custom', 'KieAI', 'OpenAI', 'Groq'].includes(provider) && (
          <div style={{ gridColumn: '1 / -1' }}>
            <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: '#e67e22' }}>Endpoint (Base URL) - Kosongkan untuk default</label>
            <input type="text" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="https://api.domain.com/v1" />
          </div>
        )}
        
        <div style={{ gridColumn: '1 / -1' }}>
          <button onClick={handleAdd} disabled={loading} className="btn" style={{ width: '100%', background: 'linear-gradient(135deg, #27ae60, #2ecc71)', color: 'white', border: 'none', padding: 10, borderRadius: 8, cursor: 'pointer', fontWeight: 'bold' }}>
            {loading ? 'Menambahkan...' : '➕ Tambah Kunci'}
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: 'rgba(0,0,0,0.2)', textAlign: 'left' }}>
              <th style={{ padding: 10 }}>Provider</th>
              <th style={{ padding: 10 }}>Akun</th>
              <th style={{ padding: 10 }}>Key</th>
              <th style={{ padding: 10 }}>Status</th>
              <th style={{ padding: 10 }}>Pakai</th>
              <th style={{ padding: 10 }}>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {keys.map(k => (
              <tr key={k.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: 10 }}>{k.provider}</td>
                <td style={{ padding: 10 }}>{k.name}</td>
                <td style={{ padding: 10, fontFamily: 'monospace' }}>{k.api_key_masked}</td>
                <td style={{ padding: 10 }}>
                  <span style={{ 
                    padding: '3px 8px', borderRadius: 12, fontSize: 11, fontWeight: 'bold',
                    background: k.status === 'Alive' ? 'rgba(46, 204, 113, 0.2)' : 'rgba(231, 76, 60, 0.2)',
                    color: k.status === 'Alive' ? '#2ecc71' : '#e74c3c'
                  }}>
                    {k.status}
                  </span>
                </td>
                <td style={{ padding: 10 }}>{k.used_count}x</td>
                <td style={{ padding: 10, display: 'flex', gap: 5 }}>
                  {k.status !== 'Alive' && (
                    <button onClick={() => handleReset(k.id)} style={{ background: 'transparent', border: '1px solid #3498db', color: '#3498db', borderRadius: 4, cursor: 'pointer', padding: '2px 5px', fontSize: 11 }}>Reset</button>
                  )}
                  <button onClick={() => handleDelete(k.id)} style={{ background: 'transparent', border: '1px solid #e74c3c', color: '#e74c3c', borderRadius: 4, cursor: 'pointer', padding: '2px 5px', fontSize: 11 }}>Hapus</button>
                </td>
              </tr>
            ))}
            {keys.length === 0 && (
              <tr><td colSpan="6" style={{ padding: 20, textAlign: 'center', color: '#7f8c8d' }}>Belum ada kunci terdaftar.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('swing');
  const [compositeData, setCompositeData] = useState([]);
  const [compositeLoading, setCompositeLoading] = useState(false);
  const [swingData, setSwingData] = useState([]);
  const [intradayData, setIntradayData] = useState([]);
    const [whaleData, setWhaleData] = useState([]);
  const [globalData, setGlobalData] = useState([]);
  const [astroForecast, setAstroForecast] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sensusLoading, setSensusLoading] = useState(false);
  const [macroData, setMacroData] = useState(null);
  const [macroLoading, setMacroLoading] = useState(false);
  const [ipoNews, setIpoNews] = useState([]);
  const [ipoLoading, setIpoLoading] = useState(false);
  const [buildingUniverse, setBuildingUniverse] = useState(false);
  const [autoSensusInterval, setAutoSensusInterval] = useState(0); // 0 means manual
  const [showEliteOnly, setShowEliteOnly] = useState(false);
  const [selectedStock, setSelectedStock] = useState(null);
  const [portfolioData, setPortfolioData] = useState([]);
  const [selectedChart, setSelectedChart] = useState(null);
  const [aiData, setAiData] = useState(null);
  const [loadingAi, setLoadingAi] = useState(false);
  const [selectedCalc, setSelectedCalc] = useState(null);


  // X-Ray State
  const [xrayTicker, setXrayTicker] = useState('');
  const [xrayData, setXrayData] = useState(null);
  const [xrayLoading, setXrayLoading] = useState(false);
  
  // Settings State
  const [watchlist, setWatchlist] = useState([]);
  const [newTicker, setNewTicker] = useState("");
  const [newMode, setNewMode] = useState("swing");
  const [serverKey, setServerKey] = useState(localStorage.getItem('SERVER_API_KEY') || "");
  const [goapiKeys, setGoapiKeys] = useState(localStorage.getItem('GOAPI_KEYS') || "");
  const [geminiKeys, setGeminiKeys] = useState(localStorage.getItem('GEMINI_KEYS') || "");

  useEffect(() => {
    if (serverKey) axios.defaults.headers.common['X-API-Key'] = serverKey;
    if (goapiKeys) axios.defaults.headers.common['X-GoAPI-Keys'] = goapiKeys;
    if (geminiKeys) axios.defaults.headers.common['X-Gemini-Keys'] = geminiKeys;
    localStorage.setItem('SERVER_API_KEY', serverKey);
    localStorage.setItem('GOAPI_KEYS', goapiKeys);
    localStorage.setItem('GEMINI_KEYS', geminiKeys);
  }, [serverKey, goapiKeys, geminiKeys]);

  // Engine Status Tracker
  const [engineStatus, setEngineStatus] = useState('idle');
  const [engineMsg, setEngineMsg] = useState('');
  const [engineElapsed, setEngineElapsed] = useState(0);

  // View Mode & Sorting State
  const [viewMode, setViewMode] = useState('cards'); // 'cards' atau 'table'
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [engineType, setEngineType] = useState('');

  const startEngineTracking = (type) => {
    setEngineStatus('running');
    setEngineType(type);
    setEngineElapsed(0);
    setEngineMsg(type === 'sensus' ? 'Sedang menyisir ~800 saham IDX...' : 'Sedang menganalisa kandidat...');
  };

  const stopEngineTracking = (success = true, msg = '') => {
    setEngineStatus(success ? 'done' : 'error');
    setEngineMsg(msg || (success ? 'Selesai!' : 'Mesin bermasalah — coba lagi'));
    setTimeout(() => setEngineStatus('idle'), 8000);
  };

  useEffect(() => {
    let interval;
    if (engineStatus === 'running') {
      interval = setInterval(() => {
        setEngineElapsed(prev => {
          if (prev >= 120) {
            stopEngineTracking(false, 'Timeout — mesin tidak merespons (>2 menit)');
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [engineStatus]);

  const fetchComposite = async () => {
    setCompositeLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/composite?premium=true`);
      setCompositeData(res.data.data);
    } catch (err) {
      console.error(err);
    }
    setCompositeLoading(false);
  };

  
  const fetchMasterIntraday = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/master/intraday`);
      setIntradayData(res.data.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const fetchMasterSwing = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/master/swing`);
      setSwingData(res.data.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };
  
  const fetchCandidates = async (mode) => {
    if (mode === 'intraday') fetchMasterIntraday();
    if (mode === 'swing') fetchMasterSwing();
  };

  const fetchWatchlist = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/watchlist`);
      setWatchlist(res.data.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMacro = async () => {
    setMacroLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/macro`);
      setMacroData(res.data);
    } catch (err) {
      console.error('Macro fetch error:', err);
    }
    setMacroLoading(false);
  };

  const fetchIpoNews = async () => {
    setIpoLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/news/ipo`);
      setIpoNews(res.data.data);
    } catch (err) {
      console.error('IPO fetch error:', err);
    }
    setIpoLoading(false);
  };

  const addTicker = async (e) => {
    e.preventDefault();
    if (!newTicker) return;
    try {
      await axios.post(`${API_BASE}/api/watchlist`, {
        ticker: newTicker,
        mode: newMode
      });
      setNewTicker("");
      fetchWatchlist();
    } catch (err) {
      alert("Gagal menambahkan saham. Mungkin sudah ada?");
    }
  };

  const deleteTicker = async (id) => {
    try {
      await axios.delete(`${API_BASE}/api/watchlist/${id}`);
      fetchWatchlist();
    } catch (err) {
      console.error(err);
    }
  };

  const buildUniverse = async (isAuto = false) => {
    if (isAuto !== true && !window.confirm("Proses Sensus Saham membutuhkan waktu sekitar 1-2 menit. Jalankan di latar belakang?")) return;
    setBuildingUniverse(true);
    startEngineTracking('sensus');
    try {
      // Trigger background task
      await axios.post(`${API_BASE}/api/universe/build`);
      
      // Start polling
      const pollInterval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE}/api/universe/status`);
          const statusData = res.data;
          
          if (statusData.status === 'running' || statusData.status === 'starting') {
            setEngineMsg(`${statusData.progress}% - ${statusData.message}`);
          } else if (statusData.status === 'done') {
            clearInterval(pollInterval);
            stopEngineTracking(true, `Sensus selesai! ${statusData.total_found} saham berhasil diklasifikasikan.`);
            setBuildingUniverse(false);
            fetchCandidates(activeTab);
          } else if (statusData.status === 'error') {
            clearInterval(pollInterval);
            stopEngineTracking(false, `Sensus gagal: ${statusData.message}`);
            setBuildingUniverse(false);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 2000);
      
    } catch (err) {
      console.error(err);
      stopEngineTracking(false, 'Gagal memulai sensus — cek koneksi server.');
      setBuildingUniverse(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'settings') {
      fetchWatchlist();
    } else if (activeTab === 'portfolio') {
      fetchPortfolio();
    } else if (activeTab === 'swing' && swingData.length === 0) { fetchMasterSwing(); } else if (activeTab === 'intraday' && intradayData.length === 0) { fetchMasterIntraday(); }
    // Fetch IPO news only once when first loading
    if (ipoNews.length === 0) {
      fetchIpoNews();
    }
  }, [activeTab]);

  const fetchPortfolio = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/portfolio`);
      setPortfolioData(res.data.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleXRaySubmit = async (e) => {
    e.preventDefault();
    if (!xrayTicker) return;
    
    setXrayLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/xray/${xrayTicker}`);
      if (res.data.error) {
        alert(res.data.error);
      } else {
        setXrayData(res.data.data);
      }
    } catch (err) {
      console.error(err);
      alert("Gagal melakukan X-Ray Scan.");
    }
    setXrayLoading(false);
  };

  const fetchAIXray = async (ticker) => {
    setXrayLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/xray/${ticker}`);
      if (res.data.error) {
        alert(res.data.error);
      } else {
        setXrayData(res.data.data);
      }
    } catch (err) {
      console.error(err);
      alert("Gagal melakukan X-Ray Scan.");
    }
    setXrayLoading(false);
  };

  const handleScan = () => {
    startEngineTracking('vip');
    const runScan = async () => {
      try {
        if (activeTab === 'swing') await fetchMasterSwing();
        else if (activeTab === 'intraday') await fetchMasterIntraday();
        else if (activeTab === 'none') await fetchKavaleri(true);
        else if (activeTab === 'none') await fetchWhale();
        else if (activeTab === 'none') await fetchGlobal();
        stopEngineTracking(true, 'Pemindaian VIP berhasil. Lihat hasil di bawah.');
      } catch (err) {
        stopEngineTracking(false, 'Pemindaian gagal - periksa koneksi atau token GoAPI Anda.');
      }
    };
    runScan();
  };

  // Sinkronisasi otomatis Sinyal VIP ke Command Center
  useEffect(() => {
    const elite = [];
    swingData.forEach(s => elite.push({...s, source: 'Swing Trading'}));
      intradayData.forEach(s => elite.push({...s, source: 'Intraday Momentum'}));
    whaleData.filter(s => s.signal).forEach(s => elite.push({...s, source: 'Radar Paus'}));
    globalData.filter(s => s.signal).forEach(s => elite.push({...s, source: 'Global Astro'}));
    
    setCompositeData(elite);
  }, [swingData, intradayData, whaleData, globalData]);

  
  // Auto-Sensus Effect
  useEffect(() => {
    let sensusTimer;
    if (autoSensusInterval > 0) {
      sensusTimer = setInterval(() => {
        if (!buildingUniverse) {
          console.log(`Auto-Sensus berjalan (${autoSensusInterval / 60000} menit)...`);
          buildUniverse(true); // isAuto = true
        }
      }, autoSensusInterval);
    }
    return () => clearInterval(sensusTimer);
  }, [autoSensusInterval, buildingUniverse]);

  const filteredSwingData = showEliteOnly 
    ? swingData.filter(d => d.smart_money_score >= 80 && d.composite_score >= 75 && d.risk_reward_ratio <= 0.4)
    : swingData;
    
  const currentData = activeTab === 'swing' ? filteredSwingData : activeTab === 'intraday' ? intradayData : whaleData;

  const totalScanned = currentData.length;
  const totalSignals = currentData.filter(d => d.composite_score > 60).length;
  const winRate = totalScanned ? Math.round((totalSignals / totalScanned) * 100) : 0;

  // Sorting Logic
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedData = [...currentData].sort((a, b) => {
    if (!sortConfig.key) return 0;
    
    let aVal = a[sortConfig.key];
    let bVal = b[sortConfig.key];
    
    // Khusus properti bersarang atau sinyal
    if (sortConfig.key === 'signal') {
      aVal = a.signal ? 1 : 0;
      bVal = b.signal ? 1 : 0;
    }
    
    if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const renderTable = () => (
    <div className="table-container" style={{ overflowX: 'auto', marginTop: '15px' }}>
      <table className="screener-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', color: 'white' }}>
        <thead>
          <tr style={{ background: 'rgba(255, 255, 255, 0.1)' }}>
            <th onClick={() => handleSort('ticker')} style={{ padding: '12px', cursor: 'pointer' }}>Ticker ↕</th>
            <th onClick={() => handleSort('price')} style={{ padding: '12px', cursor: 'pointer' }}>Harga ↕</th>
            <th onClick={() => handleSort('status')} style={{ padding: '12px', cursor: 'pointer' }}>Status ↕</th>
            <th onClick={() => handleSort('reason')} style={{ padding: '12px', cursor: 'pointer' }}>Keterangan ↕</th>
            <th onClick={() => handleSort('signal')} style={{ padding: '12px', cursor: 'pointer' }}>Sinyal VIP ↕</th>
          </tr>
        </thead>
        <tbody>
            {sortedData.length === 0 && !loading && (
              <tr>
                <td colSpan="7" style={{ padding: '40px', textAlign: 'center', background: 'rgba(255, 0, 0, 0.05)' }}>
                  <h3 style={{ color: '#ff4757', marginBottom: '10px' }}>⚠️ Data Tidak Tersedia</h3>
                  <p style={{ color: 'rgba(255,255,255,0.7)' }}>
                    Tidak ada kandidat saham saat ini. Sistem <b>TIDAK</b> menggunakan data buatan (dummy).<br/>
                    Jika tabel ini kosong, jalankan <b>Sensus Master</b> terlebih dahulu, atau tekan tombol <b>Pemindaian VIP</b>.
                  </p>
                </td>
              </tr>
            )}
          {sortedData.map((item, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', background: item.recommendation === 'STRONG BUY' ? 'rgba(255, 71, 87, 0.2)' : item.recommendation === 'BUY' ? 'rgba(46, 213, 115, 0.1)' : 'transparent' }}>
              <td style={{ padding: '12px' }}><strong>{item.ticker.replace('.JK', '')}</strong></td>
              <td style={{ padding: '12px' }}>Rp {item.close_price ? item.close_price.toLocaleString('id-ID') : '-'}</td>
              <td style={{ padding: '12px' }}>
                <span className="badge" style={{background: item.recommendation === 'STRONG BUY' ? '#ff4757' : item.recommendation === 'BUY' ? '#2ed573' : '#747d8c', color: 'white'}}>
                  {item.recommendation} (Skor: {item.composite_score})
                </span>
              </td>
              <td style={{ padding: '12px', fontSize: '13px' }}>
                <strong>{item.setup_type}</strong> | Bandar: {item.smart_money_status}
              </td>
              <td style={{ padding: '12px' }}>
                {item.target_profit ? <span className="badge success" style={{background: 'rgba(46, 213, 115, 0.2)', color: '#2ed573', padding: '5px 8px', borderRadius: '5px'}}>TP: Rp {item.target_profit.toLocaleString('id-ID')}</span> : <span className="badge neutral">-</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Activity color="var(--color-green)" />
          <span>IDX Super</span>
        </div>
        <nav className="sidebar-nav">
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <li className={`sidebar-item ${['intraday', 'swing'].includes(activeTab) ? 'active' : ''}`} onClick={() => setActiveTab('intraday')}>
            <LayoutDashboard size={18} />
            Master Trading AI
          </li>
          <li className={`sidebar-item ${activeTab === 'institutional' ? 'active' : ''}`} onClick={() => setActiveTab('institutional')}>
            <Globe size={18} />
            Radar Institusi
          </li>
          <li className={`sidebar-item ${activeTab === 'portfolio' ? 'active' : ''}`} onClick={() => setActiveTab('portfolio')}>
            <BarChart2 size={18} />
            Portofolio Robot
          </li>
          <li className={`sidebar-item ${activeTab === 'settings' ? 'active' : ''}`} style={{ marginTop: 'auto' }} onClick={() => setActiveTab('settings')}>
            <Settings size={18} />
            Pengaturan
          </li>
        </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Macro Panel di Top */}
        {activeTab !== 'home' && activeTab !== 'settings' && activeTab !== 'portfolio' && activeTab !== 'global' && (
          <div className="macro-panel" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', borderRadius: 0, padding: '12px 24px', margin: 0, background: 'rgba(255,255,255,0.02)' }}>
            <div className="macro-left">
              <Globe size={16} />
              <span className="macro-title">Kondisi Makro Pasar:</span>
              {macroData ? (
                <span className={`macro-badge ${macroData.market_condition?.toLowerCase()}`}>
                  {macroData.market_condition} ({macroData.macro_score}/100)
                </span>
              ) : (
                <span className="macro-badge netral">Belum Dicek</span>
              )}
              {macroData && (
                <div className="macro-indicators">
                  <span>IHSG: <b>{macroData.ihsg?.trend}</b></span>
                  <span>USD/IDR: <b>{macroData.usdidr?.value?.toLocaleString('id-ID')}</b></span>
                  <span>Coal: <b>{macroData.coal?.trend}</b></span>
                  <span>Gold: <b>{macroData.gold?.trend}</b></span>
                </div>
              )}
            </div>
            <button className="btn-macro" onClick={fetchMacro} disabled={macroLoading}>
              {macroLoading ? <div className="loader" style={{width:14,height:14}}></div> : <Globe size={14} />}
              Cek Makro
            </button>
          </div>
        )}
        <header className="header">
          <h1>
            {activeTab === 'home' ? 'Ultimate Command Center' : ['intraday', 'swing'].includes(activeTab) ? 'Master Trading AI' : activeTab === 'news' ? 'Berita & IPO' : activeTab === 'portfolio' ? 'Portofolio Robot' : 'Pengaturan Watchlist'}
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <form onSubmit={handleXRaySubmit} style={{ position: 'relative' }}>
              <input 
                type="text" 
                placeholder="X-Ray Ticker... (Cth: BBCA)" 
                value={xrayTicker}
                onChange={(e) => setXrayTicker(e.target.value.toUpperCase())}
                style={{
                  background: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  color: 'white',
                  padding: '8px 16px 8px 36px',
                  borderRadius: '20px',
                  outline: 'none',
                  width: '220px',
                  textTransform: 'uppercase'
                }}
              />
              <Search size={16} style={{ position: 'absolute', left: '12px', top: '10px', color: '#aaa' }} />
              {xrayLoading && <div className="loader" style={{ position: 'absolute', right: '12px', top: '8px', width: '14px', height: '14px', borderWidth: '2px' }}></div>}
            </form>
            <Bell size={20} color="var(--text-muted)" />
            <div style={{ width: 24, height: 24, background: 'var(--color-green)', borderRadius: '50%' }}></div>
          </div>
        </header>


        {/* --- TAB HOME (COMMAND CENTER) --- */}
        {activeTab === 'home' && (
          <div className="tab-content" style={{ position: 'relative', minHeight: '60vh' }}>
            {/* Watermark Radar Paus */}
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', opacity: 0.03, pointerEvents: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 0, userSelect: 'none' }}>
              <span style={{ fontSize: '250px', lineHeight: 1, filter: 'drop-shadow(0 0 50px rgba(255,255,255,0.5))' }}>🐋</span>
              <span style={{ fontSize: '60px', fontWeight: '900', color: '#fff', whiteSpace: 'nowrap', letterSpacing: '10px', textTransform: 'uppercase', textShadow: '0 0 30px rgba(255,255,255,0.5)' }}>Radar Paus</span>
            </div>
            
            <div className="command-center-header" style={{ position: 'relative', zIndex: 1 }}>
              <h2 style={{margin: 0}}>Kandidat Elite Aktif</h2>
            </div>
            
            {compositeLoading ? (
              <div className="radar-loader-container" style={{ position: 'relative', zIndex: 1 }}>
                <div className="radar-scanner"></div>
                <p>Menarik data dari 4 algoritma utama...</p>
              </div>
            ) : (
              <div className="stock-grid elite-grid" style={{ position: 'relative', zIndex: 1 }}>
                {compositeData.map((stock, i) => (
                  <div key={i} className="stock-card elite-card">
                    <div className="elite-glow"></div>
                    <div className="stock-header">
                      <h3>{stock.ticker || stock.name}</h3>
                      <span className="source-badge">{stock.source}</span>
                    </div>
                    <div className="stock-body">
                      <div className="price-row">
                        <span>Harga:</span>
                        <strong>Rp {stock.price.toLocaleString('id-ID')}</strong>
                      </div>
                      <div className="elite-reason">
                        {stock.reason || (stock.tp ? "Menunggu Konfirmasi Breakout" : "Data Sedang Berjalan")}
                      </div>
                      {stock.tp && (
                        <div className="plan-row elite-plan">
                          <span style={{color: 'var(--color-green)'}}>TP: {stock.tp.toLocaleString('id-ID')}</span>
                          <span style={{color: 'var(--color-pink)'}}>SL: {stock.sl.toLocaleString('id-ID')}</span>
                        </div>
                      )}
                    </div>
                    
                    <div style={{display: 'flex', gap: '10px', marginTop: '15px'}}>
                      <button className="btn-chart" onClick={() => setSelectedChart({ticker: stock.ticker, tp: stock.tp, sl: stock.sl, isGlobal: stock.source === 'Global Astro'})}>
                        📈 Buka Grafik
                      </button>
                      
                      {stock.sl && (
                        <button className="btn-calc" onClick={() => setSelectedCalc(stock)}>
                          🛡️ Hitung Lot
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                
                {compositeData.length === 0 && (
                  <div className="empty-state">
                    Belum ada sinyal terkonfirmasi. Klik "Scan Semua Sinyal" untuk memindai pasar.
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab !== 'home' && activeTab !== 'settings' && activeTab !== 'portfolio' && activeTab !== 'global' && (
          <div className="scan-view">




            {/* Stats Row */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon green">
                  <Activity size={24} />
                </div>
                <div className="stat-info">
                  <p>Saham Dipantau</p>
                  <h3>{totalScanned}</h3>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon pink">
                  <Zap size={24} />
                </div>
                <div className="stat-info">
                  <p>Sinyal Beli (HAKA)</p>
                  <h3>{totalSignals}</h3>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon orange">
                  <TrendingUp size={24} />
                </div>
                <div className="stat-info">
                  <p>Akurasi Mesin</p>
                  <h3>{winRate}%</h3>
                </div>
              </div>
            </div>
            {/* Master Sensus & Sub Navbar untuk Menu IDX */}
            {['intraday', 'swing'].includes(activeTab) && (
              <>
                <div className="universe-builder-card" style={{ background: 'rgba(255,255,255,0.03)', padding: 20, borderRadius: 12, marginBottom: 20, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
                    <div>
                      <h3 style={{ margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Globe size={18} color="var(--color-green)" /> Sensus Saham Induk (Master Data)
                      </h3>
                      <p style={{ color: 'var(--text-muted)', fontSize: 13, margin: 0, maxWidth: 600 }}>
                        Menyaring seluruh bursa IDX (~800 saham) menggunakan algoritma gratisan (Yahoo Finance) untuk menemukan "Kandidat Saham" potensial. Jalankan ini secara berkala sebelum menekan tombol Scan di bawah.
                      </p>
                    </div>
                    
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                      <select
                        value={autoSensusInterval}
                        onChange={(e) => setAutoSensusInterval(Number(e.target.value))}
                        style={{
                          background: '#1e1e1e', color: 'white', border: '1px solid #333', 
                          padding: '10px 14px', borderRadius: 8, fontSize: '0.9rem', outline: 'none', cursor: 'pointer'
                        }}
                      >
                        <option value={0}>🔴 Manual (Off)</option>
                        <option value={300000}>⚡ 5 Menit</option>
                        <option value={600000}>⏱️ 10 Menit</option>
                        <option value={900000}>⏳ 15 Menit</option>
                        <option value={1800000}>🕰️ 30 Menit</option>
                      </select>

                      <button
                        className="btn-scan"
                        onClick={() => buildUniverse(false)}
                        disabled={buildingUniverse}
                        style={{ background: 'linear-gradient(135deg, var(--color-green), #00b894)', color: 'black', fontWeight: 700, minWidth: 200, gap: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                      >
                        {buildingUniverse ? (
                          <><div className="loader" style={{width:14,height:14,borderWidth:2}}></div> Sedang Sensus...</>
                        ) : (
                          <><Globe size={16} /> Jalankan Sensus Master</>
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Engine Status Bar */}
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '10px 16px', borderRadius: 10, marginBottom: 4,
                  background: engineStatus === 'running' ? 'rgba(0,230,118,0.07)'
                            : engineStatus === 'done'    ? 'rgba(0,150,255,0.07)'
                            : engineStatus === 'error'   ? 'rgba(255,50,50,0.1)'
                            : 'rgba(255,255,255,0.02)',
                  border: engineStatus === 'running' ? '1px solid rgba(0,230,118,0.25)'
                        : engineStatus === 'done'    ? '1px solid rgba(0,150,255,0.2)'
                        : engineStatus === 'error'   ? '1px solid rgba(255,50,50,0.3)'
                        : '1px solid rgba(255,255,255,0.05)',
                  transition: 'all 0.4s ease'
                }}>
                  {/* Status Icon */}
                  {engineStatus === 'running' && (
                    <div style={{ position: 'relative', width: 22, height: 22, flexShrink: 0 }}>
                      <div style={{
                        width: 22, height: 22, border: '3px solid rgba(0,230,118,0.2)',
                        borderTop: '3px solid var(--color-green)', borderRadius: '50%',
                        animation: 'spin 0.7s linear infinite'
                      }} />
                    </div>
                  )}
                  {engineStatus === 'done' && <span style={{ fontSize: 18 }}>✅</span>}
                  {engineStatus === 'error' && <span style={{ fontSize: 18, animation: 'pulse 1s infinite' }}>⚠️</span>}
                  {engineStatus === 'idle' && <span style={{ fontSize: 16 }}>⚙️</span>}

                  {/* Status Text */}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 600,
                      color: engineStatus === 'running' ? 'var(--color-green)'
                           : engineStatus === 'done'    ? '#74b9ff'
                           : engineStatus === 'error'   ? '#ff6b6b'
                           : 'var(--text-muted)' }}>
                      {engineStatus === 'running' ? `⚡ Mesin Berjalan — ${engineType === 'sensus' ? 'Sensus Master' : 'Pemindaian VIP'}`
                       : engineStatus === 'done'    ? '✓ Proses Selesai'
                       : engineStatus === 'error'   ? '✗ Mesin Bermasalah'
                       : '● Status Mesin: Siap'}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      {engineStatus === 'running'
                        ? `${engineMsg} (${engineElapsed}s berjalan...)`
                        : engineMsg || 'Tekan tombol untuk memulai proses.'}
                    </div>
                  </div>

                  {/* Elapsed / Progress Pills */}
                  {engineStatus === 'running' && (
                    <div style={{
                      fontSize: 11, fontWeight: 700, color: 'black',
                      background: engineElapsed > 90 ? '#ff6b6b' : engineElapsed > 60 ? '#ffa502' : 'var(--color-green)',
                      padding: '3px 10px', borderRadius: 20, flexShrink: 0,
                      transition: 'background 0.5s'
                    }}>
                      {engineElapsed}s
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '10px', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px' }}>
                  <button className="btn-scan" onClick={() => setActiveTab('intraday')} style={{ flex: 1, background: activeTab === 'intraday' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'intraday' ? 'black' : 'white', borderRadius: '8px', fontWeight: 'bold' }}>
                    ⚡ Intraday Momentum
                  </button>
                  <button className="btn-scan" onClick={() => setActiveTab('swing')} style={{ flex: 1, background: activeTab === 'swing' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'swing' ? 'black' : 'white', borderRadius: '8px', fontWeight: 'bold' }}>
                    📈 Swing Trading
                  </button>
                </div>
              </>
            )}

            {/* Results Container */}
            <div className="results-container">
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, background: 'rgba(255,255,255,0.03)', padding: '12px 20px', borderRadius: 12, flexWrap: 'wrap', gap: 10}}>
                  <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                    {['intraday', 'swing'].includes(activeTab) && (
                      <>
                        <button className={`btn-toggle ${viewMode === 'cards' ? 'active' : ''}`} onClick={() => setViewMode('cards')} style={{ padding: '8px 12px', background: viewMode === 'cards' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: viewMode === 'cards' ? 'black' : 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>💳 Cards</button>
                        <button className={`btn-toggle ${viewMode === 'table' ? 'active' : ''}`} onClick={() => setViewMode('table')} style={{ padding: '8px 12px', background: viewMode === 'table' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: viewMode === 'table' ? 'black' : 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>📊 Table</button>
                      </>
                    )}
                    {activeTab === 'swing' && (
                      <button 
                        onClick={() => setShowEliteOnly(!showEliteOnly)} 
                        style={{ 
                          padding: '8px 12px', 
                          background: showEliteOnly ? 'linear-gradient(135deg, #f1c40f, #f39c12)' : 'rgba(255,255,255,0.1)', 
                          color: showEliteOnly ? 'black' : 'white', 
                          border: showEliteOnly ? '1px solid #f39c12' : 'none', 
                          borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold', marginLeft: '10px'
                        }}>
                        ⭐ {showEliteOnly ? 'Sembunyikan Elite Target' : 'Tampilkan Hanya Elite Target'}
                      </button>
                    )}
                  </div>
                <div style={{display:'flex', gap:'10px', alignItems: 'center'}}>
                  <button className="btn-scan" onClick={handleScan} disabled={loading} style={{background: 'var(--color-green)', color: 'black'}}>
                    {loading ? <div className="loader"></div> : <Search size={18} />}
                    {loading ? 'Memuat Data...' : '⚡ Refresh Data Lokal'}
                  </button>
                </div>
              </div>

              {viewMode === 'table' && ['intraday', 'swing'].includes(activeTab) ? (
                renderTable()
              ) : (
                <div className="stock-grid">
                  {currentData.length === 0 && !loading && (
                    <p style={{ color: 'var(--text-muted)' }}>Belum ada data. Klik tombol "Mulai Pindai".</p>
                  )}
                  
                  {currentData.map((stock) => (
                      <div 
                        key={stock.ticker} 
                        className={`stock-card ${stock.recommendation === 'STRONG BUY' ? 'highlight-green' : stock.recommendation === 'BUY' ? 'highlight-pink' : ''}`}
                        onClick={() => setSelectedStock(stock)}
                        style={{ cursor: 'pointer' }}
                      >
                        <div className="stock-card-header">
                          <div>
                            <div className="ticker">{stock.ticker}</div>
                            <div className="price">Rp {stock.close_price ? stock.close_price.toLocaleString('id-ID') : '0'}</div>
                          </div>
                          <div className="badge" style={{background: stock.recommendation === 'STRONG BUY' ? '#ff4757' : stock.recommendation === 'BUY' ? '#2ed573' : '#747d8c', color: 'white', fontWeight: 'bold'}}>
                            Skor: {stock.composite_score} | {stock.recommendation}
                          </div>
                        </div>
                        <div className="reason" style={{color: '#dfe4ea', fontSize: '0.9em', marginTop: '8px', marginBottom: '8px'}}>
                          <strong>Setup:</strong> {stock.setup_type} <br/>
                          <strong>Bandar:</strong> <span style={{color: stock.smart_money_status === 'Akumulasi Masif' ? '#2ed573' : '#ff4757'}}>{stock.smart_money_status}</span>
                        </div>
                        
                        <div className="tp-sl-container" style={{ marginTop: '10px', marginBottom: '15px' }}>
                            <div className="tp-sl-row">
                              <div className="tp-block">
                                <span className="tp-label">TARGET PROFIT</span>
                                <span className="tp-value" style={{ color: '#2ed573' }}>Rp {stock.target_profit ? stock.target_profit.toLocaleString('id-ID') : '0'}</span>
                                <span className="tp-pct tp-up">+{stock.expected_return}%</span>
                              </div>
                              <div className="sl-block" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <span className="tp-label">STOP LOSS 1</span>
                                  <span className="tp-value sl-val" style={{ color: '#ff7f50', fontSize: '1em' }}>Rp {stock.stop_loss ? stock.stop_loss.toLocaleString('id-ID') : '0'}</span>
                                  <span className="tp-pct sl-down" style={{ fontSize: '0.8em' }}>RR: {stock.risk_reward_ratio}x</span>
                                </div>
                                
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2px', paddingTop: '4px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                                  <span className="tp-label" style={{ color: '#ff4757' }}>SL 2 (MAJOR)</span>
                                  <span className="tp-value sl-val" style={{ color: '#ff4757', fontSize: '1em', fontWeight: 'bold' }}>
                                    Rp {(() => {
                                        try {
                                            const edge = typeof stock.edge_data === 'string' ? JSON.parse(stock.edge_data) : stock.edge_data;
                                            return edge?.sl2 ? edge.sl2.toLocaleString('id-ID') : stock.stop_loss;
                                        } catch { return stock.stop_loss; }
                                    })()}
                                  </span>
                                  <span className="tp-pct sl-down" style={{ fontSize: '0.7em', color: '#ff4757' }}>
                                    {(() => {
                                        try {
                                            const edge = typeof stock.edge_data === 'string' ? JSON.parse(stock.edge_data) : stock.edge_data;
                                            return edge?.sl2_uji ? `(Uji ${edge.sl2_uji}x)` : '';
                                        } catch { return ''; }
                                    })()}
                                  </span>
                                </div>
                              </div>
                            </div>
                        </div>

                        {renderEdgeData(stock)}
                        
                        <div style={{display: 'flex', gap: '10px'}}>
                          <button className="btn-ai" onClick={(e) => { e.stopPropagation(); fetchAIXray(stock.ticker); }} style={{ flex: 1, padding: '8px', background: 'linear-gradient(135deg, #9b59b6, #8e44ad)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                              🧠 AI X-Ray
                            </button>
                            <button className="btn-chart" onClick={(e) => { e.stopPropagation(); setSelectedChart({ticker: stock.ticker, tp: stock.target_profit, sl: stock.stop_loss}); }} style={{ flex: 1 }}>
                            📈 Buka Grafik
                          </button>
                        </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* --- TAB GLOBAL --- */}
        {activeTab === 'none' && (
          <div className="tab-content">
            <div className="card full-width">
              <div className="card-header">
                <h2>🌍 Global Markets (Astro Forecast)</h2>
                <button className="btn-primary" onClick={fetchGlobal} disabled={loading}>
                  {loading ? 'Memindai Langit...' : 'Scan Market Global'}
                </button>
              </div>
              
              {astroForecast.length > 0 && (
                <div className="astro-banner" style={{ background: 'rgba(142, 68, 173, 0.2)', border: '1px solid #8e44ad', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                  <h3 style={{ margin: '0 0 10px 0', color: '#d2b4de' }}>🌌 Cuaca Astrologi Saat Ini (+/- 3 Hari)</h3>
                  {astroForecast.map((forecast, idx) => (
                    <div key={idx} style={{ marginBottom: '10px' }}>
                      <strong style={{ color: '#f39c12' }}>{forecast.title}</strong>
                      <p style={{ margin: '5px 0 0 0', fontSize: '14px', lineHeight: '1.4' }}>{forecast.desc}</p>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="stock-grid">
                {globalData.map((asset) => (
                  <div key={asset.ticker} className="stock-card">
                    <div className="stock-header">
                      <h3>{asset.name}</h3>
                      <span className={`status-badge ${asset.signal ? 'haka' : 'sepi'}`}>
                        {asset.signal ? 'Signal ON' : 'Wait'}
                      </span>
                    </div>
                    <div className="stock-body">
                      <div className="price-row">
                        <span>Last Price:</span>
                        <strong>{asset.price.toLocaleString('en-US')}</strong>
                      </div>
                      {asset.tp && (
                        <div className="plan-row">
                          <span style={{color: 'var(--color-green)'}}>TP: {asset.tp.toLocaleString('en-US')}</span>
                          <span style={{color: 'var(--color-pink)'}}>SL: {asset.sl.toLocaleString('en-US')}</span>
                        </div>
                      )}
                    </div>
                    
                    <button className="btn-chart" onClick={() => setSelectedChart({ticker: asset.ticker, tp: asset.tp, sl: asset.sl, isGlobal: true})}>
                      🔭 Buka Astro Chart
                    </button>
                  </div>
                ))}
                
                {globalData.length === 0 && !loading && (
                  <div className="empty-state">
                    Belum ada data global. Klik "Scan Market Global".
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="results-container">
            <div className="universe-builder-card" style={{ background: 'rgba(255,255,255,0.03)', padding: 20, borderRadius: 12, marginBottom: 30, border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ margin: '0 0 8px 0', color: 'var(--color-orange)' }}>🔐 Brankas Kunci API (Pribadi)</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 16 }}>
                Masukkan kunci rahasia agar aplikasi Vercel ini bisa membuka gembok server dan menarik data premium. Tersimpan aman di memori browser Anda.
              </p>
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: 250 }}>
                  <ApiKeysDashboard />
                </div>
              </div>
            </div>

            <h2>Daftar Pantauan (Watchlist)</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: 24, marginTop: 8 }}>
              Kelola saham-saham spesifik yang ingin dipindai secara manual oleh mesin.
            </p>

            <form className="form-inline" onSubmit={addTicker}>
              <input 
                type="text" 
                className="input-field" 
                placeholder="Ticker (ex: GOTO)" 
                value={newTicker}
                onChange={e => setNewTicker(e.target.value)}
                required
              />
              <select className="select-field" value={newMode} onChange={e => setNewMode(e.target.value)}>
                <option value="swing">Mode Position (Swing)</option>
                <option value="scalp">Mode Scalping (Scalping)</option>
              </select>
              <button type="submit" className="btn-scan" style={{ background: 'var(--color-blue)', color: 'white' }}>
                <Plus size={18} /> Tambah Saham
              </button>
            </form>

            <table className="table-watchlist">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Mode Mesin</th>
                  <th width="100">Aksi</th>
                </tr>
              </thead>
              <tbody>
            {sortedData.length === 0 && !loading && (
              <tr>
                <td colSpan="7" style={{ padding: '40px', textAlign: 'center', background: 'rgba(255, 0, 0, 0.05)' }}>
                  <h3 style={{ color: '#ff4757', marginBottom: '10px' }}>⚠️ Data Tidak Tersedia</h3>
                  <p style={{ color: 'rgba(255,255,255,0.7)' }}>
                    Tidak ada kandidat saham saat ini. Sistem <b>TIDAK</b> menggunakan data buatan (dummy).<br/>
                    Jika tabel ini kosong, jalankan <b>Sensus Master</b> terlebih dahulu, atau tekan tombol <b>Pemindaian VIP</b>.
                  </p>
                </td>
              </tr>
            )}
                {watchlist.map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontWeight: 600 }}>{item.ticker}</td>
                    <td>
                      <span className={`badge ${item.mode === 'swing' ? 'aman' : 'waspada'}`}>
                        {item.mode.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <button className="btn-danger" onClick={() => deleteTicker(item.id)}>
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {watchlist.length === 0 && (
                  <tr>
                    <td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Belum ada data.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'institutional' && (
          <InstitutionalRadar apiKey={apiKey} />
        )}
        
        {activeTab === 'news' && (
          <div className="results-container">
            <h2>Pusat Informasi & Aksi Korporasi</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: 24, marginTop: 8 }}>
              Pantau sentimen pasar terbaru, jadwal RUPS, pembagian dividen, dan peluang saham IPO yang akan datang.
            </p>
            
            <div className="macro-panel" style={{ marginTop: '15px', flexDirection: 'column', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginBottom: '10px' }}>
                <div className="macro-left">
                  <Activity size={16} color="var(--color-pink)" />
                  <span className="macro-title">Radar Berita Terbaru:</span>
                </div>
                <button className="btn-macro" onClick={fetchIpoNews} disabled={ipoLoading} style={{ padding: '8px 16px', fontSize: '14px' }}>
                  {ipoLoading ? 'Memperbarui...' : 'Refresh Berita'}
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
                {ipoNews.length === 0 && !ipoLoading && <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Belum ada berita IPO hari ini.</p>}
                {ipoNews.map((news, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '8px' }}>
                    <span style={{ fontSize: '14px', color: 'var(--text-main)', flex: 1 }}>{news.title}</span>
                    <span style={{ fontSize: '12px', fontWeight: 'bold', color: news.color, background: 'rgba(0,0,0,0.3)', padding: '6px 12px', borderRadius: '12px', marginLeft: '10px', whiteSpace: 'nowrap' }}>
                      {news.risk}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'portfolio' && (
          <div className="results-container">
            <h2>Portofolio Robot (Paper Trading)</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: 24, marginTop: 8 }}>
              Rekaman pembelian virtual oleh mesin saat mendeteksi sinyal. Digunakan untuk membuktikan akurasi (Win Rate) secara otomatis.
            </p>

            <div className="table-responsive">
              <table className="watchlist-table">
                <thead>
                  <tr>
                    <th>Waktu</th>
                    <th>Ticker</th>
                    <th>Harga Beli</th>
                    <th>TP</th>
                    <th>SL</th>
                    <th>Status</th>
                    <th>Harga Jual</th>
                    <th>PnL</th>
                  </tr>
                </thead>
                <tbody>
            {sortedData.length === 0 && !loading && (
              <tr>
                <td colSpan="7" style={{ padding: '40px', textAlign: 'center', background: 'rgba(255, 0, 0, 0.05)' }}>
                  <h3 style={{ color: '#ff4757', marginBottom: '10px' }}>⚠️ Data Tidak Tersedia</h3>
                  <p style={{ color: 'rgba(255,255,255,0.7)' }}>
                    Tidak ada kandidat saham saat ini. Sistem <b>TIDAK</b> menggunakan data buatan (dummy).<br/>
                    Jika tabel ini kosong, jalankan <b>Sensus Master</b> terlebih dahulu, atau tekan tombol <b>Pemindaian VIP</b>.
                  </p>
                </td>
              </tr>
            )}
                  {portfolioData.map((trade) => (
                    <tr key={trade.id}>
                      <td>{new Date(trade.created_at).toLocaleString('id-ID')}</td>
                      <td><strong>{trade.ticker}</strong></td>
                      <td>Rp {trade.buy_price.toLocaleString('id-ID')}</td>
                      <td style={{color: 'var(--color-green)'}}>Rp {trade.tp_price ? trade.tp_price.toLocaleString('id-ID') : '-'}</td>
                      <td style={{color: 'var(--color-pink)'}}>Rp {trade.sl_price ? trade.sl_price.toLocaleString('id-ID') : '-'}</td>
                      <td>
                        <span className={`badge ${trade.status.toLowerCase()}`}>
                          {trade.status}
                        </span>
                      </td>
                      <td>{trade.sell_price ? `Rp ${trade.sell_price.toLocaleString('id-ID')}` : '-'}</td>
                      <td style={{ color: trade.pnl_pct > 0 ? 'var(--color-green)' : (trade.pnl_pct < 0 ? 'var(--color-pink)' : 'var(--text-main)') }}>
                        {trade.pnl_pct ? `${trade.pnl_pct.toFixed(2)}%` : '-'}
                      </td>
                    </tr>
                  ))}
                  {portfolioData.length === 0 && (
                    <tr>
                      <td colSpan="8" style={{ textAlign: 'center', padding: '20px' }}>Belum ada histori trade</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {selectedStock && (
          <ChartModal stock={selectedStock} onClose={() => setSelectedStock(null)} />
        )}

        {xrayData && (
          <XRayModal data={xrayData} onClose={() => setXrayData(null)} />
        )}

        {selectedChart && (
          <TradingChart 
            ticker={selectedChart.ticker} 
            tp={selectedChart.tp} 
            sl={selectedChart.sl} 
            isGlobal={selectedChart.isGlobal}
            onClose={() => setSelectedChart(null)} 
          />
        )}

        {selectedCalc && (
          <CalculatorModal 
            stock={selectedCalc} 
            onClose={() => setSelectedCalc(null)} 
          />
        )}
      </main>

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

    </div>
  );
}

export default App;
