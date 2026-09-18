/* API /api/etl-transform — proxy do wizard 'Novo ETL' para o backend function
 * etlRequestTransform (Base44). POST { id, notes } → { ok, status }.
 */

const UPSTREAM = "https://superagent-33c6e8f8.base44.app/functions/etlRequestTransform";

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ ok: false, error: "POST apenas" });

  const token = process.env.ETL_INTAKE_TOKEN;
  if (!token) return res.status(503).json({ ok: false, error: "ETL_INTAKE_TOKEN não configurado" });

  try {
    const upstream = await fetch(UPSTREAM, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-etl-token": token },
      body: JSON.stringify(req.body || {}),
    });
    const text = await upstream.text();
    res.status(upstream.status).setHeader("Content-Type", "application/json");
    return res.send(text);
  } catch (e) {
    return res.status(502).json({ ok: false, error: e?.message || "proxy falhou" });
  }
};
