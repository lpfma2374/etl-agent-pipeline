-- Staging: limpeza do Excel radar_de_alas.xlsx (sheet fonte de prospetos).
-- Títulos/subtítulos removidos no extract; linha de cabeçalho promovida a campos.

with source as (
    select * from {{ source('raw', 'raw_prospetos') }}
)

select
    cast("Prospeto_ID" as integer) as "Prospeto_ID",
    trim(cast("Nome do jogador" as varchar)) as "Nome do jogador",
    trim(cast("Nacionalidade" as varchar)) as "Nacionalidade",
    trim(cast("Idade" as varchar)) as "Idade",
    trim(cast("Posição" as varchar)) as "Posição",
    trim(cast("Clube atual" as varchar)) as "Clube atual",
    trim(cast("Liga onde atua" as varchar)) as "Liga onde atua",
    trim(cast("Valor atual de mercado" as varchar)) as "Valor atual de mercado",
    trim(cast("Valor potencial" as varchar)) as "Valor potencial",
    trim(cast("Principais dados de desempenho (últimos 3 anos)" as varchar)) as "Principais dados de desempenho (últimos 3 anos)",
    trim(cast("Agente" as varchar)) as "Agente",
    trim(cast("Contrato atual" as varchar)) as "Contrato atual",
    trim(cast("Vencimento atual" as varchar)) as "Vencimento atual"
from source
where "Prospeto_ID" is not null
