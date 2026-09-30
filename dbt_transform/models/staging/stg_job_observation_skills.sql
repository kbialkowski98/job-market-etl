{{ config(materialized='view') }}

select
    skills.job_id,
    skills.scraped_at,
     coalesce(skill_map.skill, skills.skill) as skill
from 
    {{ source('job_market', 'job_observation_skills') }} as skills
    left join {{ ref('skill_map') }} as skill_map on skills.skill = skill_map.raw_skill