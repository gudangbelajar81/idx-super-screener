import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace State variables
content = re.sub(r'const \[ninjaData, setNinjaData\] = useState\(\[\]\);', r'const [intradayData, setIntradayData] = useState([]);', content)
content = re.sub(r'const \[swingData, setSwingData\] = useState\(\[\]\);', r'const [swingData, setSwingData] = useState([]);', content)
content = re.sub(r'const \[kavaleriData, setKavaleriData\] = useState\(\[\]\);\n', '', content)

# 2. Replace fetch methods
fetch_replacement = """
  const fetchMasterIntraday = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/master/intraday`);
      setIntradayData(res.data.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const fetchMasterSwing = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/master/swing`);
      setSwingData(res.data.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };
"""

# We'll regex out fetchSwing, fetchNinja, fetchKavaleri completely.
# They are between fetchComposite and runSensusNinja.
content = re.sub(r'const fetchSwing = async.*?alert\("Gagal menjalankan Sensus Kavaleri\."\);\n    }\n  \};', fetch_replacement, content, flags=re.DOTALL)

# 3. Fix useEffect hooks that call fetchCandidates
content = re.sub(r"else if \(activeTab === 'swing' && swingData\.length === 0\) \{\n\s*fetchCandidates\('swing'\);\n\s*\} else if \(activeTab === 'intraday' && ninjaData\.length === 0\) \{\n\s*fetchCandidates\('ninja'\);\n\s*\} else if \(activeTab === 'none' && kavaleriData\.length === 0\) \{\n\s*fetchCandidates\('kavaleri'\);\n\s*\}", 
    r"else if (activeTab === 'swing' && swingData.length === 0) { fetchMasterSwing(); } else if (activeTab === 'intraday' && intradayData.length === 0) { fetchMasterIntraday(); }", content)

# 4. Fix data reloading after Sensus
content = re.sub(r'fetchNinja\(\);\n\s*fetchKavaleri\(\);\n\s*fetchSwing\(\);', r'fetchMasterIntraday();\n              fetchMasterSwing();', content)

# 5. Fix currentData map
content = re.sub(r"const currentData = activeTab === 'swing' \? swingData : activeTab === 'intraday' \? ninjaData : activeTab === 'none' \? kavaleriData : whaleData;", r"const currentData = activeTab === 'swing' ? swingData : activeTab === 'intraday' ? intradayData : whaleData;", content)

# 6. Fix array building
content = re.sub(r'swingData\.filter\(s => s\.signal\)\.forEach\(s => elite\.push\(\{.*?\}\)\);\n\s*kavaleriData\.filter\(s => s\.signal\)\.forEach\(s => elite\.push\(\{.*?\}\)\);\n\s*ninjaData\.filter\(s => s\.signal\)\.forEach\(s => elite\.push\(\{.*?\}\)\);', 
    r"swingData.forEach(s => elite.push({...s, source: 'Swing Trading'}));\n      intradayData.forEach(s => elite.push({...s, source: 'Intraday Momentum'}));", content)

# 7. Update useEffect dependencies
content = re.sub(r'\[swingData, kavaleriData, ninjaData, whaleData, globalData\]', r'[swingData, intradayData, whaleData, globalData]', content)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to App.jsx!")
