-- Mart final: espelho canónico do CSV "All_CMDB.csv"
-- (publicado no Airtable, base CMDB, tabela "All CMDB").

select * from {{ ref('stg_cmdb') }}
