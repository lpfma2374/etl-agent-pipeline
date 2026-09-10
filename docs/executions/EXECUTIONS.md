# Execuções do ETL_Agent — registo consolidado

Todas as execuções do pipeline ficam registadas aqui (auditoria / governação).
Uma entrada por linha, um relatório detalhado por execução nesta pasta.

| Data (UTC local) | Rota | Linhas (raw) | Carregado |
|---|---|---|---|
| 2026-09-10_2300 | csv → duckdb | {'raw_contacts': 50} | — |
| 2026-09-10_2315 | csv → duckdb | {'raw_contacts': 50} | — |
| 2026-09-10_2315 | csv → duckdb | {'raw_contacts': 50} | ✅ |
| 2026-09-10_2335 b01 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2335 b02 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2335 b03 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2335 b04 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2335 SUM | csv → duckdb (batch 50) | 4 lotes | ✅ 200 novas | cumulativo: {'contacts': 200} |
| 2026-09-10_2335 b01 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2335 b02 | csv → duckdb | {'raw_contacts': 50} | ❌ dbt build falhou:
[0m23:35:27  4 of 5 PASS not_null_mart_co |
| 2026-09-10_2335 b03 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2335 b04 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2335 SUM | csv → duckdb (batch 50) | 4 lotes | ✅ 150 novas | cumulativo: {'contacts': 150} |
| 2026-09-10_2336 b01 | csv → duckdb | {'raw_contacts': 50} | ✅ +0 |
| 2026-09-10_2336 b02 | csv → duckdb | {'raw_contacts': 50} | ❌ dbt build falhou:
[0m23:35:58  5 of 5 FAIL 1 unique_mart_co |
| 2026-09-10_2336 b03 | csv → duckdb | {'raw_contacts': 50} | ✅ +0 |
| 2026-09-10_2336 b04 | csv → duckdb | {'raw_contacts': 50} | ✅ +0 |
| 2026-09-10_2336 SUM | csv → duckdb (batch 50) | 4 lotes | ✅ 0 novas | cumulativo: {'contacts': 150} |
| 2026-09-10_2338 b01 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2338 b02 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2338 b03 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2338 b04 | csv → duckdb | {'raw_contacts': 50} | ✅ +50 |
| 2026-09-10_2338 SUM | csv → duckdb (batch 50) | 4 lotes | ✅ 200 novas | cumulativo: {'contacts': 200} |
| 2026-09-10_2339 b01 | csv → duckdb | {'raw_contacts': 50} | ✅ +0 |
| 2026-09-10_2339 b02 | csv → duckdb | {'raw_contacts': 50} | ✅ +0 |
| 2026-09-10_2339 b03 | csv → duckdb | {'raw_contacts': 50} | ✅ +0 |
| 2026-09-10_2339 b04 | csv → duckdb | {'raw_contacts': 50} | ✅ +0 |
| 2026-09-10_2339 SUM | csv → duckdb (batch 50) | 4 lotes | ✅ 0 novas | cumulativo: {'contacts': 200} |
