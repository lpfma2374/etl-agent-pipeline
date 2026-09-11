"""Loader Airtable — publica um DataFrame numa tabela de uma base.

Responsabilidades:
- garante que a tabela existe (cria-a a partir dos dtypes do DataFrame,
  via Metadata API, se ainda não existir);
- upsert idempotente por chave primária: faz listRecords paginado da PK,
  insere os registos novos em lotes de 10 (limite da API) e faz PATCH
  dos já existentes.

Notas da API Airtable:
- máx. 10 registos por POST/PATCH;
- "typecast": true aceita números como texto e vice-versa;
- nomes de campos com espaços/'#' são suportados (JSON, sem quoting);
- a BASE tem de existir (criação de bases exige access workspace-level
  do token — fora do controlo do loader).
"""

import time
import urllib.parse

import pandas as pd
import requests

from .base import BaseLoader

API = "https://api.airtable.com/v0"
BATCH_RECORDS = 10  # limite da API Airtable por pedido
MAX_RETRIES = 3


class AirtableLoader(BaseLoader):
    name = "airtable"

    def __init__(self, cfg: dict):
        import os
        self.dest_cfg = cfg or {}
        self.api_key = os.environ.get("AIRTABLE_API_KEY")
        if not self.api_key:
            raise ValueError("AIRTABLE_API_KEY em falta (variável de ambiente)")
        self.base_id = self.dest_cfg.get("base_id")
        if not self.base_id:
            raise ValueError("'base_id' em falta no bloco 'destination'")

    # ------------------------------------------------------------ HTTP com retry
    def _request(self, method: str, url: str, json_body=None, params=None):
        for attempt in range(1, MAX_RETRIES + 1):
            r = requests.request(
                method, url,
                headers={"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json"},
                json=json_body, params=params, timeout=60,
            )
            if r.status_code == 429 and attempt < MAX_RETRIES:  # rate limit
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        return {}

    # ------------------------------------------------------------ schema
    def _field_type(self, dtype) -> dict:
        """Mapeia dtype pandas -> definição de campo Airtable."""
        if isinstance(dtype, pd.ArrowDtype):
            dtype = dtype.numpy_dtype
        kind = getattr(dtype, "kind", "O")
        if kind in ("i", "u"):
            return {"type": "number", "options": {"precision": 0}}
        if kind == "f":
            return {"type": "number", "options": {"precision": 2}}
        if kind == "b":
            return {"type": "checkbox"}
        return {"type": "singleLineText"}

    def _ensure_table(self, table: str, df: pd.DataFrame) -> None:
        tables = self._request("GET", f"{API}/meta/bases/{self.base_id}/tables")
        for t in tables.get("tables", []):
            if t["name"] == table:
                return
        fields = [{"name": c, **self._field_type(df[c].dtype)}
                  for c in df.columns]
        self._request("POST", f"{API}/meta/bases/{self.base_id}/tables",
                      json_body={"name": table, "fields": fields})

    # ------------------------------------------------------------ upsert
    def _existing_pks(self, table: str, pk: str) -> dict:
        """Devolve {valor_pk: record_id} dos registos já existentes."""
        existing = {}
        # 'fields[]=<col>' com urlencode manual (colunas com espaços/'#')
        base = f"{API}/{self.base_id}/{urllib.parse.quote(table, safe='')}"
        url = base + f"?fields%5B%5D={urllib.parse.quote(pk, safe='')}"
        while True:
            data = self._request("GET", url)
            for rec in data.get("records", []):
                existing[rec["fields"].get(pk)] = rec["id"]
            offset = data.get("offset")
            if not offset:
                break
            url = base + (f"?fields%5B%5D={urllib.parse.quote(pk, safe='')}"
                         f"&offset={offset}")
        return existing

    @staticmethod
    def _fields_dict(row: pd.Series) -> dict:
        """Linha -> {"campo": valor}; valores None são omitidos."""
        out = {}
        for k, v in row.items():
            if hasattr(v, "item"):  # numpy scalar -> nativo
                v = v.item()
            if v is None or (not isinstance(v, str) and pd.isna(v)):
                continue
            out[str(k)] = v
        return out

    def load(self, df: pd.DataFrame, table_cfg: dict) -> int:
        table = table_cfg["destination_table"]
        pk = table_cfg["primary_key"]
        self._ensure_table(table, df)
        existing = self._existing_pks(table, pk)

        rows = []
        for _, row in df.iterrows():
            rows.append(self._fields_dict(row))

        to_create, to_update = [], []
        for fields in rows:
            pk_val = fields.get(pk)
            if pk_val in existing:
                to_update.append({"id": existing[pk_val], "fields": fields})
            else:
                to_create.append({"fields": fields})

        table_url = f"{API}/{self.base_id}/{urllib.parse.quote(table, safe='')}"
        for i in range(0, len(to_create), BATCH_RECORDS):
            self._request("POST", table_url,
                          json_body={"records": to_create[i:i + BATCH_RECORDS],
                                     "typecast": True})
        for i in range(0, len(to_update), BATCH_RECORDS):
            self._request("PATCH", table_url,
                          json_body={"records": to_update[i:i + BATCH_RECORDS],
                                     "typecast": True})
        return len(df)
