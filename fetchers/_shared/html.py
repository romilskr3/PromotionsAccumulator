from __future__ import annotations

from pathlib import Path

INDEX_HTML_PATH = Path(__file__).resolve().parents[2] / "output" / "index.html"

SITE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Fruit &amp; Vegetable Promotions — Dublin</title>
  <style>
    :root {
      --bg: #f4f6f8;
      --card: #fff;
      --text: #1a1a1a;
      --muted: #5c6570;
      --border: #d8dee4;
      --accent: #00539f;
      --active: #0d7a3e;
      --inactive: #9aa3ad;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }
    .wrap { max-width: 1200px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }
    .page-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 1.25rem;
    }
    .page-header h1 { font-size: 1.5rem; margin: 0 0 0.25rem; }
    .meta { color: var(--muted); font-size: 0.9rem; margin: 0; }
    .meta.error { color: #b42318; }
    #refresh-btn {
      font: inherit;
      font-weight: 600;
      padding: 0.55rem 1rem;
      border: 1px solid var(--accent);
      border-radius: 8px;
      background: var(--accent);
      color: #fff;
      cursor: pointer;
      white-space: nowrap;
    }
    #refresh-btn:hover:not(:disabled) { filter: brightness(1.08); }
    #refresh-btn:disabled { opacity: 0.65; cursor: wait; }
    .refresh-hint {
      color: var(--muted);
      font-size: 0.85rem;
      margin: 0 0 1rem;
      max-width: 42rem;
    }
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      margin-bottom: 1rem;
    }
    .filters button {
      font: inherit;
      padding: 0.45rem 0.85rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--card);
      cursor: pointer;
      color: var(--text);
    }
    .filters button[aria-pressed="true"] {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }
    #search {
      flex: 1;
      min-width: 200px;
      padding: 0.5rem 0.75rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      font: inherit;
    }
    .card {
      background: var(--card);
      border-radius: 12px;
      border: 1px solid var(--border);
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
    th, td { padding: 0.65rem 0.85rem; text-align: left; border-bottom: 1px solid var(--border); }
    th {
      background: #eef2f6;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }
    th:hover { background: #e2e8ef; }
    th .sort::after { content: " \\2195"; opacity: 0.35; font-size: 0.75em; }
    th[data-sort-dir="asc"] .sort::after { content: " \\2191"; opacity: 1; }
    th[data-sort-dir="desc"] .sort::after { content: " \\2193"; opacity: 1; }
    tr:last-child td { border-bottom: none; }
    tr[data-active="false"] { opacity: 0.72; }
    .badge {
      display: inline-block;
      padding: 0.15rem 0.5rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .badge.active { background: #d8f0e0; color: var(--active); }
    .badge.inactive { background: #eceff2; color: var(--inactive); }
    .count { color: var(--muted); font-size: 0.9rem; }
    @media (max-width: 720px) {
      .card { overflow-x: auto; }
      table { min-width: 720px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="page-header">
      <div>
        <h1>Fruit &amp; Vegetable Promotions — Dublin</h1>
        <p class="meta" id="meta">Loading promotions…</p>
      </div>
      <button type="button" id="refresh-btn" title="Download leaflets and regenerate data">Refresh data</button>
    </div>
    <p class="refresh-hint" id="refresh-hint" hidden></p>
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
    const CSV_URL = "promotions.csv";
    let ROWS = [];
    let lastGenerated = "";
    let siteConfig = null;
    let pollTimer = null;
    const tbody = document.getElementById("tbody");
    const countEl = document.getElementById("count");
    const metaEl = document.getElementById("meta");
    const searchEl = document.getElementById("search");
    const refreshBtn = document.getElementById("refresh-btn");
    const refreshHint = document.getElementById("refresh-hint");
    let statusFilter = "all";
    let sortKey = "supermarket";
    let sortDir = "asc";

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
        };
      });
      return { generated, rows };
    }

    function render() {
      const q = searchEl.value.trim().toLowerCase();
      let visible = ROWS.filter((row) => {
        if (statusFilter === "active" && !row.active) return false;
        if (statusFilter === "inactive" && row.active) return false;
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
        if (sortKey === "active") cmp = (a.active === b.active) ? 0 : a.active ? -1 : 1;
        else cmp = String(av).localeCompare(String(bv), undefined, { numeric: true });
        return sortDir === "asc" ? cmp : -cmp;
      });
      tbody.innerHTML = visible.map((row) => `
        <tr data-active="${row.active}">
          <td>${esc(row.supermarket)}</td>
          <td>${esc(row.product)}</td>
          <td>${esc(row.quantity)}</td>
          <td>${esc(row.price)}</td>
          <td>${esc(row.from)}</td>
          <td>${esc(row.until)}</td>
          <td><span class="badge ${row.active ? "active" : "inactive"}">${row.active ? "Active" : "Inactive"}</span></td>
        </tr>`).join("");
      countEl.textContent = `${visible.length} of ${ROWS.length} shown`;
      document.querySelectorAll("th").forEach((th) => {
        th.dataset.sortDir = th.dataset.key === sortKey ? sortDir : "";
      });
    }

    function esc(s) {
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    document.querySelectorAll(".filters button").forEach((btn) => {
      btn.addEventListener("click", () => {
        statusFilter = btn.dataset.filter;
        document.querySelectorAll(".filters button").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        render();
      });
    });

    searchEl.addEventListener("input", render);

    document.querySelectorAll("th[data-key]").forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.dataset.key;
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
        metaEl.textContent = generated
          ? `Generated ${generated}`
          : (rows.length ? "Promotions loaded" : "No promotions in CSV");
        render();
        return true;
      } catch (err) {
        metaEl.classList.add("error");
        metaEl.textContent = `Could not load ${CSV_URL}: ${err.message}. Run update_promotions.py and open via a local server (file:// blocks fetch).`;
        countEl.textContent = "";
        return false;
      }
    }

    function setRefreshUi(active, message) {
      refreshBtn.disabled = active;
      refreshBtn.textContent = active ? "Refreshing…" : "Refresh data";
      if (message) {
        refreshHint.hidden = false;
        refreshHint.textContent = message;
      } else {
        refreshHint.hidden = true;
        refreshHint.textContent = "";
      }
    }

    function stopPolling() {
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
    }

    function startPolling() {
      stopPolling();
      const started = Date.now();
      const timeoutMs = 12 * 60 * 1000;
      pollTimer = setInterval(async () => {
        if (Date.now() - started > timeoutMs) {
          stopPolling();
          setRefreshUi(false, "");
          metaEl.classList.add("error");
          metaEl.textContent = "Refresh timed out. Check GitHub Actions for errors, then reload the page.";
          return;
        }
        try {
          const { generated, rows } = csvToRows(await fetchCsvText());
          if (generated && generated !== lastGenerated) {
            ROWS = rows;
            lastGenerated = generated;
            stopPolling();
            setRefreshUi(false, "");
            metaEl.classList.remove("error");
            metaEl.textContent = `Generated ${generated}`;
            render();
          }
        } catch (_) { /* keep polling */ }
      }, 12000);
    }

    async function loadSiteConfig() {
      try {
        const res = await fetch("site-config.json", { cache: "no-store" });
        if (res.ok) siteConfig = await res.json();
      } catch (_) { /* optional */ }
    }

    function startRefresh() {
      if (!siteConfig?.issueRefreshUrl) {
        alert("site-config.json is missing. Run update_promotions.py and redeploy.");
        return;
      }
      const ok = confirm(
        "This downloads new leaflets and rebuilds the CSV on GitHub (about 3–8 minutes).\n\n" +
        "1. GitHub will open with a pre-filled issue\n" +
        "2. Click \"Submit new issue\" to start the refresh\n" +
        "3. This page will load new data automatically when ready"
      );
      if (!ok) return;
      window.open(siteConfig.issueRefreshUrl, "_blank", "noopener");
      setRefreshUi(
        true,
        "Submit the issue in the GitHub tab, then wait — this page will update when the CSV changes."
      );
      startPolling();
    }

    refreshBtn.addEventListener("click", startRefresh);

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
