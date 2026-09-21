# Batch-run 2026-09-21_1845 — csv → cloudflare_d1 (batch_size=50)

- **Data:** 2026-09-21T18:45:05+00:00
- **Lotes:** 2 executados | ✅ 2 | ❌ 0
- **Linhas entregues no destino (upsert idempotente):** 236
- **Contagem cumulativa no destino:** {}
- **Plano previsto:** {'raw_patrimonio_financeiro': 36, 'raw_patrimonio_configuracaocategoria': 78, 'raw_patrimonio_heranca': 2, 'raw_patrimonio_viatura': 2, 'raw_patrimonio_recheio': 18, 'raw_patrimonio_imovel': 1, 'raw_patrimonio_seguro': 10, 'raw_patrimonio_poupanca': 5, 'raw_patrimonio_credito': 5}

| Lote | Estado | Linhas (raw) | Entregues (upsert) | Erro |
|---|---|---|---|---|
| 1 | ✅ | {'raw_patrimonio_financeiro': 36, 'raw_patrimonio_configuracaocategoria': 50, 'raw_patrimonio_heranca': 2, 'raw_patrimonio_viatura': 2, 'raw_patrimonio_recheio': 18, 'raw_patrimonio_imovel': 1, 'raw_patrimonio_seguro': 10, 'raw_patrimonio_poupanca': 5, 'raw_patrimonio_credito': 5} | 129 | — |
| 2 | ✅ | {'raw_patrimonio_configuracaocategoria': 28} | 107 | — |

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*