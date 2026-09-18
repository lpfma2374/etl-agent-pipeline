-- Staging: limpeza do Excel radar_de_alas.xlsx (sheet fonte de contexto_excluidos).
-- Títulos/subtítulos removidos no extract; linha de cabeçalho promovida a campos.

with source as (
    select * from {{ source('raw', 'raw_contexto_excluidos') }}
)

select
    cast("Excluido_ID" as integer) as "Excluido_ID",
    trim(cast("Nome" as varchar)) as "Nome",
    trim(cast("Idade" as varchar)) as "Idade",
    trim(cast("Posição" as varchar)) as "Posição",
    trim(cast("Clube / Liga" as varchar)) as "Clube / Liga",
    trim(cast("Motivo da exclusão" as varchar)) as "Motivo da exclusão"
from source
where "Excluido_ID" is not null
