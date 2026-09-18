# Execução ETL — Radar de Alas (Excel → Airtable 'Teste ETL')

- **Data:** 2026-09-18 17:27–17:31 UTC
- **Origem:** `radar-de-alas.xlsx` (anexado no chat, 4 sheets: Prospetos, Contexto (excluídos), Cobertura, Metodologia e lacunas)
- **Transformação:** removidas as linhas iniciais de título/subtítulo/descrição de cada sheet (skiprows 3/2/2/2); a linha de cabeçalho foi promovida a nomes de campos. A sheet 'Metodologia e lacunas' não tem linha de cabeçalho — nomes atribuídos (`Tema`, `Descrição`). ExcelExtractor estendido com `skiprows` e `headers`.
- **Destino:** Airtable base NOVA **'Teste ETL'** (`appoxVujvUYs123Dr`, workspace wspjH5AkyLLP6J7Xv), 4 tabelas: Prospetos (3), Contexto (excluídos) (3), Cobertura (10), Metodologia e lacunas (7)
- **PKs posicionais:** Prospeto_ID, Excluido_ID, Cobertura_ID, Metodologia_ID (1..n)
- **Lotes:** 1 lote sequencial de 23 registos, limite fixo 50
- **Validação:** GE 4/4 checkpoints (schema espelho, PK não nula, PK única, volume) sobre o parquet exportado; dbt 8/8 modelos OK
- **Carga:** 23 registos carregados (upsert por PK posicional); idempotência verificada com re-run (23/23, zero duplicados)
- **Config:** `config/pipeline.radar_xlsx_airtable.json`
- **Nota:** a Web API da Airtable não permite apagar tabelas; a 1ª tabela ('Prospetos') foi pré-criada tipada no POST /meta/bases, as restantes 3 criadas pelo loader por dtypes. Base de teste anterior `apphJddGtLU7e4cM5` (com placeholder zz_setup) ficou órfã — token sem permissão de apagar bases; eliminável manualmente no UI.
