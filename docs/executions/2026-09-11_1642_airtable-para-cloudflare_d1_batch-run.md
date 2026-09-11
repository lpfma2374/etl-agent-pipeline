# Batch-run 2026-09-11_1642 — airtable → cloudflare_d1 (batch_size=50)

- **Data:** 2026-09-11T16:42:35+00:00
- **Lotes:** 1 executados | ✅ 0 | ❌ 1
- **Linhas entregues no destino (novas):** 0
- **Contagem cumulativa no destino:** {}
- **Plano previsto:** {'raw_references': None}

| Lote | Estado | Linhas (raw) | Novas no destino | Erro |
|---|---|---|---|---|
| 1 | ❌ | {'raw_references': 9} | — | 400 Client Error: Bad Request for url: https://api.cloudflare.com/client/v4/accounts/5c3d027465d3d00e9fe5362270eb226b/d1 |

<details><summary>Erro do lote 1</summary>

```
n_pipeline.py", line 99, in cmd_load
    rows = loader.load(df, table)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/app/conversations/6aa334725d5b4135ae83ecb3/etl-agent-pipeline/extract/loaders/cloudflare_d1.py", line 65, in load
    self._api("POST", "query", json={"sql": sql, "params": params})
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: https://api.cloudflare.com/client/v4/accounts/5c3d027465d3d00e9fe5362270eb226b/d1/database/61ecfa25-9270-4c57-b5d5-3df7f6006c64/query

```
</details>

*Cada lote percorreu o pipeline completo (extract → dbt → Great Expectations → load → report).*
*Lote falhado: registado e seguiu-se o lote seguinte — o destino só recebe lotes validados.*