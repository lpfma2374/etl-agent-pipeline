"""Contrato base de carga — cada destino implementa BaseLoader."""


class BaseLoader:
    """Interface: `load(df, table_cfg)` carrega um DataFrame e devolve n.º de linhas."""

    name = "base"

    def load(self, df, table_cfg: dict) -> int:
        raise NotImplementedError
