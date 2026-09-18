"""Extractor Excel (.xlsx/.xls) — leitura em lotes.

Suporta, por source_cfg:
- `sheet`: nome ou índice da folha (default: primeira);
- `skiprows`: n.º de linhas iniciais a descartar (títulos/subtítulos/descrições);
  a linha SEGUINTE passa a ser o cabeçalho (comportamento pandas);
- `headers`: lista de nomes — quando a folha NÃO tem linha de cabeçalho,
  lê-se sem header e atribuem-se estes nomes (implícito header=None);
- `positional_pk`: nome da coluna PK posicional 1..n global, contínua entre lotes.
"""

import pandas as pd

from .base import BaseExtractor


class ExcelExtractor(BaseExtractor):
    name = "excel"

    # ---------------------------------------------------------------- leitura
    def _read(self, source_cfg: dict) -> pd.DataFrame:
        path = source_cfg.get("path")
        if not path:
            raise ValueError("'path' do Excel em falta no bloco 'source'")
        sheet = source_cfg.get("sheet", 0)
        skiprows = source_cfg.get("skiprows")
        headers = source_cfg.get("headers")
        if headers:
            df = pd.read_excel(path, sheet_name=sheet,
                               skiprows=skiprows or 0, header=None)
            df = df.iloc[:, :len(headers)]           # descarta colunas extra
            df.columns = list(headers)[:df.shape[1]]
        else:
            df = pd.read_excel(path, sheet_name=sheet, skiprows=skiprows)
        df = df.dropna(how="all")                     # linhas totalmente vazias
        df = df.dropna(axis=1, how="all")              # colunas totalmente vazias
        return df

    @staticmethod
    def _with_pk(df: pd.DataFrame, pk: str | None, start: int) -> pd.DataFrame:
        if pk:
            df = df.copy()
            df.insert(0, pk, range(start + 1, start + 1 + len(df)))
        return df

    # ------------------------------------------------------------------- API
    def fetch(self, source_cfg: dict) -> pd.DataFrame:
        return self._with_pk(self._read(source_cfg),
                             source_cfg.get("positional_pk"), 0)

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        full = self._read(source_cfg)
        start = int(cursor or 0)
        batch = full.iloc[start:start + batch_size]
        if len(batch) == 0:
            return batch, None
        batch = self._with_pk(batch, source_cfg.get("positional_pk"), start)
        next_cursor = start + len(batch)
        exhausted = next_cursor >= len(full)
        return batch, (None if exhausted else next_cursor)

    def count(self, source_cfg: dict) -> int | None:
        if not source_cfg.get("path"):
            return None
        return len(self._read(source_cfg))
