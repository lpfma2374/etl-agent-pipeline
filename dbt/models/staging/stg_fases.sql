-- Staging: limpeza e tipagem do CSV 03_Fases.csv (zip Frameworks).
-- Mantém os NOMES originais das colunas (fidelidade ao destino Airtable).

with source as (
    select * from {{ source('raw', 'raw_fases') }}
)

select
    cast("Fase_ID" as integer) as "Fase_ID",
    trim("ID Processo") as "ID Processo",
    cast("Nº Processo" as integer) as "Nº Processo",
    trim("Nome do Processo") as "Nome do Processo",
    cast("Nº Fase" as integer) as "Nº Fase",
    trim("Título") as "Título",
    trim("Descrição") as "Descrição",
    trim("Questões-Chave") as "Questões-Chave",
    trim("Probabilidade") as "Probabilidade",
    trim("Fase Venda") as "Fase Venda",
    trim("Responsável") as "Responsável",
    trim("Participantes") as "Participantes",
    trim("Input") as "Input",
    trim("Output") as "Output",
    trim("Quando/Como") as "Quando/Como",
    trim("Destino") as "Destino",
    trim("Documentos Suporte") as "Documentos Suporte"
from source
where "Fase_ID" is not null
