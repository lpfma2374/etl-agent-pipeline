# ETL_Agent — Data Pipeline Open Source

[![CI](https://github.com/lpfma2374/etl-agent-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/lpfma2374/etl-agent-pipeline/actions/workflows/ci.yml)

Pipeline de dados **CI/CD 100% open source** mantido pelo agente **ETL_Agent** (Base44 Superagent).
Suporta extração/migração entre origens (ex.: Airtable, APIs REST, CSV) e destinos
(ex.: Cloudflare D1, PostgreSQL, DuckDB), com transformação (dbt), qualidade e governação
de dados (Great Expectations) e registo auditável de todas as execuções.

## Extração por lotes (regra ETL_Agent)

A extração de uma origem é feita **por lotes de, no máximo, 50 registos**,
de forma sequencial. Se a origem tiver 200 registos, o orquestrador determina
**4 lotes** e executa **o pipeline completo para cada lote**:

```
lote 1: extract(50) -> dbt -> export parquet -> Great Expectations -> load -> report
lote 2: extract(50) -> ... (se falhar: registado no report e segue o lote 3)
...
```

- **Entrega incremental:** o destino é carregado após CADA lote validado
  (dedupe por `primary_key` — lotes são idempotentes).
- **Falha isolada:** um lote que aborte (dbt, gate de qualidade, load) é
  registado no report (`docs/executions/*_batch-run.md`) e o orquestrador
  avança para o lote seguinte — sem perder os restantes.
- **Sumário auditável:** n.º de lotes, ok/falhados, linhas novas entregues e
  contagem cumulativa no destino; exit code 2 sinaliza lotes falhados.

```bash
python extract/run_batches.py --config config/pipeline.json --batch-size 50
# ou: make batch
```

## Stack (tudo free / open source)

| Camada | Ferramenta | Licença |
|---|---|---|
| Extração (Extract) | Python + pandas + conector por origem (padrão Airbyte) | MIT |
| Staging warehouse | DuckDB | MIT |
| Transformação (T) | dbt-core | Apache 2.0 |
| Qualidade / Governança | Great Expectations | Apache 2.0 |
| Orquestração | Python (make / GitHub Actions) | MIT |
| CI/CD | GitHub Actions | free p/ repositórios públicos |
| Catálogo / docs | dbt docs (GitHub Pages) + este registo de execuções | — |

## Arquitetura

```
Origem (ex. Airtable)                Destino (ex. Cloudflare D1)
        │                                        ▲
        ▼                                        │
  [1] EXTRACT ──► DuckDB (raw.*) ──► [2] TRANSFORM (dbt: staging→marts)
                                              │
                                              ▼
                                   [3] VALIDATE (Great Expectations)
                                              │  (falha → aborta, nada é carregado)
                                              ▼
                                     [4] LOAD ──► Destino
                                              │
                                              ▼
                             [5] REPORT ──► docs/executions/ + registo
```

1. **Extract** — `extract/extractors/` faz o pull da origem para o schema `raw` do DuckDB.
2. **Transform** — dbt materializa `staging` (limpeza, tipagem) e `marts` (modelo final).
3. **Validate** — Great Expectations valida os marts (nulos, unicidade, ranges). Se falhar, o pipeline aborta antes da carga (princípio de *compliance gate*).
4. **Load** — `extract/loaders/` carrega em batches para o destino.
5. **Report** — relatório de execução em Markdown, versionado em `docs/executions/` (auditoria/governação).

## Uso

```bash
pip install -r requirements.txt

# 1. configurar a execução (cópia do exemplo)
cp config/pipeline.example.json config/pipeline.json  # preencher tokens/IDs

# 2. correr o pipeline completo E-T-V-L + report
make run

# ou por passos
make extract && make transform && make validate && make load

# testes de qualidade isolados
great_expectations checkpoint run d1_pipeline_checkpoint
```

## CI/CD (GitHub Actions)

- `.github/workflows/ci.yml` — em cada push/PR: lint, `dbt build` e validação Great Expectations contra DuckDB (dados sintéticos). Garante que o pipeline está sempre verde.
- `.github/workflows/pipeline.yml` — `workflow_dispatch` para correr migrações reais com a config fornecida via secrets do repositório.

## Registo de execuções

Todas as execuções do ETL_Agent ficam registadas em:
- `docs/executions/EXECUTIONS.md` — índice consolidado (data, origem→destino, status, linhas, duração)
- `docs/executions/TEMPLATE.md` — modelo de reporte
- uma entrada por execução: `docs/executions/YYYY-MM-DD_HHMM_<origem>-para-<destino>.md`

## Adicionar uma nova origem/destino

1. Criar `extract/extractors/<origem>.py` (subclasse de `BaseExtractor`)
2. Criar `extract/loaders/<destino>.py` (subclasse de `BaseLoader`)
3. Mapeamento dbt em `dbt/models/`
4. Expectations em `great_expectations/`
5. Reporte da execução em `docs/executions/`

## Segurança

Tokens e credenciais **nunca** ficam no código: passam por variáveis de ambiente
(`AIRTABLE_API_KEY`, `CF_API_TOKEN`, `CF_ACCOUNT_ID`, `CF_DATABASE_ID`) ou GitHub Secrets.
