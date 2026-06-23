import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the currentData.map block
old_block_pattern = r"\{currentData\.map\(\(stock\).*?\{stock\.sl && \("
# Wait, regex might be tricky. Let's find the specific block to replace using split/replace.

old_block = """{currentData.map((stock) => (
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
                        
                        {activeTab === 'none' && (
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
                                <strong>dYOY GOLDEN ENTRY (Aman)</strong>
                              </div>
                            )}
                            {stock.is_danger && (
                              <div className="rr-row" style={{ color: '#ff4757' }}>
                                <strong>dYs" RAWAN GUYURAN (Tinggi)</strong>
                              </div>
                            )}
                          </div>
                        )}
                        
                        <div style={{display: 'flex', gap: '10px'}}>
                          <button className="btn-chart" onClick={() => setSelectedChart({ticker: stock.ticker, tp: stock.tp, sl: stock.sl})}>
                            dY"^ Buka Grafik
                          </button>
                          
                          {stock.sl && ("""

new_block = """{currentData.map((stock) => (
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
                          <div className={`badge ${stock.recommendation === 'STRONG BUY' ? 'strong-buy' : stock.recommendation === 'BUY' ? 'buy' : 'neutral'}`} style={{background: stock.recommendation === 'STRONG BUY' ? '#ff4757' : stock.recommendation === 'BUY' ? '#2ed573' : '#747d8c', color: 'white', fontWeight: 'bold'}}>
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
                              <div className="sl-block">
                                <span className="tp-label">STOP LOSS</span>
                                <span className="tp-value sl-val" style={{ color: '#ff4757' }}>Rp {stock.stop_loss ? stock.stop_loss.toLocaleString('id-ID') : '0'}</span>
                                <span className="tp-pct sl-down">RR: {stock.risk_reward_ratio}x</span>
                              </div>
                            </div>
                        </div>
                        
                        <div style={{display: 'flex', gap: '10px'}}>
                          <button className="btn-chart" onClick={() => setSelectedChart({ticker: stock.ticker, tp: stock.target_profit, sl: stock.stop_loss})}>
                            📈 Buka Grafik
                          </button>
                          
                          {stock.stop_loss && ("""

# Replace exact string matching if possible, otherwise use regex
content = content.replace(old_block, new_block)

# Fix the filter bug at the top of App.jsx
content = content.replace("const totalSignals = currentData.filter(d => d.signal).length;", "const totalSignals = currentData.filter(d => d.composite_score > 60).length;")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Card UI Patched")
