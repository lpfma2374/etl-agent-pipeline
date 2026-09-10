"""Loader DuckDB — publica marts noutro ficheiro/base DuckDB (testes e backup).

Modo incremental: com `primary_key` definido na config da tabela, cada lote
faz INSERT com anti-join contra o destino (registos já entregues são
ignorados) — as entregas são incrementais e idempotentes. Sem `primary_key`,
anexa tudo.
"""

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
        pk = table_cfg.get("primary_key")
        if pk and pk not in df.columns:
            raise ValueError(f"primary_key '{pk}' não existe nos dados")

        if pk:
            df = df.drop_duplicates(subset=[pk], keep="last")

        con = duckdb.connect(self.path)
        exists = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
            [dest_table],
        ).fetchone()[0]

        before = con.execute(
            f'SELECT COUNT(*) FROM "{dest_table}"').fetchone()[0] if exists else 0
        con.register("batch_df", df)

        if not exists:
            con.execute(f'CREATE TABLE "{dest_table}" AS SELECT * FROM batch_df')
        elif pk:
            con.execute(
                f'INSERT INTO "{dest_table}" '
                f'SELECT b.* FROM batch_df b '
                f'WHERE NOT EXISTS ('
                f'SELECT 1 FROM "{dest_table}" t WHERE t."{pk}" = b."{pk}")'
            )
        else:
            con.execute(f'INSERT INTO "{dest_table}" SELECT * FROM batch_df')

        after = con.execute(f'SELECT COUNT(*) FROM "{dest_table}"').fetchone()[0]
        con.unregister("batch_df")
        con.close()
        return after - before  # linhas NOVAS entregues por este lote
