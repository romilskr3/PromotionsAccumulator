from __future__ import annotations

from pathlib import Path

from fetchers._shared.csv_export import write_promotions_csv
from fetchers._shared.html import write_promotions_site
from fetchers._shared.models import Promotion

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"


def write_all_outputs(promotions: list[Promotion]) -> dict[str, Path]:
    """Write CSV data and static site under output/ for GitHub Pages."""
    csv_path = write_promotions_csv(promotions)
    index_path = write_promotions_site()
    (OUTPUT_DIR / ".nojekyll").touch()
    return {"csv": csv_path, "index": index_path}
