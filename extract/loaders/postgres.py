"""Loader PostgreSQL (ex.: Neon) — upsert idempotente por chave primária.

- Ligação via DSN em variável de ambiente (default NEON_DATABASE_URL).
- Cria a tabela se não existir (identifiers SEMPRE quoted — nomes com
  espaços/acentos, ex. "Questões-Chave").
- Upsert: INSERT ... ON CONFLICT ("pk") DO UPDATE — re-execuções não
  duplicam.
- Lotes de `batch_rows` linhas (default 50 — regra ETL_Agent: entregas
  pequenas) via executemany, uma transação por tabela.
- Suporta 'unique' (lista de listas de colunas) no table_cfg para
  constraints UNIQUE compostas.
- NOTA: FKs NÃO são criadas aqui de propósito — o batch-run carrega por
  lotes e um lote filho pode referenciar linhas do pai carregadas num
  lote posterior; as FKs são adicionadas pós-migração (ver
  extract/add_fks_neon.py).
"""

import os

import pandas as pd
import psycopg2

from .base import BaseLoader


class PostgresLoader(BaseLoader):
    name = "postgres"

    def __init__(self, dest_cfg: dict):
        self.dest_cfg = dest_cfg or {}
        self.batch_rows = int(self.dest_cfg.get("batch_rows", 50))

    def _connect(self):
        dsn_env = self.dest_cfg.get("dsn_env", "NEON_DATABASE_URL")
        dsn = os.environ.get(dsn_env)
        if not dsn:
            raise ValueError(f"{dsn_env} em falta (variável de ambiente)")
        return psycopg2.connect(dsn)

    @staticmethod
    def _sql_type(dtype) -> str:
        # .kind é robusto a dtypes exóticos (numpy 2.x, ArrowDtype)
        if isinstance(dtype, pd.ArrowDtype):
            dtype = dtype.numpy_dtype
        kind = getattr(dtype, "kind", "O")  # i/u=int, f=float, b=bool
        if kind in ("i", "u"):
            return "BIGINT"
        if kind == "f":
            return "DOUBLE PRECISION"
        if kind == "b":
            return "BOOLEAN"
        return "TEXT"

    def _ddl(self, df: pd.DataFrame, table_cfg: dict) -> str:
        table = table_cfg["destination_table"]
        pk = table_cfg.get("primary_key", "id")
        columns = list(df.columns)
        defs = [f'"{c}" {self._sql_type(df[c].dtype)}' for c in columns]
        defs.append(f'PRIMARY KEY ("{pk}")')
        for cols in table_cfg.get("unique", []):
            defs.append('UNIQUE (' + ", ".join(f'"{c}"' for c in cols) + ")")
        return f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(defs)})'

    @staticmethod
    def _plain(v):
        if hasattr(v, "item"):  # scalars numpy -> nativos
            v = v.item()
        if v is None:
            return None
        try:
            if pd.isna(v):
                return None
        except (TypeError, ValueError):
            pass
        return v

    def load(self, df: pd.DataFrame, table_cfg: dict) -> int:
        dest_table = table_cfg.get("destination_table")
        if not dest_table:
            raise ValueError("'destination_table' em falta no bloco da tabela")
        primary_key = table_cfg.get("primary_key", "id")
        columns = list(df.columns)

        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(self._ddl(df, table_cfg))
                conn.commit()

                cols_sql = ", ".join(f'"{c}"' for c in columns)
                ph = "(" + ", ".join(["%s"] * len(columns)) + ")"
                sql = (
                    f'INSERT INTO "{dest_table}" ({cols_sql}) VALUES {ph} '
                    f'ON CONFLICT ("{primary_key}") DO UPDATE SET '
                    + ", ".join(f'"{c}" = EXCLUDED."{c}"'
                                for c in columns if c != primary_key)
                )
                loaded = 0
                for start in range(0, len(df), self.batch_rows):
                    batch = df.iloc[start:start + self.batch_rows]
                    rows = [tuple(self._plain(v) for v in row)
                            for row in batch.itertuples(index=False, name=None)]
                    cur.executemany(sql, rows)
                    loaded += cur.rowcount if cur.rowcount != -1 else len(rows)
                    conn.commit()  # uma transação por lote (entregas incrementais)
            return loaded
        finally:
            conn.close()
