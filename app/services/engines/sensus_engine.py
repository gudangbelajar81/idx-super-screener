import pandas as pd
import ta
from app.services.engines.data_engine import download_daily_data
from app.services.engines.technical_engine import calc_chaikin_money_flow

# Daftar 80-100 saham berkapitalisasi besar & menengah yang aktif ditransaksikan (IDX80/Kompas100 approach)
SENSUS_UNIVERSE = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "AMMN.JK", "BREN.JK",
    "GOTO.JK", "TPIA.JK", "BRPT.JK", "KLBF.JK", "UNVR.JK", "ICBP.JK", "INDF.JK", "ADRO.JK",
    "PTBA.JK", "ITMG.JK", "UNTR.JK", "PGAS.JK", "MEDC.JK", "AKRA.JK", "INKP.JK", "TKIM.JK",
    "BRIS.JK", "ARTO.JK", "MDKA.JK", "INCO.JK", "ANTM.JK", "PTMP.JK", "CUAN.JK", "PANI.JK",
    "BBTN.JK", "SMGR.JK", "INTP.JK", "JSMR.JK", "MIKA.JK", "HEAL.JK", "SILO.JK", "CPIN.JK",
    "JPFA.JK", "MYOR.JK", "CMRY.JK", "AMRT.JK", "MIDI.JK", "ACES.JK", "ERAA.JK", "MAPI.JK",
    "MAPA.JK", "EXCL.JK", "ISAT.JK", "MTEL.JK", "TOWR.JK", "TBIG.JK", "BSDE.JK", "CTRA.JK",
    "SMRA.JK", "PWON.JK", "ASRI.JK", "SSIA.JK", "PTPP.JK", "WIKA.JK", "WSKT.JK", "ADHI.JK",
    "MBMA.JK", "NCKL.JK", "PGEO.JK", "VKTR.JK", "WIFI.JK", "WIRG.JK", "ESSA.JK", "HRUM.JK",
    "DOID.JK", "BUMI.JK", "BRMS.JK", "PSAB.JK", "AUTO.JK", "DRMA.JK", "GJTL.JK", "SIDO.JK"
]

# Daftar Saham Gorengan Liar (Lapis Tiga) untuk Sensus Ninja
SENSUS_NINJA_UNIVERSE = [
    "BSML.JK", "BSBK.JK", "STRK.JK", "VISI.JK", "CGAS.JK", "AWAN.JK", "LMAX.JK", "GTRA.JK",
    "NINE.JK", "PANI.JK", "CUAN.JK", "PTMP.JK", "OASA.JK", "GZCO.JK", "BBYB.JK", "ARTO.JK",
    "BSSR.JK", "DOID.JK", "SGER.JK", "RAFI.JK", "WIDI.JK", "CBRE.JK", "TRON.JK", "VKTR.JK",
    "DEAL.JK", "HALO.JK", "IRSX.JK", "KAYU.JK", "KING.JK", "MKTR.JK", "MUTU.JK", "NZIA.JK",
    "OMED.JK", "PACK.JK", "PEVE.JK", "VTNY.JK", "WIFI.JK", "WIRG.JK", "TRGU.JK", "BAPA.JK",
    "ELIT.JK", "GOTO.JK", "BUKA.JK", "SCMA.JK", "BABP.JK", "BRMS.JK", "DEWA.JK", "BUMI.JK",
    "MDRN.JK", "HATM.JK", "MANG.JK", "NANO.JK", "RSGK.JK", "SWAT.JK", "MICE.JK", "ZATA.JK"
]

def run_sensus_pilihan():
    """
    Mengunduh data universe saham, menyaring yang paling kuat secara teknikal.
    Syarat Lolos Sensus:
    1. Likuiditas rata-rata > Rp 5 Miliar
    2. Harga > 50
    3. Tren Jangka Menengah Kuat (EMA 50 > EMA 200)
    4. CMF > 0 (Ada akumulasi uang masuk)
    """
    print(f"Menjalankan Sensus untuk {len(SENSUS_UNIVERSE)} saham...")
    daily_data = download_daily_data(SENSUS_UNIVERSE, period="1y")
    
    passed_tickers = []
    
    for ticker, df in daily_data.items():
        if df.empty or len(df) < 200:
            continue
            
        df = df.copy()
        last_close = float(df['Close'].iloc[-1])
        
        # 1. Cek Harga Gocap
        if last_close <= 50:
            continue
            
        # 2. Cek Likuiditas (Rata-rata volume 20 hari * harga penutupan)
        avg_volume = df['Volume'].tail(20).mean()
        liquidity = avg_volume * last_close
        if liquidity < 5_000_000_000: # 5 Miliar Rupiah
            continue
            
        # 3. Hitung Indikator Tren (EMA)
        df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)
        df['EMA_200'] = ta.trend.ema_indicator(df['Close'], window=200)
        
        ema_50 = float(df['EMA_50'].iloc[-1])
        ema_200 = float(df['EMA_200'].iloc[-1])
        
        if last_close < ema_50 or ema_50 < ema_200:
            # Tidak uptrend atau belum golden cross
            continue
            
        # 4. Hitung CMF
        cmf = calc_chaikin_money_flow(df, period=20)
        if cmf <= 0:
            continue
            
        # Jika lolos semua ujian neraka ini:
        ticker_clean = ticker.replace(".JK", "")
        passed_tickers.append(ticker_clean)
        
    print(f"Sensus selesai. Menemukan {len(passed_tickers)} saham kandidat super.")
    return passed_tickers

def run_sensus_ninja():
    """
    Sensus khusus untuk saham gorengan.
    Syarat Mutlak: Volume hari ini melonjak tajam (>150% dari rata-rata volume).
    """
    print(f"Menjalankan Sensus Ninja untuk {len(SENSUS_NINJA_UNIVERSE)} saham...")
    
    # Ambil data harian selama 1 bulan untuk mengecek rata-rata volume
    daily_data = download_daily_data(SENSUS_NINJA_UNIVERSE, period="1mo")
    
    passed_tickers = []
    
    for ticker, df in daily_data.items():
        if df.empty or len(df) < 5:
            continue
            
        df = df.copy()
        
        last_close = float(df['Close'].iloc[-1])
        last_volume = float(df['Volume'].iloc[-1])
        
        # Cek saham gocap
        if last_close <= 50:
            continue
            
        # Rata-rata volume 10 hari terakhir
        avg_vol = df['Volume'].tail(10).mean()
        
        if avg_vol == 0:
            continue
            
        # Syarat Utama: Volume saat ini harus minimal 1.5x (150%) dari rata-rata volume harian
        if last_volume >= (avg_vol * 1.5):
            # Syarat Tambahan: Harga harus hijau hari ini
            if last_close > float(df['Close'].iloc[-2]):
                passed_tickers.append(ticker.replace(".JK", ""))
                
    print(f"Sensus Ninja selesai. Menemukan {len(passed_tickers)} saham liar yang siap meledak.")
    return passed_tickers

def run_sensus_kavaleri():
    """
    Sensus khusus untuk Kavaleri (Fast Swing).
    Fokus pada saham likuid yang sedang sideways atau memiliki momentum.
    """
    print(f"Menjalankan Sensus Kavaleri untuk {len(SENSUS_UNIVERSE)} saham...")
    daily_data = download_daily_data(SENSUS_UNIVERSE, period="6mo")
    
    passed_tickers = []
    for ticker, df in daily_data.items():
        if df.empty or len(df) < 50:
            continue
            
        df = df.copy()
        last_close = float(df['Close'].iloc[-1])
        
        # 1. Likuiditas Minimal 2 Miliar
        avg_volume = df['Volume'].tail(20).mean()
        liquidity = avg_volume * last_close
        if liquidity < 2_000_000_000:
            continue
            
        # Kita meloloskan semua yang likuid agar di-X-Ray oleh analyze_kavaleri_special
        # karena TTM Squeeze butuh data utuh untuk mendeteksi.
        ticker_clean = ticker.replace(".JK", "")
        passed_tickers.append(ticker_clean)
        
    print(f"Sensus Kavaleri selesai. Menyaring {len(passed_tickers)} saham likuid.")
    return passed_tickers


