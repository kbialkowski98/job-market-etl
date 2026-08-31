import logging
from typing import Optional

from sqlalchemy import Boolean, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from src import config
from src.etl.transform import JobPosting
from src.utils.logger_setup import setup_logger

# Konfiguracja logowania
setup_logger()
logger = logging.getLogger(__name__)

engine = create_engine(config.DB_URL, echo=False)


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    offer_url: Mapped[str] = mapped_column(String)

    salary_from: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_to: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    monthly_salary_from: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monthly_salary_to: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monthly_salary_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    salary_period: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    salary_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    fully_remote: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    seniority: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    technologies: Mapped[Optional[str]] = mapped_column(String, nullable=True)


def load_jobs(jobs_list: list[JobPosting]):
    # Load
    logger.info("Rozpoczeto ladowanie danych do bazy.")

    Base.metadata.create_all(engine)
    logger.info("Schemat bazy danych zweryfikowany.")

    Session = sessionmaker(bind=engine)
    with Session() as session:
        loaded_count = 0

        for item in jobs_list:
            seniority_str = ", ".join(item.seniority) if item.seniority else None

            tech_list = [t.value for t in item.tiles.values] if item.tiles else []
            technologies_str = ", ".join(tech_list) if tech_list else None

            db_job = Job(
                id=item.id,
                name=item.name,
                title=item.title,
                offer_url=item.offer_url,
                salary_from=item.salary.salary_from if item.salary else None,
                salary_to=item.salary.salary_to if item.salary else None,
                salary_avg=item.salary.salary_avg if item.salary else None,
                monthly_salary_from=item.salary.monthly_salary_from,
                monthly_salary_to=item.salary.monthly_salary_to,
                monthly_salary_avg=item.salary.monthly_salary_avg,
                salary_period=item.salary.period if item.salary else None,
                salary_type=item.salary.type if item.salary else None,
                salary_currency=item.salary.currency if item.salary else None,
                fully_remote=item.fullyRemote,
                seniority=seniority_str,
                technologies=technologies_str,
            )

            session.merge(db_job)
            loaded_count += 1

        session.commit()
        logger.info(
            f"Zaladowano/zaktualizowano {loaded_count} rekordow w bazie danych."
        )
