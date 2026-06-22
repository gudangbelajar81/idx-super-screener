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
  // isPremium=true -> GoAPI VIP (potong token), isPremium=false -> Yahoo Finance (gratis)
  const [isPremium, setIsPremium] = useState(false);

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

  const fetchSwing = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/swing?premium=${isPremium}`);
      setSwingData(res.data.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const fetchKavaleri = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/kavaleri?premium=${isPremium}`);
      setKavaleriData(res.data.data);
    } catch (err) {
      console.error(err);
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

  const fetchNinja = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/scan/ninja?premium=${isPremium}`);
      setNinjaData(res.data.data);
    } catch (err) {
      console.error(err);
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

  const runSensus = async () => {
    if (!window.confirm("Menjalankan Sensus akan mereset daftar pantauan (Watchlist) Mode Benteng Anda dan menggantinya dengan saham super terpilih. Lanjutkan?")) return;
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
    if (!window.confirm("Menjalankan Sensus Ninja akan mereset daftar pantauan Mode Ninja Anda dan menggantinya dengan saham gorengan yang sedang meledak volumenya. Lanjutkan?")) return;
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
    if (!window.confirm("Proses Sensus Saham membutuhkan waktu 1-2 menit. Lanjutkan?")) return;
    setBuildingUniverse(true);
    try {
      const res = await axios.post(`${API_BASE}/api/universe/build`);
      alert(`Sensus Berhasil! ${res.data.total} saham telah diklasifikasikan ke dalam Ember Swing dan Ninja.`);
    } catch (err) {
      console.error(err);
      alert("Sensus Gagal. Cek terminal server.");
    }
    setBuildingUniverse(false);
  };

  useEffect(() => {
    if (activeTab === 'settings') {
      fetchWatchlist();
    } else if (activeTab === 'portfolio') {
      fetchPortfolio();
    }
    // Fetch IPO news only once when first loading (or can be done unconditionally)
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
    if (activeTab === 'swing') fetchSwing();
    else if (activeTab === 'ninja') fetchNinja();
    else if (activeTab === 'kavaleri') fetchKavaleri();
    else if (activeTab === 'whale') fetchWhale();
    else if (activeTab === 'global') fetchGlobal();
  };

  const currentData = activeTab === 'swing' ? swingData : activeTab === 'ninja' ? ninjaData : activeTab === 'kavaleri' ? kavaleriData : whaleData;
  const totalScanned = currentData.length;
  const totalSignals = currentData.filter(d => d.signal).length;
  const winRate = totalScanned ? Math.round((totalSignals / totalScanned) * 100) : 0;

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
              Menu IDX
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

                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px' }}>
                  <button className="btn-scan" onClick={() => setActiveTab('swing')} style={{ background: activeTab === 'swing' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'swing' ? 'black' : 'white', borderRadius: '8px' }}>
                    Mode Benteng
                  </button>
                  <button className="btn-scan" onClick={() => setActiveTab('kavaleri')} style={{ background: activeTab === 'kavaleri' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'kavaleri' ? 'black' : 'white', borderRadius: '8px' }}>
                    Mode Kavaleri
                  </button>
                  <button className="btn-scan" onClick={() => setActiveTab('ninja')} style={{ background: activeTab === 'ninja' ? 'var(--color-green)' : 'rgba(255,255,255,0.1)', color: activeTab === 'ninja' ? 'black' : 'white', borderRadius: '8px' }}>
                    Mode Ninja
                  </button>
                </div>
              </>
            )}

            {/* Results Container */}
            <div className="results-container">
              <div className="scanner-header">
                <div>
                  <h2 style={{fontSize: '24px', margin: 0}}>{activeTab === 'swing' ? 'Alpha Engine v2' : activeTab === 'kavaleri' ? 'The Detonator Engine' : activeTab === 'whale' ? 'Whale Tracker v1' : 'Live Market Scanner'}</h2>
                  {activeTab === 'whale' && (
                    <p style={{ margin: '5px 0 0 0', color: 'var(--text-muted)' }}>Otomatis memindai Broker Asing / Paus pada Watchlist</p>
                  )}
                </div>
                <div style={{display:'flex', gap:'10px'}}>
                  <button className="btn-scan" onClick={handleScan} disabled={loading} style={{background: 'var(--color-green)', color: 'black'}}>
                    {loading ? <div className="loader"></div> : <Search size={18} />}
                    {loading ? 'Memindai...' : 'Mulai Pemindaian VIP'}
                  </button>
                </div>
              </div>

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
                <option value="swing">Mode Benteng (Swing)</option>
                <option value="scalp">Mode Ninja (Scalping)</option>
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
