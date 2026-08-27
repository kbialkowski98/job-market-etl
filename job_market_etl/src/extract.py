import json
import logging
import os

import requests

import config
from logger_setup import setup_logger


# Logger setup
setup_logger()

logger = logging.getLogger(__name__)

def extract_jobs() -> dict:
    # 1. Inicjalizacja sesji i ustawienie nagłówków
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "application/json",
        "Content-Type": "application/infiniteSearch+json",
        "nfj-global-context": '{"region":"PL","lang":"pl","global_salary_match_enabled":true}'
    })
    logger.info("Sesja zainicjalizowana.")

    # 2. Odwiedzenie strony głównej w celu pobrania ciasteczek
    session.get(config.API_BASE_URL)
    logger.info("Pobrano ciasteczka.")

    # 3. Przygotowanie parametrów zapytania i payloadu
    params = {
        'pageFrom': '1',
        'withSalaryMatch': 'true',
        'pageTo': '1',
        'pageSize': '20',
        'region': 'pl',
        'salaryCurrency': 'original',
        'salaryPeriod': 'original',
    }

    data = '{"criteriaSearch":{"category":["data"]},"pageSize":20,"withSalaryMatch":true}'

    # 4. Komunikacja z API i zapis danych
    try:
        response = session.post(config.API_POST_URL, params=params, data=data)
        response.raise_for_status()
        logger.info("Odpowiedź otrzymana pomyślnie.")

        response_json = response.json()

        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.RAW_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(response_json, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Dane zapisane do pliku: {config.RAW_DATA_PATH}")

        return response_json

    except requests.exceptions.RequestException as e:
        logger.error(f"Wystąpił błąd komunikacji z API: {e}")
        if e.response is not None:
            logger.error(f"Treść odpowiedzi: {e.response.text}")
        raise

    except OSError as e:
        logger.error(f"Wystąpił błąd podczas zapisywania pliku: {e}")
        raise