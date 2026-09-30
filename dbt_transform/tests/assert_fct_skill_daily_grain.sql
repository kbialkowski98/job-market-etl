select
    scraped_at,
    skill
from 
    {{ ref('fct_skill_daily') }}
group by 
    scraped_at, skill
having 
    count(*) > 1