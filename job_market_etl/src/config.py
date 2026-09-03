import os
from dotenv import load_dotenv

from sqlalchemy.engine import URL

# Wczytanie zmiennych środowiskowych
load_dotenv()


# KONFIGURACJA ŚCIEŻEK I KATALOGÓW
DATA_DIR = "data"
LOG_DIR = "logs"

RAW_DATA_PATH = f"{DATA_DIR}/raw_jobs.json"
VALIDATED_DATA_PATH = f"{DATA_DIR}/validated_jobs.json"
LOG_FILE_PATH = f"{LOG_DIR}/job_market_etl.log"


# KONFIGURACJA BAZ DANYCH
DB_DRIVER = os.getenv("DB_DRIVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if DB_USER and DB_PASSWORD:
    DB_URL = URL.create(
        drivername=DB_DRIVER,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
else:
    DB_URL = None


# KONFIGURACJA API
API_BASE_URL = "https://nofluffjobs.com/pl"
API_POST_URL = "https://nofluffjobs.com/api/search/posting"


# EXTRACT.PY
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
API_PAGE_SIZE = 100
REQUEST_DELAY_SECONDS = 1

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2


# KONFIGURACJA CHMURY (AZURE BLOB STORAGE)
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_RAW_CONTAINER = "raw-data"
AZURE_TRANSFORMED_CONTAINER = "transformed-data"


# FEATURE TOGGLES
SAVE_JSON_LOCAL = False
SAVE_JSON_CLOUD = True
SAVE_TO_DATABASE = True
