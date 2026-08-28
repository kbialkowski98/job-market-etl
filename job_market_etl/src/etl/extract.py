import json
import logging
import os

import requests

from src import config
from src.utils.logger_setup import setup_logger

# Konfiguracja logowania
setup_logger()
logger = logging.getLogger(__name__)


def extract_jobs() -> dict:
    # Extract
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "application/json",
            "Content-Type": "application/infiniteSearch+json",
            "nfj-global-context": '{"region":"PL","lang":"pl","global_salary_match_enabled":true}',
        }
    )
    logger.info("Zainicjalizowano sesje HTTP.")

    session.get(config.API_BASE_URL)
    logger.info("Pobrano ciasteczka z API.")

    params = {
        "pageFrom": "1",
        "withSalaryMatch": "true",
        "pageTo": "1",
        "pageSize": "20",
        "region": "pl",
        "salaryCurrency": "original",
        "salaryPeriod": "original",
    }

    data = (
        '{"criteriaSearch":{"category":["data"]},"pageSize":20,"withSalaryMatch":true}'
    )

    try:
        response = session.post(config.API_POST_URL, params=params, data=data)
        response.raise_for_status()
        logger.info("Odpowiedz z API odebrana pomyslnie.")

        response_json = response.json()

        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.RAW_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(response_json, f, ensure_ascii=False, indent=4)

        logger.info(f"Zapisano surowe dane do pliku: {config.RAW_DATA_PATH}")

        return response_json

    except requests.exceptions.RequestException as e:
        logger.error(f"Blad komunikacji z API: {e}")
        if e.response is not None:
            logger.error(f"Tresc odpowiedzi: {e.response.text}")
        raise

    except OSError as e:
        logger.error(f"Blad zapisu pliku: {e}")
        raise
