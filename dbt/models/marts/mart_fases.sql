-- Mart final: espelho canónico do CSV 03_Fases.csv (zip Frameworks)
-- (publicado no Airtable, base Frameworks, tabela 'Fases').

select * from {{ ref('stg_fases') }}
