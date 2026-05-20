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
    .favourites-wrap { display: none; }
    .favourites-wrap.visible { display: block; }
    #favourites-btn {
      font: inherit;
      font-size: 0.875rem;
      font-weight: 600;
      padding: 0.45rem 0.85rem;
      border: 1px solid var(--veg);
      border-radius: 8px;
      background: var(--card);
      color: var(--veg);
      cursor: pointer;
    }
    #favourites-btn[aria-pressed="true"] {
      background: var(--veg);
      color: #fff;
    }
    #search {
      flex: 1;
      min-width: 180px;
      padding: 0.5rem 0.85rem;
      border: 1px solid var(--border);
      border-radius: 10px;
      font: inherit;
      background: var(--card);
    }
    #search:focus {
      outline: 2px solid var(--accent);
      outline-offset: 1px;
    }
    .count { color: var(--muted); font-size: 0.875rem; }
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
    @media (max-width: 720px) {
      .card { overflow-x: auto; }
      table { min-width: 680px; }
      .category-tabs button { font-size: 0.9rem; padding: 0.65rem 0.5rem; }
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
      <div class="favourites-wrap visible" id="favourites-wrap">
        <button type="button" id="favourites-btn" aria-pressed="false">Favourites</button>
      </div>
      <span class="count" id="count"></span>
    </div>

    <div class="card" id="promo-panel" role="tabpanel">
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
                    <option value="all">All</option>
                    <option value="live">Live</option>
                    <option value="upcoming">Upcoming</option>
                    <option value="ended">Ended</option>
                  </select>
                </div>
              </div>
            </th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </div>
  <script>
    const CSV_URL = "promotions.csv";
    let ROWS = [];
    let lastGenerated = "";
    let categoryTab = "vegetable";
    let storeFilter = "all";
    let statusFilter = "all";
    let favouritesFilter = false;
    let favouritesKeywords = ["onions", "carrots", "cucumbers", "tomatoes"];
    let sortKey = "active";
    let sortDir = "asc";

    const tbody = document.getElementById("tbody");
    const countEl = document.getElementById("count");
    const metaEl = document.getElementById("meta");
    const searchEl = document.getElementById("search");
    const refreshBtn = document.getElementById("refresh-btn");
    const refreshHint = document.getElementById("refresh-hint");
    const favouritesWrap = document.getElementById("favourites-wrap");
    const favouritesBtn = document.getElementById("favourites-btn");
    const filterStore = document.getElementById("filter-store");
    const filterStatus = document.getElementById("filter-status");

    const VEG_FIRST = /\b(tomato|potato|onion|shallot|pepper|cucumber|broccoli|mushroom|radish|salad|courgette|carrot|cabbage|lettuce|spinach|leek|garlic|cauliflower|aubergine|asparagus|beans?\b|peas?\b)\b/i;
    const FRUIT = /\b(mango|oranges?|pears?|apples?|easypeelers|satsuma|clementine|mandarin|grapefruit|lemon|lime|grape|melon|pineapple|peach|strawber|blueber|raspber|banana|kiwi|fig\b|apricot|nectarine|avocado|coconut|pomegranate|rhubarb)\b/i;
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

    function matchesFavourites(product) {
      const name = product.toLowerCase();
      return favouritesKeywords.some((kw) => {
        const k = kw.toLowerCase().trim();
        if (!k) return false;
        if (name.includes(k)) return true;
        if (k.endsWith("s") && k.length > 1 && name.includes(k.slice(0, -1))) return true;
        return false;
      });
    }

    function updateFavouritesToolbar() {
      const onVeg = categoryTab === "vegetable";
      favouritesWrap.classList.toggle("visible", onVeg);
      if (!onVeg) {
        favouritesFilter = false;
        favouritesBtn.setAttribute("aria-pressed", "false");
      }
    }

    async function loadSiteConfig() {
      try {
        const res = await fetch("site-config.json", { cache: "no-store" });
        if (!res.ok) return;
        const cfg = await res.json();
        if (Array.isArray(cfg.frequentBuyKeywords) && cfg.frequentBuyKeywords.length) {
          favouritesKeywords = cfg.frequentBuyKeywords;
        }
      } catch (_) { /* use defaults */ }
    }

    function updateFilterSelectStyles() {
      filterStore.classList.toggle("is-active", storeFilter !== "all");
      filterStatus.classList.toggle("is-active", statusFilter !== "all");
    }

    function updateTabCounts() {
      const fruits = ROWS.filter((r) => r.category === "fruit").length;
      const veg = ROWS.filter((r) => r.category === "vegetable").length;
      document.getElementById("tab-fruit-count").textContent = fruits;
      document.getElementById("tab-vegetable-count").textContent = veg;
    }

    function render() {
      const q = searchEl.value.trim().toLowerCase();
      let visible = ROWS.filter((row) => {
        if (row.category !== categoryTab) return false;
        if (storeFilter !== "all" && row.supermarket !== storeFilter) return false;
        const status = rowStatus(row);
        if (statusFilter === "live" && status !== "live") return false;
        if (statusFilter === "upcoming" && status !== "upcoming") return false;
        if (statusFilter === "ended" && status !== "ended") return false;
        if (favouritesFilter && !matchesFavourites(row.product)) return false;
        if (q) {
          const hay = `${row.supermarket} ${row.product} ${row.quantity}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });
      visible.sort((a, b) => {
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

      if (!visible.length) {
        const label = categoryTab === "fruit" ? "fruit" : "vegetable";
        tbody.innerHTML = `<tr class="empty-row"><td colspan="7">No ${label} promotions match your filters.</td></tr>`;
      } else {
        tbody.innerHTML = visible.map((row) => {
          const sc = storeClass(row.supermarket) || "default";
          const rowClass = sc === "default" ? "row-default" : `row-${sc}`;
          const status = rowStatus(row);
          const statusClass = status;
          const statusLabel = status.toUpperCase();
          return `
        <tr class="${rowClass}" data-active="${row.active}" data-store="${sc}">
          <td><span class="store ${sc}">${esc(row.supermarket)}</span></td>
          <td class="product-name">${esc(cleanProductName(row.product))}</td>
          <td>${esc(row.quantity)}</td>
          <td class="price">${esc(row.price)}</td>
          <td>${esc(row.from)}</td>
          <td>${esc(row.until)}</td>
          <td><span class="badge ${statusClass}">${statusLabel}</span></td>
        </tr>`;
        }).join("");
      }

      const inTab = ROWS.filter((r) => r.category === categoryTab).length;
      countEl.textContent = `${visible.length} of ${inTab} in tab`;
      document.querySelectorAll("th[data-key]").forEach((th) => {
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
      favouritesFilter = !favouritesFilter;
      favouritesBtn.setAttribute("aria-pressed", favouritesFilter ? "true" : "false");
      render();
    });

    filterStore.addEventListener("change", () => {
      storeFilter = filterStore.value;
      updateFilterSelectStyles();
      render();
    });
    filterStatus.addEventListener("change", () => {
      statusFilter = filterStatus.value;
      updateFilterSelectStyles();
      render();
    });
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
