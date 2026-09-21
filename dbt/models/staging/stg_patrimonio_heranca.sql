-- Staging: espelho da entidade Heranca da app Base44 "Património" (app 6987c7e8dcf52dc2e3f18c42).
-- Dump lido de data/patrimonio/heranca.csv (157 registos no total, 9 entidades).

with source as (
    select * from {{ source('raw', 'raw_patrimonio_heranca') }}
)

select
    cast("id" as varchar) as "id",
    trim(cast("bem_heranca" as varchar)) as "bem_heranca",
    trim(cast("descritivo" as varchar)) as "descritivo",
    trim(cast("data_posse" as varchar)) as "data_posse",
    trim(cast("em_tribunal" as varchar)) as "em_tribunal",
    trim(cast("titular" as varchar)) as "titular",
    cast("valor_bem" as double) as "valor_bem",
    cast("created_date" as varchar) as "created_date",
    cast("updated_date" as varchar) as "updated_date",
    cast("created_by" as varchar) as "created_by",
    cast("created_by_id" as varchar) as "created_by_id"
from source
where "id" is not null
