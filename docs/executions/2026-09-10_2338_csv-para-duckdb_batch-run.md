# Batch-run 2026-09-10_2338 — csv → duckdb (batch_size=50)

- **Data:** 2026-09-10T23:38:51+00:00
- **Lotes:** 4 executados | ✅ 4 | ❌ 0
- **Linhas entregues no destino (novas):** 200
- **Contagem cumulativa no destino:** {'contacts': 200}
- **Plano previsto:** {'raw_contacts': 200}

| Lote | Estado | Linhas (raw) | Novas no destino | Erro |
|---|---|---|---|---|
| 1 | ✅ | {'raw_contacts': 50} | 50 | — |
| 2 | ✅ | {'raw_contacts': 50} | 50 | — |
| 3 | ✅ | {'raw_contacts': 50} | 50 | — |
| 4 | ✅ | {'raw_contacts': 50} | 50 | — |

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*