import logging
from typing import Optional
from datetime import date

from sqlalchemy import Boolean, Date, Float, String, create_engine, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from src import config
from src.etl.transform import JobPosting
from src.utils.logger_setup import setup_logger
from src.utils.fx import build_fx_rows

setup_logger()
logger = logging.getLogger(__name__)


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
    published_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class JobObservations(Base):
    __tablename__ = "job_observations"

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
    published_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    scraped_at: Mapped[date] = mapped_column(Date, nullable=False, primary_key=True)


class JobObservationSkills(Base):
    __tablename__ = "job_observation_skills"

    job_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    scraped_at: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    skill: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)


class FxRate(Base):
    __tablename__ = "fx_rates"

    rate_date: Mapped[date] = mapped_column(Date, primary_key=True, nullable=False)
    currency: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    rate_pln: Mapped[float] = mapped_column(Float, nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)


def load_jobs(jobs_list: list[JobPosting], scraped_at: date, db_url: str = config.DB_URL) -> None:
    if not jobs_list:
        logger.info("Brak danych do zaladowania.")
        return

    if db_url is None:
        raise ValueError("Brak konfiguracji polaczenia z baza danych (DB_USER/DB_PASSWORD).")

    logger.info(f"Data zaladowania: {scraped_at}")

    engine = create_engine(db_url, echo=False)
    logger.info("Rozpoczeto ladowanie danych do bazy.")

    Base.metadata.create_all(engine)
    logger.info("Schemat bazy danych zweryfikowany.")

    values_to_insert = {}
    skill_rows_by_key = {}
    currencies = set()

    for item in jobs_list:
        seniority_str = ", ".join(item.seniority) if item.seniority else None

        values_to_insert[item.id] = {
            "id": item.id,
            "name": item.name,
            "title": item.title,
            "offer_url": item.offer_url,
            
            "salary_from": item.salary.salary_from if item.salary else None,
            "salary_to": item.salary.salary_to if item.salary else None,
            "salary_avg": item.salary.salary_avg if item.salary else None,
            "monthly_salary_from": item.salary.monthly_salary_from if item.salary else None,
            "monthly_salary_to": item.salary.monthly_salary_to if item.salary else None,
            "monthly_salary_avg": item.salary.monthly_salary_avg if item.salary else None,
            "salary_period": item.salary.period if item.salary else None,
            "salary_type": item.salary.type if item.salary else None,
            "salary_currency": item.salary.currency if item.salary else None,
            
            "fully_remote": item.fullyRemote,
            "seniority": seniority_str,
            "published_at": item.published_at,
            
            "scraped_at": scraped_at
        }

        for raw_skill in item.technologies:
            skill = raw_skill.strip().lower()
            if not skill:
                continue
            skill_rows_by_key[(item.id, scraped_at, skill)] = {
                "job_id": item.id,
                "scraped_at": scraped_at,
                "skill": skill
            }

        if item.salary and item.salary.currency:
            currencies.add(item.salary.currency.strip().upper())


    observation_rows = list(values_to_insert.values())
    obs_stmt = insert(JobObservations).values(observation_rows)
    obs_update = {c.name: c for c in obs_stmt.excluded if c.name not in ("id", "scraped_at")}
    obs_upsert = obs_stmt.on_conflict_do_update(
        index_elements=["id", "scraped_at"],
        set_=obs_update,
    )


    job_rows = [{key: value for key, value in row.items() if key != "scraped_at"} for row in observation_rows]
    job_stmt = insert(Job).values(job_rows)
    job_update = {c.name: c for c in job_stmt.excluded if c.name != "id"}
    job_upsert = job_stmt.on_conflict_do_update(
        index_elements=["id"],
        set_=job_update,
    )


    skill_rows = list(skill_rows_by_key.values())

    logger.info(f"Waluty w zrzucie: {sorted(currencies)}")
    fx_rows = build_fx_rows(currencies, scraped_at)
    logger.info(f"Kursy: {fx_rows}")

    job_ids = list(values_to_insert.keys())

    
    Session = sessionmaker(bind=engine)
    with Session() as session:
        try:
            session.execute(obs_upsert)
            session.execute(job_upsert)

            session.execute(
                delete(JobObservationSkills).where(
                    JobObservationSkills.scraped_at == scraped_at,
                    JobObservationSkills.job_id.in_(job_ids)
                )
            )
            if skill_rows:
                session.execute(insert(JobObservationSkills).values(skill_rows))

            if fx_rows:
                fx_stmt = insert(FxRate).values(fx_rows)
                fx_update = {
                    c.name: c
                    for c in fx_stmt.excluded
                    if c.name not in ("rate_date", "currency")
                }
                fx_upsert = fx_stmt.on_conflict_do_update(
                    index_elements=["rate_date", "currency"],
                    set_=fx_update,
                )
                session.execute(fx_upsert)

            session.commit()

            logger.info(f"[job_observations] Załadowano/zaktualizowano {len(observation_rows)} rekordow.")
            logger.info(f"[jobs] Załadowano/zaktualizowano {len(job_rows)} rekordow.")
            logger.info(f"[job_skills] Załadowano/zaktualizowano {len(skill_rows)} rekordow.")
            logger.info(f"[fx_rates] Załadowano/zaktualizowano {len(fx_rows)} rekordow.")

        except Exception as e:
            session.rollback()
            logger.error(f"Wystapil blad podczas ladowania danych: {e}")
            raise