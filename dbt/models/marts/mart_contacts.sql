-- Mart final: modelo canónico que o loader publica no destino.
select
    id,
    name,
    email,
    created_at
from {{ ref('stg_contacts') }}
