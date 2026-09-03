from sqlalchemy import create_engine, text
from src import config

def test_connection():
    engine = create_engine(config.DB_URL)
    
    try:
        with engine.connect() as conn:
            # Pobieramy 5 losowych ofert z Twojej nowej hurtowni!
            result = conn.execute(text("SELECT id, title, fully_remote, salary_from FROM jobs LIMIT 5"))
            
            print("🚀 Pięć pierwszych ofert z chmury Azure:")
            print("-" * 60)
            for row in result:
                print(f"ID: {row.id[:8]}... | Tytuł: {row.title} | Zdalnie: {row.fully_remote} | Kasa od: {row.salary_from}")
                
    except Exception as e:
        print(f"BŁĄD: {e}")

if __name__ == "__main__":
    test_connection()