SHELL := /bin/bash
DB      ?= etl_agent.duckdb

.PHONY: install extract transform export validate load run report lint

install:
	pip install -r requirements.txt

extract:  ## [1] Origem -> DuckDB raw.*
	python extract/run_pipeline.py extract --config config/pipeline.json --db $(DB)

transform:  ## [2] dbt: raw -> staging -> marts (DuckDB)
	dbt build --project-dir dbt --profiles-dir dbt --target dev

export:   ## [2.5] marts -> export/*.parquet (artefacto canónico)
	python extract/run_pipeline.py export --config config/pipeline.json --db $(DB)

validate:  ## [3] Great Expectations (compliance gate sobre o parquet)
	cd great_expectations && great_expectations checkpoint run d1_pipeline_checkpoint

load:   ## [4] artefacto validado -> Destino (só depois de validate passar)
	python extract/run_pipeline.py load --config config/pipeline.json --db $(DB)

report:
	python extract/run_pipeline.py report --config config/pipeline.json --db $(DB)

run: extract transform export validate load report

lint:
	ruff check extract dbt scripts
