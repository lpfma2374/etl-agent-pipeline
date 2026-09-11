# Batch-run 2026-09-11_1632 — airtable → duckdb (batch_size=50)

- **Data:** 2026-09-11T16:32:44+00:00
- **Lotes:** 1 executados | ✅ 0 | ❌ 1
- **Linhas entregues no destino (novas):** 0
- **Contagem cumulativa no destino:** {}
- **Plano previsto:** {'raw_references': None}

| Lote | Estado | Linhas (raw) | Novas no destino | Erro |
|---|---|---|---|---|
| 1 | ❌ | {'raw_references': 9} | — | dbt build falhou: |

<details><summary>Erro do lote 1</summary>

```
a tests in 0 hours 0 minutes and 0.26 seconds (0.26s).
[0m16:32:44  
[0m16:32:44  [31mCompleted with 1 error and 0 warnings:[0m
[0m16:32:44  
[0m16:32:44    Runtime Error in model stg_references (models/staging/stg_references.sql)
  Catalog Error: Table with name raw_references does not exist!
  Did you mean "raw_contacts"?
  
  LINE 9:     select * from "etl_agent"."raw"."raw_references"
                            ^
[0m16:32:44  
[0m16:32:44  Done. PASS=0 WARN=0 ERROR=1 SKIP=4 TOTAL=5

```
</details>

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*