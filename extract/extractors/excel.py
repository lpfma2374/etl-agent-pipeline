"""Extractor Excel (.xlsx/.xls) — leitura em lotes para o wizard Novo ETL.

Lê a primeira folha. Suporta `positional_pk` como o CsvExtractor:
PK posicional 1..n global, contínua entre lotes.
"""

import pandas as pd

from .base import BaseExtractor


class ExcelExtractor(BaseExtractor):
    name = "excel"

    @staticmethod
    def _with_pk(df: pd.DataFrame, pk: str | None, start: int) -> pd.DataFrame:
        if pk:
            df = df.copy()
            df.insert(0, pk, range(start + 1, start + 1 + len(df)))
        return df

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        path = source_cfg.get("path")
        if not path:
            raise ValueError("'path' do Excel em falta no bloco 'source'")
        df = pd.read_excel(path, sheet_name=source_cfg.get("sheet", 0))
        return self._with_pk(df, source_cfg.get("positional_pk"), 0)

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        path = source_cfg.get("path")
        if not path:
            raise ValueError("'path' do Excel em falta no bloco 'source'")
        full = pd.read_excel(path, sheet_name=source_cfg.get("sheet", 0))
        start = int(cursor or 0)
        batch = full.iloc[start:start + batch_size]
        if len(batch) == 0:
            return batch, None
        batch = self._with_pk(batch, source_cfg.get("positional_pk"), start)
        next_cursor = start + len(batch)
        exhausted = next_cursor >= len(full)
        return batch, (None if exhausted else next_cursor)

    def count(self, source_cfg: dict) -> int | None:
        path = source_cfg.get("path")
        if not path:
            return None
        return len(pd.read_excel(path, sheet_name=source_cfg.get("sheet", 0)))
