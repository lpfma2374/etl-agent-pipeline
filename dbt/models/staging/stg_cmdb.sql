-- Staging: limpeza e tipagem do CSV "All_CMDB.csv" (Google Drive).
-- Mantém os NOMES originais das colunas (fidelidade ao destino Airtable).

with source as (
    select * from {{ source('raw', 'raw_cmdb') }}
)

select
    cast("CMDB_ID" as integer)                                        as "CMDB_ID",
    trim("Business Area")                                             as "Business Area",
    trim("Associated Lot")                                            as "Associated Lot",
    trim("Way of working")                                            as "Way of working",
    trim("Associated product")                                        as "Associated product",
    "Functional description",
    trim("Multi-geography?")                                          as "Multi-geography?",
    trim("Maintenance")                                                as "Maintenance",
    trim("Operation")                                                 as "Operation",
    trim("Main technology stack")                                     as "Main technology stack",
    trim("Programming language")                                      as "Programming language",
    trim("End-user technology")                                       as "End-user technology",
    trim("PaaS")                                                      as "PaaS",
    trim("Orchestrator")                                              as "Orchestrator",
    trim("IaaS")                                                      as "IaaS",
    trim("CI/CD Pipeline automated?")                                 as "CI/CD Pipeline automated?",
    trim("API based?")                                                as "API based?",
    trim("Microservices based?")                                      as "Microservices based?",
    trim("Containerized?")                                            as "Containerized?",
    trim("Cloud Type")                                                as "Cloud Type",
    trim("CloudLevel")                                                as "CloudLevel",
    trim("Database technology")                                      as "Database technology",
    trim("# of databases")                                            as "# of databases",
    trim("Database size")                                             as "Database size",
    trim("Exposure to external network?")                             as "Exposure to external network?",
    trim("Personal data?")                                            as "Personal data?",
    trim("# of interfaces")                                           as "# of interfaces",
    trim("# users")                                                   as "# users",
    cast("Total # of incidents" as double)                           as "Total # of incidents",
    cast("# of critical incidents (Show-stopper and critical)" as double)
                                                                       as "# of critical incidents (Show-stopper and critical)",
    "Legal / regulatory application?",
    trim("Organization")                                              as "Organization"
from source
where "CMDB_ID" is not null
