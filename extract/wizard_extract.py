"""Wizard 'Novo ETL' — fase EXTRACT: origem → staging DuckDB + preview JSON.

Uso:
  python3 extract/wizard_extract.py --input <ficheiro> --origin csv|xlsx|gsheets \
      --request-id <id> [--url <sheet_url>] [--workdir wizard/<id>] [--sheet <nome>]

Produz no workdir:
  staging.duckdb          — tabela stg.raw_data com TODAS as linhas
  preview.json            — {columns:[{name,dtype}], row_count, sample:[…50 linhas]}

A tabela de staging é a origem da fase TRANSFORM (run_batches.py lê daqui
por lotes de 50 — regra fixa do owner).
"""

import argparse
import json
import os
import sys
import time

import duckdb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.extractors.csv import CsvExtractor

EXCEL_OK = True
try:
    from extract.extractors.excel import ExcelExtractor
except ImportError:
    EXCEL_OK = False
from extract.extractors.gsheets import GoogleSheetsExtractor

EXTRACTORS = {"csv": CsvExtractor, "gsheets": GoogleSheetsExtractor}
if EXCEL_OK:
    EXTRACTORS["xlsx"] = ExcelExtractor
    EXTRACTORS["xls"] = ExcelExtractor


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="caminho do ficheiro local (csv/xlsx/xls)")
    ap.add_argument("--origin", required=True, choices=["csv", "xlsx", "xls", "gsheets"])
    ap.add_argument("--request-id", required=True)
    ap.add_argument("--url", default="", help="URL do Google Sheets (origin=gsheets)")
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--sheet", default=0)
    args = ap.parse_args()

    workdir = args.workdir or os.path.join("wizard", args.request_id)
    os.makedirs(workdir, exist_ok=True)

    t0 = time.time()
    source_cfg = {"path": args.input, "url": args.url, "sheet": args.sheet}
    ext_cls = EXTRACTORS[args.origin]
    if args.origin == "gsheets" and not args.url:
        print("ERRO: --url obrigatório para origin=gsheets", file=sys.stderr)
        return 2
    ext = ext_cls()

    df = ext.fetch(source_cfg)
    df.columns = [str(c).strip().replace(".", "_").replace(" ", "_") for c in df.columns]
    df.insert(0, "_row_id", range(1, len(df) + 1))  # ordem estável + PK de upsert

    con = duckdb.connect(os.path.join(workdir, "staging.duckdb"))
    con.execute("CREATE SCHEMA IF NOT EXISTS stg")
    con.execute("DROP TABLE IF EXISTS stg.raw_data")
    con.register("df_view", df)
    con.execute("CREATE TABLE stg.raw_data AS SELECT * FROM df_view")
    con.unregister("df_view")
    count = con.execute("SELECT COUNT(*) FROM stg.raw_data").fetchone()[0]
    con.close()

    sample = json.loads(df.head(50).to_json(orient="records", force_ascii=False))
    cols_info = [
        {"name": c, "dtype": str(df[c].dtype)}
        for c in df.columns
    ]
    preview = {
        "columns": cols_info,
        "row_count": int(count),
        "sample": sample,
    }
    with open(os.path.join(workdir, "preview.json"), "w", encoding="utf-8") as fh:
        json.dump(preview, fh, ensure_ascii=False)

    print(json.dumps({
        "ok": True,
        "rows": int(count),
        "columns": len(df.columns),
        "workdir": workdir,
        "seconds": round(time.time() - t0, 1),
        "preview": os.path.join(workdir, "preview.json"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
