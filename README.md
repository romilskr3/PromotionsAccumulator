# Promotions Accumulator

Fetches fruit and vegetable promotions from Dublin supermarkets (Lidl, Aldi, Tesco) and publishes a sortable comparison table on GitHub Pages.

**Live site:** [romilskr3.github.io/PromotionsAccumulator](https://romilskr3.github.io/PromotionsAccumulator/)

## Setup (once)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chromium
```

Tesco Clubcard prices need a saved browser session (Akamai blocks headless bots):

```bash
python3 scripts/save_tesco_session.py   # once, or when Tesco stops working
```

## Update the live website

From the project root, with your virtualenv active:

```bash
./scripts/refresh_and_push.sh
```

This will:

1. Download the latest leaflets and fetch offers (`--refresh-leaflets`)
2. Regenerate `output/` and `docs/` (CSV + HTML)
3. Commit and push to `main`
4. Trigger a GitHub Pages redeploy (usually within a minute)

Then open the live site and click **Reload data** (top right) to load the new `promotions.csv`.

**Optional (GitHub):** **Actions** → **Refresh promotions data** → **Run workflow** — same steps in the cloud if your account’s Actions billing is OK. Until then, use the script above.

**Manual equivalent:**

```bash
python3 scripts/update_promotions.py --refresh-leaflets
git add output/ docs/
git commit -m "Update promotions"
git push origin main
```

**Re-parse cached leaflets only** (no download):

```bash
python3 scripts/update_promotions.py --skip-download
```

**One store:**

```bash
python3 scripts/update_promotions.py --store lidl
```

## View locally

The site loads `promotions.csv` via `fetch`, which does not work on `file://`. Serve `output/`:

```bash
cd output && python3 -m http.server 8080
# http://127.0.0.1:8080/
```

## GitHub Pages (first-time deploy)

1. Create a public repo and push this project to `main`.
2. **Settings → Pages → Build and deployment:** deploy from branch `main`, folder **`/docs`**.
3. Site URL: `https://<username>.github.io/<repo-name>/`

Each push that updates `docs/` refreshes the site. No GitHub Actions workflow is required.

## Stores

| Store | Source |
|-------|--------|
| Lidl | Super Savers fruit & veg (weekly) |
| Aldi | Super 6 from leaflet spreads |
| Tesco | Fresh 4 (Clubcard prices; needs saved session) |
| SuperValu, Dunnes | Not implemented |

Cached leaflets live under [`leaflets/`](leaflets/).

## Customisation

**Favourites** keywords (vegetables tab): edit `FREQUENT_BUY_KEYWORDS` in [`fetchers/_shared/frequent_buy.py`](fetchers/_shared/frequent_buy.py), then run `./scripts/refresh_and_push.sh`.

Site UI and table logic: [`fetchers/_shared/html.py`](fetchers/_shared/html.py).
