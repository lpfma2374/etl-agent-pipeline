"""Contrato base de extração — cada origem implementa BaseExtractor.

O padrão segue a filosofia Airbyte (conectores isolados), mas sem
dependências pesadas: pandas + requests.

Extração por lotes (regra ETL_Agent): o pipeline extrai em lotes de, no
máximo, `batch_size` registos. Cada lote percorre o pipeline completo
(extract -> transform -> validate -> load -> report) para garantir
entregas incrementais no destino.
"""

import os


class BaseExtractor:
    """Interface: `fetch(source_cfg)` devolve um DataFrame pandas.

    `fetch_batch(source_cfg, batch_size, cursor)` devolve `(df, next_cursor)`
    — um lote de até `batch_size` linhas e o cursor para o lote seguinte.
    Um cursor `None` devolvido significa origem esgotada.
    `count(source_cfg)` devolve o total de registos da origem, se conhecido.
    """

    name = "base"

    def fetch(self, source_cfg: dict):
        raise NotImplementedError

    def fetch_batch(self, source_cfg: dict, batch_size: int, cursor=None):
        """Implementação por omissão: extrai tudo e fatia numericamente."""
        df = self.fetch(source_cfg)
        start = int(cursor or 0)
        batch = df.iloc[start:start + batch_size]
        next_cursor = start + len(batch)
        if len(batch) == 0 or next_cursor >= len(df):
            return batch.copy(), None
        return batch.copy(), next_cursor

    def count(self, source_cfg: dict) -> int | None:
        """Total de registos na origem; None se a origem não o souber dizer."""
        return None

    @staticmethod
    def require_env(env_keys: list[str]):
        """Valida secrets obrigatórios. Secrets apenas via variáveis de ambiente."""
        missing = [k for k in env_keys if not os.environ.get(k)]
        if missing:
            raise ValueError(f"Secrets em falta (variáveis de ambiente): {missing}")
