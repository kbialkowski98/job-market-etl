{{ config(materialized='view') }}

{{ config(materialized='table') }}

select
    scraped_at,
    count(*) as total_jobs,
    round(
        100.0 * count(*) filter (where fully_remote) / count(*),
        2
    ) as remote_jobs_percentage,
    round(avg(monthly_salary_pln) filter (where seniority = 'Junior')::numeric, 0) as avg_pln_junior,
    round(avg(monthly_salary_pln) filter (where seniority = 'Mid')::numeric, 0) as avg_pln_mid,
    round(avg(monthly_salary_pln) filter (where seniority = 'Senior')::numeric, 0) as avg_pln_senior,
    round(avg(monthly_salary_pln) filter (where seniority = 'Expert')::numeric, 0) as avg_pln_expert,
    round(avg(monthly_salary_pln) filter (where seniority = 'Lead')::numeric, 0) as avg_pln_lead
from 
    {{ ref('stg_job_observations') }}
group by 
    scraped_at