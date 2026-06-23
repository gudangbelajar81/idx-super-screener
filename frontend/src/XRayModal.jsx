import React from 'react';
import { X, CheckCircle, AlertTriangle, ShieldAlert } from 'lucide-react';
import ChartModal from './ChartModal';
import ReactMarkdown from 'react-markdown';

const XRayModal = ({ data, onClose }) => {
  if (!data) return null;

  const { ticker, price, daily, intraday, news, mentor_advice } = data;

  const getStatusColor = (signal) => signal ? 'var(--color-green)' : 'var(--color-pink)';
  const getSentimentColor = (sentiment) => {
    if (!sentiment) return '#aaa';
    if (sentiment.includes('POSITIF')) return 'var(--color-green)';
    if (sentiment.includes('NEGATIF')) return 'var(--color-pink)';
    return '#aaa';
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '600px', width: '95%', background: '#111', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}>
        
        {/* Header */}
        <div className="modal-header" style={{ padding: '20px', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
          <div>
            <h2 style={{ margin: 0, color: 'white', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🔍 X-Ray Report: {ticker}
            </h2>
            <span style={{ color: '#aaa', fontSize: '14px' }}>Harga Terakhir: Rp {price.toLocaleString('id-ID')}</span>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }}>
            <X size={24} />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body" style={{ padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Mentor Advice Box */}
          <div style={{ background: 'rgba(41, 121, 255, 0.1)', border: '1px solid rgba(41, 121, 255, 0.3)', padding: '16px', borderRadius: '8px' }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#2979ff', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={18} /> Kesimpulan Mentor Robot
            </h3>
            <div className="markdown-body" style={{ color: '#d1d5db', lineHeight: '1.6', fontSize: '14px' }}>
              <ReactMarkdown>{mentor_advice}</ReactMarkdown>
            </div>
          </div>

          {/* Quick Stats Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            
            {/* Bandarmologi (GoAPI) */}
            {data.broker && (
            <div style={{ background: '#1a1a1a', padding: '16px', borderRadius: '8px', borderLeft: `4px solid ${data.broker.status === 'AKUMULASI' ? 'var(--color-green)' : 'var(--color-pink)'}`, gridColumn: '1 / -1' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#fff', fontSize: '13px', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '6px' }}>
                👑 Bandarmologi (Data GoAPI)
              </h4>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>Aksi Bandar: <strong style={{color: data.broker.status === 'AKUMULASI' ? 'var(--color-green)' : 'var(--color-pink)'}}>{data.broker.status}</strong></p>
                  <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>Top Buyer: <strong style={{ color: 'var(--color-green)' }}>{data.broker.top_buyer}</strong></p>
                  <p style={{ margin: 0, color: '#aaa', fontSize: '13px' }}>Top Seller: <strong style={{ color: 'var(--color-pink)' }}>{data.broker.top_seller}</strong></p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>Net Vol: <strong>{data.broker.net_volume?.toLocaleString('id-ID') || 0} Lot</strong></p>
                  <p style={{ margin: 0, color: '#aaa', fontSize: '13px' }}>Avg Price: <strong>Rp {data.broker.avg_price?.toLocaleString('id-ID') || 0}</strong></p>
                </div>
              </div>
              
              {/* Highlight Jejak Kaki Bandar */}
              {data.broker.jejak_kaki && data.broker.jejak_kaki.is_golden && (
                 <div style={{ marginTop: '12px', padding: '8px', background: 'rgba(0, 255, 0, 0.1)', border: '1px solid var(--color-green)', borderRadius: '4px', color: 'var(--color-green)', fontSize: '12px', fontWeight: 'bold', textAlign: 'center' }}>
                   ✨ GOLDEN ENTRY: Harga saat ini ({data.price}) berada di bawah/sama dengan modal Bandar! ✨
                 </div>
              )}
              {data.broker.jejak_kaki && data.broker.jejak_kaki.is_danger && (
                 <div style={{ marginTop: '12px', padding: '8px', background: 'rgba(255, 0, 0, 0.1)', border: '1px solid var(--color-pink)', borderRadius: '4px', color: 'var(--color-pink)', fontSize: '12px', fontWeight: 'bold', textAlign: 'center' }}>
                   🚨 RAWAN GUYURAN: Harga sudah melonjak terlalu jauh dari modal Bandar! 🚨
                 </div>
              )}
            </div>
            )}

            {/* Swing Daily */}
            <div style={{ background: '#1a1a1a', padding: '16px', borderRadius: '8px', borderLeft: `4px solid ${getStatusColor(daily.signal)}` }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#fff', fontSize: '13px', textTransform: 'uppercase' }}>📊 Swing (Daily)</h4>
              <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>Status: <strong style={{color: getStatusColor(daily.signal)}}>{daily.signal ? 'Uptrend' : 'Downtrend'}</strong></p>
              <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>CMF (Arus Uang): <strong>{daily.cmf}</strong></p>
              <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>TP: <strong>{daily.tp ? `Rp ${daily.tp.toLocaleString('id-ID')}` : '-'}</strong></p>
              <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>SL 1 (Terdekat): <strong>{daily.sl ? `Rp ${daily.sl.toLocaleString('id-ID')}` : '-'}</strong></p>
              <p style={{ margin: 0, color: '#aaa', fontSize: '13px' }}>SL 2 (Kuat): <strong>{daily.sl2 ? `Rp ${daily.sl2.toLocaleString('id-ID')}` : '-'}</strong> {daily.sl2_uji ? <span style={{fontSize: '11px', color: '#ffb300'}}>(Diuji {daily.sl2_uji}x)</span> : null}</p>
            </div>

            {/* Ninja 5m */}
            <div style={{ background: '#1a1a1a', padding: '16px', borderRadius: '8px', borderLeft: `4px solid ${getStatusColor(intraday.signal)}` }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#fff', fontSize: '13px', textTransform: 'uppercase' }}>🥷 Ninja (5-Menit)</h4>
              <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>Status: <strong style={{color: getStatusColor(intraday.signal)}}>{intraday.signal ? 'Vol Spikes!' : 'Sepi'}</strong></p>
              <p style={{ margin: '0 0 4px 0', color: '#aaa', fontSize: '13px' }}>Akumulasi (OBV): <strong>{intraday.obv_trend || 'N/A'}</strong></p>
              <p style={{ margin: 0, color: '#aaa', fontSize: '13px' }}>Bandar (CMF): <strong>{intraday.cmf}</strong></p>
            </div>

          </div>

          {/* News Sentiment */}
          <div style={{ background: '#1a1a1a', padding: '16px', borderRadius: '8px' }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#fff', fontSize: '13px', textTransform: 'uppercase' }}>📰 Sentimen Berita</h4>
            <p style={{ margin: 0, color: getSentimentColor(news.sentiment), fontWeight: 'bold' }}>
              {news.sentiment} ({news.news_count} Berita)
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default XRayModal;
