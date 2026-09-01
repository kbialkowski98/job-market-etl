import os

from dotenv import load_dotenv

load_dotenv()

REQUEST_DELAY_SECONDS = 1

API_BASE_URL = "https://nofluffjobs.com/pl"
API_POST_URL = "https://nofluffjobs.com/api/search/posting"

DATA_DIR = "data"
LOG_DIR = "logs"

RAW_DATA_PATH = f"{DATA_DIR}/raw_jobs.json"
VALIDATED_DATA_PATH = f"{DATA_DIR}/validated_jobs.json"
LOG_FILE_PATH = f"{LOG_DIR}/job_market_etl.log"

DB_URL = f"sqlite:///{DATA_DIR}/jobs.db"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

#extract.py
API_PAGE_SIZE = 100
REQUEST_DELAY_SECONDS = 1

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2