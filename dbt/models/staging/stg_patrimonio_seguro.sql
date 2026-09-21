-- Staging: espelho da entidade Seguro da app Base44 "Património" (app 6987c7e8dcf52dc2e3f18c42).
-- Dump lido de data/patrimonio/seguro.csv (157 registos no total, 9 entidades).

with source as (
    select * from {{ source('raw', 'raw_patrimonio_seguro') }}
)

select
    cast("id" as varchar) as "id",
    trim(cast("tipo_seguro" as varchar)) as "tipo_seguro",
    trim(cast("seguradora" as varchar)) as "seguradora",
    trim(cast("apolice" as varchar)) as "apolice",
    cast("valor_anual" as double) as "valor_anual",
    trim(cast("titular" as varchar)) as "titular",
    trim(cast("imovel_associado" as varchar)) as "imovel_associado",
    trim(cast("viatura_associada" as varchar)) as "viatura_associada",
    cast("created_date" as varchar) as "created_date",
    cast("updated_date" as varchar) as "updated_date",
    cast("created_by" as varchar) as "created_by",
    cast("created_by_id" as varchar) as "created_by_id"
from source
where "id" is not null
