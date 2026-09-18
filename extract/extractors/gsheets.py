"""Extractor Google Sheets — folha PÚBLICA (link partilhado "qualquer pessoa com o link").

Converte o URL do documento no CSV export e descarrega.
Se a folha não for pública (401/403/redirect de login), falha com mensagem clara.

Formatos aceites:
  https://docs.google.com/spreadsheets/d/<ID>/edit#gid=<GID>
  https://docs.google.com/spreadsheets/d/<ID>/edit
  https://drive.google.com/file/d/<ID>/view  (ficheiro CSV partilhado no Drive)
"""

import io
import re
import urllib.request

import pandas as pd

from .base import BaseExtractor


def _csv_url(sheet_url: str) -> str:
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", sheet_url)
    if m:
        sid = m.group(1)
        gid = re.search(r"[#&?]gid=(\d+)", sheet_url)
        g = f"&gid={gid.group(1)}" if gid else ""
        return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv{g}"
    m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", sheet_url)
    if m:  # CSV no Drive
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    raise ValueError("URL do Google Sheets não reconhecido")


class GoogleSheetsExtractor(BaseExtractor):
    name = "gsheets"

    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        url = source_cfg.get("url")
        if not url:
            raise ValueError("'url' da folha em falta no bloco 'source'")
        raw = self._download(_csv_url(url))
        return pd.read_csv(io.BytesIO(raw))

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        # a folha é pequena em cenários de wizard: lê tudo e fatia
        full = self.fetch(source_cfg)
        start = int(cursor or 0)
        batch = full.iloc[start:start + batch_size]
        if len(batch) == 0:
            return batch, None
        next_cursor = start + len(batch)
        return batch, (None if next_cursor >= len(full) else next_cursor)

    def count(self, source_cfg: dict) -> int | None:
        url = source_cfg.get("url")
        if not url:
            return None
        raw = self._download(_csv_url(url))
        return len(pd.read_csv(io.BytesIO(raw)))

    @staticmethod
    def _download(csv_url: str) -> bytes:
        req = urllib.request.Request(csv_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise ValueError(
                    "A folha não é pública: partilha com 'Qualquer pessoa com o link' "
                    "(Visualizador) e volta a tentar.")
            raise
        if b"<html" in data[:200].lower():  # redirect para login do Google
            raise ValueError(
                "A folha não é pública: partilha com 'Qualquer pessoa com o link' "
                "(Visualizador) e volta a tentar.")
        return data
