import logging

from src.etl.extract import extract_jobs
from src.etl.load import load_jobs
from src.etl.transform import transform_jobs
from src.utils.logger_setup import setup_logger

# Konfiguracja logowania
setup_logger()
logger = logging.getLogger(__name__)


def run_etl():
    logger.info("Rozpoczecie procesu ETL.")

    try:
        logger.info("Etap 1: Pobieranie danych (Extract).")
        raw_data = extract_jobs()

        logger.info("Etap 2: Transformacja i walidacja (Transform).")
        clean_data = transform_jobs(raw_data)

        logger.info("Etap 3: Zapis do bazy (Load).")
        load_jobs(clean_data)

        logger.info("Proces ETL zakonczony pomyslnie.")

    except Exception as e:
        logger.error(f"Proces ETL przerwany z powodu bledu: {e}")


if __name__ == "__main__":
    run_etl()
