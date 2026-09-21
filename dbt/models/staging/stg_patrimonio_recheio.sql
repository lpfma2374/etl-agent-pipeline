-- Staging: espelho da entidade Recheio da app Base44 "Património" (app 6987c7e8dcf52dc2e3f18c42).
-- Dump lido de data/patrimonio/recheio.csv (157 registos no total, 9 entidades).

with source as (
    select * from {{ source('raw', 'raw_patrimonio_recheio') }}
)

select
    cast("id" as varchar) as "id",
    trim(cast("descricao" as varchar)) as "descricao",
    trim(cast("tipo_recheio" as varchar)) as "tipo_recheio",
    trim(cast("imovel_associado" as varchar)) as "imovel_associado",
    trim(cast("titular" as varchar)) as "titular",
    cast("valor_aquisicao" as double) as "valor_aquisicao",
    cast("sinal" as double) as "sinal",
    cast("valor_credito" as double) as "valor_credito",
    cast("valor_atual" as double) as "valor_atual",
    cast("valor_avaliacao" as double) as "valor_avaliacao",
    cast("created_date" as varchar) as "created_date",
    cast("updated_date" as varchar) as "updated_date",
    cast("created_by" as varchar) as "created_by",
    cast("created_by_id" as varchar) as "created_by_id"
from source
where "id" is not null
