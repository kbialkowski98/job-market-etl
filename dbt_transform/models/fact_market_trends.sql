{{ config(materialized='table') }}

SELECT
    published_at::date AS snapshot_date,
    COUNT(id) AS total_jobs,
    ROUND(
        (SUM(CASE WHEN fully_remote = true THEN 1 ELSE 0 END)::decimal / COUNT(id)) * 100, 
        2
    ) AS remote_jobs_percentage,
    ROUND(
        AVG(CASE WHEN LOWER(seniority) LIKE '%junior%' THEN monthly_salary_avg END)::numeric, 0
    ) AS avg_salary_junior,
    ROUND(
        AVG(CASE WHEN LOWER(seniority) LIKE '%mid%' OR LOWER(seniority) LIKE '%regular%' THEN monthly_salary_avg END)::numeric, 0
    ) AS avg_salary_mid,
    ROUND(
        AVG(CASE WHEN LOWER(seniority) LIKE ANY(ARRAY['%senior%', '%expert%', '%lead%']) THEN monthly_salary_avg END)::numeric, 0
    ) AS avg_salary_senior
FROM 
    public.jobs
WHERE 
    published_at IS NOT NULL
GROUP BY 
    published_at::date
ORDER BY 
    snapshot_date