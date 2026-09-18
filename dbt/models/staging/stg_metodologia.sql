-- Staging: limpeza do Excel radar_de_alas.xlsx (sheet fonte de metodologia).
-- Títulos/subtítulos removidos no extract; linha de cabeçalho promovida a campos.

with source as (
    select * from {{ source('raw', 'raw_metodologia') }}
)

select
    cast("Metodologia_ID" as integer) as "Metodologia_ID",
    trim(cast("Tema" as varchar)) as "Tema",
    trim(cast("Descrição" as varchar)) as "Descrição"
from source
where "Metodologia_ID" is not null
