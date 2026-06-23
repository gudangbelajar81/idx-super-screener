import os
import re

path = 'frontend/src/App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

api_keys_component = '''
import { useState, useEffect } from 'react';

const ApiKeysDashboard = () => {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState('Gemini');
  const [name, setName] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('');

  const fetchKeys = async () => {
    try {
      const res = await axios.get('/api/keys');
      if (res.data.status === 'success') {
        setKeys(res.data.data);
      }
    } catch (e) {
      console.error('Failed to fetch keys', e);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const handleAdd = async () => {
    if (!name || !apiKey) return;
    setLoading(true);
    try {
      await axios.post('/api/keys', { provider, name, api_key: apiKey, base_url: baseUrl });
      setName('');
      setApiKey('');
      setBaseUrl('');
      fetchKeys();
    } catch (e) {
      alert(e.response?.data?.detail || 'Gagal menambahkan kunci');
    }
    setLoading(false);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Hapus kunci ini?')) return;
    try {
      await axios.delete(`/api/keys/${id}`);
      fetchKeys();
    } catch (e) {
      console.error(e);
    }
  };

  const handleReset = async (id) => {
    try {
      await axios.put(`/api/keys/${id}/reset`);
      fetchKeys();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ background: 'var(--bg-card)', padding: 20, borderRadius: 12, marginTop: 20, border: '1px solid var(--border-subtle)' }}>
      <h3 style={{ margin: '0 0 15px 0', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 24 }}>🗝️</span> Pusat API Key (Omni-Gateway)
      </h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 15, marginBottom: 20 }}>
        <div>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: 'var(--color-blue)' }}>Provider</label>
          <select value={provider} onChange={e => setProvider(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }}>
            <option value="Gemini">Gemini</option>
            <option value="GoAPI">GoAPI</option>
            <option value="OpenAI">OpenAI</option>
            <option value="Groq">Groq</option>
            <option value="KieAI">Kie AI</option>
            <option value="Custom">Custom / Lainnya</option>
          </select>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: 'var(--color-blue)' }}>Nama Akun (Bebas)</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="Misal: Akun Susi" />
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: 'var(--color-blue)' }}>API Key</label>
          <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="Masukkan Kunci Rahasia" />
        </div>
        
        {['Custom', 'KieAI', 'OpenAI', 'Groq'].includes(provider) && (
          <div style={{ gridColumn: '1 / -1' }}>
            <label style={{ display: 'block', marginBottom: 5, fontSize: 13, color: '#e67e22' }}>Endpoint (Base URL) - Kosongkan untuk default</label>
            <input type="text" value={baseUrl} onChange={e => setBaseUrl(e.target.value)} className="input-field" style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'white', border: '1px solid var(--border-subtle)' }} placeholder="https://api.domain.com/v1" />
          </div>
        )}
        
        <div style={{ gridColumn: '1 / -1' }}>
          <button onClick={handleAdd} disabled={loading} className="btn" style={{ width: '100%', background: 'linear-gradient(135deg, #27ae60, #2ecc71)', color: 'white', border: 'none', padding: 10, borderRadius: 8, cursor: 'pointer', fontWeight: 'bold' }}>
            {loading ? 'Menambahkan...' : '➕ Tambah Kunci'}
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: 'rgba(0,0,0,0.2)', textAlign: 'left' }}>
              <th style={{ padding: 10 }}>Provider</th>
              <th style={{ padding: 10 }}>Akun</th>
              <th style={{ padding: 10 }}>Key</th>
              <th style={{ padding: 10 }}>Status</th>
              <th style={{ padding: 10 }}>Pakai</th>
              <th style={{ padding: 10 }}>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {keys.map(k => (
              <tr key={k.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: 10 }}>{k.provider}</td>
                <td style={{ padding: 10 }}>{k.name}</td>
                <td style={{ padding: 10, fontFamily: 'monospace' }}>{k.api_key_masked}</td>
                <td style={{ padding: 10 }}>
                  <span style={{ 
                    padding: '3px 8px', borderRadius: 12, fontSize: 11, fontWeight: 'bold',
                    background: k.status === 'Alive' ? 'rgba(46, 204, 113, 0.2)' : 'rgba(231, 76, 60, 0.2)',
                    color: k.status === 'Alive' ? '#2ecc71' : '#e74c3c'
                  }}>
                    {k.status}
                  </span>
                </td>
                <td style={{ padding: 10 }}>{k.used_count}x</td>
                <td style={{ padding: 10, display: 'flex', gap: 5 }}>
                  {k.status !== 'Alive' && (
                    <button onClick={() => handleReset(k.id)} style={{ background: 'transparent', border: '1px solid #3498db', color: '#3498db', borderRadius: 4, cursor: 'pointer', padding: '2px 5px', fontSize: 11 }}>Reset</button>
                  )}
                  <button onClick={() => handleDelete(k.id)} style={{ background: 'transparent', border: '1px solid #e74c3c', color: '#e74c3c', borderRadius: 4, cursor: 'pointer', padding: '2px 5px', fontSize: 11 }}>Hapus</button>
                </td>
              </tr>
            ))}
            {keys.length === 0 && (
              <tr><td colSpan="6" style={{ padding: 20, textAlign: 'center', color: '#7f8c8d' }}>Belum ada kunci terdaftar.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
'''

# Hapus setting lama (Kunci GoAPI dan Gemini dari file sebelumnya)
content = re.sub(
    r'<label.*?Kunci Provider \(GoAPI VIP.*?<input.*?/>\s*<label.*?Kunci AI X-Ray.*?<input.*?/>',
    '<ApiKeysDashboard />',
    content,
    flags=re.DOTALL
)

# Jika berhasil diganti, kita harus pastikan komponennya ada.
if '<ApiKeysDashboard />' in content and 'const ApiKeysDashboard' not in content:
    # Cari tempat insert setelah deklarasi App atau import
    insert_idx = content.find('function App()')
    if insert_idx == -1:
        insert_idx = content.find('const App =')
        
    if insert_idx != -1:
        content = content[:insert_idx] + api_keys_component + '\n' + content[insert_idx:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("App.jsx patched with ApiKeysDashboard UI")
