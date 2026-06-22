import yfinance as yf
import traceback
from app.services.engines.technical_engine import analyze_swing_fortress, analyze_ninja_scalper

df = yf.download("BBCA.JK", period="1y", interval="1d", progress=False)

if isinstance(df.columns, tuple) or hasattr(df.columns, 'levels'):
    df.columns = df.columns.get_level_values(0)

df = df.rename(columns={
    "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"
})

print("Testing Swing Fortress")
try:
    print(analyze_swing_fortress(df))
except Exception as e:
    traceback.print_exc()

print("Testing Ninja Scalper")
try:
    print(analyze_ninja_scalper(df))
except Exception as e:
    traceback.print_exc()
