-- Mart final: espelho canónico do CSV 05_Historico_Versoes.csv (zip Frameworks)
-- (publicado no Airtable, base Frameworks, tabela 'Historico Versoes').

select * from {{ ref('stg_historico_versoes') }}
