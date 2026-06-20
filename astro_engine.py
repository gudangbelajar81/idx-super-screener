import ephem
from datetime import datetime, timedelta
import math

def get_angular_distance(body1, body2, date_obj):
    """Menghitung jarak sudut (dalam derajat) antara dua objek kosmik."""
    body1.compute(date_obj)
    body2.compute(date_obj)
    
    # Dapatkan ekliptika longitude
    lon1 = math.degrees(body1.hlon) if hasattr(body1, 'hlon') else math.degrees(ephem.Ecliptic(body1).lon)
    lon2 = math.degrees(body2.hlon) if hasattr(body2, 'hlon') else math.degrees(ephem.Ecliptic(body2).lon)
    
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff

ASTRO_DESCRIPTIONS = {
    "v_j": {
        "title": "🌟 Venus-Jupiter (The Wealth Aspect)",
        "desc": "Kombinasi energi uang (Venus) dan ekspansi besar (Jupiter). Ini adalah puncak eforia pasar. Biasanya memicu kenaikan harga yang sangat kencang, namun sering kali menjadi penanda Puncak Harga (Market Top) sebelum terjadi koreksi."
    },
    "m_v": {
        "title": "🌙 Moon-Venus (The Daily Emotion)",
        "desc": "Pertemuan Bulan dan Venus memicu sentimen emosional positif jangka pendek. Sangat bagus untuk strategi Fast Swing atau Scalping (Ninja), karena kecenderungan pasar akan bergerak naik di hari tersebut."
    },
    "s_m": {
        "title": "🔥 Sun-Mars (The Aggression)",
        "desc": "Energi vital (Matahari) bertemu dengan perang/agresi (Mars). Pasar akan mengalami volatilitas (guncangan) ekstrem. Waspadai aksi jual panik (Panic Selling) atau sebaliknya, dorongan beli brutal (Hajar Kanan)."
    },
    "me_s": {
        "title": "⛓️ Mercury-Saturn (The Restriction)",
        "desc": "Komunikasi perdagangan (Merkurius) ditahan oleh tembok pembatasan (Saturnus). Di fase ini, pasar akan cenderung Sideways (Macet/Lambat), volume transaksi sepi, atau terjadi koreksi harga secara perlahan."
    },
    "ma_j": {
        "title": "🚀 Mars-Jupiter (Explosive Expansion)",
        "desc": "Energi pemicu perang bertemu ledakan ekspansi. Ini adalah momen Breakout! Pasar bersiap menembus tembok pertahanan (Resisten/Support) dengan volume raksasa dan pergerakan agresif."
    }
}

def get_astro_cycles(start_date_str, end_date_str):
    """
    Menghitung siklus bintang yang terjadi antara start_date dan end_date.
    Mengembalikan array berisi objek marker untuk TradingView.
    """
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    sun = ephem.Sun()
    moon = ephem.Moon()
    mercury = ephem.Mercury()
    venus = ephem.Venus()
    mars = ephem.Mars()
    jupiter = ephem.Jupiter()
    saturn = ephem.Saturn()
    
    markers = []
    
    # Toleransi orb konjungsi (derajat)
    # Bulan bergerak cepat, kita paskan toleransinya. Planet lambat orb lebih besar.
    ORB = 2.0 
    
    # Karena kita ingin mencari momen pertemuan yang presisi dan tidak mengulangi tanda berhari-hari,
    # kita catat hari terakhir planet X dan Y bertemu agar tidak ter-spam.
    last_aspects = {}

    current = start
    while current <= end:
        date_ephem = ephem.Date(current)
        
        # 1. Venus - Jupiter (Wealth / Top)
        dist_v_j = get_angular_distance(venus, jupiter, date_ephem)
        if dist_v_j <= ORB:
            if current.strftime("%Y-%m") != last_aspects.get("v_j"):
                markers.append({
                    "time": current.strftime("%Y-%m-%d"),
                    "position": "aboveBar",
                    "color": "#f1c40f",
                    "shape": "arrowDown",
                    "text": ASTRO_DESCRIPTIONS["v_j"]["title"]
                })
                last_aspects["v_j"] = current.strftime("%Y-%m")

        # 2. Moon - Venus (Daily Emotion)
        dist_m_v = get_angular_distance(moon, venus, date_ephem)
        if dist_m_v <= 5.0:
            if current.strftime("%Y-%m-%d") != last_aspects.get("m_v"):
                markers.append({
                    "time": current.strftime("%Y-%m-%d"),
                    "position": "belowBar",
                    "color": "#3498db",
                    "shape": "circle",
                    "text": ASTRO_DESCRIPTIONS["m_v"]["title"]
                })
                last_aspects["m_v"] = current.strftime("%Y-%m-%d")

        # 3. Sun - Mars (Aggression / Volatility)
        dist_s_m = get_angular_distance(sun, mars, date_ephem)
        if dist_s_m <= ORB:
            if current.strftime("%Y-%m") != last_aspects.get("s_m"):
                markers.append({
                    "time": current.strftime("%Y-%m-%d"),
                    "position": "belowBar",
                    "color": "#e74c3c",
                    "shape": "arrowUp",
                    "text": ASTRO_DESCRIPTIONS["s_m"]["title"]
                })
                last_aspects["s_m"] = current.strftime("%Y-%m")

        # 4. Mercury - Saturn (Restriction / Sideways)
        dist_me_s = get_angular_distance(mercury, saturn, date_ephem)
        if dist_me_s <= ORB:
            if current.strftime("%Y-%m") != last_aspects.get("me_s"):
                markers.append({
                    "time": current.strftime("%Y-%m-%d"),
                    "position": "aboveBar",
                    "color": "#95a5a6",
                    "shape": "arrowDown",
                    "text": ASTRO_DESCRIPTIONS["me_s"]["title"]
                })
                last_aspects["me_s"] = current.strftime("%Y-%m")

        # 5. Mars - Jupiter (Explosive Expansion)
        dist_ma_j = get_angular_distance(mars, jupiter, date_ephem)
        if dist_ma_j <= ORB:
            if current.strftime("%Y-%m") != last_aspects.get("ma_j"):
                markers.append({
                    "time": current.strftime("%Y-%m-%d"),
                    "position": "belowBar",
                    "color": "#8e44ad",
                    "shape": "arrowUp",
                    "text": ASTRO_DESCRIPTIONS["ma_j"]["title"]
                })
                last_aspects["ma_j"] = current.strftime("%Y-%m")

        current += timedelta(days=1)
        
    return markers

def get_current_astro_forecast():
    """Mengembalikan daftar event astrologi yang sedang aktif (dalam +/- 3 hari) beserta penjelasannya."""
    today = datetime.now()
    start = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    end = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    
    markers = get_astro_cycles(start, end)
    
    # Filter agar hanya unique event
    active_events = {}
    for m in markers:
        # Cari key dari deskripsi
        for key, val in ASTRO_DESCRIPTIONS.items():
            if val["title"] == m["text"]:
                active_events[key] = val
                
    results = list(active_events.values())
    if not results:
        return [{"title": "🌌 Cuaca Tata Surya Tenang", "desc": "Tidak ada aspek konjungsi mayor dalam rentang +/- 3 hari ini. Pergerakan harga akan sepenuhnya bergantung pada Teknikal dan Arus Uang (Bandarmologi)."}]
    return results

# Test kecil
if __name__ == "__main__":
    res = get_astro_cycles("2023-01-01", "2024-01-01")
    for r in res:
        print(r)
