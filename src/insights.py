# src/insights.py
import os, csv, json
from collections import Counter, defaultdict
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(__file__))
EVT = os.path.join(BASE, "data", "events.csv")
OUT = os.path.join(BASE, "data", "insights.json")

def load_events(days=7):
    evs = []
    if not os.path.exists(EVT): return evs
    with open(EVT, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            evs.append(row)
    # last N days
    cutoff = datetime.utcnow() - timedelta(days=14)
    evs = [e for e in evs if datetime.fromisoformat(e["ts"].replace("Z","")) >= cutoff]
    return evs

def rule_based_insights(evs, top_n=5):
    cnt = Counter([e["event"] for e in evs])
    by_comp = defaultdict(list)
    for e in evs:
        by_comp[e["competitor"]].append(e)

    insights = []

    # 1) price drops spike
    drop = sum(1 for e in evs if e["event"].startswith("PRICE_DOWN"))
    if drop >= 3:
        insights.append({
            "lv": f"Tirgū novērots cenu kritumu vilnis ({drop} gadījumi) — iespējama akciju fāze vai krājumu optimizācija.",
            "ru": f"Наблюдается волна снижения цен ({drop} случаев) — возможно, началась акция или распродажа остатков.",
            "action": "Pārskatīt cenas do 3–5 enkura SKU; pastiprināt komunikāciju par piegādes termiņiem."
        })

    # 2) new items
    new_items = sum(1 for e in evs if e["event"]=="NEW_ITEM")
    if new_items >= 3:
        insights.append({
            "lv": f"Konkurenti izlaiduši {new_items} jaunus SKU pēdējās 2 nedēļās.",
            "ru": f"Конкуренты добавили {new_items} новых SKU за последние 2 недели.",
            "action": "Pārvērtēt kategoriju lapas; sasva rēķinu ar pieprasītākajām specifikācijām."
        })

    # 3) availability changes
    avail_ch = sum(1 for e in evs if e["event"]=="AVAIL_CHANGE")
    if avail_ch >= 3:
        insights.append({
            "lv": f"Biežas pieejamības izmaiņas ({avail_ch}) — loģistikas svārstības tirgū.",
            "ru": f"Частые изменения наличия ({avail_ch}) — признак логистических колебаний на рынке.",
            "action": "Komunicēt piegādes laiku; rezervēt krājumus enkura pozīcijām."
        })

    # 4) most active competitor
    most = max(by_comp.items(), key=lambda kv: len(kv[1]))[0] if by_comp else None
    if most:
        insights.append({
            "lv": f"Aktīvākais konkurents: {most} (vairāk izmaiņu nedēļā).",
            "ru": f"Самый активный конкурент: {most} (больше всего изменений за неделю).",
            "action": "Sekot viņa kampaņām; salīdzināt cenu koridorus."
        })

    # ensure top_n
    return insights[:top_n]

def main():
    evs = load_events()
    ins = rule_based_insights(evs, top_n=5)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"insights": ins}, f, ensure_ascii=False, indent=2)
    print(f"[insights] wrote {OUT} ({len(ins)} items)")

if __name__ == "__main__":
    main()
