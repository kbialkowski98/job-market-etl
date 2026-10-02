Python trzyma w public tabele jobs, job_observations, job_observation_skills i fx_rates. dbt ich nie tworzy. Czyta je przez sources.yml.
stg_job_observations to oferta w dniu zrzutu, z pensją razy kurs NBP. stg_job_observation_skills to skill po mapie (postgres staje się postgresql).
fct_market_daily ma jeden wiersz na scraped_at. fct_skill_daily ma jeden wiersz na skill w tym dniu. Lista skill_blocklist wycina role w rodzaju ai.
Uruchomienie, z katalogu job_market_etl, po uzupełnieniu .env:

```bash
set -a
source .env
set +a
cd ../dbt_transform
dbt build --profiles-dir .
```

dbt nie czyta pliku .env sam. Port w profiles.yml to 5432.