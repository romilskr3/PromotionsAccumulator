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

### Output files (`output/`)

| File | Use |
|------|-----|
| `output/promotions.csv` | All promotion data (source of truth) |
| `output/index.html` | Interactive table — loads CSV in the browser |
| `output/.nojekyll` | Lets GitHub Pages serve the site as static files |

The HTML page supports **All / Active / Not active** filters, search, and **click column headers to sort**.

Cached leaflets: [`leaflets/`](leaflets/) (see [`leaflets/README.md`](leaflets/README.md))

## Publish on your personal GitHub (GitHub Pages)

One-time setup on [github.com](https://github.com) (personal account):

1. **Create a new repository** (e.g. `PromotionsAccumulator`). Public or private both work with Pages.
2. **Push this project** to that repo (`main` branch).
3. **Enable Pages:** repo → **Settings** → **Pages** → **Build and deployment**

   **Recommended if Actions fail** (e.g. billing lock): **Deploy from a branch** → `main` → **`/docs`**.  
   No workflow required; GitHub serves `docs/index.html` and `docs/promotions.csv` directly.

   **Optional:** **GitHub Actions** → workflow [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml) deploys `docs/` after each push. Requires Actions to run on your account ([Billing settings](https://github.com/settings/billing)).

4. After deploy (usually 1–2 minutes), your site is live at:

   **`https://<your-github-username>.github.io/<repository-name>/`**

   Example: `https://jane.github.io/PromotionsAccumulator/`

### Update the live site

Whenever promotions change:

```bash
python3 scripts/update_promotions.py
git add output/ docs/
git commit -m "Update promotions"
git push
```

Pages rebuilds when `docs/` changes on `main` (branch deploy), or when the deploy workflow succeeds (Actions).

### Refresh from the website

The live site has a **Refresh data** button (top right). GitHub Pages cannot run Python in the browser, so refresh uses a **GitHub Actions** workflow:

1. Click **Refresh data** on the site.
2. Confirm, then **submit the pre-filled issue** that opens in a new tab (title `[refresh-promotions]`).
3. The workflow downloads leaflets, runs `update_promotions.py`, and pushes updated `output/` and `docs/`.
4. The page polls the CSV and reloads when the timestamp changes (~3–8 minutes).

**One-time:** enable **Issues** on the repo (Settings → General → Features → Issues).

**Optional — Tesco in CI:** add repo secret `TESCO_STORAGE_STATE_B64` (base64 of `leaflets/tesco/storage-state.json`) so Clubcard prices refresh on GitHub too. Without it, Lidl and Aldi still update; Tesco uses cached data or is skipped.

Manual run: **Actions** → **Refresh promotions data** → **Run workflow**.

### Actions still show “billing issue”?

That message means GitHub is **not starting any job** on hosted runners — renaming or recreating the workflow does not fix it. Check [github.com/settings/billing](https://github.com/settings/billing) (payment method, overdue invoices, spending limits). After billing is truly cleared, use **Actions → Deploy site to GitHub Pages → Re-run all jobs**, or push any commit to `main`.

Until then, use **branch deploy** (`main` / `docs`) — your site files are already in the repo.

### View locally (no GitHub)

The site loads `promotions.csv` via `fetch`, which browsers block on `file://`. Use a local server:

```bash
cd output && python3 -m http.server 8080
# http://127.0.0.1:8080/
```

You can also open `output/promotions.csv` directly to inspect the data.

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
