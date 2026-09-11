"""Fábrica de extractors por 'type'. Adicionar novas origens aqui."""

from .airtable import AirtableExtractor
from .csv import CsvExtractor
from .gdrive import GoogleDriveExtractor

REGISTRY = {
    "airtable": AirtableExtractor,
    "csv": CsvExtractor,
    "google_drive": GoogleDriveExtractor,
}


def get_extractor(source_cfg: dict):
    stype = source_cfg.get("type")
    if stype not in REGISTRY:
        raise ValueError(
            f"Origem '{stype}' não suportada. Disponíveis: {list(REGISTRY)}")
    return REGISTRY[stype]()
