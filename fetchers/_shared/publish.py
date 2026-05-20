from __future__ import annotations

import shutil
from pathlib import Path

from fetchers._shared.csv_export import CSV_OUTPUT_PATH, write_promotions_csv
from fetchers._shared.html import INDEX_HTML_PATH, write_promotions_site
from fetchers._shared.models import Promotion

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
DOCS_DIR = REPO_ROOT / "docs"

def write_all_outputs(promotions: list[Promotion]) -> dict[str, Path]:
    """Write CSV + site to output/, mirror to docs/ for GitHub Pages."""
    csv_path = write_promotions_csv(promotions)
    index_path = write_promotions_site()
    (OUTPUT_DIR / ".nojekyll").touch()
    docs_paths = _mirror_pages_files()
    return {"csv": csv_path, "index": index_path, "docs_index": docs_paths["index"]}


def _mirror_pages_files() -> dict[str, Path]:
    """Copy site assets to docs/ (GitHub branch deploy only serves / or /docs)."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CSV_OUTPUT_PATH, DOCS_DIR / "promotions.csv")
    shutil.copy2(INDEX_HTML_PATH, DOCS_DIR / "index.html")
    shutil.copy2(OUTPUT_DIR / ".nojekyll", DOCS_DIR / ".nojekyll")
    return {"index": DOCS_DIR / "index.html"}
