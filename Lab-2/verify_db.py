from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.dal.models import (
    Developer, Customer, Category, FreeApplication, 
    PaidApplication, AppVersion, Review, Transaction, Application
)
from src.core.config import Config

def verify_database():
    engine = create_engine(Config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("🔍 --- ВЕРИФІКАЦІЯ БАЗИ ДАНИХ --- 🔍\n")

    try:
        stats = [
            ("Категорії", session.query(Category).count()),
            ("Розробники", session.query(Developer).count()),
            ("Клієнти", session.query(Customer).count()),
            ("Безкоштовні додатки", session.query(FreeApplication).count()),
            ("Платні додатки", session.query(PaidApplication).count()),
            ("Версії", session.query(AppVersion).count()),
            ("Відгуки", session.query(Review).count()),
            ("Транзакції", session.query(Transaction).count()),
        ]

        print(f"{'Сутність':<25} | {'Кількість':<10}")
        print("-" * 40)
        for name, count in stats:
            status = "✅ OK" if count > 0 else "❌ EMPTY"
            print(f"{name:<25} | {count:<10} {status}")

        print("\n📊 --- ПЕРЕВІРКА ЗВ'ЯЗКІВ (Relationships) ---")
        
        orphan_reviews = session.query(Review).filter(
            (Review.app_id == None) | (Review.customer_id == None)
        ).count()
        
        if orphan_reviews == 0:
            print("✅ Всі відгуки коректно прив'язані до додатків та клієнтів.")
        else:
            print(f"⚠️ Знайдено {orphan_reviews} відгуків без прив'язки!")

        paid_apps_count = session.query(PaidApplication).count()
        transactions_count = session.query(Transaction).count()
        print(f"✅ Транзакції: {transactions_count} записів для {paid_apps_count} платних додатків.")

    except Exception as e:
        print(f"❌ Помилка під час верифікації: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_database()