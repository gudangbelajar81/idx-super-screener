import os

path = 'frontend/src/App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Tambahkan fungsi renderEdgeData sebelum function App()
RENDER_FUNC = '''
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
'''
if 'const renderEdgeData' not in content:
    content = content.replace('function App() {', RENDER_FUNC + '\nfunction App() {')

# 2. Inject ke dalam stock-card
# Cari penutup tp-sl-container
old_block = '''                        <div className="tp-sl-container" style={{ marginTop: '10px', marginBottom: '15px' }}>
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
                        </div>'''

new_block = old_block + '\n\n                        {renderEdgeData(stock)}'

content = content.replace(old_block, new_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('App.jsx updated with Edge Data UI')
