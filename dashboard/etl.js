/* Novo ETL — wizard do dashboard.
 * Origem (ficheiro csv/xlsx ou Google Sheets) → destino (Airtable / D1 / Neon)
 * → extract para staging DuckDB (agente) → data list + comentários de
 * transformação → dbt + validação GE + load final. Polling do estado do pedido.
 */
"use strict";

const ETLM = {
  id: null,
  pollTimer: null,
  stage: null, // 1 origem, 2 transformação, 3 exportação
  originMode: "file",
};

const $$ = (s) => document.querySelector(s);

/* ---------- abrir/fechar ---------- */
function etlOpen() {
  ETLM.stage = 1; ETLM.originMode = "file";
  etlShowStep(1);
  const lastId = localStorage.getItem("etl_request_id");
  if (lastId && $$("#etl-resume-row")) {
    $$("#etl-resume-row").classList.remove("hidden");
    $$("#etl-resume-btn").onclick = () => resumeRequest(lastId);
  }
  $$("#etl-file").value = "";
  $$("#etl-file-label").textContent = "Clique para escolher um ficheiro .csv, .xlsx ou .xls (máx. 10 MB)";
  $$("#etl-sheet-url").value = "";
  $$("#etl-destination").value = "";
  $$("#etl-notes").value = "";
  etlHide("#etl-step1-error"); etlHide("#etl-step2-error");
  $$("#etl-modal").classList.remove("hidden");
}
function etlClose() {
  if (ETLM.pollTimer) { clearInterval(ETLM.pollTimer); ETLM.pollTimer = null; }
  $$("#etl-modal").classList.add("hidden");
  if (typeof load === "function") load(); // refresca a tabela de execuções
}
function etlShowStep(n) {
  ETLM.stage = n;
  [1, 2, 3].forEach((i) => $$("#etl-step" + i).classList.toggle("hidden", i !== n));
}
const etlHide = (s) => $$(s).classList.add("hidden");
const etlShow = (s) => $$(s).classList.remove("hidden");

/* ---------- passo 1: origem + destino ---------- */
function setOriginMode(mode) {
  ETLM.originMode = mode;
  $$("#etl-origin-file").classList.toggle("active", mode === "file");
  $$("#etl-origin-sheets").classList.toggle("active", mode === "gsheets");
  $$("#etl-file-zone").classList.toggle("hidden", mode !== "file");
  $$("#etl-sheets-row").classList.toggle("hidden", mode !== "gsheets");
}

async function submitIntake() {
  const err = $$("#etl-step1-error");
  err.classList.add("hidden");
  const destination = $$("#etl-destination").value;
  if (!destination) { etlFail1("Escolhe um destino."); return; }

  const fd = new FormData();
  fd.append("destination", destination);
  fd.append("origin_type", ETLM.originMode);
  if (ETLM.originMode === "file") {
    const f = $$("#etl-file").files[0];
    if (!f) { etlFail1("Escolhe um ficheiro CSV ou Excel."); return; }
    fd.append("file", f);
  } else {
    const url = $$("#etl-sheet-url").value.trim();
    if (!url) { etlFail1("Cola o link do Google Sheets."); return; }
    fd.append("sheet_url", url);
  }

  const btn = $$("#etl-extract-btn");
  btn.disabled = true; btn.textContent = "A enviar…";
  try {
    const r = await fetch("/api/etl-new", { method: "POST", body: fd });
    const body = await r.json();
    if (!r.ok || !body.ok) throw new Error(body.error || `HTTP ${r.status}`);
    ETLM.id = body.id;
    localStorage.setItem("etl_request_id", ETLM.id);
    etlShowStep(2);
    startPolling();
  } catch (e) {
    etlFail1(e.message);
  } finally {
    btn.disabled = false; btn.textContent = "Extrair para staging (DuckDB)";
  }
}
function etlFail1(msg) { const e = $$("#etl-step1-error"); e.textContent = msg; e.classList.remove("hidden"); }

function resumeRequest(id) {
  ETLM.id = id;
  etlShowStep(2);
  startPolling();
}

/* ---------- polling ---------- */
function startPolling() {
  if (ETLM.pollTimer) clearInterval(ETLM.pollTimer);
  const tick = async () => {
    if (!ETLM.id) return;
    try {
      const r = await fetch("/api/etl-status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: ETLM.id }),
      });
      const body = await r.json();
      if (!r.ok || !body.ok) throw new Error(body.error || `HTTP ${r.status}`);
      handleStatus(body);
    } catch (e) { /* transitório: tenta de novo no próximo tick */ }
  };
  tick();
  ETLM.pollTimer = setInterval(tick, 4000);
}

function handleStatus(s) {
  if (s.status === "pending_extract" || s.status === "extracting") {
    etlShowStep(2);
    etlShow("#etl-progress-1"); etlHide("#etl-data-view");
  } else if (s.status === "extracted") {
    stopPoll();
    etlHide("#etl-progress-1");
    renderPreview(s);
    etlShow("#etl-data-view");
  } else if (s.status === "pending_transform" || s.status === "transforming") {
    etlShowStep(3);
    etlShow("#etl-progress-2"); etlHide("#etl-result-view"); etlHide("#etl-fail-view");
  } else if (s.status === "loaded") {
    stopPoll();
    etlHide("#etl-progress-2");
    renderResult(s);
    etlShow("#etl-result-view");
  } else if (s.status === "failed") {
    stopPoll();
    etlHide("#etl-progress-2");
    $$("#etl-fail-body").textContent = s.error || "Erro desconhecido no pipeline.";
    etlShow("#etl-fail-view");
    if (ETLM.stage === 2) { // falhou no extract — volta ao passo 1 com o erro visível
      etlClose();
    }
  }
}
function stopPoll() { if (ETLM.pollTimer) { clearInterval(ETLM.pollTimer); ETLM.pollTimer = null; } }

/* ---------- data list (leitura) ---------- */
function renderPreview(s) {
  const p = s.preview;
  if (!p || !Array.isArray(p.columns)) {
    $$("#etl-data-meta").innerHTML = '<span class="etl-err-inline">Preview indisponível.</span>';
    return;
  }
  $$("#etl-data-count").textContent = `${p.row_count ?? "?"} registos · ${p.columns.length} colunas`;
  $$("#etl-analytics-btn").classList.toggle("hidden", !(p && p.analytics));
  $$("#etl-data-meta").innerHTML =
    (p.columns || []).map((c) =>
      `<span class="etl-chip">${esc2(c.name)} <em>${esc2(c.dtype || "")}</em></span>`).join("");

  const tbl = $$("#etl-preview-tbl");
  const cols = p.columns || [];
  const rows = p.sample || [];
  const head = `<thead><tr>${cols.map((c) => `<th>${esc2(c.name)}</th>`).join("")}</tr></thead>`;
  const body = rows.length
    ? `<tbody>${rows.map((row) =>
        `<tr>${cols.map((c) => `<td>${esc2(row[c.name] ?? "")}</td>`).join("")}</tr>`).join("")}</tbody>`
    : `<tbody><tr><td colspan="${cols.length}" class="muted" style="text-align:center;padding:32px">sem linhas de amostra</td></tr></tbody>`;
  tbl.innerHTML = head + body;
}

/* ---------- passo 2: submeter transformações ---------- */
async function submitTransform() {
  const err = $$("#etl-step2-error");
  err.classList.add("hidden");
  const notes = $$("#etl-notes").value.trim();
  if (!notes) { err.textContent = "Descreve as transformações que queres executar."; err.classList.remove("hidden"); return; }
  const btn = $$("#etl-transform-btn");
  btn.disabled = true; btn.textContent = "A enviar…";
  try {
    const r = await fetch("/api/etl-transform", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: ETLM.id, notes }),
    });
    const body = await r.json();
    if (!r.ok || !body.ok) throw new Error(body.error || `HTTP ${r.status}`);
    etlShowStep(3);
    startPolling();
  } catch (e) {
    err.textContent = e.message; err.classList.remove("hidden");
  } finally {
    btn.disabled = false; btn.textContent = "Executar transformações e exportar";
  }
}

/* ---------- passo 3: resultado ---------- */
function renderResult(s) {
  const r = s.result || {};
  const destLabel = { airtable: "Airtable", d1: "Cloudflare D1", neon: "Neon PostgreSQL" }[s.destination] || s.destination;
  const rows = [];
  rows.push(kv("Destino", esc2(r.destination_name || destLabel)));
  if (r.rows_loaded != null) rows.push(kv("Registos carregados", esc2(String(r.rows_loaded))));
  if (r.validation) rows.push(kv("Validação (GE)", esc2(r.validation)));
  if (r.transformations) rows.push(kv("Transformações aplicadas", esc2(r.transformations)));
  if (r.duration) rows.push(kv("Duração", esc2(r.duration)));
  let links = "";
  if (r.destination_url) links += `<a href="${esc2(r.destination_url)}" target="_blank" rel="noopener">abrir destino →</a> `;
  if (r.report_url) links += `<a href="${esc2(r.report_url)}" target="_blank" rel="noopener">report de auditoria →</a>`;
  if (links) rows.push(`<div class="etl-kv"><span class="k">Links</span>${links}</div>`);
  $$("#etl-result-body").innerHTML = rows.join("");
}
const kv = (k, v) => `<div class="etl-kv"><span class="k">${k}</span>${v}</div>`;

function esc2(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ---------- eventos ---------- */
document.addEventListener("DOMContentLoaded", () => {
  $$("#btn-new-etl").addEventListener("click", etlOpen);
  $$("#etl-close").addEventListener("click", etlClose);
  $$("#etl-modal").addEventListener("click", (ev) => { if (ev.target === $$("#etl-modal")) etlClose(); });
  $$("#etl-origin-file").addEventListener("click", () => setOriginMode("file"));
  $$("#etl-origin-sheets").addEventListener("click", () => setOriginMode("gsheets"));
  $$("#etl-file").addEventListener("change", () => {
    const f = $$("#etl-file").files[0];
    $$("#etl-file-label").textContent = f ? `${f.name} (${(f.size / 1024).toFixed(0)} KB)` : "Clique para escolher um ficheiro .csv, .xlsx ou .xls (máx. 10 MB)";
  });
  $$("#etl-extract-btn").addEventListener("click", submitIntake);
  $$("#etl-transform-btn").addEventListener("click", submitTransform);
  $$("#etl-view-execs").addEventListener("click", () => { etlClose(); document.getElementById("execucoes").scrollIntoView({ behavior: "smooth" }); });
  $$("#etl-done").addEventListener("click", etlClose);
  $$("#etl-done-2").addEventListener("click", etlClose);
  $$("#etl-analytics-btn").addEventListener("click", () =>
    window.etlAnalytics && window.etlAnalytics.openAnalytics(ETLM.id));
  $$("#etl-analytics-back").addEventListener("click", () =>
    window.etlAnalytics && window.etlAnalytics.closeAnalytics());
  $$("#etl-sql-run").addEventListener("click", () =>
    window.etlAnalytics && window.etlAnalytics.runExplore());
});
