from src.etl.transform import SalaryInfo


def test_yearly_salary_divided_by_12():
    salary = SalaryInfo.model_validate({
        "from": 120000,
        "to": 120000,
        "period": "year",
        "currency": "PLN",
    })

    assert salary.monthly_salary_from == 10000
    assert salary.monthly_salary_to == 10000
    assert salary.monthly_salary_avg == 10000


def test_monthly_salary():
    salary = SalaryInfo.model_validate({
        "from": 10000,
        "to": 14000,
        "period": "month",
        "currency": "PLN",
    })

    assert salary.monthly_salary_from == 10000
    assert salary.monthly_salary_to == 14000
    assert salary.monthly_salary_avg == 12000