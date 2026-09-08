import logging
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, computed_field

from src import config
from src.utils.logger_setup import setup_logger


setup_logger()
logger = logging.getLogger(__name__)


class SalaryInfo(BaseModel):
    salary_from: Optional[float] = Field(default=None, alias="from")
    salary_to: Optional[float] = Field(default=None, alias="to")
    type: Optional[str] = None
    currency: Optional[str] = None
    period: Optional[str] = None

    def _normalize_to_month(self, amount: Optional[float], period: Optional[str]) -> Optional[float]:
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
    def salary_avg(self) -> Optional[float]:
        if self.salary_from is not None and self.salary_to is not None:
            return (self.salary_from + self.salary_to) / 2
        return self.salary_from or self.salary_to

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

class LocationInfo(BaseModel):
    fullyRemote: Optional[bool] = False

class JobPosting(BaseModel):
    id: str
    name: str
    title: str
    url: str
    salary: Optional[SalaryInfo] = None
    seniority: Optional[list[str]] = None
    tiles: Optional[TilesInfo] = None
    location: Optional[LocationInfo] = None

    @computed_field
    @property
    def fullyRemote(self) -> bool:
        if self.location and self.location.fullyRemote is not None:
            return self.location.fullyRemote
        return False

    @computed_field
    @property
    def offer_url(self) -> str:
        return f"{config.API_BASE_URL}/job/{self.url}"

    @computed_field
    @property
    def technologies(self) -> list[str]:
        if not self.tiles:
            return []
        return [t.value for t in self.tiles.values if t.type == "requirement"]


def transform_jobs(raw_data: dict) -> list[JobPosting]:
    logger.info("Rozpoczeto transformacje i walidacje danych.")

    valid_postings = []
    raw_postings = raw_data.get("postings", [])

    for raw_item in raw_postings:
        try:
            job_posting = JobPosting(**raw_item)
            valid_postings.append(job_posting)
            
        except ValidationError as ve:
            job_url = raw_item.get("url", "Nieznany URL")
            logger.error(f"Blad walidacji danych dla ogloszenia {job_url}: {ve}")
            
        except Exception as e:
            logger.error(f"Nieoczekiwany blad podczas przetwarzania rekordu: {e}")

    jobs_count = len(valid_postings)
    logger.info(f"Zwalidowano pomyslnie {jobs_count} z {len(raw_postings)} ofert pracy.")

    return valid_postings