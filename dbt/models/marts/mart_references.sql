-- Mart final: espelho canónico da tabela Airtable "References"
-- (publicado no Cloudflare D1 como tabela "References").

select * from {{ ref('stg_references') }}
