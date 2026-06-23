import React, { useState, useEffect } from 'react';
import { Target, Activity, ShieldAlert, ChevronDown, ChevronUp, PlayCircle, Info } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const InstitutionalRadar = ({ apiKey }) => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [expandedRow, setExpandedRow] = useState(null);

  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/institutional/candidates`);
      setCandidates(res.data.data || []);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  const startScan = async () => {
    setScanning(true);
    try {
      const res = await axios.post(`${API_BASE}/api/institutional/build`, {}, {
        headers: { 'X-API-Key': apiKey }
      });
      alert(res.data.message);
    } catch (err) {
      alert("Gagal memulai sensus: " + err);
    }
    setScanning(false);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--color-green)';
    if (score >= 60) return '#ffb300';
    return 'var(--color-pink)';
  };

  return (
    <div className="section-container" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={28} color="var(--color-purple)" />
            Institutional Narrative Engine
          </h2>
          <p style={{ color: '#aaa', margin: '4px 0 0 0', fontSize: '14px' }}>
            Melacak saham dengan akselerasi laba, akumulasi bandar, dan narasi katalis terkuat.
          </p>
        </div>
        <button 
          onClick={startScan} 
          disabled={scanning}
          style={{
            background: 'var(--color-purple)',
            color: '#fff',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '8px',
            fontWeight: 'bold',
            cursor: scanning ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 0 15px rgba(186, 104, 200, 0.4)'
          }}
        >
          <PlayCircle size={20} />
          {scanning ? 'Menjalankan Radar...' : 'Jalankan Radar Institusi'}
        </button>
      </div>

      <div style={{ background: '#111', borderRadius: '12px', border: '1px solid #333', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', color: '#eee' }}>
          <thead>
            <tr style={{ background: '#1a1a1a', borderBottom: '2px solid #333' }}>
              <th style={{ padding: '16px', textAlign: 'left' }}>Ticker</th>
              <th style={{ padding: '16px', textAlign: 'center' }}>Composite Score</th>
              <th style={{ padding: '16px', textAlign: 'center' }}>Narrative</th>
              <th style={{ padding: '16px', textAlign: 'center' }}>Growth</th>
              <th style={{ padding: '16px', textAlign: 'center' }}>Flow</th>
              <th style={{ padding: '16px', textAlign: 'right' }}>Rekomendasi</th>
              <th style={{ padding: '16px', textAlign: 'center' }}>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', padding: '40px' }}>Memuat radar...</td></tr>
            ) : candidates.length === 0 ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', padding: '40px' }}>Belum ada data. Silakan Jalankan Radar.</td></tr>
            ) : (
              candidates.map((c) => (
                <React.Fragment key={c.ticker}>
                  <tr style={{ borderBottom: '1px solid #222', background: expandedRow === c.ticker ? '#1a1a1a' : 'transparent' }}>
                    <td style={{ padding: '16px', fontWeight: 'bold', fontSize: '18px' }}>{c.ticker}</td>
                    <td style={{ padding: '16px', textAlign: 'center' }}>
                      <span style={{ 
                        background: 'rgba(255,255,255,0.1)', 
                        color: getScoreColor(c.composite_score),
                        padding: '6px 12px', 
                        borderRadius: '20px', 
                        fontWeight: 'bold',
                        fontSize: '16px'
                      }}>
                        {c.composite_score}
                      </span>
                    </td>
                    <td style={{ padding: '16px', textAlign: 'center', color: getScoreColor(c.catalyst_score) }}>{c.catalyst_score}</td>
                    <td style={{ padding: '16px', textAlign: 'center', color: getScoreColor(c.growth_score) }}>{c.growth_score}</td>
                    <td style={{ padding: '16px', textAlign: 'center', color: getScoreColor(c.confirmation_score) }}>{c.confirmation_score}</td>
                    <td style={{ padding: '16px', textAlign: 'right' }}>
                      <span style={{
                        background: c.rekomendasi.includes('Buy') ? 'rgba(0,255,0,0.1)' : 'rgba(255,255,255,0.1)',
                        color: c.rekomendasi.includes('Buy') ? 'var(--color-green)' : '#aaa',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {c.rekomendasi}
                      </span>
                    </td>
                    <td style={{ padding: '16px', textAlign: 'center' }}>
                      <button 
                        onClick={() => setExpandedRow(expandedRow === c.ticker ? null : c.ticker)}
                        style={{ background: 'transparent', border: '1px solid #444', color: '#fff', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}
                      >
                        {expandedRow === c.ticker ? 'Tutup' : 'Detail AI'}
                      </button>
                    </td>
                  </tr>
                  
                  {expandedRow === c.ticker && (
                    <tr style={{ background: '#0a0a0a' }}>
                      <td colSpan="7" style={{ padding: '20px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                          
                          {/* Narasi Alasan Institusi */}
                          <div style={{ background: '#111', padding: '16px', borderRadius: '8px', borderLeft: '4px solid var(--color-purple)' }}>
                            <h4 style={{ margin: '0 0 10px 0', color: 'var(--color-purple)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <Target size={18} /> Thesis Institusi
                            </h4>
                            <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', color: '#ccc' }}>
                              {c.alasan_institusi}
                            </p>
                          </div>

                          {/* Faktor Pertumbuhan & Flow */}
                          <div style={{ background: '#111', padding: '16px', borderRadius: '8px', borderLeft: '4px solid var(--color-green)' }}>
                            <h4 style={{ margin: '0 0 10px 0', color: 'var(--color-green)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <Activity size={18} /> Bukti Akselerasi & Flow
                            </h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6', color: '#ccc' }}>
                              <strong>Katalis Pertumbuhan:</strong> {c.faktor_pertumbuhan}
                              {c.faktor_pertumbuhan.includes('Cek') && (
                                <div style={{ marginTop: '8px', padding: '8px', background: 'rgba(255, 179, 0, 0.1)', color: '#ffb300', borderRadius: '4px', border: '1px solid #ffb300' }}>
                                  <Info size={14} style={{ display: 'inline', marginRight: '4px', position: 'relative', top: '2px' }} />
                                  Tugas Bos: Buka RTI Business untuk cek EPS Growth & ROE. Buka Stockbit untuk cek Foreign Flow saham ini secara manual!
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Target Return & Risiko */}
                          <div style={{ background: '#111', padding: '16px', borderRadius: '8px', gridColumn: '1 / -1', display: 'flex', justifyContent: 'space-between' }}>
                            <div style={{ flex: 1 }}>
                              <h4 style={{ margin: '0 0 8px 0', color: '#aaa', fontSize: '13px' }}>Target Return (15 Hari)</h4>
                              <p style={{ margin: 0, color: 'var(--color-green)', fontWeight: 'bold', fontSize: '18px' }}>{c.expected_return_15d}</p>
                            </div>
                            <div style={{ flex: 1 }}>
                              <h4 style={{ margin: '0 0 8px 0', color: '#aaa', fontSize: '13px' }}>Target Return (3 Bulan)</h4>
                              <p style={{ margin: 0, color: 'var(--color-green)', fontWeight: 'bold', fontSize: '18px' }}>{c.expected_return_3m}</p>
                            </div>
                            <div style={{ flex: 2, borderLeft: '1px solid #333', paddingLeft: '20px' }}>
                              <h4 style={{ margin: '0 0 8px 0', color: 'var(--color-pink)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <ShieldAlert size={14} /> Risiko Utama
                              </h4>
                              <p style={{ margin: 0, color: '#ccc', fontSize: '14px' }}>{c.risiko_utama}</p>
                            </div>
                          </div>

                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InstitutionalRadar;
