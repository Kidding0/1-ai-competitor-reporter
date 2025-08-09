# src/bot.py
import os, json, argparse, requests
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(__file__))
INS = os.path.join(BASE, "data", "insights.json")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

def get_me():
    return requests.get(API_URL + "/getMe").json()

def send_message(text, parse_mode=None):
    payload = {"chat_id": CHAT_ID, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    r = requests.post(API_URL + "/sendMessage", json=payload)
    return r.json()

def main_send_latest():
    if not (BOT_TOKEN and CHAT_ID):
        print("[bot] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return
    today = datetime.now(timezone.utc).date().isoformat()
    url = url = f"https://Kidding0.github.io/1-ai-competitor-reporter/reports/{today}/report.html"
    ins = {"insights":[]}
    if os.path.exists(INS):
        ins = json.load(open(INS, encoding="utf-8"))
    # Build brief
    lines = ["📰 Konkurentu atskaite / Отчёт по конкурентам", "", "Top:" ]
    for i, it in enumerate(ins.get("insights", [])[:3], 1):
        lines.append(f"{i}. {it.get('lv')}")
    lines.append("")
    lines.append(f"Pilnā atskaite: {url}")
    send_message("\n".join(lines))

def whoami():
    if not BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN")
        return
    print(get_me())

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--send-latest", action="store_true")
    ap.add_argument("--whoami", action="store_true")
    args = ap.parse_args()
    if args.whoami:
        whoami()
    elif args.send_latest or args.send_latest:
        main_send_latest()
    else:
        print("Use --send-latest or --whoami")
