# Leaflet cache

Downloaded leaflet data is stored here before parsing. Contents are gitignored except this file.

## Layout

```
leaflets/
  {store}/                    # lidl, aldi, ...
    {YYYY-MM-DD}_{YYYY-MM-DD}/   # promotion week (from_until)
      meta.json               # store, source_url, downloaded_at, promo_from, promo_until
      publication.json        # raw payload (Lidl: Schwarz API; Aldi: spreads.json + page text)
      pages/                  # optional per-page JSON
      leaflet.pdf             # optional PDF when available
    super-savers/             # Lidl only: optional API snapshots
      {timestamp}.json
  tesco/
    storage-state.json        # Playwright cookies (gitignored; see save_tesco_session.py)
    {YYYY-MM-DD}_{YYYY-MM-DD}/
      publication.json          # Fresh 4 products + optional page_text
      meta.json
```

## Regenerating

```bash
python scripts/update_promotions.py              # download + parse
python scripts/update_promotions.py --skip-download  # parse cache only
```
