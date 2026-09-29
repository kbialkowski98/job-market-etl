from datetime import date, timedelta
import requests

def build_fx_row(payload: dict, rate_date: date) -> dict:
    rate = payload["rates"][-1]

    return {
        "rate_date": rate_date,
        "currency": payload["code"],
        "rate_pln": rate["mid"],
        "effective_date": date.fromisoformat(rate["effectiveDate"]),
        "source": "NBP-A"
    }


def nbp_url(currency: str, rate_date: date) -> str:
    start = rate_date - timedelta(days=14)
    return f"https://api.nbp.pl/api/exchangerates/rates/a/{currency.lower()}/{start.isoformat()}/{rate_date.isoformat()}/?format=json"


def fetch_nbp_payload(currency: str, rate_date: date) -> dict:
    url = nbp_url(currency, rate_date)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_fx_row(currency: str, rate_date: date) -> dict:
    payload = fetch_nbp_payload(currency, rate_date)
    return build_fx_row(payload, rate_date)


def build_fx_rows(currencies: set[str], rate_date: date) -> list[dict]:
    rows = []
    for currency in currencies:
        if not currency:
            continue
        if currency == "PLN":
            rows.append({
                "rate_date": rate_date,
                "currency": currency,
                "rate_pln": 1.0,
                "effective_date": rate_date,
                "source": "identity"
            })
        else:
            rows.append(fetch_fx_row(currency, rate_date))
    return rows
