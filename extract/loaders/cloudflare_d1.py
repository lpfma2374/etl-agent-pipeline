"""Loader Cloudflare D1 — carrega via HTTP API (query endpoint), em batches."""

import os
import time

import pandas as pd
import requests

from .base import BaseLoader


class CloudflareD1Loader(BaseLoader):
    name = "cloudflare_d1"
    BASE_URL = "https://api.cloudflare.com/client/v4"
    MAX_PARAMS = 100  # limite prático de bind params por statement na D1

    def __init__(self, dest_cfg: dict):
        self.dest_cfg = dest_cfg or {}

    def _api(self, method: str, endpoint: str, **kw):
        token = os.environ.get("CF_API_TOKEN")
        if not token:
            raise ValueError("CF_API_TOKEN em falta (variável de ambiente)")
        account = self.dest_cfg.get("account_id") or os.environ.get("CF_ACCOUNT_ID")
        db = self.dest_cfg.get("database_id") or os.environ.get("CF_DATABASE_ID")
        if not account or not db:
            raise ValueError("account_id / database_id em falta (config ou env)")
        resp = requests.request(
            method, f"{self.BASE_URL}/accounts/{account}/d1/database/{db}/{endpoint}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=120, **kw,
        )
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success"):
            raise RuntimeError(f"D1 API erro: {body.get('errors')}")
        return body

    def load(self, df: pd.DataFrame, table_cfg: dict) -> int:
        dest_table = table_cfg.get("destination_table")
        if not dest_table:
            raise ValueError("'destination_table' em falta no bloco da tabela")
        primary_key = table_cfg.get("primary_key", "id")
        columns = list(df.columns)
        rows_per_batch = max(self.MAX_PARAMS // max(len(columns), 1), 1)

        # 1. criar a tabela se não existir (mapeamento de tipos pandas -> SQL)
        self._api("POST", "query", json={"sql": self._build_ddl(dest_table, df, columns, primary_key)})

        # 2. upsert em batches (idempotente: reexecuções não duplicam)
        loaded = 0
        for start in range(0, len(df), rows_per_batch):
            batch = df.iloc[start:start + rows_per_batch]
            if batch.empty:
                break
            row_ph = "(" + ", ".join(["?"] * len(columns)) + ")"
            cols_sql = ", ".join(f'"{c}"' for c in columns)
            sql = (
                f'INSERT INTO "{dest_table}" ({cols_sql}) VALUES '
                + ", ".join([row_ph] * len(batch))
                + f' ON CONFLICT("{primary_key}") DO UPDATE SET '
                + ", ".join(f'"{c}" = excluded."{c}"' for c in columns if c != primary_key)
            )
            # NOTA D1: params TIPADOS ({"type": ...}) sobre tabelas com
            # PRIMARY KEY devolvem SQLITE_MISMATCH (bug da API D1). Os params
            # SIMPLES (valores nulos) preservam os tipos corretamente.
            def plain(v):
                # .tolist() de Series mista devolve scalars numpy
                # (np.int32/np.float64); normalizar para nativos
                if hasattr(v, "item"):
                    v = v.item()
                if v is None or (not isinstance(v, str) and pd.isna(v)):
                    return None
                return v
            params = [plain(v) for _, row in batch.iterrows() for v in row.tolist()]
            self._api("POST", "query", json={"sql": sql, "params": params})
            loaded += len(batch)
            time.sleep(0.5)  # rate limit da D1 API
        return loaded

    @staticmethod
    def _build_ddl(table: str, df: pd.DataFrame, columns: list[str], primary_key: str) -> str:
        def sql_type(dtype):
            # dtypes de origens variadas (pyarrow ArrowDtype, numpy 2.x
            # Int32DType) não são reconhecidos por pd.api.types.* — usar .kind
            if isinstance(dtype, pd.ArrowDtype):
                dtype = dtype.numpy_dtype
            kind = getattr(dtype, "kind", "O")  # i/u=int, f=float, b=bool
            if kind in ("i", "u"):
                return "INTEGER"
            if kind == "f":
                return "REAL"
            if kind == "b":
                return "BOOLEAN"
            return "TEXT"

        pk = primary_key if primary_key in columns else (columns[0] if columns else "id")
        defs = [f'"{c}" {sql_type(df[c].dtype)}' for c in columns]
        defs.append(f'PRIMARY KEY ("{pk}")')
        return f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(defs)})'
