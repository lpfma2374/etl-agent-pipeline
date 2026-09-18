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
| 2026-09-11_1632 b01 | airtable → duckdb | {'raw_references': 9} | ❌ dbt build falhou:
[0m16:32:13  Finished running 1 table mod |
| 2026-09-11_1632 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1632 b01 | airtable → duckdb | {'raw_references': 9} | ❌ dbt build falhou:
[0m16:32:35  Finished running 1 table mod |
| 2026-09-11_1632 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1632 b01 | airtable → duckdb | {'raw_references': 9} | ❌ dbt build falhou:
[0m16:32:43  Finished running 1 view mode |
| 2026-09-11_1632 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1633 b01 | airtable → duckdb | {'raw_references': 9} | ❌ name 'db_path' is not defined |
| 2026-09-11_1633 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1633 b01 | airtable → duckdb | {'raw_references': 9} | ❌ dbt build falhou:
[0m16:33:10  Finished running 1 view mode |
| 2026-09-11_1633 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1633 b01 | airtable → duckdb | {'raw_references': 9} | ❌ dbt build falhou:
[0m16:33:31  
[0m16:33:31  Finished runn |
| 2026-09-11_1633 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1633 b01 | airtable → duckdb | {'raw_references': 9} | ✅ +9 |
| 2026-09-11_1633 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 9 novas | cumulativo: {'References': 9} |
| 2026-09-11_1634 b01 | airtable → duckdb | {'raw_references': 9} | ✅ +9 |
| 2026-09-11_1634 SUM | airtable → duckdb (batch 50) | 1 lotes | ✅ 9 novas | cumulativo: {'References': 9} |
| 2026-09-11_1642 b01 | airtable → cloudflare_d1 | {'raw_references': 9} | ❌ 401 Client Error: Unauthorized for url: https://api.cloudfla |
| 2026-09-11_1642 SUM | airtable → cloudflare_d1 (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1642 b01 | airtable → cloudflare_d1 | {'raw_references': 9} | ❌ 400 Client Error: Bad Request for url: https://api.cloudflar |
| 2026-09-11_1642 SUM | airtable → cloudflare_d1 (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1643 b01 | airtable → cloudflare_d1 | {'raw_references': 9} | ✅ +9 |
| 2026-09-11_1643 SUM | airtable → cloudflare_d1 (batch 50) | 1 lotes | ✅ 9 novas | cumulativo: {} |
| 2026-09-11_1645 b01 | airtable → cloudflare_d1 | {'raw_references': 9} | ❌ 400 Client Error: Bad Request for url: https://api.cloudflar |
| 2026-09-11_1645 SUM | airtable → cloudflare_d1 (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1647 b01 | airtable → cloudflare_d1 | {'raw_references': 9} | ❌ 400 Client Error: Bad Request for url: https://api.cloudflar |
| 2026-09-11_1647 SUM | airtable → cloudflare_d1 (batch 50) | 1 lotes | ✅ 0 novas | cumulativo: {} |
| 2026-09-11_1648 b01 | airtable → cloudflare_d1 | {'raw_references': 9} | ✅ +9 |
| 2026-09-11_1648 SUM | airtable → cloudflare_d1 (batch 50) | 1 lotes | ✅ 9 novas | cumulativo: {} |
| 2026-09-11_1900 b01 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1900 b02 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1900 b03 | google_drive → airtable | {'raw_cmdb': 37} | ✅ +37 |
| 2026-09-11_1900 SUM | google_drive → airtable (batch 50) | 3 lotes | ✅ 137 novas | cumulativo: {} |
| 2026-09-11_1900 b01 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1900 b02 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1900 b03 | google_drive → airtable | {'raw_cmdb': 37} | ✅ +37 |
| 2026-09-11_1900 SUM | google_drive → airtable (batch 50) | 3 lotes | ✅ 137 novas | cumulativo: {} |
| 2026-09-11_1901 b01 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1901 b02 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1901 b03 | google_drive → airtable | {'raw_cmdb': 37} | ✅ +37 |
| 2026-09-11_1901 SUM | google_drive → airtable (batch 50) | 3 lotes | ✅ 137 entregues (upsert) | cumulativo: {} |
| 2026-09-11_1902 b01 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1902 b02 | google_drive → airtable | {'raw_cmdb': 50} | ✅ +50 |
| 2026-09-11_1902 b03 | google_drive → airtable | {'raw_cmdb': 37} | ✅ +37 |
| 2026-09-11_1902 SUM | google_drive → airtable (batch 50) | 3 lotes | ✅ 137 entregues (upsert) | cumulativo: {} |
| 2026-09-12_0901 b01 | csv → airtable | {'raw_processos_resumo': 17, 'raw_indicadores_eficacia': 50, 'raw_fases': 50, 'raw_subseccoes_fases': 50, 'raw_historico_versoes': 22, 'raw_quadro_registos': 50} | ✅ +239 |
| 2026-09-12_0901 b02 | csv → airtable | {'raw_indicadores_eficacia': 50, 'raw_fases': 40, 'raw_subseccoes_fases': 26, 'raw_quadro_registos': 7} | ✅ +162 |
| 2026-09-12_0901 b03 | csv → airtable | {'raw_indicadores_eficacia': 13} | ✅ +125 |
| 2026-09-12_0901 SUM | csv → airtable (batch 50) | 3 lotes | ✅ 526 entregues (upsert) | cumulativo: {} |
| 2026-09-12_0901 b01 | csv → airtable | {'raw_processos_resumo': 17, 'raw_indicadores_eficacia': 50, 'raw_fases': 50, 'raw_subseccoes_fases': 50, 'raw_historico_versoes': 22, 'raw_quadro_registos': 50} | ✅ +239 |
| 2026-09-12_0901 b02 | csv → airtable | {'raw_indicadores_eficacia': 50, 'raw_fases': 40, 'raw_subseccoes_fases': 26, 'raw_quadro_registos': 7} | ✅ +162 |
| 2026-09-12_0901 b03 | csv → airtable | {'raw_indicadores_eficacia': 13} | ✅ +125 |
| 2026-09-12_0901 SUM | csv → airtable (batch 50) | 3 lotes | ✅ 526 entregues (upsert) | cumulativo: {} |
| 2026-09-15_2046 b01 | airtable → postgres | {'raw_processos_resumo': 16, 'raw_indicadores_eficacia': 50, 'raw_fases': 50, 'raw_subseccoes_fases': 50, 'raw_historico_versoes': 26, 'raw_quadro_registos': 37} | ✅ +229 |
| 2026-09-15_2046 b02 | airtable → postgres | {'raw_indicadores_eficacia': 12, 'raw_fases': 36, 'raw_subseccoes_fases': 50} | ✅ +177 |
| 2026-09-15_2046 b03 | airtable → postgres | {'raw_subseccoes_fases': 50} | ✅ +177 |
| 2026-09-15_2046 b04 | airtable → postgres | {'raw_subseccoes_fases': 26} | ✅ +153 |
| 2026-09-15_2046 SUM | airtable → postgres (batch 50) | 4 lotes | ✅ 736 entregues (upsert) | cumulativo: {} |
| 2026-09-15_2047 b01 | airtable → postgres | {'raw_processos_resumo': 16, 'raw_indicadores_eficacia': 50, 'raw_fases': 50, 'raw_subseccoes_fases': 50, 'raw_historico_versoes': 26, 'raw_quadro_registos': 37} | ✅ +229 |
| 2026-09-15_2047 b02 | airtable → postgres | {'raw_indicadores_eficacia': 12, 'raw_fases': 36, 'raw_subseccoes_fases': 50} | ✅ +177 |
| 2026-09-15_2047 b03 | airtable → postgres | {'raw_subseccoes_fases': 50} | ✅ +177 |
| 2026-09-15_2047 b04 | airtable → postgres | {'raw_subseccoes_fases': 26} | ✅ +153 |
| 2026-09-15_2047 SUM | airtable → postgres (batch 50) | 4 lotes | ✅ 736 entregues (upsert) | cumulativo: {} |

| 2026-09-18 15:40 | Novo ETL (wizard) | radar-de-alas.xlsx -> Airtable Scout_Radar/scout | 1 | 3 | success |
