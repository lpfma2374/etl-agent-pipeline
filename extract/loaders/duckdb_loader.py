"""Loader DuckDB — escreve marts para outro ficheiro/base DuckDB (testes e backup)."""

import duckdb

from .base import BaseLoader


class DuckDbLoader(BaseLoader):
    name = "duckdb"

    def __init__(self, dest_cfg: dict):
        self.path = (dest_cfg or {}).get("path", "destination.duckdb")

    def load(self, df, table_cfg: dict) -> int:
        dest_table = table_cfg.get("destination_table")
        if not dest_table:
            raise ValueError("'destination_table' em falta no bloco da tabela")
        con = duckdb.connect(self.path)
        con.register("batch_df", df)
        con.execute(f'CREATE OR REPLACE TABLE "{dest_table}" AS SELECT * FROM batch_df')
        con.unregister("batch_df")
        con.close()
        return len(df)
