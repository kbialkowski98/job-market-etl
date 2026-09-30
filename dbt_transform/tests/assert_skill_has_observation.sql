select
    skills.job_id,
    skills.scraped_at
from 
    {{ ref('stg_job_observation_skills') }} as skills
    left join {{ ref('stg_job_observations') }} as observations
        on observations.id = skills.job_id
        and observations.scraped_at = skills.scraped_at
where 
    observations.id is null