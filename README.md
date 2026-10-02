# Rynek pracy data — dzienne ETL

Codzienny zrzut ofert z kategorii `data` na [NoFluffJobs](https://nofluffjobs.com/pl). Python pobiera, waliduje i ładuje historię do Postgresa oraz surowe pliki do Azure Blob. dbt buduje z tego dzienne zestawienia rynku i skilli.

Oferta, która zniknęła z API, zostaje w historii. Drugi przebieg tego samego dnia aktualizuje wiersz z tej daty i nie rusza poprzednich dni.

## Przebieg

1. **Extract.** Paginacja API, trzy próby, odstęp rośnie wykładniczo.
2. **Transform.** Pydantic odrzuca rekord bez tytułu i idzie dalej. Pensja roczna, tygodniowa, dzienna i godzinowa schodzi na miesiąc. Z kafelków zostają tylko wymagania (`requirement`), zapisane małymi literami.
3. **Load.** Jedna transakcja: aktualny stan oferty, obserwacja dnia, skille tego dnia i kursy. Spadek liczby ofert o co najmniej 40% względem wczoraj przerywa zapis, zanim powstanie `INSERT`.
4. **dbt.** Staging liczy pensję w PLN i podmienia synonimy skilli. Marty agregują dzień.

Surowy JSON i wersja po walidacji lądują w Azure jako `raw/RRRR/MM/DD/jobs.json` i `validated/RRRR/MM/DD/jobs.json`. Przełączniki `SAVE_JSON_LOCAL`, `SAVE_JSON_CLOUD` i `SAVE_TO_DATABASE` są w `job_market_etl/src/config.py`.

## Tabele

Wszystko w schemacie `public`. Python tworzy brakujące tabele przez `create_all`. To nie zmienia kolumn, które już istnieją.

| Tabela | Ziarno | Znaczenie |
| --- | --- | --- |
| `jobs` | `id` | Ostatni znany stan oferty |
| `job_observations` | `id`, `scraped_at` | Oferta tak, jak wyglądała danego dnia |
| `job_observation_skills` | `job_id`, `scraped_at`, `skill` | Skille oferty w tym dniu. Lista może się skurczyć, więc dzisiejsze wiersze ofert z paczki są kasowane i wstawiane od nowa |
| `fx_rates` | `rate_date`, `currency` | Kurs NBP, tabela A. `rate_date` to dzień zrzutu, `effective_date` to dzień publikacji NBP. PLN ma kurs `1.0` i źródło `identity` |

`scraped_at` jest liczone raz w `main.py` i przekazane do loadu.

W dbt:

- `stg_job_observations` mnoży `monthly_salary_avg` przez kurs z dnia zrzutu.
- `stg_job_observation_skills` podmienia synonim ze słownika (`postgres` → `postgresql`, `k8s` → `kubernetes`). Brak synonimu zostawia surową nazwę.
- `fct_market_daily` to jeden wiersz na dzień: liczba ofert, udział remote, średnia pensja w PLN dla Junior, Mid, Senior, Expert i Lead.
- `fct_skill_daily` to jeden wiersz na skill i dzień. Seed `skill_blocklist` wycina kategorie `ai` i `data engineering`, nie synonimy.

## Uruchomienie lokalne

Z katalogu `job_market_etl`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary

cp .env.example .env
```

Uzupełnij `.env`. Potem testy i ETL:

```bash
python -m pytest tests/test_salary.py -q
python -m src.main
```

dbt nie czyta pliku `.env`. Zmienne trzeba wyeksportować, a port w `dbt_transform/profiles.yml` jest wpisany na sztywno jako `5432`.

```bash
set -a
source .env
set +a
cd ../dbt_transform
dbt build --profiles-dir .
```

`dbt build` odpala seedy, modele i testy. Test dbt pada, gdy zapytanie zwróci jakikolwiek wiersz albo gdy `scraped_at` w `fct_market_daily` nie jest unikalne.

## GitHub Actions

Workflow `Daily Job Market ETL` startuje codziennie o 03:00 UTC i ręcznie przez `workflow_dispatch`. Kolejność: instalacja, `pytest`, ETL, `dbt build`. Czerwony test zatrzymuje load. Secrety mają te same nazwy co zmienne w `.env.example`.
