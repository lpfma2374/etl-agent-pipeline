"""Extractor Google Drive — lê um ficheiro CSV partilhado via file_id.

Usa o token OAuth do conector googledrive (variável de ambiente
GOOGLEDRIVE_ACCESS_TOKEN). O ficheiro é descarregado por inteiro
(pandas + requests) e, se indicado `positional_pk`, injeta uma PK
posicional (1..n) antes do slicing em lotes — determinística e
estável enquanto a ordem das linhas do ficheiro não mudar.
"""

import io
import os

import pandas as pd
import requests

from .base import BaseExtractor


class GoogleDriveExtractor(BaseExtractor):
    name = "google_drive"
    API = "https://www.googleapis.com/drive/v3"

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        file_id = source_cfg.get("file_id")
        if not file_id:
            raise ValueError("'file_id' em falta no bloco 'source'")
        self.require_env(["GOOGLEDRIVE_ACCESS_TOKEN"])
        token = os.environ["GOOGLEDRIVE_ACCESS_TOKEN"]
        r = requests.get(
            f"{self.API}/files/{file_id}",
            params={"alt": "media"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120,
        )
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content))
        pk = source_cfg.get("positional_pk")
        if pk:
            df.insert(0, pk, range(1, len(df) + 1))
        return df

    def count(self, source_cfg: dict) -> int | None:
        return None  # total desconhecido — extração até esgotar
