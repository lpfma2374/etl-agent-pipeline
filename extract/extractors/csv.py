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
