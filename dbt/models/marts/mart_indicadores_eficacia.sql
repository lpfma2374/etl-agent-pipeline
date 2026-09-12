-- Mart final: espelho canónico do CSV 02_Indicadores_Eficacia.csv (zip Frameworks)
-- (publicado no Airtable, base Frameworks, tabela 'Indicadores Eficacia').

select * from {{ ref('stg_indicadores_eficacia') }}
