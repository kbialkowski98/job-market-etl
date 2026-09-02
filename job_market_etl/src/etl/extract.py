import json
import logging
import os
import time

import requests

from src import config
from src.utils.logger_setup import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


def extract_jobs() -> dict:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": config.USER_AGENT,
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

    while True:
        params = {
            "pageFrom": str(page),
            "pageTo": str(page),
            "pageSize": str(config.API_PAGE_SIZE),
            "withSalaryMatch": "true",
            "region": "pl",
            "salaryCurrency": "original",
            "salaryPeriod": "original",
        }
        
        payload = json.dumps(
            {
                "criteriaSearch": {"category": ["data"]},
                "pageSize": config.API_PAGE_SIZE,
                "withSalaryMatch": True,
            }
        )

        # Wykonanie zapytania z mechanizmem Retry
        for attempt in range(config.MAX_RETRIES):
            try:
                response = session.post(config.API_POST_URL, params=params, data=payload)
                response.raise_for_status()
                logger.info(f"Odpowiedz z API odebrana pomyslnie (strona {page}).")
                break

            except requests.exceptions.RequestException as e:
                logger.warning(f"Blad komunikacji z API (proba {attempt + 1}/{config.MAX_RETRIES}): {e}")

                if attempt == config.MAX_RETRIES - 1:
                    logger.error("Wyczerpano limit prob. Przerwanie skryptu.")
                    if e.response is not None:
                        logger.error(f"Tresc odpowiedzi: {e.response.text}")
                    raise

                sleep_time = (2 ** attempt) * config.BASE_BACKOFF_SECONDS
                logger.info(f"Czekam {sleep_time} sekund przed kolejna proba...")
                time.sleep(sleep_time)

        # Przetwarzanie poprawnej odpowiedzi
        page_json = response.json()
        postings = page_json.get("postings", [])

        if not postings:
            break

        all_postings.extend(postings)
        logger.info(f"Pobrano {len(postings)} ofert pracy ze strony {page}.")

        if len(postings) < config.API_PAGE_SIZE:
            break

        page += 1
        time.sleep(config.REQUEST_DELAY_SECONDS)

    result = {"postings": all_postings}

    # Zapis pobranych danych na dysk
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.RAW_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        logger.info(f"Zapisano surowe dane do pliku: {config.RAW_DATA_PATH}")
    except OSError as e:
        logger.error(f"Blad zapisu pliku: {e}")
        raise

    return result