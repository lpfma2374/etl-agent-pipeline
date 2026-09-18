// Novo ETL — proxy do wizard para etlRequestTransform (Base44).
// POST { id, notes } → { ok, status }
export default async function handler(req) {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "POST apenas" }), {
      status: 405, headers: { "Content-Type": "application/json" },
    });
  }
  const token = process.env.ETL_INTAKE_TOKEN;
  if (!token) {
    return new Response(JSON.stringify({ ok: false, error: "ETL_INTAKE_TOKEN não configurado no Vercel" }), {
      status: 503, headers: { "Content-Type": "application/json" },
    });
  }
  const body = await req.text();
  const upstream = await fetch("https://superagent-33c6e8f8.base44.app/functions/etlRequestTransform", {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-etl-token": token },
    body,
  });
  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
