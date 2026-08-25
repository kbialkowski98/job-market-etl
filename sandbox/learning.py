from datetime import datetime

from pydantic import BaseModel, PositiveInt, Field, computed_field

raw_job = {
    "id": "abc-123",
    "name": "Data Engineer",
    "company": {
        "name": "DataTech Sp. z o.o.",
        "url": "https://datatech.pl"
    },
    "salary": {
        "from": 15000,
        "to": 22000,
        "currency": "PLN",
        "type": "b2b"
    },
    "tiles": {
        "mustHave": [
            {"value": "Python", "experience": 3},
            {"value": "SQL", "experience": 3},
            {"value": "Airflow", "experience": 1}
        ]
    }
}

"""
title TEXT,
company_name TEXT,
salary_from INTEGER,
salary_to INTEGER,
salary_avg REAL,
technologies TEXT
"""


class CompanyInfo(BaseModel):
    name: str = "Brak danych"
    url: str | None = None

class Salary(BaseModel):
    salary_from: int | None = Field(default=None, alias="from")
    salary_to: int | None = Field(default=None, alias="to")

    @computed_field
    @property
    def salary_avg(self) -> float | None:
        if self.salary_from is not None and self.salary_to is not None:
            return (self.salary_from + self.salary_to) / 2
        return None

class Skill(BaseModel):
    value: str = "Brak danych"
    experience: PositiveInt = None

class TilesInfo(BaseModel):
    mustHave: list[Skill] = []

class Job(BaseModel):
    id: str
    name: str
    company: CompanyInfo
    salary: Salary
    tiles: TilesInfo

try:
    parsed_job = Job(**raw_job)
    print(parsed_job.model_dump_json(indent=2))
except Exception as e:
    print(e.errors())





