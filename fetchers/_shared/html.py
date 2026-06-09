from __future__ import annotations

from pathlib import Path

INDEX_HTML_PATH = Path(__file__).resolve().parents[2] / "output" / "index.html"
FAVICON_PATH = Path(__file__).resolve().parent / "favicon.svg"

SITE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="favicon.svg" type="image/svg+xml" />
  <title>Who should we buy from?</title>
  <style>
    :root {
      --bg: #f0f2f5;
      --card: #fff;
      --text: #1c2127;
      --muted: #5c6570;
      --border: #dde3ea;
      --accent: #2563eb;
      --active: #15803d;
      --inactive: #94a3b8;
      --fruit: #ea580c;
      --fruit-soft: #fff7ed;
      --veg: #16a34a;
      --veg-soft: #f0fdf4;
      --shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 12px rgba(15, 23, 42, 0.04);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      background: linear-gradient(165deg, #eef2f7 0%, var(--bg) 40%, #e8eef4 100%);
      color: var(--text);
      line-height: 1.45;
      min-height: 100vh;
    }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 1.25rem 1rem 3rem; }
    .page-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 1rem;
    }
    .page-header h1 {
      font-size: 1.65rem;
      font-weight: 700;
      margin: 0 0 0.2rem;
      letter-spacing: -0.02em;
    }
    .meta { color: var(--muted); font-size: 0.875rem; margin: 0; }
    .meta.error { color: #b42318; }
    #refresh-btn {
      font: inherit;
      font-weight: 600;
      font-size: 0.9rem;
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 10px;
      background: var(--accent);
      color: #fff;
      cursor: pointer;
      box-shadow: 0 1px 2px rgba(37, 99, 235, 0.25);
    }
    #refresh-btn:hover:not(:disabled) { filter: brightness(1.06); }
    #refresh-btn:disabled { opacity: 0.65; cursor: wait; }
    .refresh-hint {
      color: var(--muted);
      font-size: 0.85rem;
      margin: 0 0 0.75rem;
    }
    .local-refresh-help {
      font-size: 0.85rem;
      color: var(--muted);
      margin: 0 0 1rem;
    }
    .local-refresh-help summary { cursor: pointer; color: var(--accent); }
    .local-refresh-help pre {
      margin: 0.5rem 0 0;
      padding: 0.75rem;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow-x: auto;
      font-size: 0.8rem;
    }
    .category-tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      padding: 0.35rem;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      box-shadow: var(--shadow);
    }
    .category-tabs button {
      flex: 1;
      font: inherit;
      font-weight: 600;
      font-size: 1rem;
      padding: 0.75rem 1rem;
      border: 2px solid transparent;
      border-radius: 10px;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
    }
    .category-tabs button .tab-count {
      font-size: 0.8rem;
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 999px;
      background: rgba(0,0,0,0.06);
      min-width: 1.5rem;
      text-align: center;
    }
    .category-tabs button[data-category="fruit"][aria-selected="true"] {
      background: var(--fruit-soft);
      border-color: var(--fruit);
      color: #9a3412;
    }
    .category-tabs button[data-category="fruit"][aria-selected="true"] .tab-count {
      background: var(--fruit);
      color: #fff;
    }
    .category-tabs button[data-category="vegetable"][aria-selected="true"] {
      background: var(--veg-soft);
      border-color: var(--veg);
      color: #166534;
    }
    .category-tabs button[data-category="vegetable"][aria-selected="true"] .tab-count {
      background: var(--veg);
      color: #fff;
    }
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.65rem;
      align-items: center;
      margin-bottom: 0.85rem;
    }
    .count {
      color: var(--muted);
      font-size: 0.875rem;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
      flex-shrink: 0;
      min-width: 6.75rem;
      text-align: right;
    }
    .favourites-wrap {
      display: flex;
      flex-shrink: 0;
    }
    .favourites-control {
      display: inline-flex;
      align-items: stretch;
      flex-shrink: 0;
      border: 1px solid var(--veg);
      border-radius: 10px;
      background: var(--card);
      overflow: hidden;
      box-shadow: 0 1px 2px rgba(22, 101, 52, 0.1);
    }
    .favourites-control.is-active {
      border-color: #15803d;
      background: var(--veg);
    }
    #favourites-btn {
      font: inherit;
      font-size: 0.875rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      min-width: 7rem;
      padding: 0.45rem 0.75rem;
      border: none;
      background: transparent;
      color: var(--veg);
      cursor: pointer;
    }
    #favourites-btn:focus-visible,
    #favourites-edit-btn:focus-visible {
      outline: 2px solid rgba(37, 99, 235, 0.55);
      outline-offset: -2px;
    }
    #favourites-btn .favourites-star {
      font-size: 0.95rem;
      line-height: 1;
      opacity: 0.85;
    }
    .favourites-control.is-active #favourites-btn {
      color: #fff;
    }
    .favourites-control.is-active #favourites-btn .favourites-star {
      opacity: 1;
    }
    .favourites-divider {
      width: 1px;
      align-self: stretch;
      background: rgba(22, 101, 52, 0.18);
      flex-shrink: 0;
    }
    .favourites-control.is-active .favourites-divider {
      background: rgba(255, 255, 255, 0.25);
    }
    #favourites-edit-btn {
      font: inherit;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 2.25rem;
      padding: 0;
      border: none;
      background: transparent;
      color: var(--veg);
      cursor: pointer;
      flex-shrink: 0;
    }
    #favourites-edit-btn svg {
      width: 1rem;
      height: 1rem;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    #favourites-edit-btn:hover {
      background: var(--veg-soft);
    }
    .favourites-control.is-active #favourites-edit-btn {
      color: #fff;
    }
    .favourites-control.is-active #favourites-edit-btn:hover {
      background: rgba(255, 255, 255, 0.12);
    }
    .favourites-control.is-fruit {
      border-color: var(--fruit);
      box-shadow: 0 1px 2px rgba(234, 88, 12, 0.12);
    }
    .favourites-control.is-fruit #favourites-btn,
    .favourites-control.is-fruit #favourites-edit-btn {
      color: var(--fruit);
    }
    .favourites-control.is-fruit .favourites-divider {
      background: rgba(234, 88, 12, 0.2);
    }
    .favourites-control.is-fruit #favourites-edit-btn:hover {
      background: var(--fruit-soft);
    }
    .favourites-control.is-fruit.is-active {
      border-color: #c2410c;
      background: var(--fruit);
    }
    .favourites-control.is-fruit.is-active #favourites-btn,
    .favourites-control.is-fruit.is-active #favourites-edit-btn {
      color: #fff;
    }
    .favourites-control.is-fruit.is-active .favourites-divider {
      background: rgba(255, 255, 255, 0.25);
    }
    .favourites-control.is-fruit.is-active #favourites-edit-btn:hover {
      background: rgba(255, 255, 255, 0.12);
    }
    .favourites-dialog {
      border: none;
      border-radius: 14px;
      padding: 0;
      max-width: 420px;
      width: calc(100% - 2rem);
      box-shadow: 0 12px 40px rgba(15, 23, 42, 0.18);
    }
    .favourites-dialog::backdrop {
      background: rgba(15, 23, 42, 0.35);
    }
    .favourites-dialog-inner {
      padding: 1.1rem 1.15rem 1rem;
    }
    .favourites-dialog h2 {
      margin: 0 0 0.35rem;
      font-size: 1.1rem;
    }
    .favourites-help {
      margin: 0 0 0.85rem;
      font-size: 0.85rem;
      color: var(--muted);
    }
    .favourites-list {
      list-style: none;
      margin: 0 0 0.85rem;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      max-height: 220px;
      overflow-y: auto;
    }
    .favourites-list li {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      padding: 0.45rem 0.65rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fafbfc;
      font-size: 0.9rem;
    }
    .favourites-list .remove-kw {
      font: inherit;
      border: none;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-size: 1.1rem;
      line-height: 1;
      padding: 0.15rem 0.35rem;
      border-radius: 6px;
    }
    .favourites-list .remove-kw:hover {
      background: #fee2e2;
      color: #b42318;
    }
    .favourites-add {
      display: flex;
      gap: 0.45rem;
      margin-bottom: 0.85rem;
    }
    .favourites-add input {
      flex: 1;
      min-width: 0;
      font: inherit;
      font-size: 0.95rem;
      padding: 0.45rem 0.65rem;
      border: 1px solid var(--border);
      border-radius: 8px;
    }
    .favourites-add button {
      font: inherit;
      font-weight: 600;
      font-size: 0.875rem;
      padding: 0.45rem 0.85rem;
      border: none;
      border-radius: 8px;
      background: var(--veg);
      color: #fff;
      cursor: pointer;
    }
    .favourites-dialog-footer {
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      justify-content: flex-end;
    }
    .favourites-dialog-footer button {
      font: inherit;
      font-size: 0.875rem;
      font-weight: 600;
      padding: 0.45rem 0.85rem;
      border-radius: 8px;
      cursor: pointer;
    }
    #favourites-reset-btn {
      margin-right: auto;
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--muted);
    }
    #favourites-close-btn {
      border: none;
      background: var(--accent);
      color: #fff;
    }
    .favourites-empty {
      margin: 0 0 0.85rem;
      font-size: 0.875rem;
      color: var(--muted);
      font-style: italic;
    }
    #search {
      flex: 1;
      min-width: 180px;
      padding: 0.5rem 0.85rem;
      border: 1px solid var(--border);
      border-radius: 10px;
      font: inherit;
      font-size: 1rem;
      background: var(--card);
    }
    .toolbar-filters-mobile {
      display: none;
      gap: 0.5rem;
      margin-bottom: 0.85rem;
    }
    .toolbar-filters-mobile .mobile-filter {
      flex: 1;
      min-width: 0;
      font-size: 1rem;
      padding: 0.55rem 1.75rem 0.55rem 0.65rem;
    }
    .promo-cards {
      display: none;
      flex-direction: column;
      gap: 0.55rem;
    }
    .promo-card {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 0.85rem 1rem 0.9rem;
      background: var(--card);
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .promo-card-head {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      flex-wrap: wrap;
      margin-bottom: 0.5rem;
    }
    .promo-card-head .badge { margin-left: auto; }
    .promo-card-main {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 0.75rem;
      margin-bottom: 0.35rem;
    }
    .promo-card-product {
      margin: 0;
      flex: 1;
      min-width: 0;
      font-size: 1.05rem;
      font-weight: 600;
      line-height: 1.3;
      color: var(--text);
    }
    .promo-card-price {
      flex-shrink: 0;
      font-size: 1.2rem;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      color: var(--text);
      line-height: 1.3;
    }
    .promo-card-meta {
      margin: 0;
      font-size: 0.875rem;
      color: var(--muted);
    }
    .promo-card.row-lidl {
      background: #fffbeb;
      border-color: #fde68a;
      box-shadow: inset 4px 0 0 #ea580c;
    }
    .promo-card.row-aldi {
      background: #eff6ff;
      border-color: #bfdbfe;
      box-shadow: inset 4px 0 0 #00529f;
    }
    .promo-card.row-tesco {
      background: #fef2f2;
      border-color: #fecaca;
      box-shadow: inset 4px 0 0 #ee1c2e;
    }
    .promo-card.row-supervalu {
      background: #f8d7da;
      border-color: #e8a0a8;
      box-shadow: inset 4px 0 0 #8b0000;
    }
    .promo-card.row-default {
      background: #fafbfc;
      box-shadow: inset 4px 0 0 #94a3b8;
    }
    .promo-cards-empty {
      text-align: center;
      color: var(--muted);
      padding: 2rem 1rem;
      font-style: italic;
      margin: 0;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
    }
    #search:focus {
      outline: 2px solid var(--accent);
      outline-offset: 1px;
    }
    .card {
      background: var(--card);
      border-radius: 14px;
      border: 1px solid var(--border);
      overflow: hidden;
      box-shadow: var(--shadow);
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.925rem; }
    th, td { padding: 0.7rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
    th {
      background: #f8fafc;
      font-weight: 600;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      vertical-align: top;
    }
    th.th-sortable { cursor: pointer; user-select: none; }
    th.th-sortable:hover { background: #f1f5f9; }
    th.th-has-filter {
      white-space: nowrap;
    }
    th.th-has-filter.th-sortable { cursor: pointer; user-select: none; }
    th.th-has-filter.th-sortable:hover { background: #f1f5f9; }
    th.th-has-filter .th-sort { flex-shrink: 0; }
    th.th-has-filter[data-key="supermarket"] { min-width: 9.5rem; }
    th.th-has-filter[data-key="active"] { min-width: 8.5rem; }
    .th-head {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 0.45rem;
      flex-wrap: nowrap;
      min-height: 1.875rem;
    }
    .col-filter-wrap {
      position: relative;
      flex: 1;
      min-width: 0;
    }
    .th-sort {
      font: inherit;
      font-weight: 600;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      background: none;
      border: none;
      padding: 0;
      cursor: pointer;
      text-align: left;
    }
    .th-sort .sort::after { content: " \2195"; opacity: 0.35; font-size: 0.75em; }
    th[data-sort-dir="asc"] .th-sort .sort::after,
    th.th-sortable[data-sort-dir="asc"] .th-sort .sort::after { content: " \2191"; opacity: 1; color: var(--text); }
    th[data-sort-dir="desc"] .th-sort .sort::after,
    th.th-sortable[data-sort-dir="desc"] .th-sort .sort::after { content: " \2193"; opacity: 1; color: var(--text); }
    .col-filter {
      width: 100%;
      max-width: 100%;
      margin: 0;
      appearance: none;
      -webkit-appearance: none;
      font: inherit;
      font-size: 0.75rem;
      font-weight: 600;
      line-height: 1.25;
      text-transform: none;
      letter-spacing: normal;
      padding: 0.35rem 1.65rem 0.35rem 0.5rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      background-color: var(--card);
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%235c6570' stroke='%235c6570' stroke-width='0.5' d='M2.5 4.5 6 8 9.5 4.5'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 0.55rem center;
      background-size: 0.7rem;
      color: var(--text);
      cursor: pointer;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
      transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
    }
    .col-filter:hover {
      border-color: #b8c4d0;
      background-color: #fff;
    }
    .col-filter:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18);
    }
    .col-filter.is-active {
      border-color: #94a3b8;
      background-color: #f8fafc;
      color: var(--text);
    }
    .col-filter.is-active:not(:focus) {
      box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.06);
    }
    tr:last-child td { border-bottom: none; }
    tbody tr.row-lidl td {
      background: #fffbeb;
      border-bottom-color: #fde68a;
    }
    tbody tr.row-lidl td:first-child { box-shadow: inset 4px 0 0 #ea580c; }
    tbody tr.row-aldi td {
      background: #eff6ff;
      border-bottom-color: #bfdbfe;
    }
    tbody tr.row-aldi td:first-child { box-shadow: inset 4px 0 0 #00529f; }
    tbody tr.row-tesco td {
      background: #fef2f2;
      border-bottom-color: #fecaca;
    }
    tbody tr.row-tesco td:first-child { box-shadow: inset 4px 0 0 #ee1c2e; }
    tbody tr.row-supervalu td {
      background: #f8d7da;
      border-bottom-color: #e8a0a8;
    }
    tbody tr.row-supervalu td:first-child { box-shadow: inset 4px 0 0 #8b0000; }
    tbody tr.row-default td { background: #fafbfc; }
    .store {
      display: inline-block;
      font-size: 0.8rem;
      font-weight: 700;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      letter-spacing: 0.02em;
    }
    .store.lidl { background: #ffd500; color: #1a1a1a; }
    .store.aldi { background: #00529f; color: #fff; }
    .store.tesco { background: #ee1c2e; color: #fff; }
    .store.supervalu { background: #8b0000; color: #fff; }
    .store.default { background: #475569; color: #fff; }
    .price { font-weight: 600; font-variant-numeric: tabular-nums; }
    .product-name { font-weight: 500; }
    .badge {
      display: inline-block;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .badge.live { background: #15803d; color: #fff; }
    .badge.upcoming { background: #475569; color: #fff; }
    .badge.ended { background: #94a3b8; color: #fff; }
    .empty-row td {
      text-align: center;
      color: var(--muted);
      padding: 2rem 1rem;
      font-style: italic;
    }
    .ended-section {
      margin-top: 1.5rem;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: var(--card);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .ended-section summary {
      cursor: pointer;
      font-weight: 600;
      font-size: 0.95rem;
      padding: 0.85rem 1rem;
      color: var(--muted);
      list-style: none;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      user-select: none;
    }
    .ended-section summary::-webkit-details-marker { display: none; }
    .ended-section summary::before {
      content: "";
      width: 0.45rem;
      height: 0.45rem;
      border-right: 2px solid currentColor;
      border-bottom: 2px solid currentColor;
      transform: rotate(-45deg);
      transition: transform 0.15s;
      flex-shrink: 0;
    }
    .ended-section[open] summary::before { transform: rotate(45deg); }
    .ended-section summary:hover { color: var(--text); background: #f8fafc; }
    .ended-section .ended-count {
      font-size: 0.8rem;
      font-weight: 700;
      background: #e2e8f0;
      color: #475569;
      padding: 0.15rem 0.5rem;
      border-radius: 999px;
    }
    .ended-section .ended-panel {
      border-top: 1px solid var(--border);
      padding: 0 0 0.25rem;
    }
    .ended-section .ended-panel .card {
      border: none;
      border-radius: 0;
      box-shadow: none;
      margin: 0;
    }
    .ended-section:not(:has(tbody tr:not(.empty-row))) {
      display: none;
    }
    @media (max-width: 720px) {
      .wrap { padding: 1rem 0.75rem 2.5rem; }
      .page-header h1 { font-size: 1.35rem; }
      #refresh-btn {
        width: 100%;
        padding: 0.65rem 1rem;
        font-size: 1rem;
      }
      .page-header { flex-direction: column; align-items: stretch; }
      .category-tabs button {
        font-size: 0.95rem;
        padding: 0.75rem 0.5rem;
        min-height: 2.75rem;
      }
      .toolbar {
        flex-direction: column;
        align-items: stretch;
      }
      #search { min-width: 0; width: 100%; }
      .favourites-wrap {
        width: 100%;
      }
      .favourites-control {
        width: 100%;
      }
      #favourites-btn {
        flex: 1;
        min-width: 0;
        padding: 0.6rem 0.85rem;
        font-size: 1rem;
      }
      .count {
        width: 100%;
        min-width: 0;
        text-align: left;
      }
      #favourites-edit-btn {
        width: 2.75rem;
      }
      .toolbar-filters-mobile { display: flex; }
      .promo-panel-desktop { display: none !important; }
      .promo-cards { display: flex; }
      .ended-desktop { display: none !important; }
      .ended-cards { display: flex; }
    }
    @media (min-width: 721px) {
      .toolbar-filters-mobile { display: none !important; }
      .promo-cards { display: none !important; }
      .ended-cards { display: none !important; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="page-header">
      <div>
        <h1>Who should we buy from?</h1>
        <p class="meta" id="meta">Loading promotions…</p>
      </div>
      <button type="button" id="refresh-btn" title="Reload promotions.csv from GitHub">Reload data</button>
    </div>
    <p class="refresh-hint" id="refresh-hint" hidden></p>
    <details class="local-refresh-help">
      <summary>Update data (run on your Mac)</summary>
      <pre>./scripts/refresh_and_push.sh</pre>
      <p>Then click <strong>Reload data</strong>.</p>
    </details>

    <div class="category-tabs" role="tablist" aria-label="Produce category">
      <button type="button" role="tab" id="tab-vegetable" data-category="vegetable" aria-selected="true" aria-controls="promo-panel">
        <span>Vegetables</span>
        <span class="tab-count" id="tab-vegetable-count">0</span>
      </button>
      <button type="button" role="tab" id="tab-fruit" data-category="fruit" aria-selected="false" aria-controls="promo-panel">
        <span>Fruits</span>
        <span class="tab-count" id="tab-fruit-count">0</span>
      </button>
    </div>

    <div class="toolbar">
      <input id="search" type="search" placeholder="Search in this tab…" autocomplete="off" />
      <div class="favourites-wrap" id="favourites-wrap">
        <div class="favourites-control" id="favourites-control">
          <button type="button" id="favourites-btn" aria-pressed="false">
            <span class="favourites-star" aria-hidden="true">★</span>
            <span>Favourites</span>
          </button>
          <span class="favourites-divider" aria-hidden="true"></span>
          <button type="button" id="favourites-edit-btn" aria-label="Edit favourites list" title="Edit favourites">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
            </svg>
          </button>
        </div>
      </div>
      <span class="count" id="count"></span>
    </div>

    <div class="toolbar-filters-mobile" id="mobile-filters">
      <select class="col-filter mobile-filter" id="filter-store-mobile" aria-label="Filter by store">
        <option value="all">All stores</option>
        <option value="Lidl">Lidl</option>
        <option value="Aldi">Aldi</option>
        <option value="Tesco">Tesco</option>
        <option value="SuperValu">SuperValu</option>
      </select>
      <select class="col-filter mobile-filter" id="filter-status-mobile" aria-label="Filter by status">
        <option value="all">All active</option>
        <option value="live">Live</option>
        <option value="upcoming">Upcoming</option>
      </select>
    </div>

    <div id="promo-panel" role="tabpanel">
      <div class="card promo-panel-desktop">
      <table id="promo-table">
        <thead>
          <tr>
            <th class="th-has-filter th-sortable" data-key="supermarket">
              <div class="th-head">
                <button type="button" class="th-sort" data-sort-key="supermarket">Store<span class="sort"></span></button>
                <div class="col-filter-wrap">
                  <select class="col-filter" id="filter-store" aria-label="Filter by store">
                    <option value="all">All</option>
                    <option value="Lidl">Lidl</option>
                    <option value="Aldi">Aldi</option>
                    <option value="Tesco">Tesco</option>
                    <option value="SuperValu">SuperValu</option>
                  </select>
                </div>
              </div>
            </th>
            <th class="th-sortable" data-key="product">
              <div class="th-head"><button type="button" class="th-sort" data-sort-key="product">Product<span class="sort"></span></button></div>
            </th>
            <th class="th-sortable" data-key="quantity">
              <div class="th-head"><button type="button" class="th-sort" data-sort-key="quantity">Qty<span class="sort"></span></button></div>
            </th>
            <th class="th-sortable" data-key="price">
              <div class="th-head"><button type="button" class="th-sort" data-sort-key="price">Price<span class="sort"></span></button></div>
            </th>
            <th class="th-sortable" data-key="from">
              <div class="th-head"><button type="button" class="th-sort" data-sort-key="from">From<span class="sort"></span></button></div>
            </th>
            <th class="th-sortable" data-key="until">
              <div class="th-head"><button type="button" class="th-sort" data-sort-key="until">To<span class="sort"></span></button></div>
            </th>
            <th class="th-has-filter th-sortable" data-key="active">
              <div class="th-head">
                <button type="button" class="th-sort" data-sort-key="active">Status<span class="sort"></span></button>
                <div class="col-filter-wrap">
                  <select class="col-filter" id="filter-status" aria-label="Filter by status">
                    <option value="all">All active</option>
                    <option value="live">Live</option>
                    <option value="upcoming">Upcoming</option>
                  </select>
                </div>
              </div>
            </th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
      </div>
      <div class="promo-cards" id="promo-cards" aria-live="polite"></div>
    </div>

    <details class="ended-section" id="ended-section">
      <summary>
        <span>View ended promotions</span>
        <span class="ended-count" id="ended-count">0</span>
      </summary>
      <div class="ended-panel">
        <div class="card ended-desktop">
          <table id="ended-table" aria-label="Ended promotions">
            <thead>
              <tr>
                <th>Store</th>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th>From</th>
                <th>To</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="ended-tbody"></tbody>
          </table>
        </div>
        <div class="promo-cards ended-cards" id="ended-cards" aria-live="polite"></div>
      </div>
    </details>

    <dialog id="favourites-dialog" class="favourites-dialog">
      <div class="favourites-dialog-inner">
        <h2 id="favourites-dialog-title">Favourites</h2>
        <p class="favourites-help" id="favourites-help">Match products that contain these words.</p>
        <ul class="favourites-list" id="favourites-list"></ul>
        <p class="favourites-empty" id="favourites-empty" hidden>Add your first favourite below.</p>
        <div class="favourites-add">
          <input id="favourites-input" type="text" placeholder="e.g. peppers" autocomplete="off" />
          <button type="button" id="favourites-add-btn">Add</button>
        </div>
        <div class="favourites-dialog-footer">
          <button type="button" id="favourites-reset-btn">Reset to defaults</button>
          <button type="button" id="favourites-close-btn">Confirm</button>
        </div>
      </div>
    </dialog>
  </div>
  <script>
    const CSV_URL = "promotions.csv";
    let ROWS = [];
    let lastGenerated = "";
    let categoryTab = "vegetable";
    let storeFilter = "all";
    let statusFilter = "all";
    const FAVOURITES_STORAGE_KEY = "promotionsAccumulator.favourites";
    const BUILTIN_FAVOURITE_DEFAULTS = {
      vegetable: ["onions", "carrots", "cucumbers", "tomatoes"],
      fruit: ["bananas", "apples"],
    };
    let defaultFavouritesByCategory = {
      vegetable: [...BUILTIN_FAVOURITE_DEFAULTS.vegetable],
      fruit: [...BUILTIN_FAVOURITE_DEFAULTS.fruit],
    };
    let favouritesByCategory = {
      vegetable: [...BUILTIN_FAVOURITE_DEFAULTS.vegetable],
      fruit: [...BUILTIN_FAVOURITE_DEFAULTS.fruit],
    };
    let favouritesFilterByCategory = { vegetable: false, fruit: false };
    let draftFavouritesKeywords = [];
    let sortKey = "active";
    let sortDir = "asc";

    const tbody = document.getElementById("tbody");
    const promoCards = document.getElementById("promo-cards");
    const endedTbody = document.getElementById("ended-tbody");
    const endedCards = document.getElementById("ended-cards");
    const endedCountEl = document.getElementById("ended-count");
    const endedSection = document.getElementById("ended-section");
    const countEl = document.getElementById("count");
    const metaEl = document.getElementById("meta");
    const searchEl = document.getElementById("search");
    const refreshBtn = document.getElementById("refresh-btn");
    const refreshHint = document.getElementById("refresh-hint");
    const favouritesWrap = document.getElementById("favourites-wrap");
    const favouritesControl = document.getElementById("favourites-control");
    const favouritesBtn = document.getElementById("favourites-btn");
    const favouritesEditBtn = document.getElementById("favourites-edit-btn");
    const favouritesDialog = document.getElementById("favourites-dialog");
    const favouritesListEl = document.getElementById("favourites-list");
    const favouritesEmptyEl = document.getElementById("favourites-empty");
    const favouritesInput = document.getElementById("favourites-input");
    const favouritesAddBtn = document.getElementById("favourites-add-btn");
    const favouritesResetBtn = document.getElementById("favourites-reset-btn");
    const favouritesCloseBtn = document.getElementById("favourites-close-btn");
    const favouritesHelpEl = document.getElementById("favourites-help");
    const favouritesDialogTitle = document.getElementById("favourites-dialog-title");
    const filterStore = document.getElementById("filter-store");
    const filterStatus = document.getElementById("filter-status");
    const filterStoreMobile = document.getElementById("filter-store-mobile");
    const filterStatusMobile = document.getElementById("filter-status-mobile");

    const VEG_FIRST = /\b(tomato|potato|onion|shallot|pepper|cucumber|broccoli|mushroom|radish|salad|courgette|carrot|cabbage|lettuce|spinach|leek|garlic|cauliflower|aubergine|asparagus|beans?\b|peas?\b)\b/i;
    const FRUIT = /\b(mango|oranges?|pears?|apples?|easypeelers|satsuma|clementine|mandarin|grapefruit|lemon|lime|grape|melon|pineapple|peaches?|strawber|blueber|raspber|bananas?|kiwi|fig\b|apricots?|nectarines?|avocado|coconut|pomegranate|rhubarb)\b/i;
    function classifyProduct(name) {
      const text = name.toLowerCase();
      if (text.includes("salad trio")) return "vegetable";
      if (VEG_FIRST.test(name)) return "vegetable";
      if (FRUIT.test(name)) return "fruit";
      return "vegetable";
    }

    function storeClass(name) {
      const s = name.toLowerCase();
      if (s.includes("lidl")) return "lidl";
      if (s.includes("aldi")) return "aldi";
      if (s.includes("tesco")) return "tesco";
      if (s.includes("supervalu")) return "supervalu";
      return "";
    }

    function cleanProductName(name) {
      let text = (name || "").trim();
      const prefixes = [
        "SuperValu Signature Tastes",
        "SuperValu",
        "Lidl",
        "Aldi",
        "Tesco",
      ];
      for (const prefix of prefixes) {
        if (text.toLowerCase().startsWith(prefix.toLowerCase())) {
          text = text.slice(prefix.length).trim();
          break;
        }
      }
      const patterns = [
        /\s+was\s+.*$/i,
        /\s+NOW\s+.*$/i,
        /\s+Save\s+\d+%.*$/i,
        /\s*\(Details In-store.*$/i,
        /\s*-\s*€[\d.,]+\/kg\s*$/i,
        /\s*\d+pce\s*$/i,
        /\s*\d+\s*kg\s*$/i,
        /\s*\d+\s*g\s*$/i,
        /\s+Tray\s*$/i,
      ];
      for (const re of patterns) text = text.replace(re, "").trim();
      return text;
    }

    function parseGeneratedInstant(raw) {
      const s = raw.replace(/\s+Europe\/Dublin\s*$/i, "").trim();
      const legacy = /^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})$/.exec(s);
      if (legacy) return new Date(`${legacy[1]}T${legacy[2]}:00+01:00`);
      const iso = s.includes("T") ? s : s.replace(" ", "T");
      const d = new Date(iso);
      return Number.isNaN(d.getTime()) ? null : d;
    }

    function formatGeneratedLabel(raw) {
      const d = parseGeneratedInstant(raw);
      if (!d) return "";
      return "Updated " + d.toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    }

    function parseCsvLine(line) {
      const fields = [];
      let field = "";
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const c = line[i];
        if (inQuotes) {
          if (c === '"') {
            if (line[i + 1] === '"') { field += '"'; i++; }
            else inQuotes = false;
          } else field += c;
        } else if (c === '"') inQuotes = true;
        else if (c === ",") { fields.push(field); field = ""; }
        else field += c;
      }
      fields.push(field);
      return fields;
    }

    function dublinTodayIso() {
      return new Date().toLocaleDateString("en-CA", { timeZone: "Europe/Dublin" });
    }

    function rowStatus(row) {
      const statusCol = (row.statusCol ?? "").toLowerCase();
      if (statusCol === "live" || statusCol === "upcoming" || statusCol === "ended") {
        return statusCol;
      }
      const today = dublinTodayIso();
      if (row.from_sort && row.until_sort) {
        if (today >= row.from_sort && today <= row.until_sort) return "live";
        if (today < row.from_sort) return "upcoming";
        return "ended";
      }
      return row.active ? "live" : "ended";
    }

    function csvToRows(text) {
      let generated = "";
      const trimmed = text.replace(/^\uFEFF/, "");
      const lines = trimmed.split(/\r?\n/).filter((l) => l.length);
      const dataLines = [];
      for (const line of lines) {
        if (line.startsWith("# Generated:")) {
          generated = line.replace(/^# Generated:\s*/, "").trim();
        } else dataLines.push(line);
      }
      const parsed = dataLines.map(parseCsvLine);
      if (!parsed.length) return { generated, rows: [] };
      const headers = parsed[0].map((h) => h.trim());
      const rows = parsed.slice(1).filter((r) => r.some((c) => c.trim())).map((cells) => {
        const rec = {};
        headers.forEach((h, i) => { rec[h] = (cells[i] ?? "").trim(); });
        let category = (rec["category"] ?? "").toLowerCase();
        if (category !== "fruit" && category !== "vegetable") {
          category = classifyProduct(rec["Product"] ?? "");
        }
        return {
          supermarket: rec["Supermarket"] ?? "",
          product: rec["Product"] ?? "",
          quantity: rec["Quantity"] ?? "",
          price: rec["Price"] ?? "",
          from: rec["From Date"] ?? "",
          until: rec["Until Date"] ?? "",
          from_sort: rec["from_sort"] ?? "",
          until_sort: rec["until_sort"] ?? "",
          active: (rec["Active today"] ?? "").toLowerCase() === "true",
          statusCol: (rec["Status"] ?? "").toLowerCase(),
          category,
        };
      });
      return { generated, rows };
    }

    function favouritesForCategory(category) {
      return favouritesByCategory[category] || [];
    }

    function defaultsForCategory(category) {
      return defaultFavouritesByCategory[category] || [];
    }

    function isFavouritesFilterActive() {
      return favouritesFilterByCategory[categoryTab] === true;
    }

    function cloneFavouritesDefaults() {
      return {
        vegetable: [...defaultsForCategory("vegetable")],
        fruit: [...defaultsForCategory("fruit")],
      };
    }

    function matchesFavourites(product) {
      const name = product.toLowerCase();
      return favouritesForCategory(categoryTab).some((kw) => {
        const k = kw.toLowerCase().trim();
        if (!k) return false;
        if (name.includes(k)) return true;
        if (k.endsWith("s") && k.length > 1 && name.includes(k.slice(0, -1))) return true;
        return false;
      });
    }

    function updateFavouritesToolbar() {
      favouritesControl.classList.toggle("is-fruit", categoryTab === "fruit");
      const active = isFavouritesFilterActive();
      favouritesBtn.setAttribute("aria-pressed", active ? "true" : "false");
      favouritesControl.classList.toggle("is-active", active);
    }

    function setFavouritesActive(active) {
      favouritesFilterByCategory[categoryTab] = active;
      favouritesBtn.setAttribute("aria-pressed", active ? "true" : "false");
      favouritesControl.classList.toggle("is-active", active);
    }

    function updateFavouritesDialogCopy() {
      const label = categoryTab === "fruit" ? "Fruit" : "Vegetable";
      favouritesDialogTitle.textContent = `${label} favourites`;
      favouritesHelpEl.textContent = "Match products that contain these words.";
      favouritesInput.placeholder = categoryTab === "fruit" ? "e.g. strawberries" : "e.g. peppers";
    }

    function normaliseKeyword(value) {
      return String(value || "").trim().toLowerCase();
    }

    function normaliseKeywordList(values) {
      return values.map(normaliseKeyword).filter(Boolean);
    }

    function loadFavouritesFromStorage() {
      favouritesByCategory = cloneFavouritesDefaults();
      try {
        const raw = localStorage.getItem(FAVOURITES_STORAGE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          favouritesByCategory.vegetable = normaliseKeywordList(parsed);
          return;
        }
        if (parsed && typeof parsed === "object") {
          for (const category of ["vegetable", "fruit"]) {
            if (Array.isArray(parsed[category])) {
              favouritesByCategory[category] = normaliseKeywordList(parsed[category]);
            }
          }
        }
      } catch (_) {
        favouritesByCategory = cloneFavouritesDefaults();
      }
    }

    function saveFavouritesToStorage() {
      try {
        localStorage.setItem(
          FAVOURITES_STORAGE_KEY,
          JSON.stringify(favouritesByCategory),
        );
      } catch (_) { /* private mode / quota */ }
    }

    function renderFavouritesEditor() {
      favouritesListEl.innerHTML = draftFavouritesKeywords
        .map(
          (kw, idx) => `
            <li>
              <span>${esc(kw)}</span>
              <button type="button" class="remove-kw" data-idx="${idx}" aria-label="Remove ${esc(kw)}">×</button>
            </li>`,
        )
        .join("");
      favouritesEmptyEl.hidden = draftFavouritesKeywords.length > 0;
    }

    function addFavouriteKeyword(raw) {
      const kw = normaliseKeyword(raw);
      if (!kw) return false;
      if (draftFavouritesKeywords.includes(kw)) return false;
      draftFavouritesKeywords = [...draftFavouritesKeywords, kw];
      renderFavouritesEditor();
      return true;
    }

    function removeFavouriteKeyword(index) {
      draftFavouritesKeywords = draftFavouritesKeywords.filter((_, i) => i !== index);
      renderFavouritesEditor();
    }

    function resetFavouritesDraft() {
      draftFavouritesKeywords = [...defaultsForCategory(categoryTab)];
      renderFavouritesEditor();
    }

    function applyFavouritesDraft() {
      favouritesByCategory[categoryTab] = [...draftFavouritesKeywords];
      saveFavouritesToStorage();
      render();
    }

    function openFavouritesEditor() {
      draftFavouritesKeywords = [...favouritesForCategory(categoryTab)];
      updateFavouritesDialogCopy();
      renderFavouritesEditor();
      favouritesInput.value = "";
      if (typeof favouritesDialog.showModal === "function") {
        favouritesDialog.showModal();
      } else {
        favouritesDialog.setAttribute("open", "");
      }
      favouritesInput.focus();
    }

    function closeFavouritesEditor() {
      if (typeof favouritesDialog.close === "function") {
        favouritesDialog.close();
      } else {
        favouritesDialog.removeAttribute("open");
      }
    }

    async function loadSiteConfig() {
      try {
        const res = await fetch("site-config.json", { cache: "no-store" });
        if (!res.ok) return;
        const cfg = await res.json();
        if (cfg.favouriteKeywords && typeof cfg.favouriteKeywords === "object") {
          for (const category of ["vegetable", "fruit"]) {
            const values = cfg.favouriteKeywords[category];
            if (Array.isArray(values) && values.length) {
              defaultFavouritesByCategory[category] = normaliseKeywordList(values);
            }
          }
        } else if (Array.isArray(cfg.frequentBuyKeywords) && cfg.frequentBuyKeywords.length) {
          defaultFavouritesByCategory.vegetable = normaliseKeywordList(cfg.frequentBuyKeywords);
        }
      } catch (_) { /* use defaults */ }
      loadFavouritesFromStorage();
    }

    function updateFilterSelectStyles() {
      const activeStore = storeFilter !== "all";
      const activeStatus = statusFilter !== "all";
      for (const el of [filterStore, filterStoreMobile]) {
        el.classList.toggle("is-active", activeStore);
      }
      for (const el of [filterStatus, filterStatusMobile]) {
        el.classList.toggle("is-active", activeStatus);
      }
    }

    function setStoreFilter(value) {
      storeFilter = value;
      filterStore.value = value;
      filterStoreMobile.value = value;
      updateFilterSelectStyles();
      render();
    }

    function setStatusFilter(value) {
      statusFilter = value;
      filterStatus.value = value;
      filterStatusMobile.value = value;
      updateFilterSelectStyles();
      render();
    }

    function isEndedRow(row) {
      return rowStatus(row) === "ended";
    }

    function matchesSharedFilters(row, q) {
      if (row.category !== categoryTab) return false;
      if (storeFilter !== "all" && row.supermarket !== storeFilter) return false;
      if (isFavouritesFilterActive() && !matchesFavourites(row.product)) return false;
      if (q) {
        const hay = `${row.supermarket} ${row.product} ${row.quantity}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    }

    function sortRows(rows) {
      return [...rows].sort((a, b) => {
        let av = a[sortKey] ?? "";
        let bv = b[sortKey] ?? "";
        if (sortKey === "from") { av = a.from_sort; bv = b.from_sort; }
        if (sortKey === "until") { av = a.until_sort; bv = b.until_sort; }
        let cmp;
        if (sortKey === "active") {
          const order = { live: 0, upcoming: 1, ended: 2 };
          cmp = order[rowStatus(a)] - order[rowStatus(b)];
        }
        else cmp = String(av).localeCompare(String(bv), undefined, { numeric: true });
        return sortDir === "asc" ? cmp : -cmp;
      });
    }

    function rowToHtml(row) {
      const sc = storeClass(row.supermarket) || "default";
      const rowClass = sc === "default" ? "row-default" : `row-${sc}`;
      const status = rowStatus(row);
      return `
        <tr class="${rowClass}" data-active="${row.active}" data-store="${sc}">
          <td><span class="store ${sc}">${esc(row.supermarket)}</span></td>
          <td class="product-name">${esc(cleanProductName(row.product))}</td>
          <td>${esc(row.quantity)}</td>
          <td class="price">${esc(row.price)}</td>
          <td>${esc(row.from)}</td>
          <td>${esc(row.until)}</td>
          <td><span class="badge ${status}">${status.toUpperCase()}</span></td>
        </tr>`;
    }

    function fillTableBody(target, rows, emptyMessage) {
      if (!rows.length) {
        target.innerHTML = `<tr class="empty-row"><td colspan="7">${emptyMessage}</td></tr>`;
      } else {
        target.innerHTML = rows.map(rowToHtml).join("");
      }
    }

    function cardMetaLine(row) {
      const parts = [];
      if (row.quantity && row.quantity !== "—") parts.push(row.quantity);
      if (row.from && row.until) parts.push(`${row.from} – ${row.until}`);
      return parts.join(" · ") || "—";
    }

    function rowToCardHtml(row) {
      const sc = storeClass(row.supermarket) || "default";
      const rowClass = sc === "default" ? "row-default" : `row-${sc}`;
      const status = rowStatus(row);
      return `
        <article class="promo-card ${rowClass}">
          <div class="promo-card-head">
            <span class="store ${sc}">${esc(row.supermarket)}</span>
            <span class="badge ${status}">${status.toUpperCase()}</span>
          </div>
          <div class="promo-card-main">
            <h3 class="promo-card-product">${esc(cleanProductName(row.product))}</h3>
            <span class="promo-card-price">${esc(row.price)}</span>
          </div>
          <p class="promo-card-meta">${esc(cardMetaLine(row))}</p>
        </article>`;
    }

    function fillCardList(target, rows, emptyMessage) {
      if (!rows.length) {
        target.innerHTML = `<p class="promo-cards-empty">${emptyMessage}</p>`;
      } else {
        target.innerHTML = rows.map(rowToCardHtml).join("");
      }
    }

    function updateTabCounts() {
      const active = (r) => !isEndedRow(r);
      const fruits = ROWS.filter((r) => r.category === "fruit" && active(r)).length;
      const veg = ROWS.filter((r) => r.category === "vegetable" && active(r)).length;
      document.getElementById("tab-fruit-count").textContent = fruits;
      document.getElementById("tab-vegetable-count").textContent = veg;
    }

    function render() {
      const q = searchEl.value.trim().toLowerCase();
      const activeRows = ROWS.filter((row) => {
        if (isEndedRow(row)) return false;
        if (!matchesSharedFilters(row, q)) return false;
        const status = rowStatus(row);
        if (statusFilter === "live" && status !== "live") return false;
        if (statusFilter === "upcoming" && status !== "upcoming") return false;
        return true;
      });
      const visible = sortRows(activeRows);

      const label = categoryTab === "fruit" ? "fruit" : "vegetable";
      const emptyActive = `No ${label} promotions match your filters.`;
      fillTableBody(tbody, visible, emptyActive);
      fillCardList(promoCards, visible, emptyActive);

      const endedRows = sortRows(
        ROWS.filter((row) => {
          if (!isEndedRow(row)) return false;
          return matchesSharedFilters(row, q);
        }),
      );
      const emptyEnded = `No ended ${label} promotions match your filters.`;
      fillTableBody(endedTbody, endedRows, emptyEnded);
      fillCardList(endedCards, endedRows, emptyEnded);

      const endedTotal = ROWS.filter((r) => isEndedRow(r)).length;
      const endedInTab = ROWS.filter(
        (r) => r.category === categoryTab && isEndedRow(r),
      ).length;
      endedCountEl.textContent = String(endedInTab);
      endedSection.hidden = endedTotal === 0;

      const inTab = ROWS.filter(
        (r) => r.category === categoryTab && !isEndedRow(r),
      ).length;
      countEl.textContent = `${visible.length} of ${inTab} in tab`;
      document.querySelectorAll("#promo-table th[data-key]").forEach((th) => {
        th.dataset.sortDir = th.dataset.key === sortKey ? sortDir : "";
      });
      updateFilterSelectStyles();
    }

    function esc(s) {
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    document.querySelectorAll(".category-tabs button").forEach((btn) => {
      btn.addEventListener("click", () => {
        categoryTab = btn.dataset.category;
        document.querySelectorAll(".category-tabs button").forEach((b) => {
          b.setAttribute("aria-selected", b === btn ? "true" : "false");
        });
        updateFavouritesToolbar();
        render();
      });
    });

    favouritesBtn.addEventListener("click", () => {
      setFavouritesActive(!isFavouritesFilterActive());
      render();
    });

    favouritesEditBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      openFavouritesEditor();
    });
    favouritesEditBtn.addEventListener("mousedown", (e) => {
      e.stopPropagation();
    });
    favouritesCloseBtn.addEventListener("click", () => {
      applyFavouritesDraft();
      closeFavouritesEditor();
    });
    favouritesResetBtn.addEventListener("click", resetFavouritesDraft);
    favouritesAddBtn.addEventListener("click", () => {
      if (addFavouriteKeyword(favouritesInput.value)) {
        favouritesInput.value = "";
      }
      favouritesInput.focus();
    });
    favouritesInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (addFavouriteKeyword(favouritesInput.value)) {
          favouritesInput.value = "";
        }
      }
    });
    favouritesListEl.addEventListener("click", (e) => {
      const btn = e.target.closest(".remove-kw");
      if (!btn) return;
      const idx = Number(btn.dataset.idx);
      if (!Number.isNaN(idx)) removeFavouriteKeyword(idx);
    });
    favouritesDialog.addEventListener("click", (e) => {
      if (e.target === favouritesDialog) closeFavouritesEditor();
    });

    filterStore.addEventListener("change", () => setStoreFilter(filterStore.value));
    filterStoreMobile.addEventListener("change", () => setStoreFilter(filterStoreMobile.value));
    filterStatus.addEventListener("change", () => setStatusFilter(filterStatus.value));
    filterStatusMobile.addEventListener("change", () => setStatusFilter(filterStatusMobile.value));
    filterStore.addEventListener("click", (e) => e.stopPropagation());
    filterStatus.addEventListener("click", (e) => e.stopPropagation());

    searchEl.addEventListener("input", render);

    document.querySelectorAll(".th-sort").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.dataset.sortKey;
        if (sortKey === key) sortDir = sortDir === "asc" ? "desc" : "asc";
        else { sortKey = key; sortDir = "asc"; }
        render();
      });
    });

    async function fetchCsvText() {
      const res = await fetch(`${CSV_URL}?t=${Date.now()}`, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.text();
    }

    async function load() {
      try {
        const { generated, rows } = csvToRows(await fetchCsvText());
        ROWS = rows;
        if (generated) lastGenerated = generated;
        metaEl.classList.remove("error");
        const generatedLabel = formatGeneratedLabel(generated);
        metaEl.textContent = generatedLabel
          || (rows.length ? "Promotions loaded" : "No promotions in CSV");
        updateTabCounts();
        updateFavouritesToolbar();
        render();
        return true;
      } catch (err) {
        metaEl.classList.add("error");
        metaEl.textContent = `Could not load ${CSV_URL}: ${err.message}.`;
        countEl.textContent = "";
        return false;
      }
    }

    async function reloadData() {
      const prev = lastGenerated;
      refreshBtn.disabled = true;
      refreshBtn.textContent = "Reloading…";
      refreshHint.hidden = false;
      await load();
      refreshBtn.disabled = false;
      refreshBtn.textContent = "Reload data";
      refreshHint.textContent = lastGenerated && lastGenerated !== prev
        ? "Loaded newer data from GitHub."
        : "Same data as before. Run update locally and push to publish new leaflets.";
    }

    refreshBtn.addEventListener("click", reloadData);
    (async () => {
      await loadSiteConfig();
      await load();
    })();
  </script>
</body>
</html>
"""


def write_promotions_site(path: Path | None = None) -> Path:
    path = path or INDEX_HTML_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SITE_HTML, encoding="utf-8")
    return path
