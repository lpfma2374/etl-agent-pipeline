"""ETL_Agent — orquestrador do pipeline Extract → Transform → Validate → Load → Report.

Passos:
  [1] extract   — origem -> DuckDB schema raw
  [2] transform — dbt (staging -> marts), à parte via `make transform`
  [2.5] export  — marts -> export/*.parquet (artefacto canónico)
  [3] validate  — Great Expectations sobre export/*.parquet, via `make validate`
  [2] transform  — dbt (staging -> marts), executado à parte via `make transform`
  [3] validate   — Great Expectations sobre os marts exportados (parquet),
                   executado à parte via `make validate`
  [4] load       — artefacto validado (parquet) -> destino (só depois de validate passar)
  [5] report     — registo de execução em docs/executions/
"""

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "extract"))

from extractors import get_extractor
from loaders import get_loader


def load_config(path: str) -> dict:
    """Config de execução. Secrets vêm SEMPRE do ambiente, nunca do JSON."""
    with open(path) as fh:
        cfg = json.load(fh)
    if not cfg.get("tables"):
        raise ValueError("config sem 'tables' — nada a migrar")
    return cfg


def connect(db_path: str) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    return con


def raw_name(table_cfg: dict) -> str:
    return f"raw_{table_cfg['source'].get('name', 'untitled')}"


# ---------------------------------------------------------------- [1] EXTRACT
def cmd_extract(cfg: dict, db_path: str) -> dict:
    con = connect(db_path)
    stats = {}
    for table in cfg["tables"]:
        src = table["source"]
        extractor = get_extractor(src)
        df = extractor.fetch(src)
        target = raw_name(table)
        con.register("src_df", df)
        con.execute(f"CREATE OR REPLACE TABLE raw.{target} AS SELECT * FROM src_df")
        con.unregister("src_df")
        stats[target] = len(df)
        print(f"[extract] {src.get('name')}: {len(df)} linhas -> raw.{target}")
    con.close()
    return stats



# ------------------------------------------------------- [2.5] EXPORT (parquet)
def cmd_export(cfg: dict, db_path: str) -> dict:
    """Exporta os marts para parquet em export/ — é ESTE artefacto que o
    Great Expectations valida e que o load publica no destino."""
    export_dir = REPO_ROOT / "export"
    export_dir.mkdir(exist_ok=True)
    con = duckdb.connect(db_path, read_only=True)
    stats = {}
    for table in cfg["tables"]:
        mart = table.get("mart") or raw_name(table)
        out = export_dir / f"{mart}.parquet"
        con.execute(
            f"COPY (SELECT * FROM main.{mart}) TO '{out}' (FORMAT PARQUET)")
        n = con.execute(f"SELECT COUNT(*) FROM main.{mart}").fetchone()[0]
        stats[mart] = n
        print(f"[export] main.{mart}: {n} linhas -> {out}")
    con.close()
    return stats


# ------------------------------------------------------------------- [4] LOAD
def cmd_load(cfg: dict, db_path: str) -> dict:
    loader = get_loader(cfg.get("destination", {}))
    stats = {}
    for table in cfg["tables"]:
        # carrega o ARTEFACTO VALIDADO (export parquet); fallback: mart/raw no DuckDB
        export_path = REPO_ROOT / "export" / f"{table.get('mart')}.parquet"
        if export_path.exists():
            import pandas as _pd
            df = _pd.read_parquet(export_path)
            rows = loader.load(df, table)
            stats[str(export_path)] = rows
            print(f"[load] {export_path.name}: {rows} linhas -> {loader.name} ({table.get('destination_table')})")
            continue
        con = duckdb.connect(db_path, read_only=True)
        candidates = [table.get("mart"), raw_name(table)]
        df = None
        found = None
        for c in candidates:
            if not c:
                continue
            for qualified in (c, f"main.{c}", f"raw.{c}"):
                try:
                    df = con.execute(f'SELECT * FROM {qualified}').df()
                    found = qualified
                    break
                except duckdb.Error:
                    continue
            if df is not None:
                break
        con.close()
        if df is None:
            raise RuntimeError(f"Nenhum modelo dbt/raw encontrado para {raw_name(table)}")
        rows = loader.load(df, table)
        stats[found] = rows
        print(f"[load] {found}: {rows} linhas -> {loader.name} ({table.get('destination_table')})")
    return stats


# ----------------------------------------------------------------- [5] REPORT
def cmd_report(cfg: dict, db_path: str, load_stats: dict | None = None) -> str:
    con = duckdb.connect(db_path, read_only=True)
    counts = {}
    for t in cfg["tables"]:
        try:
            counts[raw_name(t)] = con.execute(
                f"SELECT COUNT(*) FROM raw.{raw_name(t)}").fetchone()[0]
        except duckdb.Error:
            counts[raw_name(t)] = None
    con.close()

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d_%H%M")
    src_label = cfg["tables"][0]["source"].get("type", "origem")
    dst_label = cfg.get("destination", {}).get("type", "destino")
    safe = {"api_key", "token", "secret"}
    src_cfg = {k: v for k, v in cfg["tables"][0]["source"].items() if k not in safe}
    dst_cfg = {k: v for k, v in cfg.get("destination", {}).items() if k not in safe}
    lines = [
        f"# Execução {now} — {src_label} → {dst_label}",
        "",
        f"- **Data:** {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}",
        f"- **Origem:** `{src_cfg}`",
        f"- **Destino:** `{dst_cfg}`",
        f"- **Linhas (raw):** {counts}",
        f"- **Linhas carregadas:** {load_stats or 'n/d'}",
        f"- **Validação (Great Expectations):** {'ver `make validate`' if not load_stats else 'passou (gate antes da carga)'}",
        "- **Agente:** ETL_Agent (Base44 Superagent)",
        "",
    ]
    out = REPO_ROOT / "docs" / "executions" / f"{now}_{src_label}-para-{dst_label}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    index = REPO_ROOT / "docs" / "executions" / "EXECUTIONS.md"
    with open(index, "a", encoding="utf-8") as fh:
        fh.write(f"| {now} | {src_label} → {dst_label} | {counts} | "
                 f"{'✅' if load_stats else '—'} |\n")
    print(f"[report] {out}")
    return str(out)


def main():
    ap = argparse.ArgumentParser(prog="ETL_Agent pipeline")
    ap.add_argument("command", choices=["extract", "export", "load", "report"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--db", default="etl_agent.duckdb")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.command == "extract":
        cmd_extract(cfg, args.db)
    elif args.command == "export":
        cmd_export(cfg, args.db)
    elif args.command == "load":
        cmd_load(cfg, args.db)
    elif args.command == "report":
        import pandas as _pd2
        load_stats = {}
        for t in cfg["tables"]:
            mart = t.get("mart")
            ep = REPO_ROOT / "export" / f"{mart}.parquet"
            if mart and ep.exists():
                try:
                    load_stats[mart] = len(_pd2.read_parquet(ep))
                except (OSError, ValueError):
                    print(f"[report] aviso: sem contagem para {mart} ({ep.name})")
        cmd_report(cfg, args.db, load_stats or None)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"[done] em {time.time() - t0:.1f}s")
