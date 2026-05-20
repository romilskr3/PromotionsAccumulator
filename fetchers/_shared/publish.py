from __future__ import annotations

import shutil
from pathlib import Path

from fetchers._shared.csv_export import CSV_OUTPUT_PATH, write_promotions_csv
from fetchers._shared.html import FAVICON_PATH, INDEX_HTML_PATH, write_promotions_site
from fetchers._shared.models import Promotion
from fetchers._shared.site_config import write_site_config

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
DOCS_DIR = REPO_ROOT / "docs"

def write_all_outputs(promotions: list[Promotion]) -> dict[str, Path]:
    """Write CSV + site to output/, mirror to docs/ for GitHub Pages."""
    csv_path = write_promotions_csv(promotions)
    index_path = write_promotions_site()
    favicon_path = _copy_favicon(OUTPUT_DIR / "favicon.svg")
    (OUTPUT_DIR / ".nojekyll").touch()
    write_site_config(OUTPUT_DIR / "site-config.json")
    docs_paths = _mirror_pages_files()
    return {
        "csv": csv_path,
        "index": index_path,
        "favicon": favicon_path,
        "docs_index": docs_paths["index"],
    }


def _copy_favicon(dest: Path) -> Path:
    shutil.copy2(FAVICON_PATH, dest)
    return dest


def _mirror_pages_files() -> dict[str, Path]:
    """Copy site assets to docs/ (GitHub branch deploy only serves / or /docs)."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CSV_OUTPUT_PATH, DOCS_DIR / "promotions.csv")
    shutil.copy2(INDEX_HTML_PATH, DOCS_DIR / "index.html")
    shutil.copy2(OUTPUT_DIR / ".nojekyll", DOCS_DIR / ".nojekyll")
    shutil.copy2(OUTPUT_DIR / "site-config.json", DOCS_DIR / "site-config.json")
    shutil.copy2(FAVICON_PATH, DOCS_DIR / "favicon.svg")
    return {"index": DOCS_DIR / "index.html"}
