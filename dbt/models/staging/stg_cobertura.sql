-- Staging: limpeza do Excel radar_de_alas.xlsx (sheet fonte de cobertura).
-- Títulos/subtítulos removidos no extract; linha de cabeçalho promovida a campos.

with source as (
    select * from {{ source('raw', 'raw_cobertura') }}
)

select
    cast("Cobertura_ID" as integer) as "Cobertura_ID",
    trim(cast("País" as varchar)) as "País",
    trim(cast("Competição" as varchar)) as "Competição",
    trim(cast("Estado" as varchar)) as "Estado",
    trim(cast("Nota" as varchar)) as "Nota"
from source
where "Cobertura_ID" is not null
