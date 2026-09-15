"""Fábrica de loaders por 'type'. Adicionar novos destinos aqui."""

from .airtable import AirtableLoader
from .cloudflare_d1 import CloudflareD1Loader
from .duckdb_loader import DuckDbLoader
from .postgres import PostgresLoader

REGISTRY = {
    "cloudflare_d1": CloudflareD1Loader,
    "duckdb": DuckDbLoader,
    "postgres": PostgresLoader,
    "airtable": AirtableLoader,
}


def get_loader(dest_cfg: dict):
    dtype = dest_cfg.get("type")
    if dtype not in REGISTRY:
        raise ValueError(
            f"Destino '{dtype}' não suportado. Disponíveis: {list(REGISTRY)}")
    return REGISTRY[dtype](dest_cfg)
