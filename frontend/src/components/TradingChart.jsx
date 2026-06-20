import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import axios from 'axios';

const TradingChart = ({ ticker, tp, sl, isGlobal = false, onClose }) => {
  const chartContainerRef = useRef();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let chart = null;
    let candlestickSeries = null;
    let volumeSeries = null;

    let isMounted = true;

    const initChart = async () => {
      try {
        setLoading(true);
        const url = isGlobal ? `http://localhost:8000/api/chart/${ticker}?is_global=true` : `http://localhost:8000/api/chart/${ticker}`;
        const res = await axios.get(url);
        
        if (!isMounted) return;
        
        const data = res.data.data;
        const markers = res.data.markers || [];

        if (!data || data.length === 0) {
          setError("Data grafik tidak ditemukan.");
          setLoading(false);
          return;
        }

        // Bersihkan container jika ada sisa grafik (StrictMode bug)
        if (chartContainerRef.current) {
          chartContainerRef.current.innerHTML = '';
        }

        // Initialize Chart
        chart = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth,
          height: 400,
          layout: {
            background: { type: 'solid', color: '#131722' },
            textColor: '#d1d4dc',
          },
          grid: {
            vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
            horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
          },
          crosshair: {
            mode: 0,
          },
          timeScale: {
            borderColor: '#2B2B43',
            timeVisible: true,
          },
        });

        // Add Candlestick Series
        candlestickSeries = chart.addCandlestickSeries({
          upColor: '#26a69a',
          downColor: '#ef5350',
          borderVisible: false,
          wickUpColor: '#26a69a',
          wickDownColor: '#ef5350',
        });

        candlestickSeries.setData(data.map(item => ({
          time: item.time,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        })));

        // Add TP and SL Lines
        if (tp) {
          candlestickSeries.createPriceLine({
            price: tp,
            color: '#26a69a',
            lineWidth: 2,
            lineStyle: 2, // Dashed
            axisLabelVisible: true,
            title: '🎯 TARGET PROFIT',
          });
        }

        if (sl) {
          candlestickSeries.createPriceLine({
            price: sl,
            color: '#ef5350',
            lineWidth: 2,
            lineStyle: 2, // Dashed
            axisLabelVisible: true,
            title: '🛑 STOP LOSS',
          });
        }
        
        // Add Astro Markers
        if (markers && markers.length > 0) {
            // Urutkan marker berdasar waktu dan filter marker yang berada dalam rentang data
            const validTimes = new Set(data.map(d => d.time));
            const validMarkers = markers.filter(m => validTimes.has(m.time));
            // Hapus duplikat marker untuk hari yang sama
            const uniqueMarkers = validMarkers.filter((v,i,a)=>a.findIndex(v2=>(v2.time===v.time && v2.text===v.text))===i);
            
            candlestickSeries.setMarkers(uniqueMarkers.sort((a,b) => new Date(a.time) - new Date(b.time)));
        }

        // Fit Content
        chart.timeScale().fitContent();
        setLoading(false);

      } catch (err) {
        console.error("Chart Error:", err);
        setError("Gagal memuat grafik.");
        setLoading(false);
      }
    };

    initChart();

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
  }, [ticker, tp, sl]);

  return (
    <div className="trading-chart-modal">
      <div className="trading-chart-content">
        <div className="trading-chart-header">
          <h2>📊 Grafik Harian: {ticker}</h2>
          <button onClick={onClose} className="btn-close-chart">✖ Tutup</button>
        </div>
        
        {loading && <div className="chart-loading">Memuat Data Lilin (Candlestick)...</div>}
        {error && <div className="chart-error">{error}</div>}
        
        <div 
          style={{ width: '100%', height: '400px', position: 'relative', visibility: loading || error ? 'hidden' : 'visible' }}
        >
          <div ref={chartContainerRef} style={{ width: '100%', height: '100%' }} />
        </div>
      </div>
    </div>
  );
};

export default TradingChart;
