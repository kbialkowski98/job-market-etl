{{ config(materialized='view') }}

select
    job_observations.id,
    job_observations.scraped_at,
    job_observations.title,
    job_observations.seniority,
    job_observations.fully_remote,
    job_observations.salary_currency,
    job_observations.monthly_salary_avg,
    job_observations.monthly_salary_avg * fx_rates.rate_pln as monthly_salary_pln
from 
    {{source('job_market', 'job_observations')}} as job_observations
    left join {{source('job_market', 'fx_rates')}} as fx_rates
        on fx_rates.currency = job_observations.salary_currency
        and fx_rates.rate_date = job_observations.scraped_at