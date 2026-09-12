-- Staging: limpeza e tipagem do CSV 01_Processos_Resumo.csv (zip Frameworks).
-- Mantém os NOMES originais das colunas (fidelidade ao destino Airtable).

with source as (
    select * from {{ source('raw', 'raw_processos_resumo') }}
)

select
    trim("ID Processo") as "ID Processo",
    cast("Nº Processo" as integer) as "Nº Processo",
    trim("Nome do Processo") as "Nome do Processo",
    cast("Versão" as double) as "Versão",
    trim("Data Versão") as "Data Versão",
    trim("Unidade Responsável") as "Unidade Responsável",
    trim("Pessoa Responsável") as "Pessoa Responsável",
    trim("Estado") as "Estado",
    trim("Objetivo") as "Objetivo",
    trim("Âmbito") as "Âmbito",
    trim("Processos Relacionados") as "Processos Relacionados",
    trim("Lista de Templates") as "Lista de Templates",
    trim("Data Criação") as "Data Criação",
    trim("Última Atualização") as "Última Atualização"
from source
where "ID Processo" is not null
