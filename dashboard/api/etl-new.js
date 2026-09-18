// Novo ETL — proxy do wizard para o backend function etlUpload (Base44).
// O token ETL_INTAKE_TOKEN vive no env do Vercel; o browser nunca o vê.
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
  const upstream = await fetch("https://superagent-33c6e8f8.base44.app/functions/etlUpload", {
    method: "POST",
    headers: { "x-etl-token": token },
    body: await req.formData(), // reencaminha o multipart tal qual
  });
  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
