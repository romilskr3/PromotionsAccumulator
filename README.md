# Promotions Accumulator

Fetches fruit and vegetable promotions from Dublin supermarkets (Lidl, Aldi, Tesco) and publishes a sortable comparison table on GitHub Pages.

**Live site:** [romilskr3.github.io/PromotionsAccumulator](https://romilskr3.github.io/PromotionsAccumulator/)

## Setup (once)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chrome
```

Tesco Fresh 4 is public (no sign-in). If Akamai blocks automated fetches, optionally save a browser session:

```bash
python3 scripts/save_tesco_session.py   # only when Tesco stops working locally
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

Then open the live site and click **Refresh data** (top right) to fetch new leaflets via GitHub Actions and load the updated CSV.

### One-time: enable Refresh data for everyone

GitHub requires authentication to start a workflow. To let **any visitor** click Refresh without pasting a token:

1. Create a [fine-grained personal access token](https://github.com/settings/tokens?type=beta) with **Actions: Read and write** on this repo only (no other permissions needed).
2. In the repo: **Settings → Secrets and variables → Actions → New repository secret**
3. Name: `REFRESH_DISPATCH_TOKEN`, value: your token
4. Run **Actions → Refresh promotions data** once (or `./scripts/refresh_and_push.sh` with `REFRESH_DISPATCH_TOKEN` set locally)

The workflow embeds the token in `docs/site-config.json` so the site can trigger refreshes. The token is visible in that public file — keep the PAT scoped to Actions on this repo only. The workflow also has concurrency limits to reduce duplicate runs.

**Alternative:** **Actions** → **Refresh promotions data** → **Run workflow**, or `./scripts/refresh_and_push.sh` from your Mac.

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

If a store fetch **succeeds**, new rows are merged with that store’s existing CSV rows (same product+week is updated from the fetch; older weeks stay until their dates show as Ended). If a fetch **fails** or returns no rows, previous rows for that store are kept. Unselected stores are unchanged when using `--store`.

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
| Tesco | Fresh 4 (Clubcard prices; Playwright + Chrome) |
| SuperValu | [`supervalu.ie/offers`](https://supervalu.ie/offers) + `/offers/leaflet/{id}` PDF; falls back to local cache if this week is offline ([details](leaflets/README.md#supervalu-sources)) |
| Dunnes | Not implemented |

Cached leaflets live under [`leaflets/`](leaflets/).

## Customisation

**Favourites** keywords (vegetables and fruits tabs): edit `DEFAULT_FAVOURITE_KEYWORDS` in [`fetchers/_shared/frequent_buy.py`](fetchers/_shared/frequent_buy.py), then run `./scripts/refresh_and_push.sh`.

Site UI and table logic: [`fetchers/_shared/html.py`](fetchers/_shared/html.py).
