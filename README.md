# Dzienny ETL ofert pracy

Projekt monitoruje rynek pracy w kategorii data na NoFluffJobs (liczba ogłoszeń, udział pracy zdalnej, widełki płacowe wg doświadczenia i popularność technologii).

Python pobiera dane z API, waliduje je i ładuje historię do PostgreSQL oraz kopie JSON do Azure Blob Storage. Następnie dbt generuje dzienne modele analityczne. Całość jest idempotentna - ponowne uruchomienie w tym samym dniu aktualizuje bieżący rekord, nie naruszając historii, a usunięte z portalu oferty pozostają w bazie.

## Przebieg

1. **Extract.** Paginacja API z mechanizmem ponawiania.
2. **Transform.** Walidacja Pydantic (odrzucenie rekordów bez tytułu), normalizacja stawek (rocznych, tygodniowych, dziennych i godzinowych) do kwoty miesięcznej oraz ekstrakcja wymagań technicznych.
3. **Load.** Jedna transakcja: aktualny stan oferty, obserwacja dnia, wymagania tego dnia i kursy NBP. Spadek liczby ofert o co najmniej 40% względem wczoraj przerywa zapis, zanim cokolwiek wejdzie do bazy.
4. **dbt.** Przeliczenie stawek na PLN, standaryzacja synonimów skilli i budowa zagregowanych martów.

Surowy JSON i wersja po walidacji lądują w Azure jako `raw/RRRR/MM/DD/jobs.json` i `validated/RRRR/MM/DD/jobs.json`. Przełączniki `SAVE_JSON_LOCAL`, `SAVE_JSON_CLOUD` i `SAVE_TO_DATABASE` są w `job_market_etl/src/config.py`.

## Tabele

Wszystko w schemacie `public`. Python tworzy brakujące tabele przez `create_all`. To nie zmienia kolumn, które już istnieją.

| Tabela | Klucz główny | Znaczenie |
| --- | --- | --- |
| `jobs` | `id` | Ostatni znany stan oferty |
| `job_observations` | `id`, `scraped_at` | Oferta tak, jak wyglądała danego dnia |
| `job_observation_skills` | `job_id`, `scraped_at`, `skill` | Wymagania oferty w tym dniu. Lista może się skurczyć, więc dzisiejsze wiersze ofert z paczki są kasowane i wstawiane od nowa |
| `fx_rates` | `rate_date`, `currency` | Kursy walut, które występują w ofertach. Pobierane z NBP |

`scraped_at` jest liczone raz w `main.py` i przekazane do loadu.

## Modele dbt

| Model | Znaczenie |
| --- | --- |
| `stg_job_observations` | Widok. Oferta z danego dnia, pensja miesięczna razy kurs NBP |
| `stg_job_observation_skills` | Widok. Wymaganie po słowniku synonimów. Brak synonimu zostawia surową nazwę |
| `fct_market_daily` | Tabela. Jeden wiersz na dzień: liczba ofert, udział remote, średnie pensje |
| `fct_skill_daily` | Tabela. Jeden wiersz na wymaganie i dzień. `ai` i `data engineering` to kategorie z ogłoszenia, nie technologie, więc nie wchodzą do rankingu |

## Przykład wyniku

Jeden wiersz `fct_market_daily` to jeden dzień zrzutu. Średnie są miesięczne i już w PLN, po kursie NBP. Oferty bez pensji wchodzą do liczby ofert i udziału pracy zdalnej, ale nie do średniej.

| scraped_at | total_jobs | remote_jobs_percentage | avg_pln_junior | avg_pln_mid | avg_pln_senior | avg_pln_expert | avg_pln_lead |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-15 | 3069 | 86.74 | 16037 | 21511 | 25472 | 27529 | 29600 |
| 2026-10-14 | 3059 | 86.47 | 16037 | 21471 | 25660 | 27909 | 29600 |
| 2026-10-13 | 3027 | 86.75 | 16705 | 21371 | 25636 | 27570 | 29723 |

## Uruchomienie lokalne

Z katalogu `job_market_etl`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Uzupełnij `.env`. Potem testy i ETL:

```bash
python -m pytest tests/test_salary.py -q
python -m src.main
```

Po ETL odpal dbt. Najpierw wyeksportuj zmienne z `.env`, potem zbuduj modele:

```bash
set -a
source .env
set +a
cd ../dbt_transform
dbt build --profiles-dir .
```

`dbt build` ładuje seedy, buduje modele i uruchamia testy. Połączenie idzie na port `5432`.

## GitHub Action

Workflow startuje codziennie o 03:00 UTC lub można go odpalić ręcznie. Testy wykonują się przed pobraniem ofert. Nieudany pytest zatrzymuje dalszy proces, więc do bazy nic nie trafia. Po zapisie danych uruchamiane jest `dbt build`.
