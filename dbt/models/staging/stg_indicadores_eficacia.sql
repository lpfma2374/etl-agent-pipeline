-- Staging: limpeza e tipagem do CSV 02_Indicadores_Eficacia.csv (zip Frameworks).
-- Mantém os NOMES originais das colunas (fidelidade ao destino Airtable).

with source as (
    select * from {{ source('raw', 'raw_indicadores_eficacia') }}
)

select
    cast("Indicador_ID" as integer) as "Indicador_ID",
    trim("ID Processo") as "ID Processo",
    cast("Nº Processo" as integer) as "Nº Processo",
    trim("Nome do Processo") as "Nome do Processo",
    trim("Indicador") as "Indicador"
from source
where "Indicador_ID" is not null
