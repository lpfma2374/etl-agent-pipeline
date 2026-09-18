-- Mart final: metodologia do radar_de_alas.xlsx (base Airtable "Teste ETL").

select * from {{ ref('stg_metodologia') }}
