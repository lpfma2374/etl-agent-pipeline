"""Extractor staging DuckDB — lê a tabela staging.raw_data do wizard 'Novo ETL'.

source_cfg: {"type": "duckdb_staging", "path": "...", "table": "stg.raw_data"}
Lotes via OFFSET/LIMIT, ordem estável por _row_id (fallback: rowid).
"""

import duckdb
import pandas as pd

from .base import BaseExtractor


class DuckDBStagingExtractor(BaseExtractor):
    name = "duckdb_staging"

    @staticmethod
    def _qual(table: str) -> str:
        sch, _, tbl = table.partition(".")
        return f'"{sch}"."{tbl}"'

    def _order(self, con, table: str) -> str:
        cols = {r[0] for r in con.execute(
            f"SELECT column_name FROM information_schema.columns "
            f"WHERE table_name = '{table.split('.')[-1]}'").fetchall()}
        return "_row_id" if "_row_id" in cols else "rowid"

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        path = source_cfg.get("path")
        table = source_cfg.get("table", "stg.raw_data")
        if not path:
            raise ValueError("'path' do DuckDB em falta no bloco 'source'")
        con = duckdb.connect(path, read_only=True)
        try:
            return con.execute(f'SELECT * FROM {self._qual(table)}').fetchdf()
        finally:
            con.close()

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        path = source_cfg.get("path")
        table = source_cfg.get("table", "stg.raw_data")
        if not path:
            raise ValueError("'path' do DuckDB em falta no bloco 'source'")
        con = duckdb.connect(path, read_only=True)
        try:
            order = self._order(con, table)
            start = int(cursor or 0)
            batch = con.execute(
                f'SELECT * FROM {self._qual(table)} ORDER BY {order} '
                f"LIMIT {int(batch_size)} OFFSET {start}").fetchdf()
            if len(batch) == 0:
                return batch, None
            next_cursor = start + len(batch)
            total = con.execute(f'SELECT COUNT(*) FROM {self._qual(table)}').fetchone()[0]
            return batch, (None if next_cursor >= total else next_cursor)
        finally:
            con.close()

    def count(self, source_cfg: dict) -> int | None:
        path = source_cfg.get("path")
        table = source_cfg.get("table", "stg.raw_data")
        if not path:
            return None
        con = duckdb.connect(path, read_only=True)
        try:
            return con.execute(f'SELECT COUNT(*) FROM {self._qual(table)}').fetchone()[0]
        finally:
            con.close()
