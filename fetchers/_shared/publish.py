from __future__ import annotations

from pathlib import Path

from fetchers._shared.html import HTML_OUTPUT_PATH, render_promotions_html
from fetchers._shared.markdown import write_promotions
from fetchers._shared.models import Promotion

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "index.html"


def write_all_outputs(promotions: list[Promotion]) -> dict[str, Path]:
    """Write markdown, local HTML, and docs/index.html for GitHub Pages."""
    html_content = render_promotions_html(promotions)
    html_path = _write_html(HTML_OUTPUT_PATH, html_content)
    docs_path = _write_html(DOCS_INDEX_PATH, html_content)
    (DOCS_INDEX_PATH.parent / ".nojekyll").touch()
    return {
        "markdown": write_promotions(promotions),
        "html": html_path,
        "pages": docs_path,
    }


def _write_html(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
