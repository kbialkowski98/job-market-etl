import json
import logging
import os

from src.utils.logger_setup import setup_logger


setup_logger()
logger = logging.getLogger(__name__)


def save_json(data: dict | list, file_path: str) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logger.info(f"Zapisano dane do pliku: {file_path}")

    except OSError as e:
        logger.error(f"Blad zapisu do pliku {file_path}: {e}")
        raise
