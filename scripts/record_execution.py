"""Regista execuções do pipeline ETL (GitHub Actions) no Cloudflare D1.

Fonte: GitHub Actions API (runs + jobs/steps por run).
Destino: D1 'etl-executions' (REST API da Cloudflare — mesmos endpoints do
CloudflareD1Loader), tabela 'executions' — upsert por run_id (idempotente).

Modos:
  CI (sem args)      usa envs GITHUB_RUN_ID + GH_TOKEN (workflow step, `if:
                     always()` — regista sucesso E falha)
  --run-id <id>      regista/atualiza um run específico
  --all              backfill de TODOS os runs (workflow CI + Pipeline)

Env: CF_API_TOKEN, CF_ACCOUNT_ID; opcional CF_EXECUTIONS_DB_ID (uuid D1).
GH_TOKEN opcional em backfill (fallback: API anónima, 60 req/h).
"""

import argparse
import json
import os
import time
import urllib.request

GH_API = "https://api.github.com/repos/lpfma2374/etl-agent-pipeline"
CF_API = "https://api.cloudflare.com/client/v4"
DB_UUID = "0e8da115-1e4e-4db4-b9f9-2fc0833a3578"  # etl-executions

# gates canónicos do ETL (nome do gate -> tool) — para o swimlane
GATE_TOOLS = [
    ("[1] Extract", "Extract", "pandas + requests (padrão Airbyte)"),
    ("[2] Transform", "Transform", "dbt-core (DuckDB staging)"),
    ("[3] Validate", "Validate", "Great Expectations (gate de qualidade)"),
    ("[4] Load", "Load", "Loader destino (upsert por PK)"),
    ("[5] Commit", "Report", "Report de auditoria (docs/executions)"),
    ("Batch-run", "Pipeline completo", "run_batches.py (extract→dbt→GE→load→report)"),
    ("Lint", "Lint", "ruff"),
    ("Gerar dados sintéticos", "Seed", "make_seed.py (dados sintéticos)"),
    ("Publicar relatório", "Publicação", "git push (auditoria)"),
    ("Instalar dependências", "Setup", "pip install"),
    ("dbt docs", "dbt docs", "dbt-core"),
]


def _req(url, token=None, payload=None):
    headers = {"Accept": "application/vnd.github+json"}
    if "api.github.com" in url and token:
        headers["Authorization"] = f"Bearer {token}"
    elif "cloudflare" in url:
        headers["Authorization"] = f"Bearer {os.environ['CF_API_TOKEN']}"
        headers["Content-Type"] = "application/json"
    with urllib.request.urlopen(
            urllib.request.Request(url, headers=headers), timeout=60) as resp:
        return resp.headers, json.loads(resp.read())



def _paginate(url, token):
    """Percorre paginação via header Link (runs/jobs da GitHub API)."""
    while url:
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {token}"} if token else {})})
        with urllib.request.urlopen(req, timeout=60) as resp:
            yield json.loads(resp.read())
            link = resp.headers.get("Link", "")
            url = next((l.split(";")[0].strip("<>") for l in link.split(",")
                        if 'rel="next"' in l), None)


def get_run(run_id, token):
    _, run = _req(f"{GH_API}/actions/runs/{run_id}", token)
    return run


def get_jobs(run_id, token):
    jobs = []
    for page in _paginate(f"{GH_API}/actions/runs/{run_id}/jobs?per_page=100", token):
        jobs += page.get("jobs", [])
    return jobs


def _iso(ts):
    return (ts or "").replace("Z", "+00:00")


def _seconds(a, b):
    if not a or not b:
        return None
    from datetime import datetime
    ta = datetime.fromisoformat(_iso(a))
    tb = datetime.fromisoformat(_iso(b))
    return round((tb - ta).total_seconds(), 1)


def _gate_name(step_name):
    for prefix, gate, tool in GATE_TOOLS:
        if prefix.lower() in step_name.lower():
            return gate, tool
    return None, None  # step de infra (checkout/setup/upload) — sem gate


WF_NAMES = {".github/workflows/ci.yml": "CI",
            ".github/workflows/pipeline.yml": "Pipeline (migração real)"}


def _wf_name(run):
    """nome amigável; runs antigos devolvem o path no lugar do nome."""
    name = run.get("name")
    if name and not name.startswith("."):
        return name
    return WF_NAMES.get(run.get("path"), name or run.get("path", "?"))


def build_record(run, jobs, report_hint=None):
    steps, errors = [], []
    for job in jobs:
        for st in job.get("steps", []):
            gate, tool = _gate_name(st.get("name", ""))
            if st.get("conclusion") not in ("success", "skipped", None):
                errors.append(f"[{st['name']}] {st['conclusion']}")
            steps.append({
                "step": st.get("name"), "gate": gate, "tool": tool,
                "status": st.get("conclusion") or st.get("status"),
                "seconds": _seconds(st.get("started_at"), st.get("completed_at")),
            })
    dur = _seconds(run.get("run_started_at") or run.get("created_at"),
                   run.get("updated_at"))
    commit_msg = (run.get("head_commit") or {}).get("message", "")
    # o report existe se algum step/publicação referiu docs/executions OU
    # workflow Pipeline com sucesso; o dashboard liga por data se houver
    return {
        "run_id": str(run["id"]),
        "workflow": _wf_name(run),
        "run_number": run.get("run_number"),
        "event": run.get("event"),
        "head_sha": run.get("head_sha", "")[:7] if run.get("head_sha") else "",
        "commit_message": commit_msg.split("\n")[0][:120],
        "status": run.get("conclusion") or run.get("status"),
        "duration_seconds": dur,
        "run_started_at": run.get("run_started_at") or run.get("created_at"),
        "updated_at": run.get("updated_at"),
        "html_url": run.get("html_url"),
        "gates": json.dumps(steps, ensure_ascii=False),
        "errors": "; ".join(errors) or None,
        "report_path": report_hint,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
    }


DDL = """CREATE TABLE IF NOT EXISTS executions (
  run_id TEXT PRIMARY KEY, workflow TEXT, run_number INTEGER, event TEXT,
  head_sha TEXT, commit_message TEXT, status TEXT, duration_seconds REAL,
  run_started_at TEXT, updated_at TEXT, html_url TEXT, gates TEXT,
  errors TEXT, report_path TEXT, recorded_at TEXT)"""


def d1_query(sql, params=None):
    payload = {"sql": sql}
    if params is not None:
        payload["params"] = params
    req = urllib.request.Request(
        f"{CF_API}/accounts/{os.environ['CF_ACCOUNT_ID']}/d1/database/"
        f"{os.environ.get('CF_EXECUTIONS_DB_ID', DB_UUID)}/query",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}",
                 "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read())
    if not body.get("success"):
        raise RuntimeError(f"D1 erro: {body.get('errors')}")
    return body["result"][0]["results"]


def upsert(rec):
    d1_query(DDL)
    cols = list(rec.keys())
    sql = (
        f'INSERT INTO executions ({", ".join(cols)}) '
        f'VALUES ({", ".join("?" * len(cols))}) '
        f'ON CONFLICT(run_id) DO UPDATE SET '
        + ", ".join(f'{c} = excluded.{c}' for c in cols if c != "run_id"))
    d1_query(sql, [rec[c] for c in cols])


def record_run(run_id, token, report_hint=None):
    run = get_run(run_id, token)
    jobs = get_jobs(run_id, token)
    rec = build_record(run, jobs, report_hint)
    upsert(rec)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not os.environ.get("CF_API_TOKEN") or not os.environ.get("CF_ACCOUNT_ID"):
        raise SystemExit("CF_API_TOKEN / CF_ACCOUNT_ID em falta (env)")
    if args.all:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_ACCESS_TOKEN")
        n = 0
        for page in _paginate(f"{GH_API}/actions/runs?per_page=100", token):
            for run in page.get("workflow_runs", []):
                rec = record_run(run["id"], token)
                n += 1
                print(f"[run] {rec['workflow']} #{rec['run_number']} "
                      f"{rec['status']} | {rec['duration_seconds']}s | "
                      f"gates: {len(json.loads(rec['gates']))} steps")
                time.sleep(0.15)
        print(f"[fim] backfill: {n} execuções registadas no D1")
    else:
        run_id = args.run_id or os.environ.get("GITHUB_RUN_ID")
        token = (os.environ.get("GH_TOKEN")
                 or os.environ.get("GITHUB_ACCESS_TOKEN"))
        if not run_id:
            raise SystemExit("GITHUB_RUN_ID em falta (modo CI) ou --run-id")
        rec = record_run(run_id, token)
        print(f"[run] {rec['workflow']} #{rec['run_number']} {rec['status']} "
              f"registado no D1 (run_id {rec['run_id']})")


if __name__ == "__main__":
    main()
