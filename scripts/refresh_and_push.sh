#!/usr/bin/env bash
# Fetch latest leaflets, regenerate CSV/site, commit and push to GitHub.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/update_promotions.py --refresh-leaflets "$@"

git add output/ docs/
if git diff --staged --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "Update promotions"
git push origin main
echo "Pushed. Open the site and click Reload data (or wait ~1 min for Pages)."
