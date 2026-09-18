/* API /api/etl-new — proxy do wizard 'Novo ETL' para o backend function
 * etlUpload (Base44). Reencaminha o multipart tal qual; o token
 * ETL_INTAKE_TOKEN vive no env do Vercel e nunca chega ao browser.
 */

const UPSTREAM = "https://superagent-33c6e8f8.base44.app/functions/etlUpload";

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ ok: false, error: "POST apenas" });

  const token = process.env.ETL_INTAKE_TOKEN;
  if (!token) return res.status(503).json({ ok: false, error: "ETL_INTAKE_TOKEN não configurado" });

  try {
    const chunks = [];
    for await (const c of req) chunks.push(c);
    const body = Buffer.concat(chunks);
    const upstream = await fetch(UPSTREAM, {
      method: "POST",
      headers: {
        "x-etl-token": token,
        "content-type": req.headers["content-type"] || "",
      },
      body,
    });
    const text = await upstream.text();
    res.status(upstream.status).setHeader("Content-Type", "application/json");
    return res.send(text);
  } catch (e) {
    return res.status(502).json({ ok: false, error: e?.message || "proxy falhou" });
  }
};
