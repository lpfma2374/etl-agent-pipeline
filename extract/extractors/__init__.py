"""Fábrica de extractors por 'type'. Adicionar novas origens aqui."""

from .airtable import AirtableExtractor
from .csv import CsvExtractor
from .duckdb_staging import DuckDBStagingExtractor
from .excel import ExcelExtractor
from .gdrive import GoogleDriveExtractor
from .gsheets import GoogleSheetsExtractor

REGISTRY = {
    "airtable": AirtableExtractor,
    "csv": CsvExtractor,
    "excel": ExcelExtractor,
    "gsheets": GoogleSheetsExtractor,
    "google_drive": GoogleDriveExtractor,
    "duckdb_staging": DuckDBStagingExtractor,
}


def get_extractor(source_cfg: dict):
    stype = source_cfg.get("type")
    if stype not in REGISTRY:
        raise ValueError(
            f"Origem '{stype}' não suportada. Disponíveis: {list(REGISTRY)}")
    return REGISTRY[stype]()
