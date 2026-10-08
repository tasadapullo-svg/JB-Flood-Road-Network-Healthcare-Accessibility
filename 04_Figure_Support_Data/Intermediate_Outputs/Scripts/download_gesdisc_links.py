"""
Download a GES DISC generated subset-links TXT file without putting credentials in this script.

Setup:
1. Create %USERPROFILE%\.netrc on Windows:
   machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD

2. In the GES DISC web interface create the spatial/temporal subset and download the links-list TXT.

3. Run:
   python download_gesdisc_links.py subset_links.txt IMERG_JB_2016_2024

Security:
- This script reads Earthdata credentials locally from .netrc.
- Do not upload .netrc.
"""

from pathlib import Path
import sys, netrc, requests, re, hashlib, csv, time

if len(sys.argv) < 2:
    raise SystemExit("Usage: python download_gesdisc_links.py subset_links.txt [output_dir]")

link_file = Path(sys.argv[1])
out_dir = Path(sys.argv[2] if len(sys.argv) >= 3 else "IMERG_JB_SUBSET")
out_dir.mkdir(parents=True, exist_ok=True)

auth = netrc.netrc().authenticators("urs.earthdata.nasa.gov")
if not auth:
    raise SystemExit("Earthdata credentials not found in .netrc")

username, _, password = auth
session = requests.Session()
session.auth = (username, password)
session.headers.update({"User-Agent":"JB-Step5A2-IMERG-downloader/1.0"})

links = [x.strip() for x in link_file.read_text(encoding="utf-8").splitlines()
         if x.strip() and not x.lstrip().startswith("#")]

inventory = []

def safe_name(url, i):
    label = re.search(r"[?&]LABEL=([^&]+)", url)
    if label:
        return requests.utils.unquote(label.group(1))
    tail = url.split("?")[0].rstrip("/").split("/")[-1]
    return tail or f"subset_{i:05d}.nc4"

for i, url in enumerate(links, 1):
    name = safe_name(url, i)
    dest = out_dir / name
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[{i}/{len(links)}] exists: {name}")
    else:
        print(f"[{i}/{len(links)}] downloading: {name}")
        with session.get(url, stream=True, allow_redirects=True, timeout=180) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(1024*1024):
                    if chunk:
                        f.write(chunk)

    h = hashlib.sha256()
    with dest.open("rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)

    inventory.append({
        "file": dest.name,
        "size_bytes": dest.stat().st_size,
        "sha256": h.hexdigest(),
        "source_url": url
    })
    time.sleep(0.05)

with (out_dir/"IMERG_download_inventory.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["file","size_bytes","sha256","source_url"])
    w.writeheader()
    w.writerows(inventory)

print("DONE:", len(inventory), "files")
print("Inventory:", out_dir/"IMERG_download_inventory.csv")
