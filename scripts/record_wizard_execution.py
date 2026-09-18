"""Regista execuções do wizard 'Novo ETL' no Cloudflare D1 (dashboard).

Uso:
  python3 scripts/record_wizard_execution.py --request-id <id> \
      --status in_progress|success|failure --workflow-id <uuid> \
      [--dataset <nome>] [--duration 12.3] [--message "..."] \
      [--gates-json '[{"gate":"Extract","tool":"pandas","status":"success","seconds":2.1}, …]'

run_id = etlreq_<request_id>. Upsert idempotente (re-runs atualizam).
Env: CF_API_TOKEN, CF_ACCOUNT_ID (opcional CF_EXECUTIONS_DB_ID).
"""

import argparse
import json
import os
import time
import urllib.request

CF_API = "https://api.cloudflare.com/client/v4"
DB_UUID = os.environ.get("CF_EXECUTIONS_DB_ID",
                         "0e8da115-1e4e-4db4-b9f9-2fc0833a3578")  # etl-executions

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
        f"{DB_UUID}/query",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}",
                 "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read())
    if not body.get("success"):
        raise RuntimeError(f"D1 erro: {body.get('errors')}")
    return body["result"][0]["results"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-id", required=True)
    ap.add_argument("--status", required=True,
                    choices=["in_progress", "success", "failure", "cancelled"])
    ap.add_argument("--dataset", default="")
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--message", default="")
    ap.add_argument("--gates-json", default="")
    ap.add_argument("--report-path", default="")
    args = ap.parse_args()

    run_id = f"etlreq_{args.request_id}"
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())

    rec = {
        "run_id": run_id,
        "workflow": "Novo ETL (wizard)",
        "run_number": None,
        "event": "dashboard",
        "head_sha": "",
        "commit_message": args.message or args.dataset,
        "status": args.status,
        "duration_seconds": args.duration,
        "run_started_at": now,
        "updated_at": now,
        "html_url": "",
        "gates": args.gates_json or "",
        "errors": "",
        "report_path": args.report_path,
        "recorded_at": now,
    }

    d1_query(DDL)
    # preserva run_started_at/duração de registos já existentes (update parcial)
    prev = d1_query("SELECT run_started_at, duration_seconds, run_number "
                   "FROM executions WHERE run_id = ?", [run_id])
    if prev:
        p = prev[0]
        if args.status == "in_progress" and p.get("run_started_at"):
            rec["run_started_at"] = p["run_started_at"]
        if args.duration is None and p.get("duration_seconds") is not None:
            rec["duration_seconds"] = p["duration_seconds"]
        if p.get("run_number") is not None:
            rec["run_number"] = p["run_number"]

    cols = list(rec.keys())
    sql = (
        f'INSERT INTO executions ({", ".join(cols)}) '
        f'VALUES ({", ".join("?" * len(cols))}) '
        f'ON CONFLICT(run_id) DO UPDATE SET '
        + ", ".join(f'{c} = excluded.{c}' for c in cols if c != "run_id"))
    d1_query(sql, [rec[c] for c in cols])
    print(json.dumps({"ok": True, "run_id": run_id, "status": args.status}))


if __name__ == "__main__":
    main()
