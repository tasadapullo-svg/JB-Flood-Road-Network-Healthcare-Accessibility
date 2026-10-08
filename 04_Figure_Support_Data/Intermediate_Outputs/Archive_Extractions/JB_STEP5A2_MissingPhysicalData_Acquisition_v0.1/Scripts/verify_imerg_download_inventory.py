from pathlib import Path
import re
import pandas as pd
from datetime import date

ROOT = Path(r"./IMERG_JB_SUBSET_2016_2025")

START = date(2016, 1, 1)
END   = date(2025, 12, 31)
EXPECTED_DAYS = (END - START).days + 1
EXPECTED_MONTHS = 120

files = [p for p in ROOT.rglob("*") if p.is_file()]
rows = []
for p in files:
    m = re.search(r"(20\d{6})", p.name)
    rows.append({
        "file": str(p),
        "size_bytes": p.stat().st_size,
        "yyyymmdd_in_name": m.group(1) if m else ""
    })

df = pd.DataFrame(rows)
print("files:", len(df))
print("expected daily timesteps:", EXPECTED_DAYS)
print("expected monthly timesteps:", EXPECTED_MONTHS)
df.to_csv("IMERG_download_inventory.csv", index=False)

# This script intentionally does not authenticate or download data.
# Use the official GES DISC subsetter, then run this inventory/QC locally.
