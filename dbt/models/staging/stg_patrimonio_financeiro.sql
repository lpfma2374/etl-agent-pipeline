-- Staging: espelho da entidade Financeiro da app Base44 "Património" (app 6987c7e8dcf52dc2e3f18c42).
-- Dump lido de data/patrimonio/financeiro.csv (157 registos no total, 9 entidades).

with source as (
    select * from {{ source('raw', 'raw_patrimonio_financeiro') }}
)

select
    cast("id" as varchar) as "id",
    trim(cast("tipo_movimento" as varchar)) as "tipo_movimento",
    trim(cast("descricao" as varchar)) as "descricao",
    trim(cast("categoria" as varchar)) as "categoria",
    cast("valor" as double) as "valor",
    trim(cast("debito_direto" as varchar)) as "debito_direto",
    trim(cast("titular" as varchar)) as "titular",
    trim(cast("imovel_associado" as varchar)) as "imovel_associado",
    trim(cast("viatura_associada" as varchar)) as "viatura_associada",
    cast("created_date" as varchar) as "created_date",
    cast("updated_date" as varchar) as "updated_date",
    cast("created_by" as varchar) as "created_by",
    cast("created_by_id" as varchar) as "created_by_id"
from source
where "id" is not null
