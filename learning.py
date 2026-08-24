import sqlite3

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

def parse_job(job_dict:dict) -> dict:
    title = job_dict.get("name", "Brak nazwy")
    company_name = job_dict.get("company", {}).get("name", "Brak nazwy")

    salary_info = job_dict.get("salary", {})
    salary_from = salary_info.get("from", None)
    salary_to = salary_info.get("to", None)

    salary_avg = None

    if salary_from is not None and salary_to is not None:
        salary_avg = (salary_to + salary_from) / 2 

            

    must_have = job_dict.get("tiles", {}).get("mustHave",[])
    technologies = ", ".join([req.get("value","") for req in must_have]) 

    return {
            "title":title, 
            "company_name":company_name, 
            "salary_from":salary_from,
            "salary_to":salary_to, 
            "salary_avg":salary_avg,
            "technologies" : technologies
            }

#LOAD

cleaned_job = parse_job(raw_job)

database = "jobs.db"
create_table = """
    CREATE TABLE IF NOT EXISTS job_offers (
    title TEXT,
    company_name TEXT,
    salary_from INTEGER,
    salary_to INTEGER,
    salary_avg REAL,
    technologies TEXT
)"""

insert_into = """
    INSERT INTO job_offers(
    title, 
    company_name, 
    salary_from, 
    salary_to, 
    salary_avg, 
    technologies
    ) 
    VALUES (?,?,?,?,?,?)
"""

try:
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table)   
        cursor.execute(insert_into,tuple(cleaned_job.values()))
        conn.commit()

except sqlite3.OperationalError as e:
    print(e)