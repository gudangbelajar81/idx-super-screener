import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import axios from 'axios';
import { X } from 'lucide-react';

const ChartModal = ({ stock, onClose }) => {
  const chartContainerRef = useRef();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let chart;
    let isMounted = true;
    const fetchAndRender = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/api/chart/${stock.ticker}`);
        const data = res.data.data;
        
        if (!isMounted) return;
        
        if (!data || data.length === 0) {
          setLoading(false);
          return;
        }

        // Clear previous children just in case
        if (chartContainerRef.current) {
          chartContainerRef.current.innerHTML = '';
        }

        chart = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth,
          height: 350,
          layout: {
            background: { type: 'solid', color: '#111' },
            textColor: '#d1d5db',
          },
          grid: {
            vertLines: { color: '#333' },
            horzLines: { color: '#333' },
          },
          crosshair: {
            mode: 1, // Magnet
          },
          timeScale: {
            borderColor: '#333',
            timeVisible: true,
          },
        });

        const candlestickSeries = chart.addCandlestickSeries({
          upColor: '#10b981',
          downColor: '#ef4444',
          borderVisible: false,
          wickUpColor: '#10b981',
          wickDownColor: '#ef4444',
        });

        candlestickSeries.setData(data);

        // Add TP/SL Lines if available
        if (stock.tp) {
          candlestickSeries.createPriceLine({
            price: stock.tp,
            color: '#10b981',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'Take Profit',
          });
        }
        
        if (stock.sl) {
          candlestickSeries.createPriceLine({
            price: stock.sl,
            color: '#ef4444',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'Stop Loss',
          });
        }

        // Add Volume Histogram
        const volumeSeries = chart.addHistogramSeries({
          color: '#26a69a',
          priceFormat: {
            type: 'volume',
          },
          priceScaleId: '', // set as an overlay
          scaleMargins: {
            top: 0.8, // highest point of the series will be at 80% of the chart height
            bottom: 0,
          },
        });

        const volumeData = data.map(d => ({
          time: d.time,
          value: d.value,
          color: d.close > d.open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
        }));
        
        volumeSeries.setData(volumeData);

        chart.timeScale().fitContent();
        setLoading(false);
      } catch (err) {
        console.error(err);
        if (isMounted) setLoading(false);
      }
    };

    fetchAndRender();

    const handleResize = () => {
      if (chart && chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      isMounted = false;
      window.removeEventListener('resize', handleResize);
      if (chart) {
        chart.remove();
      }
    };
  }, [stock]);

  return (
    <div className="modal-overlay">
      <div className="modal-content chart-modal" style={{ maxWidth: '800px', width: '95%', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}>
        <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', borderBottom: '1px solid #333', flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
            <h2 style={{ margin: 0, color: 'white' }}>{stock.ticker}</h2>
            <span style={{ fontSize: '18px', color: '#aaa' }}>
              Rp {stock.price.toLocaleString('id-ID')}
            </span>
            <span style={{ background: stock.signal ? '#10b981' : '#444', padding: '4px 8px', borderRadius: '4px', color: 'white', fontSize: '12px' }}>
              {stock.status}
            </span>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }}>
            <X size={24} />
          </button>
        </div>
        <div className="modal-body" style={{ background: '#111', display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
          <div style={{ position: 'relative', minHeight: '350px', width: '100%' }}>
            {loading && (
              <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'white', zIndex: 10 }}>
                Loading Chart...
              </div>
            )}
            <div ref={chartContainerRef} style={{ width: '100%', height: '350px' }} />
          </div>
          
          <div className="chart-info-panel" style={{ padding: '16px', background: '#1a1a1a', borderTop: '1px solid #333', color: '#ccc', fontSize: '14px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <h4 style={{ margin: '0 0 8px 0', color: '#fff', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>📝 Alasan Deteksi</h4>
              <p style={{ margin: 0, lineHeight: '1.5', color: 'var(--color-green)' }}>{stock.reason}</p>
              
              {stock.sentiment && (
                <div style={{ marginTop: '12px' }}>
                  <h4 style={{ margin: '0 0 8px 0', color: '#fff', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>📰 Sentimen Berita</h4>
                  <p style={{ margin: 0, color: stock.sentiment.includes('POSITIF') ? 'var(--color-green)' : (stock.sentiment.includes('NEGATIF') ? 'var(--color-pink)' : '#aaa') }}>
                    {stock.sentiment}
                  </p>
                </div>
              )}
            </div>
            
            <div>
              <h4 style={{ margin: '0 0 8px 0', color: '#fff', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>🎯 Target Trading</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '6px' }}>
                  <span>Harga Masuk (Buy):</span>
                  <strong style={{ color: '#fff' }}>Rp {stock.price.toLocaleString('id-ID')}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(16, 185, 129, 0.1)', padding: '8px', borderRadius: '6px' }}>
                  <span>Take Profit (TP):</span>
                  <strong style={{ color: 'var(--color-green)' }}>{stock.tp ? `Rp ${stock.tp.toLocaleString('id-ID')}` : 'Tidak Ada'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(239, 68, 68, 0.1)', padding: '8px', borderRadius: '6px' }}>
                  <span>Stop Loss (SL):</span>
                  <strong style={{ color: 'var(--color-pink)' }}>{stock.sl ? `Rp ${stock.sl.toLocaleString('id-ID')}` : 'Tidak Ada'}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartModal;
