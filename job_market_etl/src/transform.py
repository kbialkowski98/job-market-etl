import json
import logging
import os
from typing import Optional

from pydantic import BaseModel, Field, computed_field

import config
from logger_setup import setup_logger

# Logger setup
setup_logger()

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


def transform_jobs(raw_data: dict) -> list[JobPosting]:
    logger.info("Rozpoczynam proces transformacji (Transform)...")
    logger.info("Rozpoczynam walidację Pydantic...")

    try:
        validated_data = NFJResponse(**raw_data)
        
        jobs_count = len(validated_data.postings)
        logger.info(f"Sukces! Pomyślnie zwalidowano {jobs_count} ofert pracy.")
        
        if jobs_count > 0:
            with open(config.VALIDATED_DATA_PATH, "w", encoding="utf-8") as f:
                f.write(validated_data.model_dump_json(indent=4))
            logger.info(f"Zapisano zwalidowane dane do pliku: {config.VALIDATED_DATA_PATH}")
            
        return validated_data.postings
            
    except Exception as e:
        logger.error(f"Błąd walidacji danych: {e}")
        raise