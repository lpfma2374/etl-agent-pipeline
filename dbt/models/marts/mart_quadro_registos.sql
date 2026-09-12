-- Mart final: espelho canónico do CSV 06_Quadro_Registos.csv (zip Frameworks)
-- (publicado no Airtable, base Frameworks, tabela 'Quadro Registos').

select * from {{ ref('stg_quadro_registos') }}
