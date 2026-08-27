import logging
import os
import config

def setup_logger():
    os.makedirs(config.LOG_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(config.LOG_FILE_PATH, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )