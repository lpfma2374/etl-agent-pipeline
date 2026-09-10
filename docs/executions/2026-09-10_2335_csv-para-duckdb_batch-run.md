# Batch-run 2026-09-10_2335 — csv → duckdb (batch_size=50)

- **Data:** 2026-09-10T23:35:35+00:00
- **Lotes:** 4 executados | ✅ 3 | ❌ 1
- **Linhas entregues no destino (novas):** 150
- **Contagem cumulativa no destino:** {'contacts': 150}
- **Plano previsto:** {'raw_contacts': 200}

| Lote | Estado | Linhas (raw) | Novas no destino | Erro |
|---|---|---|---|---|
| 1 | ✅ | {'raw_contacts': 50} | 50 | — |
| 2 | ❌ | {'raw_contacts': 50} | — | dbt build falhou: |
| 3 | ✅ | {'raw_contacts': 50} | 50 | — |
| 4 | ✅ | {'raw_contacts': 50} | 50 | — |

<details><summary>Erro do lote 2</summary>

```
 3 data tests in 0 hours 0 minutes and 0.41 seconds (0.41s).
[0m23:35:27  
[0m23:35:27  [31mCompleted with 1 error and 0 warnings:[0m
[0m23:35:27  
[0m23:35:27  [31mFailure in test unique_mart_contacts_id (models/marts/schema.yml)[0m
[0m23:35:27    Got 1 result, configured to fail if != 0
[0m23:35:27  
[0m23:35:27    compiled code at ../target/compiled/etl_agent/models/marts/schema.yml/unique_mart_contacts_id.sql
[0m23:35:27  
[0m23:35:27  Done. PASS=4 WARN=0 ERROR=1 SKIP=0 TOTAL=5

```
</details>

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*