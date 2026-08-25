import os
import json
import requests
import logging

os.makedirs("job_market_etl/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("job_market_etl/logs/job_market_etl.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

URL = "https://nofluffjobs.com/pl"
URL_POST = "https://nofluffjobs.com/api/search/posting"

def extract_jobs():
    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "application/json",
        "Content-Type": "application/infiniteSearch+json",
        "nfj-global-context": '{"region":"PL","lang":"pl","global_salary_match_enabled":true}'
    })

    logger.info("Sesja zainicjalizowana.")

    session.get(URL)
    logger.info("Pobrano ciasteczka")

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

    try:
        response = session.post(URL_POST, params=params, data=data)

        response.raise_for_status()
        logger.info("Odpowiedź otrzymana pomyślnie.")

        response_json = response.json()

        os.makedirs("job_market_etl/data", exist_ok=True)
        with open("job_market_etl/data/raw_jobs.json", "w", encoding="utf-8") as f:
            json.dump(response_json, f, ensure_ascii=False, indent=4)
        logger.info("Dane zapisane do pliku raw_jobs.json")

    except requests.exceptions.RequestException as e:
        logger.error(f"Wystąpił błąd: {e}")
        if e.response is not None:
            logger.error(f"Treść odpowiedzi: {e.response.text}")

    except OSError as e:
        logger.error(f"Wystąpił błąd podczas zapisywania pliku: {e}")

if __name__ == "__main__":
    extract_jobs()
