import random
import uuid
from typing import List, Dict, Any
from faker import Faker 

from src.dal.interfaces import IDataRepository
from src.dal.models import (
    Developer, Category, FreeApplication, 
    PaidApplication, AppVersion, Review,
    Customer, Transaction
)

fake = Faker()

class GooglePlayService:
    def __init__(self, repository: IDataRepository):
        self._repository = repository

    def import_data_from_csv(self, file_path: str):
        raw_rows = self._repository.read_raw_data_from_csv(file_path)
        if not raw_rows:
            return

        developers_cache = {}
        categories_cache = {}
        customers_cache = {}
        entities_to_save = []

        print(f"🔄 Початок обробки {len(raw_rows)} рядків...")

        for row in raw_rows:
            # 1. Обробка категорії (Aggregation)
            cat_name = row['category']
            if cat_name not in categories_cache:
                category = Category(name=cat_name)
                categories_cache[cat_name] = category
                entities_to_save.append(category)
            current_category = categories_cache[cat_name]

            # 2. Обробка розробника (Association)
            dev_key = row['dev_key']
            if dev_key not in developers_cache:
                developer = Developer(
                    company_name=row['company_name'],
                    dev_key=dev_key,
                    email=row['dev_email'],
                    password="dev_password_123"
                )
                developers_cache[dev_key] = developer
                entities_to_save.append(developer)
            current_developer = developers_cache[dev_key]

            # 3. Обробка клієнта (Association)
            customer_name = row['review_author']
            if customer_name not in customers_cache:
                customer = Customer(
                    email=f"{customer_name.lower().replace(' ', '_')}@{fake.domain_name()}",
                    password="customer_pass_123",
                    payment_method=random.choice(["Credit Card", "PayPal", "Google Pay"]),
                    wallet_balance=round(random.uniform(10.0, 500.0), 2)
                )
                customers_cache[customer_name] = customer
                entities_to_save.append(customer)
            current_customer = customers_cache[customer_name]

            # 4. Створення додатка (Inheritance)
            if row['is_free'].lower() == 'true':
                app = FreeApplication(
                    app_id=row['app_id'],
                    title=row['title'],
                    average_rating=float(row['avg_rating']),
                    current_version=row['current_version'],
                    contains_ads=(row['contains_ads'].lower() == 'true'),
                    developer=current_developer,
                    category=current_category
                )
            else:
                app = PaidApplication(
                    app_id=row['app_id'],
                    title=row['title'],
                    average_rating=float(row['avg_rating']),
                    current_version=row['current_version'],
                    price=float(row['price']),
                    currency=row['currency'],
                    developer=current_developer,
                    category=current_category
                )
                
                # 5. Транзакція (якщо додаток платний)
                transaction = Transaction(
                    transaction_id=str(uuid.uuid4()),
                    amount=app.price,
                    status="Completed",
                    customer=current_customer,
                    paid_app=app
                )
                entities_to_save.append(transaction)
            
            entities_to_save.append(app)

            # 6. Версія та відгук (Composition)
            entities_to_save.append(AppVersion(
                version_tag=row['version_tag'],
                release_notes=row['release_notes'],
                application=app
            ))

            entities_to_save.append(Review(
                stars=int(row['review_stars']),
                comment=row['review_comment'],
                application=app,
                customer=current_customer
            ))

        self._repository.save_entities(entities_to_save)
        print("🚀 Бізнес-логіка: Обробка завершена.")

    def get_statistics(self):
        """Метод для надання даних презентаційному рівню."""
        apps = self._repository.get_all_applications()
        return f"📊 Статистика: У базі зараз перебуває {len(apps)} додатків."