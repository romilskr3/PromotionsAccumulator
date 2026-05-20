# Promotions Accumulator

Personal tool to fetch fruit and vegetable promotions from Dublin supermarkets into a sortable table, published on GitHub Pages.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chromium
```

If Playwright cannot find browsers, set:

```bash
export PLAYWRIGHT_BROWSERS_PATH="$HOME/Library/Caches/ms-playwright"
```

## Usage

```bash
# Download leaflets + fetch offers + update outputs
python3 scripts/update_promotions.py

# Re-parse cached leaflets only (no leaflet download)
python3 scripts/update_promotions.py --skip-download

# Force fresh leaflet download
python3 scripts/update_promotions.py --refresh-leaflets

# One store
python3 scripts/update_promotions.py --store lidl

# Tesco: save Clubcard browser session once (Akamai blocks headless bots)
python3 scripts/save_tesco_session.py
python3 scripts/update_promotions.py --store tesco
```

### Output files

| File | Use |
|------|-----|
| `output/promotions.md` | Plain markdown (local) |
| `output/promotions.html` | Interactive table (local) |
| `docs/index.html` | Same interactive table — **published on GitHub Pages** |

The HTML page supports **All / Active / Not active** filters, search, and **click column headers to sort**.

Cached leaflets: [`leaflets/`](leaflets/) (see [`leaflets/README.md`](leaflets/README.md))

## Publish on your personal GitHub (GitHub Pages)

One-time setup on [github.com](https://github.com) (personal account):

1. **Create a new repository** (e.g. `PromotionsAccumulator`). Public or private both work with Pages.
2. **Push this project** to that repo (`main` branch).
3. **Enable Pages:** repo → **Settings** → **Pages** → **Build and deployment**
   - **Source:** GitHub Actions  
   (The workflow [`.github/workflows/pages.yml`](.github/workflows/pages.yml) deploys the `docs/` folder.)
4. After the first successful deploy, your site is live at:

   **`https://<your-github-username>.github.io/<repository-name>/`**

   Example: `https://jane.github.io/PromotionsAccumulator/`

### Update the live site

Whenever promotions change:

```bash
python3 scripts/update_promotions.py
git add docs/index.html
git commit -m "Update promotions"
git push
```

GitHub Actions redeploys automatically when `docs/` changes.

### View locally (no GitHub)

Open `output/promotions.html` in a browser, or:

```bash
cd output && python3 -m http.server 8080
# http://127.0.0.1:8080/promotions.html
```

## Roadmap

- **Lidl Plus app login** (deferred): authenticated weekly offers from the app API, after a few more stores are done.
- **Aldi**: Super 6 from leaflet `spreads.json` page text; biweekly Savers dates (e.g. Thu 7 May – Wed 20 May).

## Stores

| Store | Status |
|-------|--------|
| Lidl | Super Savers fruit & veg only (6 per week) |
| Aldi | Super 6 fruit & veg from leaflet spreads (biweekly Savers dates) |
| Tesco | Fresh 4 fruit & veg (Clubcard prices from buy-list page) |
| SuperValu | Stub |
| Dunnes | Stub |

## Table columns

Supermarket, Product, Quantity, Price, From Date, Until Date, Active today
