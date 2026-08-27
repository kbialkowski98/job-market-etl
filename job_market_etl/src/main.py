import logging

from extract import extract_jobs
from transform import transform_jobs
from load import load_jobs
from logger_setup import setup_logger

# 1. Konfiguracja logowania dla Orkiestratora
setup_logger()
logger = logging.getLogger(__name__)


def run_etl():
    logger.info("==== START PROCESU ETL ====")
    
    try:
        # Krok 1: Extract
        logger.info("-> Rozpoczynam Krok 1/3: Pobieranie danych...")
        raw_data = extract_jobs()
        
        # Krok 2: Transform
        logger.info("-> Rozpoczynam Krok 2/3: Transformacja i walidacja...")
        clean_data = transform_jobs(raw_data)
        
        # Krok 3: Load
        logger.info("-> Rozpoczynam Krok 3/3: Ładowanie do bazy danych...")
        load_jobs(clean_data)
        
        logger.info("==== PROCES ETL ZAKOŃCZONY POMYŚLNIE ====")
        
    except Exception as e:
        logger.error("==== BŁĄD: PROCES ETL PRZERWANY ====")
        logger.error(f"Szczegóły błędu: {e}")


if __name__ == "__main__":
    run_etl()