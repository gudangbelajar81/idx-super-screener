import { useState, useEffect } from 'react';
import axios from 'axios';
import { LayoutDashboard, TrendingUp, Zap, Activity, Settings, Bell, Search, BarChart2, Trash2, Plus, Globe } from 'lucide-react';
import ChartModal from './ChartModal';
import XRayModal from './XRayModal';
import TradingChart from './components/TradingChart';
import CalculatorModal from './CalculatorModal';
import './index.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [compositeData, setCompositeData] = useState([]);
  const [compositeLoading, setCompositeLoading] = useState(false);
  const [swingData, setSwingData] = useState([]);
  const [ninjaData, setNinjaData] = useState([]);
  const [kavaleriData, setKavaleriData] = useState([]);
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
  const [selectedStock, setSelectedStock] = useState(null);
  const [portfolioData, setPortfolioData] = useState([]);
  const [selectedChart, setSelectedChart] = useState(null);
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
  const [goapiKey, setGoapiKey] = useState(localStorage.getItem('GOAPI_KEY') || "");

  useEffect(() => {
    if (serverKey) axios.defaults.headers.common['X-API-Key'] = serverKey;
    if (goapiKey) axios.defaults.headers.common['X-GoAPI-Key'] = goapiKey;
    localStorage.setItem('SERVER_API_KEY', serverKey);
    localStorage.setItem('GOAPI_KEY', goapiKey);
  }, [serverKey, goapiKey]);

  // === PREMIUM / FREE MODE TOGGLE ===
  const [isPremium, setIsPremium] = useState(false);

  // Engine Status Tracker
  const [engineStatus, setEngineStatus] = useState('idle');
  const [engineMsg, setEngineMsg] = useState('');
  const [engineElapsed, setEngineElapsed] = useState(0);

  // View Mode & Sorting State
  const [viewMode, setViewMode] = useState('cards'); // 'cards' atau 'table'
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [liveRadar, setLiveRadar] = useState(false);
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
      const res = await axios.get(`${API_BASE}/api/composite?premium=${isPremium}`);
      setCompositeData(res.data.data);
    } catch (err) {
      console.error(err);
    }
    setCompositeLoading(false);
  };

  const fetchSwing = async (forcePremium = isPremium) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/swing?premium=${forcePremium}`);
      setSwingData(res.data.data);
    } catch (err) {
      // Jika premium gagal, fallback ke yahoo finance
      if (forcePremium) {
        console.warn('GoAPI error, fallback ke Yahoo Finance...');
        try {
          const res2 = await axios.get(`${API_BASE}/api/scan/swing?premium=false`);
          setSwingData(res2.data.data);
          setIsPremium(false);
        } catch (err2) { console.error(err2); }
      } else { console.error(err); }
    }
    setLoading(false);
  };

  const fetchKavaleri = async (forcePremium = isPremium) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/kavaleri?premium=${forcePremium}`);
      setKavaleriData(res.data.data);
    } catch (err) {
      if (forcePremium) {
        console.warn('GoAPI error, fallback ke Yahoo Finance...');
        try {
          const res2 = await axios.get(`${API_BASE}/api/scan/kavaleri?premium=false`);
          setKavaleriData(res2.data.data);
          setIsPremium(false);
        } catch (err2) { console.error(err2); }
      } else { console.error(err); }
    }
    setLoading(false);
  };

  const fetchWhale = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/whale`);
      setWhaleData(res.data.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const fetchGlobal = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/global`);
      setGlobalData(res.data.data);
      
      const resAstro = await axios.get(`${API_BASE}/api/astro/forecast`);
      setAstroForecast(resAstro.data.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const fetchNinja = async (forcePremium = isPremium) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/ninja?premium=${forcePremium}`);
      setNinjaData(res.data.data);
    } catch (err) {
      if (forcePremium) {
        console.warn('GoAPI error, fallback ke Yahoo Finance...');
        try {
          const res2 = await axios.get(`${API_BASE}/api/scan/ninja?premium=false`);
          setNinjaData(res2.data.data);
          setIsPremium(false);
        } catch (err2) { console.error(err2); }
      } else { console.error(err); }
    }
    setLoading(false);
  };

  const fetchAll = async () => {
    setLoading(true);
    try {
      if (activeTab === 'swing') {
        const res = await axios.get(`${API_BASE}/api/scan/all-swing?premium=${isPremium}`);
        if (res.data.message) alert(res.data.message);
        setSwingData(res.data.data || []);
      } else if (activeTab === 'kavaleri') {
        const res = await axios.get(`${API_BASE}/api/scan/kavaleri?premium=${isPremium}`);
        if (res.data.message) alert(res.data.message);
        setKavaleriData(res.data.data || []);
      } else {
        const res = await axios.get(`${API_BASE}/api/scan/all-ninja?premium=${isPremium}`);
        if (res.data.message) alert(res.data.message);
        setNinjaData(res.data.data || []);
      }
    } catch (err) {
      console.error(err);
      alert("Gagal scan keseluruhan. Pastikan server nyala.");
    }
    setLoading(false);
  };

  const fetchCandidates = async (mode) => {
    setLoading(true);
    try {
      if (mode === 'swing' || mode === 'kavaleri') {
        const res = await axios.get(${API_BASE}/api/scan/);
        if (mode === 'swing') setSwingData(res.data.data);
        else if (mode === 'kavaleri') setKavaleriData(res.data.data);
      } else {
        const res = await axios.get(${API_BASE}/api/candidates/);
        setNinjaData(res.data.data);
      }
    } catch (err) {
      console.error('Fetch error:', err);
    }
    setLoading(false);
  };

  const runSensus = async () => {
    if (!window.confirm("Menjalankan Sensus akan mereset daftar pantauan (Watchlist) Mode Position Anda dan menggantinya dengan saham super terpilih. Lanjutkan?")) return;
    setSensusLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/sensus`);
      alert(res.data.message);
      fetchWatchlist();
      fetchSwing();
    } catch (err) {
      console.error(err);
      alert("Gagal menjalankan Sensus.");
    }
    setSensusLoading(false);
  };

  const runSensusNinja = async () => {
    if (!window.confirm("Menjalankan Sensus Ninja akan mereset daftar pantauan Mode Scalping Anda dan menggantinya dengan saham gorengan yang sedang meledak volumenya. Lanjutkan?")) return;
    setSensusLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/sensus/ninja`);
      alert(res.data.message);
      fetchWatchlist();
      fetchNinja(); // Reload the ninja screener
    } catch (err) {
      console.error(err);
      alert("Gagal menjalankan Sensus Ninja.");
    }
    setSensusLoading(false);
  };

  const runSensusKavaleri = async () => {
    if (!window.confirm("Menjalankan Sensus Kavaleri akan mereset Watchlist Kavaleri Anda. Lanjutkan?")) return;
    setSensusLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/sensus/kavaleri`);
      alert(res.data.message);
      fetchWatchlist();
      fetchKavaleri(); 
    } catch (err) {
      console.error(err);
      alert("Gagal menjalankan Sensus Kavaleri.");
    }
    setSensusLoading(false);
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

  const buildUniverse = async () => {
    if (!window.confirm("Proses Sensus Saham membutuhkan waktu sekitar 1-2 menit. Jalankan di latar belakang?")) return;
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
    } else if (activeTab === 'swing' && swingData.length === 0) {
      fetchCandidates('swing');
    } else if (activeTab === 'ninja' && ninjaData.length === 0) {
      fetchCandidates('ninja');
    } else if (activeTab === 'kavaleri' && kavaleriData.length === 0) {
      fetchCandidates('kavaleri');
    }
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

  const handleScan = () => {
    // Auto-aktifkan Premium saat VIP Scan ditekan
    setIsPremium(true);
    startEngineTracking('vip');
    const runScan = async () => {
      try {
        if (activeTab === 'swing') await fetchSwing(true);
        else if (activeTab === 'ninja') await fetchNinja(true);
        else if (activeTab === 'kavaleri') await fetchKavaleri(true);
        else if (activeTab === 'whale') await fetchWhale();
        else if (activeTab === 'global') await fetchGlobal();
        stopEngineTracking(true, 'Pemindaian VIP berhasil. Lihat hasil di bawah.');
      } catch (err) {
        stopEngineTracking(false, 'Pemindaian gagal — coba lagi atau gunakan Free Mode.');
      }
    };
    runScan();
  };

  // Sinkronisasi otomatis Sinyal VIP ke Command Center
  useEffect(() => {
    const elite = [];
    swingData.filter(s => s.signal).forEach(s => elite.push({...s, source: 'Position'}));
    kavaleriData.filter(s => s.signal).forEach(s => elite.push({...s, source: 'Swing'}));
    ninjaData.filter(s => s.signal).forEach(s => elite.push({...s, source: 'Scalping'}));
    whaleData.filter(s => s.signal).forEach(s => elite.push({...s, source: 'Radar Paus'}));
    globalData.filter(s => s.signal).forEach(s => elite.push({...s, source: 'Global Astro'}));
    
    setCompositeData(elite);
  }, [swingData, kavaleriData, ninjaData, whaleData, globalData]);

  
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

  const totalScanned = currentData.length;
  const totalSignals = currentData.filter(d => d.signal).length;
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
            <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', background: item.signal ? 'rgba(46, 204, 113, 0.1)' : 'transparent' }}>
              <td style={{ padding: '12px' }}><strong>{item.ticker.replace('.JK', '')}</strong></td>
              <td style={{ padding: '12px' }}>Rp {item.price ? item.price.toLocaleString('id-ID') : '-'}</td>
              <td style={{ padding: '12px' }}>
                <span className={`badge ${item.status ? item.status.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z-]/g,'') : ''}`}>
                  {item.status}
                </span>
              </td>
              <td style={{ padding: '12px', fontSize: '13px' }}>{item.reason || '-'}</td>
              <td style={{ padding: '12px' }}>
                {item.signal ? <span className="badge success">ADA SINYAL</span> : <span className="badge neutral">-</span>}
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
            <li className={`sidebar-item elite-home ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>
              <LayoutDashboard size={18} color="#00ffcc" />
              <span style={{color: '#00ffcc', fontWeight: 'bold', textShadow: '0 0 5px rgba(0, 255, 204, 0.5)'}}>Command Center</span>
            </li>
            <li className={`sidebar-item ${['swing', 'kavaleri', 'ninja'].includes(activeTab) ? 'active' : ''}`} onClick={() => setActiveTab('swing')}>
              <TrendingUp size={18} />
              Screener IDX
            </li>
            <li className={`sidebar-item ${activeTab === 'news' ? 'active' : ''}`} onClick={() => setActiveTab('news')}>
              <Activity size={18} />
              Berita dan IPO
            </li>

          <li className={`sidebar-item premium-glow ${activeTab === 'global' ? 'active' : ''}`} onClick={() => setActiveTab('global')}>
            <Globe size={18} color="#f1c40f" />
            <span style={{color: '#f1c40f', fontWeight: 'bold'}}>Global Astro</span>
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
            {activeTab === 'home' ? 'Ultimate Command Center' : ['swing', 'kavaleri', 'ninja'].includes(activeTab) ? 'Master Scanner IDX' : activeTab === 'news' ? 'Berita & IPO' : activeTab === 'whale' ? 'Radar Paus (Whale Tracker)' : activeTab === 'global' ? 'Global Markets' : activeTab === 'portfolio' ? 'Portofolio Robot' : 'Pengaturan Watchlist'}
          </h1>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>

            {/* === PREMIUM TOGGLE BUTTON === */}
            <div
              id="premium-toggle"
              onClick={() => setIsPremium(p => !p)}
              title={isPremium ? 'Mode PREMIUM aktif (GoAPI VIP - Token terpotong)' : 'Mode GRATIS aktif (Yahoo Finance - Tidak potong token)'}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer',
                padding: '6px 14px',
                borderRadius: '999px',
                border: isPremium ? '1px solid #f1c40f' : '1px solid rgba(255,255,255,0.2)',
                background: isPremium
                  ? 'linear-gradient(135deg, rgba(241,196,15,0.25), rgba(230,126,34,0.15))'
                  : 'rgba(255,255,255,0.07)',
                transition: 'all 0.3s ease',
                userSelect: 'none',
                boxShadow: isPremium ? '0 0 12px rgba(241,196,15,0.4)' : 'none',
              }}
            >
              {/* Toggle Track */}
              <div style={{
                position: 'relative',
                width: '38px',
                height: '20px',
                borderRadius: '999px',
                background: isPremium ? 'linear-gradient(90deg, #f1c40f, #e67e22)' : 'rgba(255,255,255,0.15)',
                transition: 'background 0.3s ease',
                flexShrink: 0,
              }}>
                <div style={{
                  position: 'absolute',
                  top: '3px',
                  left: isPremium ? '20px' : '3px',
                  width: '14px',
                  height: '14px',
                  borderRadius: '50%',
                  background: 'white',
                  transition: 'left 0.3s ease',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
                }} />
              </div>
              <span style={{
                fontSize: '12px',
                fontWeight: '700',
                color: isPremium ? '#f1c40f' : '#aaa',
                letterSpacing: '0.5px',
                transition: 'color 0.3s',
              }}>
                {isPremium ? 'PREMIUM ON' : 'FREE MODE'}
              </span>
            </div>

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
            {['swing', 'kavaleri', 'ninja'].includes(activeTab) && (
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
                    <button
                      className="btn-scan"
                      onClick={buildUniverse}
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
              </>
            )}

            {/* Results Container */}
            <div className="results-container">
              <div className="scanner-header" style={{ justifyContent: 'space-between' }}>
                <div style={{display: 'flex', gap: '10px'}}>
                  {['swing', 'ninja', 'kavaleri'].includes(activeTab) && (
                    <>
                      <button className={`btn-toggle ${viewMode === 'cards' ? 'active' : ''}`} onClick={() => setViewMode('cards')} style={{ padding: '8px 12px', background: viewMode === 'cards' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: viewMode === 'cards' ? 'black' : 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>💳 Cards</button>
                      <button className={`btn-toggle ${viewMode === 'table' ? 'active' : ''}`} onClick={() => setViewMode('table')} style={{ padding: '8px 12px', background: viewMode === 'table' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: viewMode === 'table' ? 'black' : 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>📄 Table</button>
                    </>
                  )}
                </div>
                <div style={{display:'flex', gap:'10px', alignItems: 'center'}}>
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
                  <button className="btn-scan" onClick={handleScan} disabled={loading} style={{background: 'var(--color-green)', color: 'black'}}>
                    {loading ? <div className="loader"></div> : <Search size={18} />}
                    {loading ? 'Memindai...' : 'Mulai Pemindaian VIP'}
                  </button>
                </div>
              </div>

              {viewMode === 'table' && ['swing', 'ninja', 'kavaleri'].includes(activeTab) ? (
                renderTable()
              ) : (
                <div className="stock-grid">
                  {currentData.length === 0 && !loading && (
                    <p style={{ color: 'var(--text-muted)' }}>Belum ada data. Klik tombol "Mulai Pindai".</p>
                  )}
                  
                  {currentData.map((stock) => (
                    <div 
                      key={stock.ticker} 
                      className={`stock-card ${stock.signal ? (activeTab === 'swing' ? 'highlight-green' : 'highlight-pink') : ''}`}
                      onClick={() => setSelectedStock(stock)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="stock-card-header">
                        <div>
                          <div className="ticker">{stock.ticker}</div>
                          <div className="price">Rp {stock.price.toLocaleString('id-ID')}</div>
                        </div>
                        <div className={`badge ${stock.status.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z-]/g,'')}`}>
                          {stock.status}
                        </div>
                      </div>
                      <div className="reason">{stock.reason}</div>
                      
                      {activeTab === 'whale' && (
                        <div className="tp-sl-container" style={{ marginTop: '10px' }}>
                          <div className="tp-sl-row">
                            <div className="tp-block">
                              <span className="tp-label">TOP BUYER</span>
                              <span className="tp-value" style={{ color: '#fff' }}>{stock.top_buyer}</span>
                              <span className="tp-pct tp-up">+{stock.net_volume.toLocaleString('id-ID')} Lot</span>
                            </div>
                            <div className="sl-block">
                              <span className="tp-label">MODAL BANDAR</span>
                              <span className="tp-value sl-val">Rp {stock.avg_price.toLocaleString('id-ID')}</span>
                              <span className={`tp-pct ${stock.diff_pct < 0 ? 'sl-down' : 'tp-up'}`}>{stock.diff_pct}%</span>
                            </div>
                          </div>
                          {stock.is_golden && (
                            <div className="rr-row" style={{ color: 'var(--color-green)' }}>
                              <strong>🌟 GOLDEN ENTRY (Aman)</strong>
                            </div>
                          )}
                          {stock.is_danger && (
                            <div className="rr-row" style={{ color: '#ff4757' }}>
                              <strong>🚨 RAWAN GUYURAN (Tinggi)</strong>
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div style={{display: 'flex', gap: '10px'}}>
                        <button className="btn-chart" onClick={() => setSelectedChart({ticker: stock.ticker, tp: stock.tp, sl: stock.sl})}>
                          📈 Buka Grafik
                        </button>
                        
                        {stock.sl && (
                          <button className="btn-calc" onClick={() => setSelectedCalc(stock)}>
                            🛡️ Hitung Lot
                          </button>
                        )}
                      </div>
                      
                      {stock.sentiment && stock.sentiment !== 'NETRAL' && (
                        <div className={`sentiment-badge ${stock.sentiment.includes('POSITIF') ? 'pos' : stock.sentiment.includes('NEGATIF') ? 'neg' : 'net'}`}>
                          {stock.sentiment.includes('POSITIF') ? '✔' : '⚠'} Berita: {stock.sentiment}
                        </div>
                      )}

                      {activeTab === 'kavaleri' && (
                        <div style={{marginTop: '10px', display: 'flex', gap: '5px'}}>
                          {stock.squeeze_fired && (
                            <span style={{background: '#ffa502', color: '#000', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold'}}>💣 SQUEEZE FIRED</span>
                          )}
                          {stock.smc_trap && (
                            <span style={{background: '#ff4757', color: '#fff', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold'}}>🏦 SMC TRAP DETECTED</span>
                          )}
                        </div>
                      )}
                      
                      {stock.signal && stock.tp && stock.sl && (
                        <div className="tp-sl-container">
                          <div className="tp-sl-row">
                            <div className="tp-block">
                              <span className="tp-label">TARGET PROFIT</span>
                              <span className="tp-value">Rp {Number(stock.tp).toLocaleString('id-ID')}</span>
                              <span className="tp-pct tp-up">+{(((stock.tp - stock.price) / stock.price) * 100).toFixed(1)}%</span>
                            </div>
                            <div className="sl-block">
                              <span className="tp-label">STOP LOSS</span>
                              <span className="tp-value sl-val">Rp {Number(stock.sl).toLocaleString('id-ID')}</span>
                              <span className="tp-pct sl-down">{(((stock.sl - stock.price) / stock.price) * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                          {stock.rr && (
                            <div className="rr-row">
                              Risk/Reward: <strong>{stock.rr}x</strong>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* --- TAB GLOBAL --- */}
        {activeTab === 'global' && (
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
                  <label style={{ display: 'block', marginBottom: 6, fontSize: 13, color: 'var(--color-green)' }}>Kunci Server (X-API-Key)</label>
                  <input type="password" value={serverKey} onChange={e => setServerKey(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="Masukkan Kunci Server" />
                </div>
                <div style={{ flex: 1, minWidth: 250 }}>
                  <label style={{ display: 'block', marginBottom: 6, fontSize: 13, color: 'var(--color-blue)' }}>Kunci Provider (GoAPI VIP)</label>
                  <input type="password" value={goapiKey} onChange={e => setGoapiKey(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="Masukkan Kunci GoAPI" />
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
    </div>
  );
}

export default App;
