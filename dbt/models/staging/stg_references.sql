-- Staging: limpeza e tipagem da tabela Airtable "References".
-- Mantém os NOMES originais dos campos do Airtable (fidelidade ao destino).

with source as (
    select * from {{ source('raw', 'raw_references') }}
)

select
    cast("RefID" as integer)                    as "RefID",
    cast("_airtable_id" as text)                as "Airtable Record ID",
    cast("_airtable_created" as text)           as "Created Time",
    trim("Client Name")                         as "Client Name",
    "About the Client",
    "Challenge",
    "Solution",
    "Results",
    "Feedback",
    cast("Volume in Euros" as double)           as "Volume in Euros",
    cast("Number of Resources" as integer)      as "Number of Resources",
    "Area",
    cast("Form Response Edit URL" as text)      as "Form Response Edit URL",
    cast("Start Date" as text)                  as "Start Date",
    "Delivery",
    "Add document"
from source
where "RefID" is not null
