"""Extractor CSV — leitura local (útil para testes e importações em lote)."""

import pandas as pd

from .base import BaseExtractor


class CsvExtractor(BaseExtractor):
    name = "csv"

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        path = source_cfg.get("path")
        if not path:
            raise ValueError("'path' do CSV em falta no bloco 'source'")
        return pd.read_csv(path)

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        path = source_cfg.get("path")
        if not path:
            raise ValueError("'path' do CSV em falta no bloco 'source'")
        start = int(cursor or 0)
        # linha 0 é o header; saltamos 1..start (inclusive)
        batch = pd.read_csv(
            path,
            skiprows=lambda r: 1 <= r <= start,
            nrows=batch_size,
        )
        if len(batch) == 0:
            return batch, None
        next_cursor = start + len(batch)
        exhausted = len(batch) < batch_size
        return batch, (None if exhausted else next_cursor)

    def count(self, source_cfg: dict) -> int | None:
        path = source_cfg.get("path")
        if not path:
            return None
        with open(path, encoding="utf-8") as fh:
            return sum(1 for _ in fh) - 1
