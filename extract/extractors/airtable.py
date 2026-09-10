"""Extractor Airtable — lê uma tabela de uma base via API REST (paginado).

Extração por lotes: cada `fetch_batch` faz UM pedido à API com
`pageSize = batch_size` (máx. 100 imposto pela API). O cursor é o token
opaco `offset` devolvido pela própria Airtable.
"""

import json
import os
import time

import pandas as pd
import requests

from .base import BaseExtractor


class AirtableExtractor(BaseExtractor):
    name = "airtable"
    BASE_URL = "https://api.airtable.com/v0"
    MAX_PAGE = 100  # limite da API Airtable

    @staticmethod
    def _to_df(records: list) -> pd.DataFrame:
        df = pd.DataFrame(records)
        if df.empty:
            return df
        # campos de listas/dict -> JSON string para caber num RDBMS
        for col in df.columns:
            if df[col].apply(lambda v: isinstance(v, (list, dict))).any():
                df[col] = df[col].apply(lambda v: json.dumps(v, default=str))
        return df

    def _request_page(self, source_cfg: dict, page_size: int, cursor=None):
        api_key = os.environ.get("AIRTABLE_API_KEY")
        base_id = source_cfg.get("base_id")
        table = source_cfg.get("table")
        if not api_key:
            raise ValueError("AIRTABLE_API_KEY em falta (variável de ambiente)")
        if not base_id or not table:
            raise ValueError("base_id e table são obrigatórios no bloco 'source'")
        params = {"pageSize": min(page_size, self.MAX_PAGE)}
        if cursor:
            params["offset"] = cursor
        resp = requests.get(
            f"{self.BASE_URL}/{base_id}/{table}",
            headers={"Authorization": f"Bearer {api_key}"},
            params=params, timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return ([r["fields"] for r in data.get("records", [])],
                data.get("offset"))

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        """Extração completa (todos os lotes) — usada fora do modo batch."""
        records, cursor = [], None
        while True:
            page, cursor = self._request_page(source_cfg, self.MAX_PAGE, cursor)
            records.extend(page)
            if not cursor:
                break
            time.sleep(0.25)  # respeita rate limit (5 req/s)
        return self._to_df(records)

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        page, next_cursor = self._request_page(source_cfg, batch_size, cursor)
        return self._to_df(page), next_cursor
