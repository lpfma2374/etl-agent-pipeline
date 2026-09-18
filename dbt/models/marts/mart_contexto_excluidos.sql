-- Mart final: contexto_excluidos do radar_de_alas.xlsx (base Airtable "Teste ETL").

select * from {{ ref('stg_contexto_excluidos') }}
