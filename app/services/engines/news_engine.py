import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

# Kata-kata kunci untuk analisis sentimen
POSITIVE_KEYWORDS = [
    "naik", "untung", "laba", "profit", "dividen", "akuisisi", "kontrak baru",
    "ekspansi", "positif", "rekor", "tertinggi", "meningkat", "tumbuh",
    "kerjasama", "merger", "buyback", "IPO", "rights issue", "kuat", "optimis"
]

NEGATIVE_KEYWORDS = [
    "rugi", "turun", "delisting", "gagal bayar", "default", "pailit", "bangkrut",
    "negatif", "terendah", "menurun", "suspensi", "korupsi", "fraud", "manipulasi",
    "kerugian", "merosot", "terpuruk", "sanksi", "denda", "tuntutan", "gugatan"
]


def get_news_sentiment(ticker: str, max_articles: int = 5) -> dict:
    """
    Mengambil berita terbaru tentang sebuah saham dari Kontan.co.id
    dan menganalisis sentimennya.
    
    Analogi: Ini adalah "Intel" atau intelijen di lapangan.
    Mesin teknikal hanya melihat grafik — tapi berita bisa memberi
    konteks kenapa grafik bergerak seperti itu.
    
    ticker: Kode saham tanpa .JK (contoh: BBCA, GOTO)
    """
    ticker_clean = ticker.replace(".JK", "").upper()
    
    result = {
        "ticker": ticker_clean,
        "news_count": 0,
        "sentiment_score": 0,  # Positif = +, Negatif = -
        "sentiment": "NETRAL",
        "headlines": [],
        "error": None
    }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Search di Kontan
        search_url = f"https://search.kontan.co.id/search.htm?q={ticker_clean}&npage=1"
        response = requests.get(search_url, headers=headers, timeout=8)
        
        if response.status_code != 200:
            result["error"] = f"HTTP {response.status_code}"
            return result
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Ambil artikel-artikel yang ditemukan
        articles = soup.find_all("div", class_="hnews")
        if not articles:
            # Coba selector alternatif
            articles = soup.find_all("li", class_="search-result")
        
        score = 0
        headlines = []
        count = 0
        
        for article in articles[:max_articles]:
            title_tag = article.find("a") or article.find("h2") or article.find("h3")
            if not title_tag:
                continue
            
            title = title_tag.get_text(strip=True)
            if not title or ticker_clean.lower() not in title.lower():
                continue
            
            # Hitung skor sentimen dari judul
            title_lower = title.lower()
            article_score = 0
            
            for kw in POSITIVE_KEYWORDS:
                if kw in title_lower:
                    article_score += 1
            
            for kw in NEGATIVE_KEYWORDS:
                if kw in title_lower:
                    article_score -= 1
            
            score += article_score
            headlines.append({
                "title": title[:120],
                "score": article_score
            })
            count += 1
        
        result["news_count"] = count
        result["sentiment_score"] = score
        result["headlines"] = headlines
        
        if score >= 2:
            result["sentiment"] = "POSITIF"
        elif score <= -2:
            result["sentiment"] = "NEGATIF"
        elif score > 0:
            result["sentiment"] = "CENDERUNG POSITIF"
        elif score < 0:
            result["sentiment"] = "CENDERUNG NEGATIF"
        else:
            result["sentiment"] = "NETRAL"
        
    except requests.exceptions.Timeout:
        result["error"] = "Timeout"
        result["sentiment"] = "NETRAL"
    except Exception as e:
        result["error"] = str(e)[:100]
        result["sentiment"] = "NETRAL"
    
    return result


def get_ipo_news() -> list:
    """
    Mengambil berita IPO & Aksi Korporasi dari Kontan RSS (Jalur Anti-Blokir).
    """
    import xml.etree.ElementTree as ET
    headlines = []
    
    try:
        url = "https://investasi.kontan.co.id/rss"
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            for item in root.findall('./channel/item'):
                title_elem = item.find("title")
                if title_elem is None:
                    continue
                    
                title_text = title_elem.text.strip()
                title_lower = title_text.lower()
                
                # Saring berita Aksi Korporasi & IPO
                keywords = ["ipo", "melantai", "dividen", "right issue", "akuisisi", "saham baru", "tender offer"]
                if not any(k in title_lower for k in keywords):
                    continue
                
                # Deteksi Ticker (Kode Emiten) jika ada 4 huruf kapital di dalam kurung
                import re
                ticker_match = re.search(r'\(([A-Z]{4})\)', title_text)
                ticker_badge = f" [{ticker_match.group(1)}]" if ticker_match else ""
                
                # Analisis Risiko
                risk_level = "Aman (Menarik)"
                risk_color = "var(--color-green)"
                
                if any(word in title_lower for word in ["mahal", "utang", "rugi", "turun", "sepi", "waspada", "hati-hati", "suspend", "gagal"]):
                    risk_level = "Berbahaya (Hindari)"
                    risk_color = "#ff4d4d"
                elif any(word in title_lower for word in ["oversubscribed", "laba", "menarik", "diburu", "tertinggi", "dividen jumbo"]):
                    risk_level = "Potensi ARA (HAKA)"
                    risk_color = "var(--color-green)"
                else:
                    risk_level = "Netral (Pantau)"
                    risk_color = "var(--color-orange)"
                
                headlines.append({
                    "title": title_text + ticker_badge,
                    "risk": risk_level,
                    "color": risk_color
                })
                
                if len(headlines) >= 5:
                    break
                    
    except Exception as e:
        print(f"Error scraping IPO RSS: {e}")
        
    # Beri data fallback jika kebetulan tidak ada aksi korporasi minggu ini
    if not headlines:
        headlines = [
            {"title": "[INFO] Belum ada berita IPO/Aksi Korporasi terbaru dari bursa hari ini.", "risk": "Netral (Pantau)", "color": "var(--color-orange)"}
        ]
        
    return headlines

if __name__ == "__main__":
    import json
    print("Test sentimen BBCA...")
    data = get_news_sentiment("BBCA")
    print(json.dumps(data, indent=2, ensure_ascii=False))
