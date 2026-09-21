-- Staging: espelho da entidade ConfiguracaoCategoria da app Base44 "Património" (app 6987c7e8dcf52dc2e3f18c42).
-- Dump lido de data/patrimonio/configuracaocategoria.csv (157 registos no total, 9 entidades).

with source as (
    select * from {{ source('raw', 'raw_patrimonio_configuracaocategoria') }}
)

select
    cast("id" as varchar) as "id",
    trim(cast("categoria" as varchar)) as "categoria",
    trim(cast("valor" as varchar)) as "valor",
    cast("ordem" as double) as "ordem",
    cast("created_date" as varchar) as "created_date",
    cast("updated_date" as varchar) as "updated_date",
    cast("created_by" as varchar) as "created_by",
    cast("created_by_id" as varchar) as "created_by_id"
from source
where "id" is not null
