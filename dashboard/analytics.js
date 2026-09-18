/* Analytics do wizard 'Novo ETL' — 100% open source e client-side.
 * DuckDB-WASM (MIT) corre o DuckDB no browser; Apache ECharts (Apache-2.0)
 * renderiza os gráficos. Dados: staging parquet servido same-origin por
 * /api/etl-analytics. Perfil automático + exploração SQL ao vivo.
 */
import * as duckdb from "https://esm.sh/@duckdb/duckdb-wasm@1.29.0";

let db = null;          // AsyncDuckDBConnection
let analyticsData = null; // { rows, columns: [{name, type, kind}] }
const charts = [];

const $ = (s) => document.querySelector(s);

/* ---------- init DuckDB-WASM (lazy, na 1ª abertura) ---------- */
async function initDuckDB() {
  if (db) return db;
  const bundles = duckdb.getJsDelivrBundles();
  const bundle = await duckdb.selectBundle(bundles);
  const worker = new Worker(bundle.mainWorker);
  const logger = new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING);
  const dd = new duckdb.AsyncDuckDB(logger, worker);
  await dd.instantiate(bundle.mainModule, bundle.pthreadWorker);
  db = await dd.connect();
  return db;
}

/* ---------- carregar staging ---------- */
async function loadStaging(requestId) {
  const c = await initDuckDB();
  const r = await fetch("/api/etl-analytics", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: requestId }),
  });
  if (!r.ok) {
    let msg = `HTTP ${r.status}`;
    try { msg = (await r.json()).error || msg; } catch { /* binário */ }
    throw new Error(msg);
  }
  const truncated = r.headers.get("x-analytics-truncated") === "1";
  const buf = new Uint8Array(await r.arrayBuffer());
  await c.registerFileBuffer("staging.parquet", buf);
  await c.send("CREATE OR REPLACE TABLE staging AS SELECT * FROM read_parquet('staging.parquet')");
  const cols = (await c.query(`
    SELECT column_name, data_type
    FROM information_schema.columns WHERE table_name = 'staging'`)).toArray()
    .map((r) => ({ name: r.column_name, type: r.data_type }));
  const [{ n }] = (await c.query("SELECT COUNT(*) n FROM staging")).toArray();
  analyticsData = { rows: Number(n), columns: cols.map(classify) };
  return analyticsData;
}

const classify = (c) => ({
  name: c.name,
  type: c.type,
  kind: /INT|DECIMAL|REAL|DOUBLE|FLOAT|BIGINT|HUGEINT/.test(c.type) ? "num"
    : /DATE|TIME/.test(c.type) ? "date"
    : "cat",
});

/* ---------- perfil automático ---------- */
async function profile() {
  const c = await initDuckDB();
  const out = [];
  for (const col of analyticsData.columns) {
    const avgExpr = col.kind === "num" ? `AVG(CAST("${col.name}" AS DOUBLE))` : "NULL";
    const q = await c.query(`
      SELECT COUNT(*) AS total,
             COUNT("${col.name}") AS filled,
             COUNT(DISTINCT "${col.name}") AS distincts,
             MIN("${col.name}") AS min,
             MAX("${col.name}") AS max,
             ${avgExpr} AS avg
      FROM staging`);
    const [st] = q.toArray();
    out.push({ col, total: Number(st.total), filled: Number(st.filled),
      nulls: Number(st.total) - Number(st.filled), distincts: Number(st.distincts),
      min: st.min, max: st.max, avg: st.avg == null ? null : Number(st.avg) });
  }
  let dupRows = null;
  try {
    const d = await c.query(`
      SELECT COUNT(*) - COUNT(DISTINCT k) AS dup FROM
        (SELECT hash(to_json(staging)) AS k FROM staging)`);
    dupRows = Number(d.toArray()[0].dup);
  } catch { /* to_json indisponível — métrica opcional */ }
  out.dupRows = dupRows;
  return out;
}

/* histograma / top valores por coluna */
async function chartData(col) {
  const c = await initDuckDB();
  if (col.kind === "num") {
    const r = (await c.query(`
      SELECT CAST("${col.name}" AS DOUBLE) AS v FROM staging
      WHERE "${col.name}" IS NOT NULL`)).toArray();
    return { type: "hist", values: r.map((x) => x.v) };
  }
  const r = (await c.query(`
    SELECT "${col.name}" AS v, COUNT(*) AS n FROM staging
    WHERE "${col.name}" IS NOT NULL
    GROUP BY 1 ORDER BY n DESC LIMIT 8`)).toArray();
  return { type: "bar", values: r.map((x) => ({ name: String(x.v), n: Number(x.n) })) };
}

/* ---------- render ---------- */
function renderOverview(p) {
  const nulls = p.reduce((a, x) => a + x.nulls, 0);
  $("#an-overview").innerHTML = `
    <div class="an-stat"><span class="k">Linhas</span><span class="v">${analyticsData.rows}</span></div>
    <div class="an-stat"><span class="k">Colunas</span><span class="v">${analyticsData.columns.length}</span></div>
    <div class="an-stat"><span class="k">Nulos</span><span class="v ${nulls ? "warn" : ""}">${nulls}</span></div>
    <div class="an-stat"><span class="k">Duplicados</span><span class="v ${p.dupRows ? "warn" : ""}">${p.dupRows ?? "—"}</span></div>`;
}

async function renderCharts(p) {
  const grid = $("#an-grid");
  grid.innerHTML = "";
  charts.forEach((ch) => ch.dispose());
  charts.length = 0;
  const BLUE = "#0071e3", GRID = "#e8e8ed";

  for (const stat of p) {
    const { col } = stat;
    const card = document.createElement("div");
    card.className = "an-card";
    card.innerHTML = `
      <div class="an-card-head">
        <strong>${esc(col.name)}</strong>
        <span class="an-chip">${col.type}</span>
      </div>
      <div class="an-card-meta">
        ${stat.nulls ? `<span class="an-chip warn">${((stat.nulls / stat.total) * 100).toFixed(0)}% nulos</span>` : '<span class="an-chip ok">0% nulos</span>'}
        <span class="an-chip">${stat.distincts} distincts</span>
        ${col.kind === "num" ? `<span class="an-chip">min ${fmt(stat.min)} · máx ${fmt(stat.max)}</span>` : ""}
      </div>
      <div class="an-chart" id="an-c-${col.name.replace(/\W/g, "_")}"></div>`;
    grid.appendChild(card);

    const data = await chartData(col);
    const el = card.querySelector(".an-chart");
    const ch = echarts.init(el);
    if (data.type === "hist") {
      const { bins, counts } = histogram(data.values, 16);
      ch.setOption({
        grid: { left: 34, right: 8, top: 8, bottom: 20 },
        tooltip: { trigger: "axis" },
        xAxis: { type: "category", data: bins, axisLabel: { fontSize: 9, color: "#6e6e73" }, axisLine: { lineStyle: { color: GRID } } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: GRID } }, axisLabel: { fontSize: 9, color: "#6e6e73" } },
        series: [{ type: "bar", data: counts, itemStyle: { color: BLUE, borderRadius: [3, 3, 0, 0] } }],
      });
    } else if (data.values.length) {
      ch.setOption({
        grid: { left: 70, right: 20, top: 8, bottom: 20 },
        tooltip: {},
        xAxis: { type: "value", splitLine: { lineStyle: { color: GRID } }, axisLabel: { fontSize: 9, color: "#6e6e73" } },
        yAxis: { type: "category", data: data.values.map((x) => x.name).reverse(),
          axisLabel: { fontSize: 10, color: "#1d1d1f", width: 62, overflow: "truncate" }, axisLine: { lineStyle: { color: GRID } } },
        series: [{ type: "bar", data: data.values.map((x) => x.n).reverse(),
          itemStyle: { color: BLUE, borderRadius: [0, 3, 3, 0] }, barMaxWidth: 14 }],
      });
    } else {
      el.innerHTML = '<div class="an-empty">sem valores</div>';
    }
    charts.push(ch);
  }
}

/* ---------- exploração SQL ---------- */
async function runExplore() {
  const out = $("#an-explore-out");
  const sql = $("#an-sql").value.trim();
  if (!sql) return;
  out.textContent = "a executar…";
  try {
    const c = await initDuckDB();
    const q = sql.replace(/;+\s*$/, "");
    const r = await c.query(`SELECT * FROM (${q}) LIMIT 200`);
    const rows = r.toArray();
    const cols = r.schema.fields.map((f) => f.name);
    out.innerHTML = rows.length
      ? `<table class="an-sql-table"><thead><tr>${cols.map((c2) => `<th>${esc(c2)}</th>`).join("")}</tr></thead>
         <tbody>${rows.map((row) => `<tr>${cols.map((c2) => `<td>${esc(row[c2] ?? "")}</td>`).join("")}</tr>`).join("")}</tbody></table>
         <div class="an-sql-note">${rows.length}${rows.length === 200 ? "+" : ""} linhas</div>`
      : "0 linhas";
  } catch (e) {
    out.innerHTML = `<span class="an-sql-err">${esc(e.message)}</span>`;
  }
}

/* ---------- helpers ---------- */
function histogram(values, nbins) {
  if (!values.length) return { bins: [], counts: [] };
  const mn = Math.min(...values), mx = Math.max(...values);
  const w = (mx - mn) / nbins || 1;
  const counts = new Array(nbins).fill(0);
  values.forEach((v) => {
    counts[Math.min(nbins - 1, Math.floor((v - mn) / w))] += 1;
  });
  const bins = Array.from({ length: nbins }, (_, i) => fmt2(mn + i * w));
  return { bins, counts };
}
const fmt = (v) => v == null ? "—" : (typeof v === "number" ? fmt2(v) : String(v).slice(0, 24));
const fmt2 = (v) => Math.abs(v) >= 1000 ? v.toFixed(0) : v.toPrecision(4).replace(/\.?0+$/, "");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

/* ---------- API pública ---------- */
async function openAnalytics(requestId) {
  const view = $("#etl-analytics-view");
  view.classList.remove("hidden");
  $("#etl-data-view").classList.add("hidden");
  $("#an-status").textContent = "a carregar DuckDB-WASM e dados de staging…";
  try {
    await loadStaging(requestId);
    const p = await profile();
    $("#an-status").textContent = `${analyticsData.rows} linhas · ${analyticsData.columns.length} colunas · perfil gerado`
      + (truncated ? " · amostra (cap 50k linhas)" : "");
    renderOverview(p);
    await renderCharts(p);
  } catch (e) {
    $("#an-status").innerHTML = `<span class="an-sql-err">${esc(e.message)}</span>`;
  }
}
function closeAnalytics() {
  $("#etl-analytics-view").classList.add("hidden");
  $("#etl-data-view").classList.remove("hidden");
}
window.etlAnalytics = { openAnalytics, closeAnalytics, runExplore };
