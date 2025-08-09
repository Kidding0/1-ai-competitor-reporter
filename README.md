# AI Competitor Reporter — $0 MVP

Minimalistiska sistēma, kas reizi nedēļā automātiski vāc publiskus datus par konkurentiem,
salīdzina ar iepriekšējo periodu un ģenerē **HTML/PDF atskaiti** ar 3–5 "insightiem" un konkrētām darbībām.
("LV/RU" — galvenās sadaļas būs abās valodās — lv/ru.)

**Bez maksas** uz GitHub Actions + GitHub Pages + Telegram botu.

---

## Īsumā kā tas strādā

- `src/scrape.py` — paņem katru vietni no `config/competitors.yaml`, atver kategoriju URL, nolasa produktus (nosaukums/cena/saite/krājumi).
- `src/diff.py` — salīdzina ar iepriekšējo nedēļu un ģenerē notikumus: `NEW_ITEM`, `PRICE_DOWN_10`, `BACK_IN_STOCK`, `PROMO_BANNER_CHANGE`.
- `src/insights.py` — **noteikumu bāzēts** (bez LLM) ģenerē īsus secinājumus un "ko darīt" (LV/RU).
- `src/report.py` — renderē `docs/reports/YYYY-MM-DD/report.html`, saglabā grafikus PNG, atjauno `docs/index.html`.
- `src/bot.py` — nosūta Telegram ziņu ar īsu kopsavilkumu + saiti uz atskaiti.
- `.github/workflows/run.yml` — palaidējs (cron + manuāls Start).

**Hostings:** GitHub Pages (no `docs/` mapes).  
**Datu glabāšana:** CSV (`data/`) + git vēsture.  
**Valoda/valūta:** LV/RU, €.

---

## Setup (once)

1. **Izveido jaunu repo** pie sevis GitHub: `ai-competitor-reporter` un ielādē visu šī ZIP saturu.
2. **Secrets** (Repo → Settings → Secrets and variables → Actions → New repository secret):
   - `TELEGRAM_BOT_TOKEN` — izveido botu @BotFather, ieliec te tokenu
   - `TELEGRAM_CHAT_ID` — tava čata ID (pēc /start botā; vari iegūt arī ar `python src/bot.py --whoami` lokāli)
   - *(opc.)* `OPENAI_API_KEY` — ja gribi skaistāku teksta formulēšanu (pagaidām neobligāti)
3. **GitHub Pages**: Repo → Settings → Pages → `Deploy from a branch` → Branch: `main` / Folder: `/docs`.
4. Atver `config/competitors.yaml` un aizpildi **reālos** URL + selektorus (skat. komentārus tajā failā). Sākt vari ar 3–5 saitēm.
5. Atver **Actions** cilni un palaid manuāli workflow **"Build & Report"** (vai pagaidi pirmdienas grafiku).

> Pēc pirmā skrējiena atskaite būs pieejama: `https://<tavs_niks>.github.io/ai-competitor-reporter/reports/YYYY-MM-DD/report.html`

---

## Konfigurācija

- `config/settings.yaml` — vispārējie iestatījumi (signāli, valoda, sliekšņi u.c.).
- `config/competitors.yaml` — vietņu saraksts un CSS selektori (skat. piemērus failā).
- **Svarīgi:** Šis MVP izmanto vienkāršus CSS selektorus; sākumam izvēlies lapas bez smagiem JS.

---

## Lokalā palaišana (pēc vēlēšanās)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install --with-deps
python src/scrape.py
python src/diff.py
python src/insights.py
python src/report.py
python src/bot.py --send-latest
```

---

## Ieteikumi nišai "santehnika/Flīzes Baltijā"

Sākt ar 3–5 lieliem veikaliem (piemēram, 220.lv kategorijas, Kurši/Depo flīžu sadaļas u.c.).
Ievadi to **kategoriju URL** `competitors.yaml` un pamazām dod klāt pārējos.
(Selektorus var paņemt caur DevTools → Inspect element — `.product-card`, `.price`, `.title` utt.)

---

## Juridika

Tiek vākta **tikai publiski pieejama informācija**. Ievēro `robots.txt`, liec saprātīgu grafiku (cron), izmanto kešus. 
Ja kāda vietne bloķē skrāpēšanu — respektē un izņem to no saraksta.

---

## Autors / Pielāgojumi

Repo sagatave atbalsta **LV/RU** tekstus. Tālāk var pievienot e-pasta piegādi, Postgres, Apify u.c.
