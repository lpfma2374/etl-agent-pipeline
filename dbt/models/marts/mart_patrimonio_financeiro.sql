-- Mart final: Financeiro (app Base44 Património -> Cloudflare D1 base "patrimonio").

select * from {{ ref('stg_patrimonio_financeiro') }}
