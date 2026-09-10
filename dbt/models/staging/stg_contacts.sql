-- Staging: limpeza e tipagem a partir do schema raw.
-- O nome da tabela raw é parametrizado por variável dbt
-- (ver models/staging/sources.yml) — ajustar por migração.

with source as (
    select * from {{ source('raw', 'raw_contacts') }}
)

select
    cast(id as integer)      as id,
    trim(lower(name))        as name,
    lower(trim(email))       as email,
    cast(created_at as text) as created_at
from source
where email is not null
