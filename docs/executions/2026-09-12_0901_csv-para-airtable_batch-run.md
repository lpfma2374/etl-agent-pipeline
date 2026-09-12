# Batch-run 2026-09-12_0901 — csv → airtable (batch_size=50)

- **Data:** 2026-09-12T09:01:58+00:00
- **Lotes:** 3 executados | ✅ 3 | ❌ 0
- **Linhas entregues no destino (upsert idempotente):** 526
- **Contagem cumulativa no destino:** {}
- **Plano previsto:** {'raw_processos_resumo': 219, 'raw_indicadores_eficacia': 113, 'raw_fases': 1036, 'raw_subseccoes_fases': 405, 'raw_historico_versoes': 22, 'raw_quadro_registos': 57}

| Lote | Estado | Linhas (raw) | Entregues (upsert) | Erro |
|---|---|---|---|---|
| 1 | ✅ | {'raw_processos_resumo': 17, 'raw_indicadores_eficacia': 50, 'raw_fases': 50, 'raw_subseccoes_fases': 50, 'raw_historico_versoes': 22, 'raw_quadro_registos': 50} | 239 | — |
| 2 | ✅ | {'raw_indicadores_eficacia': 50, 'raw_fases': 40, 'raw_subseccoes_fases': 26, 'raw_quadro_registos': 7} | 162 | — |
| 3 | ✅ | {'raw_indicadores_eficacia': 13} | 125 | — |

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*