# Batch-run 2026-09-11_1900 — google_drive → airtable (batch_size=50)

- **Data:** 2026-09-11T19:00:46+00:00
- **Lotes:** 3 executados | ✅ 3 | ❌ 0
- **Linhas entregues no destino (novas):** 137
- **Contagem cumulativa no destino:** {}
- **Plano previsto:** {'raw_cmdb': None}

| Lote | Estado | Linhas (raw) | Novas no destino | Erro |
|---|---|---|---|---|
| 1 | ✅ | {'raw_cmdb': 50} | 50 | — |
| 2 | ✅ | {'raw_cmdb': 50} | 50 | — |
| 3 | ✅ | {'raw_cmdb': 37} | 37 | — |

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*