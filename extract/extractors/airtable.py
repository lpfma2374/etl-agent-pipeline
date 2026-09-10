"""Extractor Airtable — lê uma tabela de uma base via API REST (paginado)."""

import json
import os
import time

import pandas as pd
import requests

from .base import BaseExtractor


class AirtableExtractor(BaseExtractor):
    name = "airtable"
    BASE_URL = "https://api.airtable.com/v0"

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        api_key = os.environ.get("AIRTABLE_API_KEY")
        base_id = source_cfg.get("base_id")
        table = source_cfg.get("table")
        if not api_key:
            raise ValueError("AIRTABLE_API_KEY em falta (variável de ambiente)")
        if not base_id or not table:
            raise ValueError("base_id e table são obrigatórios no bloco 'source'")

        headers = {"Authorization": f"Bearer {api_key}"}
        records, offset = [], None
        while True:
            params = {"pageSize": 100}
            if offset:
                params["offset"] = offset
            resp = requests.get(
                f"{self.BASE_URL}/{base_id}/{table}",
                headers=headers, params=params, timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            records.extend(r["fields"] for r in data.get("records", []))
            offset = data.get("offset")
            if not offset:
                break
            time.sleep(0.25)  # respeita rate limit (5 req/s)

        df = pd.DataFrame(records)
        if df.empty:
            return df
        # campos de listas/dict -> JSON string para caber num RDBMS
        for col in df.columns:
            if df[col].apply(lambda v: isinstance(v, (list, dict))).any():
                df[col] = df[col].apply(lambda v: json.dumps(v, default=str))
        return df
