import os
import json
import requests

def extract_jobs():
    cookies = {
        '_gcl_au': '1.1.894055234.1780923752',
        'country_iso': 'PL',
        'nfj_new_user': 'true',
        'nfj_session_id': 'f2c0ec81-993c-4733-9f2e-0c849c73a78b.1787574591498',
        'nfj_visited_pl': 'true',
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pl-PL,pl;q=0.5',
        'content-type': 'application/infiniteSearch+json',
        'nfj-global-context': '{"region":"PL","lang":"pl","global_is_employer_logged_in":false,"global_is_candidate_logged_in":false,"global_internal_traffic":false,"global_salary_match_enabled":true}',
        'origin': 'https://nofluffjobs.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
    }

    params = {
        'pageFrom': '1',
        'withSalaryMatch': 'true',
        'pageTo': '1',
        'pageSize': '20',
        'salaryCurrency': 'original',
        'salaryPeriod': 'original',
        'region': 'pl',
        'language': 'pl-PL',
    }

    data = '{"criteriaSearch":{"category":["data"]},"pageSize":20,"withSalaryMatch":true}'

    print("Pobieram dane z NoFluffJobs API...")
    
    try:
        response = requests.post(
            'https://nofluffjobs.com/api/search/posting', 
            params=params, 
            cookies=cookies, 
            headers=headers, 
            data=data
        )
        response.raise_for_status()
        
        response_json = response.json()
        
        os.makedirs("data", exist_ok=True)
        file_path = "1st_project/data/raw_jobs.json"
        
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(response_json, file, ensure_ascii=False, indent=4)
            
        print(f"Sukces! Zapisano dane do: {file_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Wystąpił błąd podczas połączenia: {e}")

if __name__ == "__main__":
    extract_jobs()