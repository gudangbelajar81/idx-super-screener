import React, { useState, useEffect } from 'react';

const CalculatorModal = ({ stock, onClose }) => {
  const [capital, setCapital] = useState(100000000); // Default 100 Juta
  const [riskPct, setRiskPct] = useState(1); // Default 1%

  // Jika tidak ada SL, tidak bisa dihitung
  if (!stock || !stock.sl) return null;

  const entry = stock.price;
  const sl = stock.sl;
  
  // Validasi SL
  const lossPerShare = entry - sl;
  const lossPerLot = lossPerShare * 100;
  
  let maxLots = 0;
  let totalCost = 0;
  let projectedLoss = 0;
  let maxRiskAllowed = 0;
  let buyingPowerLots = 0;

  if (lossPerShare > 0) {
    maxRiskAllowed = capital * (riskPct / 100);
    const maxLotsByRisk = Math.floor(maxRiskAllowed / lossPerLot);
    
    // Pastikan tidak melebihi total daya beli (Capital)
    buyingPowerLots = Math.floor(capital / (entry * 100));
    
    maxLots = Math.min(maxLotsByRisk, buyingPowerLots);
    totalCost = maxLots * entry * 100;
    projectedLoss = maxLots * lossPerLot;
  }

  return (
    <div className="calculator-modal">
      <div className="calculator-content">
        <div className="calculator-header">
          <h2>🛡️ Kalkulator Perisai Modal: {stock.ticker || stock.name}</h2>
          <button onClick={onClose} className="btn-close-calc">✖ Tutup</button>
        </div>

        <div className="calc-body">
          <div className="calc-inputs">
            <div className="input-group">
              <label>💰 Total Modal Anda (Rp)</label>
              <input 
                type="number" 
                value={capital} 
                onChange={(e) => setCapital(Number(e.target.value))} 
                className="calc-input"
              />
            </div>
            <div className="input-group">
              <label>⚠️ Toleransi Risiko Per Trade (%)</label>
              <input 
                type="number" 
                step="0.5"
                value={riskPct} 
                onChange={(e) => setRiskPct(Number(e.target.value))} 
                className="calc-input"
              />
              <small style={{display:'block', marginTop:'5px', color:'#95a5a6'}}>
                Maksimal Kerugian: Rp {maxRiskAllowed.toLocaleString('id-ID')}
              </small>
            </div>
          </div>

          <div className="calc-market-data">
            <div className="market-row">
              <span>Harga Beli (Entry)</span>
              <strong>Rp {entry.toLocaleString('id-ID')}</strong>
            </div>
            <div className="market-row" style={{color: 'var(--color-pink)'}}>
              <span>Stop Loss (Batas Cutloss)</span>
              <strong>Rp {sl.toLocaleString('id-ID')}</strong>
            </div>
            <div className="market-row">
              <span>Jarak Kerugian per Lot</span>
              <strong>Rp {lossPerLot.toLocaleString('id-ID')}</strong>
            </div>
          </div>

          {lossPerShare <= 0 ? (
            <div className="calc-error">
              ❌ Harga Stop Loss harus lebih rendah dari Harga Entry!
            </div>
          ) : (
            <div className="calc-result">
              <h3>⚡ INSTRUKSI EKSEKUSI</h3>
              <div className="result-highlight">
                BELI MAKSIMAL: <span>{maxLots.toLocaleString('id-ID')} Lot</span>
              </div>
              <p className="result-note">
                (Daya beli penuh Anda = {buyingPowerLots.toLocaleString('id-ID')} Lot)
              </p>
              
              <div className="result-details">
                <div className="detail-row">
                  <span>Modal yang Terpakai:</span>
                  <strong>Rp {totalCost.toLocaleString('id-ID')}</strong>
                </div>
                <div className="detail-row" style={{borderTop: '1px solid #333', paddingTop: '10px', marginTop: '10px'}}>
                  <span>Proyeksi Rugi Jika Kena SL:</span>
                  <strong style={{color: 'var(--color-pink)'}}>- Rp {projectedLoss.toLocaleString('id-ID')}</strong>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CalculatorModal;
