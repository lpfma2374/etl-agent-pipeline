-- Staging: limpeza e tipagem do CSV 05_Historico_Versoes.csv (zip Frameworks).
-- Mantém os NOMES originais das colunas (fidelidade ao destino Airtable).

with source as (
    select * from {{ source('raw', 'raw_historico_versoes') }}
)

select
    cast("Versao_ID" as integer) as "Versao_ID",
    trim("ID Processo") as "ID Processo",
    cast("Nº Processo" as integer) as "Nº Processo",
    trim("Nome do Processo") as "Nome do Processo",
    cast("Versão" as double) as "Versão",
    trim("Descrição") as "Descrição",
    trim("Data") as "Data",
    trim("Implicações") as "Implicações"
from source
where "Versao_ID" is not null
