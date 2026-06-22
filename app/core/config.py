# Daftar Saham untuk Mode Benteng (Swing Trading - Blue Chips & Mid Caps)
# Kita tambahkan .JK karena kita menggunakan data Yahoo Finance untuk bursa Indonesia (IDX).
SWING_UNIVERSE = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", # Big Banks
    "TLKM.JK", "ASII.JK", "UNVR.JK", "ICBP.JK", # Consumer & Telco
    "AMMN.JK", "BREN.JK", "PGEO.JK", "BRPT.JK"  # Energy / Conglomerate
]

# Daftar Saham untuk Mode Ninja (Scalping / Gorengan / High Volatility)
# Saham lapis dua atau tiga yang sering digerakkan dengan cepat oleh market maker.
SCALP_UNIVERSE = [
    "CUAN.JK", "PANI.JK", "BREN.JK", "STRK.JK", 
    "GOTO.JK", "BRMS.JK", "BUMI.JK", "DOID.JK"
]

# Konfigurasi Teknis
MIN_DAILY_VOLUME = 5_000_000_000 # 5 Miliar Rupiah per hari untuk keamanan Swing Trading

import os
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "KunciRahasiaBos88")
