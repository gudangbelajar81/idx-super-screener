import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "{currentData.map((stock) => (" in line:
        start_idx = i
        break

if start_idx != -1:
    # Find the closing button for Buka Grafik
    for i in range(start_idx, len(lines)):
        if "Buka Grafik" in lines[i]:
            # The next few lines should be the end of the stock card
            for j in range(i, len(lines)):
                if "{stock.sl && (" in lines[j] or "{stock.stop_loss && (" in lines[j] or "</div>" in lines[j]:
                    # Let's just find the exact `onClick={() => setSelectedChart`
                    pass
            break

# The safer way is Regex with DOTALL
with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r"\{currentData\.map\(\(stock\) => \(\s*<div\s*key=\{stock\.ticker\}.*?Buka Grafik\s*</button>.*?</div>"
# This regex might be too complex or fail. Let's just write a python script that injects the new block from `{currentData.map((stock) => (` until `{stock.sl && (`

start_str = "{currentData.map((stock) => ("
end_str = "Buka Grafik\n                          </button>"

s_idx = text.find(start_str)
e_idx = text.find(end_str)

if s_idx != -1 and e_idx != -1:
    # Add offset to include the closing button tag
    e_idx = e_idx + len(end_str)
    
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
                          <button className="btn-chart" onClick={(e) => { e.stopPropagation(); setSelectedChart({ticker: stock.ticker, tp: stock.target_profit, sl: stock.stop_loss}); }}>
                            📈 Buka Grafik
                          </button>"""
                          
    new_text = text[:s_idx] + new_block + text[e_idx:]
    
    with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Replaced successfully")
else:
    print("Could not find start or end index")
