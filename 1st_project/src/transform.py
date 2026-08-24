import json
import csv
import os

Project_folder = "1st_project/data"

def transform_jobs():
    input_file = "1st_project/data/raw_jobs.json"
    output_file = "1st_project/data/cleaned_jobs.csv"

    if not os.path.exists(input_file):
        print(f"Brak pliku {input_file}. Uruchom najpierw extract.py!")
        return

    print("Rozpoczynam przetwarzanie danych...")

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # W NoFluffJobs lista ofert zazwyczaj znajduje się pod kluczem 'postings'
    postings = data.get("postings", [])
    
    if not postings:
        print("Nie znaleziono ofert (klucz 'postings' jest pusty). Sprawdź strukturę raw_jobs.json.")
        return

    # Przygotowanie danych do zapisu
    cleaned_jobs = []
    
    for job in postings:
        # Bezpieczne pobieranie wartości (używamy .get() aby uniknąć błędów, jeśli pola brakuje)
        title = job.get("name", "Brak nazwy")
        company = job.get("company", {}).get("name", "Brak firmy")
        
        # Wyciąganie wymagań (technologii). Są to zazwyczaj listy.
        must_have = job.get("tiles", {}).get("mustHave", [])
        technologies = ", ".join([req.get("value", "") for req in must_have])

        # Widełki płacowe (w NFJ jest to zwykle zagnieżdżone)
        salary_info = job.get("salary", {})
        salary_from = salary_info.get("from", "")
        salary_to = salary_info.get("to", "")
        currency = salary_info.get("currency", "")
        
        # Formatowanie pensji jako string, np. "15000 - 20000 PLN"
        if salary_from and salary_to:
            salary_formatted = f"{salary_from} - {salary_to} {currency}"
        else:
            salary_formatted = "Brak widełek"

        cleaned_jobs.append({
            "Tytul": title,
            "Firma": company,
            "Technologie": technologies,
            "Widelki": salary_formatted
        })

    # Zapis do CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Tytul", "Firma", "Technologie", "Widelki"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(cleaned_jobs)

    print(f"Przetworzono {len(cleaned_jobs)} ofert. Wynik zapisano w: {output_file}")

if __name__ == "__main__":
    transform_jobs()