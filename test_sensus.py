from app.services.engines.data_engine import download_daily_data
from app.services.engines.master_engine import calculate_master_score

chunk = ['BBCA.JK', 'BMRI.JK']
print("Downloading data...")
batch_data = download_daily_data(chunk, period="1y", use_premium=True)

for ticker, df in batch_data.items():
    print(f"--- {ticker} ---")
    if df is None or df.empty:
        print("Empty DataFrame!")
        continue
    analysis = calculate_master_score(df)
    if analysis.get("error"):
        print(f"Error in analysis: {analysis['error']}")
    else:
        print(f"Success! Score: {analysis['composite_score']}")
        print(f"Recommendations: {analysis['recommendation']}")
