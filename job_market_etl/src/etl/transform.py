import logging
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from src import config
from src.utils.logger_setup import setup_logger

# Konfiguracja logowania
setup_logger()
logger = logging.getLogger(__name__)


class SalaryInfo(BaseModel):
    salary_from: Optional[float] = Field(default=None, alias="from")
    salary_to: Optional[float] = Field(default=None, alias="to")
    type: Optional[str] = None
    currency: Optional[str] = None
    period: Optional[str] = None

    @computed_field
    @property
    def salary_avg(self) -> Optional[float]:
        if self.salary_from is not None and self.salary_to is not None:
            return (self.salary_from + self.salary_to) / 2
        return self.salary_from or self.salary_to

    def _normalize_to_month(
        self, amount: Optional[float], period: Optional[str]
    ) -> Optional[float]:
        if amount is None or period is None:
            return amount

        multiplier = {
            "month": 1.0,
            "year": 1 / 12,
            "week": 4.33,
            "day": 21.67,
            "hour": 173.33,
        }

        period_lower = period.lower()
        if period_lower not in multiplier:
            logger.warning(f"Nieznany okres wynagrodzenia: {period}.")
            return round(amount, 2)

        return round(amount * multiplier[period_lower], 2)

    @computed_field
    @property
    def monthly_salary_from(self) -> Optional[float]:
        return self._normalize_to_month(self.salary_from, self.period)

    @computed_field
    @property
    def monthly_salary_to(self) -> Optional[float]:
        return self._normalize_to_month(self.salary_to, self.period)

    @computed_field
    @property
    def monthly_salary_avg(self) -> Optional[float]:
        return self._normalize_to_month(self.salary_avg, self.period)


class TilesValues(BaseModel):
    value: str
    type: str


class TilesInfo(BaseModel):
    values: list[TilesValues] = []


class JobPosting(BaseModel):
    id: str
    name: str
    title: str
    url: str
    salary: Optional[SalaryInfo] = None
    fullyRemote: Optional[bool] = None
    seniority: Optional[list[str]] = None
    tiles: Optional[TilesInfo] = None

    @computed_field
    @property
    def offer_url(self) -> str:
        return f"{config.API_BASE_URL}/job/{self.url}"


class NFJResponse(BaseModel):
    postings: list[JobPosting] = []


def transform_jobs(raw_data: dict) -> list[JobPosting]:
    # Transform
    logger.info("Rozpoczeto transformacje i walidacje danych.")

    try:
        validated_data = NFJResponse(**raw_data)

        jobs_count = len(validated_data.postings)
        logger.info(f"Zwalidowano pomyslnie {jobs_count} ofert pracy.")

        if jobs_count > 0:
            with open(config.VALIDATED_DATA_PATH, "w", encoding="utf-8") as f:
                f.write(validated_data.model_dump_json(indent=4))
            logger.info(
                f"Zapisano zwalidowane dane do pliku: {config.VALIDATED_DATA_PATH}"
            )

        return validated_data.postings

    except Exception as e:
        logger.error(f"Blad walidacji danych: {e}")
        raise
