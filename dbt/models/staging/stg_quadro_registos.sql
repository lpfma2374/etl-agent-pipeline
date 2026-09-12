-- Staging: limpeza e tipagem do CSV 06_Quadro_Registos.csv (zip Frameworks).
-- Mantém os NOMES originais das colunas (fidelidade ao destino Airtable).

with source as (
    select * from {{ source('raw', 'raw_quadro_registos') }}
)

select
    cast("Registo_ID" as integer) as "Registo_ID",
    trim("ID Processo") as "ID Processo",
    cast("Nº Processo" as integer) as "Nº Processo",
    trim("Nome do Processo") as "Nome do Processo",
    trim("Item") as "Item",
    trim("Local de Arquivo") as "Local de Arquivo",
    trim("Acesso Leitura") as "Acesso Leitura",
    trim("Acesso Atualização") as "Acesso Atualização",
    trim("Responsável (Owner)") as "Responsável (Owner)",
    trim("Prazo de Retenção") as "Prazo de Retenção"
from source
where "Registo_ID" is not null
