import asyncio
import sys
from app.services.engines.data_engine import download_daily_data, download_intraday_data
from app.api.routes import scan_swing, scan_ninja

def test_free_mode():
    print("Testing Free Mode Downloads...")
    daily = download_daily_data(["BBCA.JK"], period="1mo", use_premium=False)
    if "BBCA.JK" in daily and not daily["BBCA.JK"].empty:
        print("✅ Daily Free Data Works!")
    else:
        print("❌ Daily Free Data Failed!")
        
    intra = download_intraday_data(["BBCA.JK"], interval="5m", period="1d", use_premium=False)
    if "BBCA.JK" in intra and not intra["BBCA.JK"].empty:
        print("✅ Intraday Free Data Works!")
    else:
        print("❌ Intraday Free Data Failed!")

def test_routes():
    print("\nTesting Scan Routes (Free Mode)...")
    try:
        swing_res = scan_swing(premium=False)
        print("✅ Swing Scan Route Works!")
    except Exception as e:
        print(f"❌ Swing Scan Route Failed: {e}")

if __name__ == "__main__":
    test_free_mode()
    test_routes()
    print("\nAll tests completed.")
