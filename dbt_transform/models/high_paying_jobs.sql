{{ config(materialized='table') }}

SELECT
    id,
    title,
    fully_remote,
    salary_from
FROM public.jobs
WHERE salary_from >= 15000
ORDER BY salary_from DESC