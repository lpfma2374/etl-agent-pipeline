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
        # 'fields' opcional: subconjunto explícito de colunas (útil para
        # excluir campos link/lookup/attachment e manter o espelho limpo)
        params = [("pageSize", min(page_size, self.MAX_PAGE))]
        if cursor:
            params.append(("offset", cursor))
        for f in source_cfg.get("fields") or []:
            params.append(("fields[]", f))
        resp = requests.get(
            f"{self.BASE_URL}/{base_id}/{table}",
            headers={"Authorization": f"Bearer {api_key}"},
            params=params, timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        records = [
            {"_airtable_id": r["id"],
             "_airtable_created": r.get("createdTime"),
             **r["fields"]}
            for r in data.get("records", [])
        ]
        return (records, data.get("offset"))

    def schema(self, source_cfg: dict) -> list | None:
        """Nomes dos campos da tabela via metadata API (None se o token não
        tiver permissão de schema). O Airtable só devolve campos POPULADOS
        nos registos — com o schema garantimos colunas em falta como NULL."""
        api_key = os.environ.get("AIRTABLE_API_KEY")
        base_id, table_id = source_cfg.get("base_id"), source_cfg.get("table")
        if not api_key or not base_id:
            return None
        if source_cfg.get("fields"):
            return list(source_cfg["fields"])
        try:
            resp = requests.get(
                f"{self.BASE_URL}/meta/bases/{base_id}/tables",
                headers={"Authorization": f"Bearer {api_key}"}, timeout=60,
            )
            resp.raise_for_status()
            for t in resp.json().get("tables", []):
                if t["id"] == table_id or t["name"] == table_id:
                    return [f["name"] for f in t.get("fields", [])]
        except requests.RequestException:
            return None
        return None

    def _fill_schema(self, df: pd.DataFrame, source_cfg: dict) -> pd.DataFrame:
        """Reindexa o lote para o schema completo (colunas vazias -> NULL).
        Com 'fields' explícito no source_cfg, usa essa lista (não chama a
        metadata API)."""
        fields = source_cfg.get("fields") or self.schema(source_cfg)
        if not fields or df.empty:
            return df
        meta = [c for c in df.columns if c.startswith("_airtable_")]
        missing = [f for f in fields if f not in df.columns]
        for f in missing:
            df[f] = None
        return df[meta + fields]

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        """Extração completa (todos os lotes) — usada fora do modo batch."""
        records, cursor = [], None
        while True:
            page, cursor = self._request_page(source_cfg, self.MAX_PAGE, cursor)
            records.extend(page)
            if not cursor:
                break
            time.sleep(0.25)  # respeita rate limit (5 req/s)
        return self._fill_schema(self._to_df(records), source_cfg)

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        page, next_cursor = self._request_page(source_cfg, batch_size, cursor)
        return self._fill_schema(self._to_df(page), source_cfg), next_cursor
