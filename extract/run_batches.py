"""ETL_Agent — orquestrador de batches (modo incremental).

Regra do workflow ETL_Agent: a extração de uma origem é feita por lotes de,
no máximo, `batch_size` registos (predefinição: 50). Cada lote percorre o
pipeline completo — extract -> transform (dbt) -> validate (Great
Expectations) -> load -> report. Se um lote abortar com erro, a falha é
registada no report e o orquestrador avança para o lote seguinte, de forma
sequencial. O destino recebe entregas incrementais: após cada lote bem
sucedido, os seus registos ficam publicados.
"""

import datetime as dt
import subprocess
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extractors import get_extractor

from extract.run_pipeline import (
    REPO_ROOT,
    cmd_export,
    cmd_load,
    connect,
    load_config,
    raw_name,
)


def _run_dbt(cfg: dict, db_path: str) -> None:
    """[2] Transform — dbt build (staging -> marts) sobre o raw do lote atual.
    Só constrói os marts da config (+ pais) — raw de outras migrações não existe."""
    marts = sorted({t.get("mart") or raw_name(t) for t in cfg["tables"]})
    import os
    env = {**os.environ, "DBT_DUCKDB_PATH": db_path}
    r = subprocess.run(
        ["dbt", "build", "--project-dir", "dbt", "--profiles-dir", "dbt",
         "--target", "dev", "--select", " ".join("+" + m for m in marts)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False, env=env,
    )
    if r.returncode != 0:
        tail = "\n".join((r.stdout or "").splitlines()[-12:])
        raise RuntimeError(f"dbt build falhou:\n{tail}")


def _validate_ge(checkpoint: str = "d1_pipeline_checkpoint") -> int:
    """[3] Validate — Great Expectations sobre o parquet exportado (gate)."""
    import great_expectations as gx
    ctx = gx.get_context(context_root_dir=str(REPO_ROOT / "great_expectations"))
    result = ctx.run_checkpoint(checkpoint)
    if not result.success:
        raise RuntimeError("gate de qualidade GE falhou — lote NÃO é carregado")
    return 1  # checkpoint executado


def _extract_batch_slice(con, cfg: dict, batch_no: int, slices: dict) -> None:
    """[1] Extract — escreve o slice do lote atual no schema raw (com _batch_id)."""
    import pandas as pd
    for table in cfg["tables"]:
        key = raw_name(table)
        df = slices.get(key)
        if df is None:
            continue
        out = df.copy()
        out["_batch_id"] = batch_no
        con.register("src_df", pd.DataFrame(out))
        con.execute(f"CREATE OR REPLACE TABLE raw.{key} AS SELECT * FROM src_df")
        con.unregister("src_df")
        print(f"[batch {batch_no}] extract {key}: {len(out)} linhas -> raw.{key}")


def _destination_totals(cfg: dict) -> dict:
    """Contagens cumulativas no destino (para o sumário do batch-run)."""
    import duckdb
    dest = cfg.get("destination", {})
    if dest.get("type") != "duckdb":
        return {}
    try:
        con = duckdb.connect(dest.get("path", "destination.duckdb"), read_only=True)
    except duckdb.Error:
        return {}
    totals = {}
    for t in cfg["tables"]:
        name = t.get("destination_table")
        if not name:
            continue
        try:
            totals[name] = con.execute(
                f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        except duckdb.Error:
            totals[name] = None
    con.close()
    return totals


def run_batches(cfg: dict, db_path: str, batch_size: int,
                checkpoint: str = "d1_pipeline_checkpoint") -> dict:
    """Executa a migração completa em lotes sequenciais de `batch_size` registos."""
    # estado por tabela: cursor + done
    state = {raw_name(t): {"cursor": None, "done": False} for t in cfg["tables"]}

    # plano: total conhecido? -> n.º de lotes previstos
    plan = {}
    for t in cfg["tables"]:
        try:
            total = get_extractor(t["source"]).count(t["source"])
        except (OSError, ValueError, KeyError):
            total = None  # total é apenas informativo — não trava o run
        plan[raw_name(t)] = total
    known = {k: v for k, v in plan.items() if v is not None}
    if known:
        nb = {k: -(-v // batch_size) for k, v in known.items()}
        print(f"[batch-run] plano: {known} -> lotes previstos: {nb} (batch_size={batch_size})")
    else:
        print(f"[batch-run] total desconhecido na origem; extração até esgotar (batch_size={batch_size})")

    results = []
    batch_no = 0
    while not all(st["done"] for st in state.values()):
        batch_no += 1
        # apanhar o slice deste lote para cada tabela ainda ativa
        slices, batch_src_rows = {}, {}
        for t in cfg["tables"]:
            key, st = raw_name(t), state[raw_name(t)]
            if st["done"]:
                continue
            try:
                df, next_cursor = get_extractor(t["source"]).fetch_batch(
                    t["source"], batch_size, st["cursor"])
            except Exception as e:  # noqa: BLE001 — regra: falha registada, lote seguinte
                print(f"[batch {batch_no}] FALHOU (extract {key}): {e} — registo no report")
                results.append({
                    "batch": batch_no, "table": key, "status": "failed",
                    "error": f"extract: {e}", "rows": 0,
                })
                st["done"] = True  # origem indisponível — não travar os restantes
                continue
            if len(df) == 0:
                st["done"] = True
                continue
            slices[key] = df
            batch_src_rows[key] = len(df)
            st["cursor"] = next_cursor
            if next_cursor is None:
                st["done"] = True
        if not slices:
            break

        # ---- pipeline COMPLETO para este lote ----
        try:
            con = connect(db_path)
            _extract_batch_slice(con, cfg, batch_no, slices)
            con.close()
            _run_dbt(cfg, db_path)                          # [2] transform
            cmd_export(cfg, db_path)                     # [2.5] artefacto
            _validate_ge(checkpoint)                        # [3] gate
            loaded = cmd_load(cfg, db_path)               # [4] load incremental
            rows_loaded = sum(
                v for k, v in loaded.items()
                if Path(k).name.endswith(".parquet")
            )
            print(f"[batch {batch_no}] OK: {batch_src_rows} extraídos, "
                  f"{rows_loaded} linhas NOVAS no destino")
            results.append({
                "batch": batch_no, "status": "ok",
                "rows": batch_src_rows, "loaded": rows_loaded,
            })
        except Exception as e:  # noqa: BLE001 — regra: falha registada, lote seguinte
            tb = traceback.format_exc(limit=3)
            print(f"[batch {batch_no}] FALHOU: {e} — registo no report; "
                  f"avança para o lote seguinte")
            results.append({
                "batch": batch_no, "status": "failed",
                "rows": batch_src_rows,
                "error": str(e)[:500], "trace": tb[-500:],
            })

    return _batch_report(cfg, db_path, batch_size, results, plan)


def _batch_report(cfg, db_path, batch_size, results, plan) -> dict:
    """[5] Report — registo auditável do batch-run (docs/executions/)."""
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%d_%H%M")
    src_label = cfg["tables"][0]["source"].get("type", "origem")
    dst_label = cfg.get("destination", {}).get("type", "destino")

    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] == "failed"]
    totals = _destination_totals(cfg)
    rows_delivered = sum(r.get("loaded", 0) for r in ok)

    lines = [
        f"# Batch-run {stamp} — {src_label} → {dst_label} (batch_size={batch_size})",
        "",
        f"- **Data:** {now.isoformat(timespec='seconds')}",
        f"- **Lotes:** {len(results)} executados | ✅ {len(ok)} | ❌ {len(failed)}",
        f"- **Linhas entregues no destino (novas):** {rows_delivered}",
        f"- **Contagem cumulativa no destino:** {totals}",
        f"- **Plano previsto:** {plan}",
        "",
        "| Lote | Estado | Linhas (raw) | Novas no destino | Erro |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        err_txt = (r.get("error") or "").replace("|", "/")
        err = err_txt.splitlines()[0][:120] if err_txt else ""
        lines.append(
            f"| {r['batch']} | {'✅' if r['status'] == 'ok' else '❌'} "
            f"| {r.get('rows', 0)} | {r.get('loaded', '—')} | {err or '—'} |")
    for r in failed:
        if r.get("trace"):
            lines += ["", f"<details><summary>Erro do lote {r['batch']}</summary>",
                      "", "```", r["trace"], "```", "</details>"]
    lines += ["",
              ("*Cada lote percorreu o pipeline completo "
               "(extract → dbt → Great Expectations → load → report).*"),
              ("*Lote falhado: registado e seguiu-se o lote seguinte — "
               "o destino só recebe lotes validados.*")]

    out = REPO_ROOT / "docs" / "executions" / f"{stamp}_{src_label}-para-{dst_label}_batch-run.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    index = REPO_ROOT / "docs" / "executions" / "EXECUTIONS.md"
    with open(index, "a", encoding="utf-8") as fh:
        for r in results:
            fh.write(
                f"| {stamp} b{r['batch']:02d} | {src_label} → {dst_label} "
                f"| {r.get('rows', 0)} | "
                f"{'✅ +' + str(r['loaded']) if r['status'] == 'ok' else '❌ ' + (r.get('error', '') or '')[:60]} |\n")
        fh.write(
            f"| {stamp} SUM | {src_label} → {dst_label} (batch {batch_size}) "
            f"| {len(results)} lotes | ✅ {rows_delivered} novas | cumulativo: {totals} |\n")

    summary = {
        "batches_total": len(results),
        "batches_ok": len(ok),
        "batches_failed": len(failed),
        "rows_delivered": rows_delivered,
        "destination_totals": totals,
        "report": str(out),
    }
    print(f"[report] {out}")
    print(f"[batch-run] CONCLUÍDO: {len(ok)}/{len(results)} lotes OK, "
          f"{rows_delivered} linhas novas no destino, cumulativo {totals}")
    return summary


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="ETL_Agent batch-run")
    ap.add_argument("--config", required=True)
    ap.add_argument("--db", default="etl_agent.duckdb")
    ap.add_argument("--batch-size", type=int, default=50,
                    help="máx. de registos por lote (predefinição: 50)")
    ap.add_argument("--checkpoint", default="d1_pipeline_checkpoint",
                    help="checkpoint Great Expectations (gate de qualidade)")
    args = ap.parse_args()
    cfg = load_config(args.config)
    summary = run_batches(cfg, args.db, args.batch_size, args.checkpoint)
    if summary["batches_failed"]:
        sys.exit(2)  # há falhas registadas — sinaliza sem abortar os lotes restantes
    sys.exit(0)


if __name__ == "__main__":
    main()
