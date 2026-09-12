-- Staging: limpeza e tipagem do CSV 04_Subseccoes_Fases.csv (zip Frameworks).
-- Mantém os NOMES originais das colunas (fidelidade ao destino Airtable).

with source as (
    select * from {{ source('raw', 'raw_subseccoes_fases') }}
)

select
    cast("Subseccao_ID" as integer) as "Subseccao_ID",
    trim("ID Processo") as "ID Processo",
    cast("Nº Processo" as integer) as "Nº Processo",
    trim("Nome do Processo") as "Nome do Processo",
    cast("Nº Fase" as integer) as "Nº Fase",
    trim("Título Fase") as "Título Fase",
    trim("Subtítulo") as "Subtítulo",
    trim("Conteúdo") as "Conteúdo"
from source
where "Subseccao_ID" is not null
