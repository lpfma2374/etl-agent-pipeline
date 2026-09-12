-- Mart final: espelho canónico do CSV 04_Subseccoes_Fases.csv (zip Frameworks)
-- (publicado no Airtable, base Frameworks, tabela 'Subseccoes Fases').

select * from {{ ref('stg_subseccoes_fases') }}
