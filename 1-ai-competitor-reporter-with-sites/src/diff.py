# src/diff.py
import os, csv
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(__file__))
CUR = os.path.join(BASE, "data", "current.csv")
PREV = os.path.join(BASE, "data", "previous.csv")
EVT = os.path.join(BASE, "data", "events.csv")

def load_csv(path):
    rows = []
    if not os.path.exists(path): return rows
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
    return rows

def index_by_key(rows, key):
    d = {}
    for x in rows:
        d[x[key]] = x
    return d

def pct_change(a, b):
    try:
        a = float(a); b = float(b)
        if a == 0: return None
        return (b - a) / a * 100.0
    except Exception:
        return None

def main():
    cur = load_csv(CUR)
    prev = load_csv(PREV)
    prev_idx = index_by_key(prev, "url")
    events = []

    for row in cur:
        url = row["url"]
        ts = row["ts"]
        comp = row["competitor"]
        prev_row = prev_idx.get(url)
        if not prev_row:
            events.append([ts, comp, "NEW_ITEM", url, "", row.get("price","")])
            continue
        if row.get("price") and prev_row.get("price"):
            pc = pct_change(prev_row["price"], row["price"])
            if pc is not None and abs(pc) >= 8:
                ev = "PRICE_UP_8" if pc>0 else "PRICE_DOWN_8"
                events.append([ts, comp, ev, url, prev_row["price"], row["price"]])
        if (row.get("availability") or "") != (prev_row.get("availability") or ""):
            events.append([ts, comp, "AVAIL_CHANGE", url, prev_row.get("availability",""), row.get("availability","")])

    # write events
    os.makedirs(os.path.dirname(EVT), exist_ok=True)
    write_header = not os.path.exists(EVT)
    with open(EVT, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["ts","competitor","event","url","old_price","new_price"])
        w.writerows(events)

    # rotate current->previous
    import shutil
    shutil.copyfile(CUR, PREV)
    print(f"[diff] events appended: {len(events)}")

if __name__ == "__main__":
    main()
