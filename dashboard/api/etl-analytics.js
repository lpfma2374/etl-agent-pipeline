/* API /api/etl-analytics — proxy do wizard 'Novo ETL'.
 * POST { id } → lê o pedido no backend (etlRequestStatus), obtém o
 * analytics.parquet_url dos dados de staging e devolve o parquet
 * same-origin (o URL de storage nunca chega ao browser).
 */

const UPSTREAM = "https://superagent-33c6e8f8.base44.app/functions/etlRequestStatus";

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ ok: false, error: "POST apenas" });

  const token = process.env.ETL_INTAKE_TOKEN;
  if (!token) return res.status(503).json({ ok: false, error: "ETL_INTAKE_TOKEN não configurado" });

  try {
    const id = (req.body || {}).id;
    if (!id) return res.status(400).json({ ok: false, error: "id em falta" });

    const st = await fetch(UPSTREAM, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-etl-token": token },
      body: JSON.stringify({ id }),
    });
    const info = await st.json();
    if (!st.ok || !info.ok) {
      return res.status(st.status || 502).json({ ok: false, error: info.error || "pedido não encontrado" });
    }
    const url = info.preview?.analytics?.parquet_url;
    if (!url) {
      return res.status(404).json({ ok: false, error: "analytics indisponível para este pedido" });
    }
    const pq = await fetch(url);
    if (!pq.ok) return res.status(502).json({ ok: false, error: `storage ${pq.status}` });

    const buf = Buffer.from(await pq.arrayBuffer());
    res.setHeader("Content-Type", "application/octet-stream");
    res.setHeader("Content-Disposition", 'inline; filename="staging.parquet"');
    return res.send(buf);
  } catch (e) {
    return res.status(502).json({ ok: false, error: e?.message || "proxy falhou" });
  }
};
