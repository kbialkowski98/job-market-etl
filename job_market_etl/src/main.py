import logging
import datetime

from src import config
from src.utils.file_io import save_json
from src.utils.azure_storage import upload_to_blob
from src.etl.extract import extract_jobs
from src.etl.load import load_jobs
from src.etl.transform import transform_jobs
from src.utils.logger_setup import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

def run_etl():
    logger.info("Rozpoczecie procesu ETL.")
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")

    try:
        # --- ETAP 1: EXTRACT ---
        logger.info("Etap 1: Pobieranie danych (Extract).")
        raw_data = extract_jobs()

        if config.SAVE_JSON_LOCAL or config.SAVE_JSON_CLOUD:
            save_json(raw_data, config.RAW_DATA_PATH)

        if config.SAVE_JSON_CLOUD:
            upload_to_blob(config.RAW_DATA_PATH, config.AZURE_RAW_CONTAINER, f"raw_jobs_{today_str}.json")

        # --- ETAP 2: TRANSFORM ---
        logger.info("Etap 2: Transformacja i walidacja (Transform).")
        clean_data = transform_jobs(raw_data)

        if config.SAVE_JSON_LOCAL or config.SAVE_JSON_CLOUD:
            clean_data_save = [job.model_dump() for job in clean_data]
            save_json(clean_data_save, config.VALIDATED_DATA_PATH)

        if config.SAVE_JSON_CLOUD:
            upload_to_blob(config.VALIDATED_DATA_PATH, config.AZURE_TRANSFORMED_CONTAINER, f"validated_jobs_{today_str}.json")

        # --- ETAP 3: LOAD ---
        logger.info("Etap 3: Zapis do bazy (Load).")
        if config.SAVE_TO_DATABASE:
            load_jobs(clean_data, today)

        logger.info("Proces ETL zakonczony pomyslnie.")

    except Exception as e:
        logger.error(f"Proces ETL przerwany z powodu bledu: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    run_etl()