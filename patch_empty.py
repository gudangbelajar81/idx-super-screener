import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

empty_state_cards = '''<div className="cards-grid">
            {sortedData.length === 0 && !loading && (
              <div style={{ padding: '30px', textAlign: 'center', gridColumn: '1 / -1', background: 'rgba(255, 0, 0, 0.05)', borderRadius: '12px', border: '1px dashed rgba(255,0,0,0.3)', marginTop: '20px' }}>
                <h3 style={{ color: '#ff4757', marginBottom: '10px' }}>⚠️ Data Tidak Tersedia</h3>
                <p style={{ color: 'rgba(255,255,255,0.7)', lineHeight: '1.6' }}>
                  Tidak ada kandidat saham saat ini. Sistem <b>TIDAK</b> menggunakan data buatan (dummy).<br/>
                  Jika tabel ini kosong, jalankan <b>Sensus Master</b> terlebih dahulu, atau tekan tombol <b>Pemindaian VIP</b>.
                </p>
              </div>
            )}'''

empty_state_table = '''<tbody>
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
            )}'''

content = content.replace('<div className="cards-grid">', empty_state_cards)
content = content.replace('<tbody>', empty_state_table)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Empty state added to App.jsx')
