import os
import re

advanced_dir = r"D:\PROJEK APLIKASI\IDX_SuperScreener\app\services\advanced"

def process_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        new_content = content
        
        # Replace backend.app.services.technical -> app.services.advanced.technical
        new_content = new_content.replace("backend.app.services.technical", "app.services.advanced.technical")
        
        # In bandarmology_engine.py, we have backend.app.schemas... and backend.app.services...
        # We need to strip out the API specific logic. For now, just fix imports and comment out or remove specific functions.
        if "bandarmology_engine.py" in filepath:
            # We want to keep only build_bandarmology and enrich_ohlcv and related calculators
            # We can strip the rest if we want, or just leave it and remove the import errors.
            new_content = re.sub(r"from backend\.app\.schemas.*?import.*?\n", "", new_content)
            new_content = re.sub(r"from backend\.app\.services.*?import.*?\n", "from app.services.advanced.utils import clamp\n", new_content)
            new_content = re.sub(r"from sqlalchemy.*?import.*?\n", "", new_content)
            
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated imports in {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

for root, dirs, files in os.walk(advanced_dir):
    for file in files:
        if file.endswith(".py"):
            process_file(os.path.join(root, file))

print("Clean advanced files done.")
