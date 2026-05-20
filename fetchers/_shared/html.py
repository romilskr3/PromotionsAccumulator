from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

from fetchers._shared.markdown import COLUMNS, _sort_key
from fetchers._shared.models import DUBLIN, Promotion

HTML_OUTPUT_PATH = Path(__file__).resolve().parents[2] / "output" / "promotions.html"


def render_promotions_html(promotions: list[Promotion]) -> str:
    now = datetime.now(DUBLIN).strftime("%Y-%m-%d %H:%M")
    rows = [_promotion_row(p) for p in sorted(promotions, key=_sort_key)]
    data_json = json.dumps(rows, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Fruit &amp; Vegetable Promotions — Dublin</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --card: #fff;
      --text: #1a1a1a;
      --muted: #5c6570;
      --border: #d8dee4;
      --accent: #00539f;
      --active: #0d7a3e;
      --inactive: #9aa3ad;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }}
    h1 {{ font-size: 1.5rem; margin: 0 0 0.25rem; }}
    .meta {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1.25rem; }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      margin-bottom: 1rem;
    }}
    .filters {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
    .filters button {{
      border: 1px solid var(--border);
      background: var(--card);
      padding: 0.4rem 0.85rem;
      border-radius: 999px;
      cursor: pointer;
      font-size: 0.9rem;
    }}
    .filters button[aria-pressed="true"] {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }}
    #search {{
      flex: 1;
      min-width: 200px;
      padding: 0.5rem 0.75rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 0.95rem;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
    thead {{ background: #eef2f6; }}
    th {{
      text-align: left;
      padding: 0.65rem 0.75rem;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      user-select: none;
      cursor: pointer;
    }}
    th:hover {{ background: #e2e8ef; }}
    th .sort {{ opacity: 0.45; font-size: 0.75rem; margin-left: 0.25rem; }}
    th[data-sort-dir="asc"] .sort::after {{ content: "▲"; opacity: 1; }}
    th[data-sort-dir="desc"] .sort::after {{ content: "▼"; opacity: 1; }}
    td {{ padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); }}
    tr:last-child td {{ border-bottom: none; }}
    tr.hidden {{ display: none; }}
    .badge {{
      display: inline-block;
      padding: 0.15rem 0.5rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
    }}
    .badge.active {{ background: #d8f0e0; color: var(--active); }}
    .badge.inactive {{ background: #eceff2; color: var(--inactive); }}
    .count {{ color: var(--muted); font-size: 0.9rem; }}
    @media (max-width: 720px) {{
      .card {{ overflow-x: auto; }}
      table {{ min-width: 720px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Fruit &amp; Vegetable Promotions — Dublin</h1>
    <p class="meta">Generated {html.escape(now)} Europe/Dublin</p>
    <div class="toolbar">
      <div class="filters" role="group" aria-label="Filter by active status">
        <button type="button" data-filter="all" aria-pressed="true">All</button>
        <button type="button" data-filter="active" aria-pressed="false">Active</button>
        <button type="button" data-filter="inactive" aria-pressed="false">Not active</button>
      </div>
      <input id="search" type="search" placeholder="Search product or store…" autocomplete="off" />
      <span class="count" id="count"></span>
    </div>
    <div class="card">
      <table id="promo-table">
        <thead>
          <tr>
            <th data-key="supermarket">Supermarket<span class="sort"></span></th>
            <th data-key="product">Product<span class="sort"></span></th>
            <th data-key="quantity">Quantity<span class="sort"></span></th>
            <th data-key="price">Price<span class="sort"></span></th>
            <th data-key="from">From Date<span class="sort"></span></th>
            <th data-key="until">Until Date<span class="sort"></span></th>
            <th data-key="active">Active<span class="sort"></span></th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </div>
  <script>
    const ROWS = {data_json};
    const tbody = document.getElementById("tbody");
    const countEl = document.getElementById("count");
    const searchEl = document.getElementById("search");
    let statusFilter = "all";
    let sortKey = "supermarket";
    let sortDir = "asc";

    function render() {{
      const q = searchEl.value.trim().toLowerCase();
      let visible = ROWS.filter((row) => {{
        if (statusFilter === "active" && !row.active) return false;
        if (statusFilter === "inactive" && row.active) return false;
        if (q) {{
          const hay = `${{row.supermarket}} ${{row.product}} ${{row.quantity}}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }}
        return true;
      }});
      visible.sort((a, b) => {{
        let av = a[sortKey] ?? "";
        let bv = b[sortKey] ?? "";
        if (sortKey === "from") {{ av = a.from_sort; bv = b.from_sort; }}
        if (sortKey === "until") {{ av = a.until_sort; bv = b.until_sort; }}
        let cmp;
        if (sortKey === "active") cmp = (a.active === b.active) ? 0 : a.active ? -1 : 1;
        else cmp = String(av).localeCompare(String(bv), undefined, {{ numeric: true }});
        return sortDir === "asc" ? cmp : -cmp;
      }});
      tbody.innerHTML = visible.map((row) => `
        <tr data-active="${{row.active}}">
          <td>${{esc(row.supermarket)}}</td>
          <td>${{esc(row.product)}}</td>
          <td>${{esc(row.quantity)}}</td>
          <td>${{esc(row.price)}}</td>
          <td>${{esc(row.from)}}</td>
          <td>${{esc(row.until)}}</td>
          <td><span class="badge ${{row.active ? "active" : "inactive"}}">${{row.active ? "Active" : "Inactive"}}</span></td>
        </tr>`).join("");
      countEl.textContent = `${{visible.length}} of ${{ROWS.length}} shown`;
      document.querySelectorAll("th").forEach((th) => {{
        th.dataset.sortDir = th.dataset.key === sortKey ? sortDir : "";
      }});
    }}

    function esc(s) {{
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }}

    document.querySelectorAll(".filters button").forEach((btn) => {{
      btn.addEventListener("click", () => {{
        statusFilter = btn.dataset.filter;
        document.querySelectorAll(".filters button").forEach((b) => {{
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        }});
        render();
      }});
    }});

    searchEl.addEventListener("input", render);

    document.querySelectorAll("th[data-key]").forEach((th) => {{
      th.addEventListener("click", () => {{
        const key = th.dataset.key;
        if (sortKey === key) sortDir = sortDir === "asc" ? "desc" : "asc";
        else {{ sortKey = key; sortDir = "asc"; }}
        render();
      }});
    }});

    render();
  </script>
</body>
</html>
"""


def _promotion_row(promotion: Promotion) -> dict:
    return {
        "supermarket": promotion.supermarket,
        "product": promotion.product,
        "quantity": promotion.format_quantity(),
        "price": promotion.format_price(promotion.promotional_price),
        "from": promotion.promotion_from.strftime("%d/%m"),
        "until": promotion.promotion_until.strftime("%d/%m"),
        "from_sort": promotion.promotion_from.isoformat(),
        "until_sort": promotion.promotion_until.isoformat(),
        "active": promotion.active_today(),
    }


def write_promotions_html(
    promotions: list[Promotion], path: Path | None = None
) -> Path:
    path = path or HTML_OUTPUT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_promotions_html(promotions), encoding="utf-8")
    return path
