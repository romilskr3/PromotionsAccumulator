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

**Caches are never auto-deleted.** Old week folders stay on disk until you remove them manually.

### SuperValu sources

| Step | URL |
|------|-----|
| Hub (preferred) | `https://supervalu.ie/offers` |
| Per-cycle manifest | `https://supervalu.ie/offers/leaflet/{id}` (e.g. `608`) |
| PDF | `https://supervalu.ie/image/var/files/pdf2web/{filename}` |

If this week’s leaflet is not on the site yet (or the hub only shows a short teaser), download falls back to the best **local** cached PDF: a week that is still valid today, or else the most recent `promo_until` on disk. Archived PDFs that remain online but whose dates have ended are not written over an active cache.
