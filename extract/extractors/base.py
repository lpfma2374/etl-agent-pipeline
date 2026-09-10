"""Contrato base de extração — cada origem implementa BaseExtractor.

O padrão segue a filosofia Airbyte (conectores isolados), mas sem
dependências pesadas: pandas + requests.
"""

import os


class BaseExtractor:
    """Interface: `fetch(source_cfg)` devolve um DataFrame pandas."""

    name = "base"

    def fetch(self, source_cfg: dict):
        raise NotImplementedError

    @staticmethod
    def require_env(env_keys: list[str]):
        """Valida secrets obrigatórios. Secrets apenas via variáveis de ambiente."""
        missing = [k for k in env_keys if not os.environ.get(k)]
        if missing:
            raise ValueError(f"Secrets em falta (variáveis de ambiente): {missing}")
