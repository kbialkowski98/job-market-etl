import json
import logging
import os
import time

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

    all_postings = []
    page = 1
    page_size = 100

    # Pobieranie ofert pracy z API w pętli
    while True:
        params = {
            "pageFrom": str(page),
            "pageTo": str(page),
            "pageSize": str(page_size),
            "withSalaryMatch": "true",
            "region": "pl",
            "salaryCurrency": "original",
            "salaryPeriod": "original",
        }

        payload = json.dumps(
            {
                "criteriaSearch": {"category": ["data"]},
                "pageSize": page_size,
                "withSalaryMatch": True,
            }
        )

        try:
            response = session.post(config.API_POST_URL, params=params, data=payload)
            response.raise_for_status()
            logger.info(f"Odpowiedz z API odebrana pomyslnie (strona {page}).")
        except requests.exceptions.RequestException as e:
            logger.error(f"Blad komunikacji z API: {e}")
            if e.response is not None:
                logger.error(f"Tresc odpowiedzi: {e.response.text}")
            raise

        page_json = response.json()
        postings = page_json.get("postings", [])

        if not postings:
            break

        all_postings.extend(postings)
        logger.info(f"Pobrano {len(postings)} ofert pracy ze strony {page}.")

        if len(postings) < page_size:
            break

        page += 1
        time.sleep(config.REQUEST_DELAY_SECONDS)

    result = {"postings": all_postings}

    # Zapisanie surowych danych do pliku JSON
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.RAW_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        logger.info(f"Zapisano surowe dane do pliku: {config.RAW_DATA_PATH}")
    except OSError as e:
        logger.error(f"Blad zapisu pliku: {e}")
        raise

    return result
