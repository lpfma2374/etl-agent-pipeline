# Batch-run 2026-09-18_1730 — excel → airtable (batch_size=50)

- **Data:** 2026-09-18T17:30:47+00:00
- **Lotes:** 1 executados | ✅ 1 | ❌ 0
- **Linhas entregues no destino (upsert idempotente):** 23
- **Contagem cumulativa no destino:** {}
- **Plano previsto:** {'raw_prospetos': 3, 'raw_contexto_excluidos': 3, 'raw_cobertura': 10, 'raw_metodologia': 7}

| Lote | Estado | Linhas (raw) | Entregues (upsert) | Erro |
|---|---|---|---|---|
| 1 | ✅ | {'raw_prospetos': 3, 'raw_contexto_excluidos': 3, 'raw_cobertura': 10, 'raw_metodologia': 7} | 23 | — |

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*