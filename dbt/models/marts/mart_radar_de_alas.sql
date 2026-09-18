{{ config(materialized='table') }}
select * from read_parquet('wizard/6aad5a6631e8c2f2f1ca6b8/transformed.parquet')
