# Refresh trigger worker

Cloudflare Worker that starts the GitHub Actions refresh workflow. The site calls this URL; the GitHub PAT stays in Cloudflare secrets (never in the repo).

## One-time setup

1. Install [Wrangler](https://developers.cloudflare.com/workers/wrangler/install-and-update/): `npm install -g wrangler`
2. Log in: `wrangler login`
3. From this directory:

```bash
cd workers/refresh-trigger
wrangler secret put GITHUB_TOKEN
# Paste the same fine-grained PAT (Actions: Read and write on this repo only)
wrangler deploy
```

4. Copy the worker URL (e.g. `https://promotions-accumulator-refresh.<subdomain>.workers.dev`)
5. In GitHub repo **Settings → Secrets and variables → Actions → Variables**, add:
   - Name: `REFRESH_API_URL`
   - Value: your worker URL
6. Run **Actions → Refresh promotions data** once (writes the URL into `site-config.json`)

After that, anyone can click **Refresh data** on the live site.
