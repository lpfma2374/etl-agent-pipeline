# Batch-run 2026-09-15_2046 — airtable → postgres (batch_size=50)

- **Data:** 2026-09-15T20:46:19+00:00
- **Lotes:** 4 executados | ✅ 4 | ❌ 0
- **Linhas entregues no destino (upsert idempotente):** 736
- **Contagem cumulativa no destino:** {}
- **Plano previsto:** {'raw_processos_resumo': None, 'raw_indicadores_eficacia': None, 'raw_fases': None, 'raw_subseccoes_fases': None, 'raw_historico_versoes': None, 'raw_quadro_registos': None}

| Lote | Estado | Linhas (raw) | Entregues (upsert) | Erro |
|---|---|---|---|---|
| 1 | ✅ | {'raw_processos_resumo': 16, 'raw_indicadores_eficacia': 50, 'raw_fases': 50, 'raw_subseccoes_fases': 50, 'raw_historico_versoes': 26, 'raw_quadro_registos': 37} | 229 | — |
| 2 | ✅ | {'raw_indicadores_eficacia': 12, 'raw_fases': 36, 'raw_subseccoes_fases': 50} | 177 | — |
| 3 | ✅ | {'raw_subseccoes_fases': 50} | 177 | — |
| 4 | ✅ | {'raw_subseccoes_fases': 26} | 153 | — |

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*