{{ config(materialized='table') }}

-- Rozbijamy listę i ujednolicamy tekst
WITH unnested_technologies AS (
    SELECT
        id,
        monthly_salary_avg,
        LOWER(TRIM(UNNEST(string_to_array(technologies, ',')))) AS raw_skill
    FROM 
        public.jobs
    WHERE 
        technologies IS NOT NULL 
        AND monthly_salary_avg IS NOT NULL
),

-- Czyszczenie
cleaned_technologies AS (
    SELECT
        id,
        monthly_salary_avg,
        -- MAPOWANIE
        CASE 
            WHEN raw_skill IN ('elt', 'etl/elt') THEN 'etl'
            WHEN raw_skill IN ('postgresql', 'postgres', 'mysql', 'oracle', 'pl/sql', 'spark sql') THEN 'sql'
            WHEN raw_skill IN ('ms excel', 'ms office', 'excel') THEN 'excel'
            WHEN raw_skill = 'google bigquery' THEN 'bigquery'
            WHEN raw_skill = 'data modelling' THEN 'data modeling'
            WHEN raw_skill IN ('k8s', 'kubernetes') THEN 'kubernetes'
            WHEN raw_skill IN ('azure', 'azure cloud', 'microsoft azure platform') THEN 'azure'
            WHEN raw_skill IN ('gcp', 'google cloud services') THEN 'gcp'
            WHEN raw_skill IN ('aws data platform', 'aws') THEN 'aws'
            WHEN raw_skill IN ('ai', 'ai/ml') THEN 'ai/ml'
            ELSE raw_skill
        END AS skill
    FROM 
        unnested_technologies
    -- CZARNA LISTA
    WHERE 
        raw_skill NOT IN (
            -- Role i ogólniki
            'dba', 'cybersecurity', 'data science', 'data engineering', 
            'cloud', 'ai', 'bi', 'machine learning', 'degree', 'architecture',
            'cloud platform', 'enterprise architect', 'sparx enterprise architect',
            -- Kompetencje miękkie i zarządzanie
            'communication skills', 'analytical skills', 'interpersonal skills', 
            'organizational skills', 'problem-solving', 'experimantation skills',
            'forecasting', 'resource management', 'user stories', 'finanse',
            'workday hcm certification',
            -- Metodyki i procesy
            'data analysis', 'data management', 'data governance', 
            'data migration', 'security', 'controlling', 'programming', 
            'ml expertise', 'data platform design', 'business inteligence', 
            'data processing', 'analytics', 'database', 'testing', 'data analytics', 
            'data visualization', 'big data', 'performance tuning', 'data quality', 
            'data structures', 'ai governance', 'statistical analysis'
        )
        AND raw_skill != ''
)

-- Gotowa tabela
SELECT
    skill,
    COUNT(id) AS job_count,
    ROUND(AVG(monthly_salary_avg)::numeric, 0) AS monthly_salary_avg
FROM 
    cleaned_technologies
GROUP BY 
    skill
HAVING 
    COUNT(id) >= 30
ORDER BY 
    job_count DESC