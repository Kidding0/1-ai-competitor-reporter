# src/report.py
import os, json, pandas as pd
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(__file__))
DATA_CUR = os.path.join(BASE, "data", "current.csv")
EVENTS = os.path.join(BASE, "data", "events.csv")
INS = os.path.join(BASE, "data", "insights.json")
TEMPL_DIR = os.path.join(BASE, "templates")
OUT_DIR = os.path.join(BASE, "docs", "reports")
INDEX = os.path.join(BASE, "docs", "index.html")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def make_price_chart(df, outpath):
    # Simple price distribution chart by competitor
    plt.figure()
    if not df.empty and "competitor" in df.columns and "price" in df.columns:
        df2 = df.dropna(subset=["price"])
        if not df2.empty:
            box = df2.boxplot(by="competitor", column="price", grid=False, rot=35)
    plt.title("")
    plt.suptitle("")
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()

def render_report():
    today = datetime.utcnow().date().isoformat()
    outdir = os.path.join(OUT_DIR, today)
    ensure_dir(outdir)

    cur = load_csv(DATA_CUR)
    ev = load_csv(EVENTS)
    ins = {"insights": []}
    if os.path.exists(INS):
        ins = json.load(open(INS, encoding="utf-8"))

    # Chart
    fig_prices = os.path.join(outdir, "fig_prices.png")
    make_price_chart(cur, fig_prices)

    # Template
    env = Environment(loader=FileSystemLoader(TEMPL_DIR))
    tpl = env.get_template("report.html.j2")

    # Build events for table
    events_list = []
    for _, r in ev.tail(100).iterrows():
        events_list.append({
            "competitor": r.get("competitor",""),
            "label": r.get("event",""),
            "url": r.get("url","")
        })

    html = tpl.render(
        period_label=f"Nedēļa / Неделя • {today}",
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        top_n=len(ins["insights"]),
        insights=ins["insights"],
        events=events_list
    )
    out_html = os.path.join(outdir, "report.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    # Update index
    # naive append if not exists
    if os.path.exists(INDEX):
        idx = open(INDEX, encoding="utf-8").read()
    else:
        idx = "<html><body><h1>Atskaites</h1><ul></ul></body></html>"
    insertion = f'<li><a href="reports/{today}/report.html">{today}</a></li>'
    if insertion not in idx:
        idx = idx.replace("</ul>", f"{insertion}\n</ul>")
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(idx)

    print(f"[report] wrote {out_html}")

if __name__ == "__main__":
    render_report()
