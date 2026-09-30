{{ config(materialized='table') }}

select
    skills.scraped_at,
    skills.skill,
    count(*) as job_count,
    round(avg(observations.monthly_salary_pln)::numeric, 0) as avg_monthly_pln
from 
    {{ ref('stg_job_observation_skills') }} as skills
    join {{ ref('stg_job_observations') }} as observations
        on observations.id = skills.job_id
        and observations.scraped_at = skills.scraped_at
where 
    observations.monthly_salary_pln is not null
    and not exists (
    select 1
    from 
        {{ ref('skill_blocklist') }} as blocked
    where 
        blocked.skill = skills.skill
)
group by 
    skills.scraped_at,
    skills.skill