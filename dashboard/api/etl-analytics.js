/* API /api/etl-analytics — proxy do wizard 'Novo ETL' para o backend function
 * etlAnalyticsFile (Base44). POST { id } → bytes do parquet de staging,
 * same-origin (o parquet viaja no EtlRequest; nenhum URL de storage chega
 * ao browser).
 */

const UPSTREAM = "https://superagent-33c6e8f8.base44.app/functions/etlAnalyticsFile";

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
    if (!upstream.ok) {
      const text = await upstream.text();
      let msg = `upstream ${upstream.status}`;
      try { msg = JSON.parse(text).error || msg; } catch { /* binário */ }
      return res.status(upstream.status).json({ ok: false, error: msg });
    }
    const buf = Buffer.from(await upstream.arrayBuffer());
    if (upstream.headers.get("x-analytics-truncated") === "1") {
      res.setHeader("X-Analytics-Truncated", "1");
    }
    res.setHeader("Content-Type", "application/octet-stream");
    res.setHeader("Content-Length", buf.length);
    return res.send(buf);
  } catch (e) {
    return res.status(502).json({ ok: false, error: e?.message || "proxy falhou" });
  }
};
