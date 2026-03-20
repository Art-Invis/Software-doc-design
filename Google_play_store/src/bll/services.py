import random
import uuid
from typing import List, Optional
from faker import Faker 
from datetime import datetime
from src.dal.interfaces import IDataRepository
from src.dal.models import (
    Application, Developer, Category, FreeApplication, 
    PaidApplication, AppVersion, Review,
    Customer, Transaction
)

fake = Faker()

class GooglePlayService:
    def __init__(self, repository: IDataRepository):
        self._repository = repository

    def get_all_apps(self) -> List[Application]:
        """Отримує всі додатки для головної сторінки."""
        return self._repository.get_all_applications()

    def get_app_by_id(self, app_id: str) -> Optional[Application]:
        return self._repository.get_app_by_id(app_id)

    def get_all_developers(self) -> List[Developer]:
        """Потрібно для вибору розробника у формі створення."""
        return self._repository.get_all_developers()

    def get_all_categories(self) -> List[Category]:
        """Потрібно для вибору категорії у формі створення."""
        return self._repository.get_all_categories()

    def create_application(self, data: dict):
        developer = next((d for d in self.get_all_developers() if str(d.user_id) == str(data['developer_id'])), None)
        category = next((c for c in self.get_all_categories() if str(c.category_id) == str(data['category_id'])), None)

        if not developer or not category:
            print("❌ Помилка: Розробника або категорію не знайдено")
            return

        description_text = data.get('description', 'No description provided.')

        if data['is_free']:
            new_app = FreeApplication(
                app_id=str(uuid.uuid4())[:8],
                title=data['title'],
                description=description_text, 
                average_rating=0.0,
                current_version="1.0.0",
                contains_ads=data.get('contains_ads', False),
                developer=developer,
                category=category
            )
        else:
            new_app = PaidApplication(
                app_id=str(uuid.uuid4())[:8],
                title=data['title'],
                description=description_text, 
                price=float(data['price']),
                currency="USD",
                developer=developer,
                category=category
            )
        
        self._repository.save_entities([new_app])


    def update_application(self, app_id: str, new_data: dict):
        """Оновлює існуючий додаток."""
        app = self.get_app_by_id(app_id)
        if app:
            app.title = new_data.get('title', app.title)
            if 'description' in new_data:
                app.description = new_data['description']
                
            if isinstance(app, PaidApplication) and 'price' in new_data:
                app.price = float(new_data['price'])
                
            self._repository.save_entities([app])

    def delete_application(self, app_id: str):
        """Видаляє додаток із системи."""
        app = self.get_app_by_id(app_id)
        if app:
            self._repository.delete_entity(app) 

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
                    category=current_category,
                    description = row.get('description', '')
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
                    category=current_category,
                    description = row.get('description', '')
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
    
    def get_apps_by_category(self, category_id: str) -> List[Application]:
        """Повертає додатки лише обраної категорії."""
        all_apps = self.get_all_apps()
        return [a for a in all_apps if str(a.category_id) == str(category_id)]
    

    def simulate_purchase(self, app):
        """Імітує створення транзакції для останнього зареєстрованого клієнта."""
        customers = self._repository.get_all_customers()
        customer = customers[-1] if customers else None
        
        if customer and app:
            is_paid = hasattr(app, 'price') and app.app_type == 'paid_app'
            
            new_tx = Transaction(
                transaction_id=str(uuid.uuid4())[:8],
                amount=float(app.price) if is_paid else 0.0,
                status="Completed",
                date=datetime.now(),
                customer_id=customer.user_id, 
                paid_app_id=app.app_id if is_paid else None
            )
            
            self._repository.save_entities([new_tx])

            print(f"✅ Транзакція успішно створена для клієнта ID: {customer.user_id}")

    def add_user_review(self, data):
        """Додає новий відгук до бази."""
        app = self.get_app_by_id(data['app_id'])
        customers = self._repository.get_all_customers()
        customer = customers[-1] if customers else None
        
        if app and customer:
            new_review = Review(
                stars=data['stars'],
                comment=data['comment'],
                application=app,
                customer=customer,
                date=datetime.utcnow()
            )
            self._repository.save_entities([new_review])

    def get_user_by_email(self, email: str):
        """Шукає користувача за email."""
        customers = self._repository.get_all_customers()
        developers = self._repository.get_all_developers()
        
        for u in customers + developers:
            if u.email.lower() == email.lower():
                return u
        return None

    def create_developer(self, data):
        if self.get_user_by_email(data['email']):
            return False, "Користувач з таким Email вже існує!"
        
        new_dev = Developer(
            email=data['email'],
            password=data['password'],
            company_name=data['company_name'],
            dev_key=data['dev_key'],
            user_type="developer"
        )
        self._repository.save_entities([new_dev])
        return True, "Розробника успішно створено."

    def create_customer(self, data):
        if self.get_user_by_email(data['email']):
            return False, "Користувач з таким Email вже існує!"
        
        new_cust = Customer(
            email=data['email'],
            password=data['password'],
            payment_method=data['payment_method'],
            wallet_balance=200.0, 
            user_type="customer"
        )
        self._repository.save_entities([new_cust])
        return True, "Клієнта успішно створено."
    
    def authenticate_user(self, email, password):
        """Перевіряє облікові дані користувача."""
        user = self.get_user_by_email(email)
        if user and user.password == password:
            return user
        return None