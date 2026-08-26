import json
import logging
import os
from typing import Optional

from pydantic import BaseModel, Field, computed_field

import config

# Konfiguracja struktury katalogów i logowania
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

logger = logging.getLogger(__name__)


class SalaryInfo(BaseModel):
    salary_from: Optional[float] = Field(default=None, alias="from")
    salary_to: Optional[float] = Field(default=None, alias="to")
    type: Optional[str] = None
    currency: Optional[str] = None

    @computed_field
    @property
    def salary_avg(self) -> Optional[float]:
        if self.salary_from is not None and self.salary_to is not None:
            return (self.salary_from + self.salary_to) / 2
        return None


class TilesValues(BaseModel):
    value: str
    type: str


class TilesInfo(BaseModel):
    values: list[TilesValues] = []


class JobPosting(BaseModel):
    id: str
    name: str
    title: str
    salary: Optional[SalaryInfo] = None
    fullyRemote: Optional[bool] = None
    seniority: Optional[list[str]] = None
    tiles: Optional[TilesInfo] = None


class NFJResponse(BaseModel):
    postings: list[JobPosting] = []


def transform_jobs():
    logger.info("Rozpoczynam proces transformacji (Transform)...")
    
    
    if not os.path.exists(config.RAW_DATA_PATH):
        logger.error(f"Nie znaleziono pliku: {config.RAW_DATA_PATH}. Uruchom najpierw extract.py!")
        return

    with open(config.RAW_DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    logger.info("Dane wczytane z dysku. Rozpoczynam walidację Pydantic...")

    try:
        validated_data = NFJResponse(**raw_data)
        
        jobs_count = len(validated_data.postings)
        logger.info(f"Sukces! Pomyślnie zwalidowano {jobs_count} ofert pracy.")
        
        if jobs_count > 0:
            with open(config.VALIDATED_DATA_PATH, "w", encoding="utf-8") as f:
                f.write(validated_data.model_dump_json(indent=4))
            logger.info(f"Zapisano zwalidowane dane do pliku: {config.VALIDATED_DATA_PATH}")
            
    except Exception as e:
        logger.error(f"Błąd walidacji danych: {e}")


if __name__ == "__main__":
    transform_jobs()