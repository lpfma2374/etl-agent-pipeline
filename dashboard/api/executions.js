/* API /api/executions — serve o registo de execuções do pipeline ETL.
 * Fonte: Cloudflare D1 (REST API) — base 'etl-executions' (tabela executions).
 * GET  -> lista de execuções (mais recentes primeiro)
 * POST -> upsert de uma execução (protegido por x-auth-token == RECORD_TOKEN;
 *         o CI usa escrita direta no D1, este endpoint é alternativa)
 * Env necessárias no projeto Vercel: CF_API_TOKEN, CF_ACCOUNT_ID,
 * CF_EXECUTIONS_DB_ID (opcional: RECORD_TOKEN para POST).
 */

const CF_API = "https://api.cloudflare.com/client/v4";

module.exports = async (req, res) => {
  // CORS (mesma origem no normal, mas não custa)
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, x-auth-token");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  if (req.method === "OPTIONS") return res.status(204).end();

  const account = process.env.CF_ACCOUNT_ID;
  const db = process.env.CF_EXECUTIONS_DB_ID || "0e8da115-1e4e-4db4-b9f9-2fc0833a3578";
  const token = process.env.CF_API_TOKEN;

  const d1 = async (sql, params) => {
    const r = await fetch(`${CF_API}/accounts/${account}/d1/database/${db}/query`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params ? { sql, params } : { sql }),
    });
    const body = await r.json();
    if (!body.success) throw new Error(JSON.stringify(body.errors));
    return body.result[0].results;
  };

  try {
    if (req.method === "GET") {
      const rows = await d1(
        "SELECT * FROM executions ORDER BY run_started_at DESC, run_number DESC LIMIT 500"
      );
      res.setHeader("Cache-Control", "no-store");
      return res.status(200).json({
        executions: rows.map((r) => ({ ...r, gates: safe(r.gates) })),
        generated_at: new Date().toISOString(),
      });
    }

    if (req.method === "POST") {
      if (!process.env.RECORD_TOKEN || req.headers["x-auth-token"] !== process.env.RECORD_TOKEN) {
        return res.status(401).json({ error: "não autorizado" });
      }
      const rec = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
      if (!rec || !rec.run_id) return res.status(400).json({ error: "run_id obrigatório" });
      const cols = Object.keys(rec);
      await d1(
        `INSERT INTO executions (${cols.join(", ")}) VALUES (${cols.map(() => "?").join(", ")})
         ON CONFLICT(run_id) DO UPDATE SET ${cols.filter((c) => c !== "run_id").map((c) => `${c} = excluded.${c}`).join(", ")}`,
        cols.map((c) => rec[c] ?? null)
      );
      return res.status(201).json({ ok: true, run_id: rec.run_id });
    }

    return res.status(405).json({ error: "método não suportado" });
  } catch (e) {
    return res.status(502).json({ error: "D1 indisponível", detail: String(e).slice(0, 300) });
  }
};

function safe(j) {
  try { return JSON.parse(j); } catch { return []; }
}
