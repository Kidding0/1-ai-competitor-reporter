# src/scrape.py
import os, sys, time, yaml, csv, re
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG = os.path.join(BASE_DIR, "config", "competitors.yaml")
OUT = os.path.join(BASE_DIR, "data", "current.csv")

def parse_price(text: str):
    if not text: return None
    t = re.sub(r"[^\d,.\-]", "", text).replace(",", ".")
    try:
        return float(re.findall(r"-?\d+(?:\.\d+)?", t)[0])
    except Exception:
        return None

def scrape_site(page, spec):
    page.goto(spec["base_url"], timeout=60000)
    page.wait_for_timeout(1500)
    sels = spec["selectors"]
    items = page.query_selector_all(sels["item"])
    rows = []
    for it in items[:200]:
        title = (it.query_selector(sels["title"]).inner_text().strip()
                 if it.query_selector(sels["title"]) else "")
        price_t = (it.query_selector(sels["price"]).inner_text().strip()
                 if it.query_selector(sels["price"]) else "")
        link_e = it.query_selector(sels["link"])
        link = link_e.get_attribute("href") if link_e else spec["base_url"]
        if link and link.startswith("/"):
            from urllib.parse import urljoin
            link = urljoin(spec["base_url"], link)
        avail = (it.query_selector(sels.get("availability","")).inner_text().strip()
                 if sels.get("availability") and it.query_selector(sels["availability"]) else "")
        price = parse_price(price_t)
        if not title: 
            continue
        rows.append([spec["name"], link or spec["base_url"], title, price if price is not None else "", avail, datetime.utcnow().isoformat()])
    return rows

def main():
    with open(CONFIG, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows_all = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for site in config.get("sites", []):
            try:
                print(f"[scrape] {site['name']} -> {site['base_url']}")
                rows = scrape_site(page, site)
                print(f"  got {len(rows)} rows")
                rows_all.extend(rows)
            except Exception as e:
                print(f"[error] {site['name']}: {e}")
        browser.close()

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["competitor","url","title","price","availability","ts"])
        w.writerows(rows_all)
    print(f"[scrape] wrote {len(rows_all)} rows to {OUT}")

if __name__ == "__main__":
    main()
