#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for meta_path in root.rglob("*.restore.json"):
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    out = meta_path.with_name(meta["original_file_name"])
    h = hashlib.sha256()
    with out.open("wb") as dst:
        for part in meta["parts"]:
            p = meta_path.parent / part["file"]
            ph = hashlib.sha256(p.read_bytes()).hexdigest()
            if ph != part["sha256"]:
                raise SystemExit(f"Part checksum mismatch: {p}")
            data = p.read_bytes()
            h.update(data)
            dst.write(data)
    if h.hexdigest() != meta["original_sha256"]:
        raise SystemExit(f"Restored checksum mismatch: {out}")
    print(f"Restored {out.relative_to(root)}")
