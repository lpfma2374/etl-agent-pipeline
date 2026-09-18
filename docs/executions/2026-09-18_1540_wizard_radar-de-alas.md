# Execução ETL — Radar de Alas

- **Request:** `6aad5a6631e8c2f2f1ca6b8f`
- **Workflow:** Novo ETL (wizard)
- **Origem:** `radar-de-alas.xlsx` / DuckDB staging
- **Destino:** Airtable `Scout_Radar`, tabela `scout`
- **Transformação:** removidas 2 linhas de preâmbulo, a linha de cabeçalho foi promovida a nomes de campos; restantes valores mantidos sem alterações.
- **Lotes:** 1 lote sequencial de 3 registos, limite fixo 50
- **Validação:** Great Expectations, 4/4 expectations OK, 3 linhas, `_row_id` não nulo e único
- **Carga:** 3 registos carregados/upsertados; confirmação por consulta dos três nomes
- **Dados:** Gessime Yassine, Mouad Dahak, Shion Nakayama
- **Parquet transformado:** `export/mart_radar_de_alas.parquet`
- **Modelo dbt:** `dbt/models/marts/mart_radar_de_alas.sql`
- **Commit:** será registado no repositório após esta execução
