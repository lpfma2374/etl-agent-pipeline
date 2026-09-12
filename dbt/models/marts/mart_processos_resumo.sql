-- Mart final: espelho canónico do CSV 01_Processos_Resumo.csv (zip Frameworks)
-- (publicado no Airtable, base Frameworks, tabela 'Processos Resumo').

select * from {{ ref('stg_processos_resumo') }}
