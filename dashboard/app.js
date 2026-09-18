/* ETL Pipeline dashboard — app logic
 * Dados: /api/executions (serverless Vercel -> Cloudflare D1 'etl-executions')
 * Header stats + swimlane da cascade ETL + lista tabular com detalhe por run.
 */
"use strict";

const GATE_ORDER = ["Lint", "Seed", "Extract", "Transform", "Validate",
  "Load", "Report", "Pipeline completo", "dbt docs", "Publicação", "Setup"];
let EXECUTIONS = [];
let currentDetail = null;

/* ---------------- utils ---------------- */
const $ = (sel) => document.querySelector(sel);

function fmtDur(s) {
  if (s == null) return "—";
  if (s < 60) return `${Math.round(s)}s`;
  const m = Math.floor(s / 60);
  return `${m}m ${String(Math.round(s % 60)).padStart(2, "0")}s`;
}

function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "short" });
}

function statusClass(s) {
  if (s === "success") return "ok";
  if (s === "failure") return "fail";
  if (s === "cancelled") return "cancel";
  if (s === "skipped") return "skip";
  return "cancel";
}
const statusLabel = { success: "OK", failure: "FALHA", cancelled: "CANCELADO", skipped: "SKIPPED" };

function isCritical(e) {
  return e.status === "failure" && (e.event === "push" || e.event === "workflow_dispatch");
}

/* ---------------- dados ---------------- */
async function load() {
  try {
    const r = await fetch("/api/executions", { cache: "no-store" });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const body = await r.json();
    EXECUTIONS = body.executions || [];
    render();
    $("#last-updated").textContent =
      `atualizado às ${new Date().toLocaleTimeString("pt-PT")}`;
  } catch (e) {
    $("#last-updated").textContent = "erro ao carregar";
    $("#tbody").innerHTML =
      `<tr><td colspan="7" class="muted">Sem ligação à API de execuções (${e.message}).</td></tr>`;
  }
}

/* ---------------- header ---------------- */
function renderStats() {
  const withDur = EXECUTIONS.filter((e) => e.duration_seconds > 0);
  const avg = withDur.length
    ? withDur.reduce((a, e) => a + e.duration_seconds, 0) / withDur.length
    : null;
  const crit = EXECUTIONS.filter(isCritical).length;
  const succ = EXECUTIONS.filter((e) => e.status === "success").length;
  const rate = EXECUTIONS.length ? Math.round((100 * succ) / EXECUTIONS.length) : null;

  $("#stat-total").textContent = EXECUTIONS.length;
  $("#stat-total-foot").textContent =
    `${EXECUTIONS.filter((e) => e.workflow || "").length} runs · GitHub Actions`;
  $("#stat-errors").textContent = crit;
  $("#stat-errors-foot").textContent = "runs com conclusão failure";
  $("#stat-avg").textContent = fmtDur(avg);
  $("#stat-avg-foot").textContent =
    `${withDur.length} runs com duração registada`;
  $("#stat-rate").textContent = rate == null ? "—" : `${rate}%`;
  $("#stat-rate-foot").textContent = `${succ} sucesso / ${EXECUTIONS.length}`;
}

/* ---------------- swimlane ---------------- */
function gatesOf(e) {
  const gates = (e.gates || []).filter((g) => g.gate && g.status !== "skipped");
  const rank = (g) => {
    const i = GATE_ORDER.indexOf(g.gate);
    return i === -1 ? 99 : i;
  };
  return gates.sort((a, b) => rank(a) - rank(b));
}

function lane(g, idx, total) {
  const cls = statusClass(g.status);
  const chip = statusLabel[g.status] || (g.status || "?").toUpperCase();
  const frag = document.createElement("template");
  frag.innerHTML = `
    <div class="lane ${cls}">
      <div class="lane-gate">${esc(g.gate)}</div>
      <div class="lane-tool">${esc(g.tool || g.step || "")}</div>
      <div class="lane-foot">
        <span class="chip ${cls}">${chip}</span>
        <span class="lane-dur">${fmtDur(g.seconds)}</span>
      </div>
    </div>
    ${idx < total - 1 ? '<span class="arrow">→</span>' : ""}`;
  return frag.content.firstElementChild;
}

function renderSwimlane(e) {
  const box = $("#swimlane");
  box.innerHTML = "";
  const gates = gatesOf(e);
  if (!gates.length) {
    box.innerHTML = '<div class="muted">sem gates registados nesta execução.</div>';
  } else {
    gates.forEach((g, i) => box.appendChild(lane(g, i, gates.length)));
  }
  $("#swimlane-meta").textContent =
    `${e.workflow} #${e.run_number} · ${fmtDate(e.run_started_at)} · ` +
    `${e.head_sha ? e.head_sha + " · " : ""}${esc(e.commit_message || e.event || "")}`;
}

/* ---------------- tabela ---------------- */
function renderTable() {
  const tb = $("#tbody");
  tb.innerHTML = "";
  $("#table-count").textContent = `${EXECUTIONS.length} execuções registadas`;
  EXECUTIONS.forEach((e) => {
    const tr = document.createElement("tr");
    tr.className = "row";
    tr.innerHTML = `
      <td>${fmtDate(e.run_started_at)}</td>
      <td>${esc(e.workflow)} <span class="muted">#${e.run_number}</span></td>
      <td class="muted" title="${esc(e.commit_message || "")}">${esc(e.head_sha || "—")}</td>
      <td class="num">${fmtDur(e.duration_seconds)}</td>
      <td class="err-cell" title="${esc(e.errors || "")}">${e.errors ? esc(e.errors) : "—"}</td>
      <td><span class="status"><i class="dot ${statusClass(e.status)}"></i>${statusLabel[e.status] || e.status || "?"}</span></td>
      <td><button class="btn-detail">ver detalhe</button></td>`;
    tr.querySelector(".btn-detail").addEventListener("click", () => openDetail(e));
    tr.addEventListener("click", (ev) => {
      if (ev.target.tagName === "BUTTON" || ev.target.closest("a")) return;
      renderSwimlane(e);
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    tb.appendChild(tr);
  });
}

/* ---------------- modal detalhe ---------------- */
function openDetail(e) {
  currentDetail = e;
  $("#modal-title").textContent = `${e.workflow} #${e.run_number}`;
  const gates = e.gates || [];
  const steps = gates.map((s) => `
    <tr>
      <td>${esc(s.step || "")}</td>
      <td class="muted">${esc(s.gate || "")}</td>
      <td><span class="chip ${statusClass(s.status)}">${statusLabel[s.status] || s.status || "?"}</span></td>
      <td class="num muted">${fmtDur(s.seconds)}</td>
    </tr>`).join("");
  $("#modal-body").innerHTML = `
    <div class="detail-meta">
      <div><span class="k">Data</span>${fmtDate(e.run_started_at)}</div>
      <div><span class="k">Status</span>${statusLabel[e.status] || e.status || "?"}</div>
      <div><span class="k">Duração total</span>${fmtDur(e.duration_seconds)}</div>
      <div><span class="k">Evento</span>${esc(e.event || "—")}</div>
      <div><span class="k">Commit</span>${esc(e.head_sha || "—")}</div>
      <div><span class="k">Mensagem</span>${esc(e.commit_message || "—")}</div>
    </div>
    <h2 style="font-size:14px;margin:14px 0 8px">Cascade completa (steps)</h2>
    <table class="step-list">
      <thead><tr><th>Step</th><th>Gate</th><th>Status</th><th>Tempo</th></tr></thead>
      <tbody>${steps || '<tr><td colspan="4" class="muted">sem steps registados</td></tr>'}</tbody>
    </table>
    ${e.errors ? `<div class="errors-box">${esc(e.errors)}</div>` : ""}
    <div class="modal-links">
      ${e.html_url ? `<a href="${esc(e.html_url)}" target="_blank" rel="noopener">ver run no GitHub →</a>` : ""}
      <a href="https://github.com/lpfma2374/etl-agent-pipeline/tree/main/docs/executions" target="_blank" rel="noopener">reports de auditoria →</a>
    </div>`;
  $("#modal").classList.remove("hidden");
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ---------------- init ---------------- */
function render() {
  renderStats();
  renderTable();
  if (EXECUTIONS.length) renderSwimlane(EXECUTIONS[0]);
}

$("#modal-close").addEventListener("click", () => $("#modal").classList.add("hidden"));
$("#modal").addEventListener("click", (ev) => {
  if (ev.target === $("#modal")) $("#modal").classList.add("hidden");
});
$("#btn-refresh").addEventListener("click", load);
load();
setInterval(load, 90_000);
