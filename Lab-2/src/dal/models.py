from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

# Базовий клас SQLAlchemy
class Base(DeclarativeBase):
    pass

# --- МОДЕЛІ КОРИСТУВАЧІВ ---

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(String(20)) # Дискримінатор для поліморфізму

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    # Методи поведінки з діаграми
    def login(self) -> bool:
        print(f"User {self.email} logged in successfully.")
        return True

    def logout(self):
        print(f"User {self.email} logged out.")

    def get_role(self) -> str:
        return self.user_type

class Developer(User):
    __tablename__ = 'developers'
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    company_name = Column(String)
    dev_key = Column(String)

    applications = relationship("Application", back_populates="developer")

    __mapper_args__ = {
        'polymorphic_identity': 'developer',
    }

    # Методи розробника
    def upload_app(self, app):
        print(f"Developer {self.company_name} is uploading: {app.title}")

    def manage_releases(self, app):
        print(f"Managing releases for: {app.title}")

class Customer(User):
    __tablename__ = 'customers'
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    payment_method = Column(String)
    wallet_balance = Column(Float, default=0.0)

    transactions = relationship("Transaction", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")

    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

    # Методи клієнта
    def purchase_app(self, app):
        print(f"Customer purchasing app: {app.title} via {self.payment_method}")

    def install_app(self, app):
        print(f"Installing {app.title} on device...")

    def rate_app(self, app, stars: int):
        print(f"Rated {app.title}: {stars}/5 stars.")

# --- МОДЕЛІ КОНТЕНТУ ---

class Category(Base):
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    applications = relationship("Application", back_populates="category")

    # Метод пошуку для категорій
    def search(self, query: str):
        print(f"Searching for '{query}' in category: {self.name}")

class Application(Base):
    __tablename__ = 'applications'
    
    app_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    average_rating = Column(Float, default=0.0)
    current_version = Column(String)
    app_type = Column(String(20))

    developer_id = Column(Integer, ForeignKey('developers.user_id'))
    category_id = Column(Integer, ForeignKey('categories.category_id'))

    developer = relationship("Developer", back_populates="applications")
    category = relationship("Category", back_populates="applications")
    versions = relationship("AppVersion", back_populates="application", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="application", cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'application',
        'polymorphic_on': app_type
    }

    # Базові методи додатка
    def get_metadata(self) -> str:
        return f"App: {self.title}, Version: {self.current_version}"

    def download_app(self):
        # Базовий метод, який буде перевизначено
        print(f"Preparing download for {self.title}...")

    def search(self, query: str):
        print(f"Searching for '{query}' inside application content.")

class FreeApplication(Application):
    __tablename__ = 'free_applications'
    app_id = Column(String, ForeignKey('applications.app_id'), primary_key=True)
    contains_ads = Column(Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_identity': 'free_app',
    }

    # ПЕРЕВИЗНАЧЕННЯ: Download для безкоштовних додатків
    def download_app(self):
        ad_status = "with ads" if self.contains_ads else "ad-free"
        print(f"✅ Downloading {self.title} ({ad_status}). No payment required.")

class PaidApplication(Application):
    __tablename__ = 'paid_applications'
    app_id = Column(String, ForeignKey('applications.app_id'), primary_key=True)
    price = Column(Float)
    currency = Column(String, default='USD')

    transactions = relationship("Transaction", back_populates="paid_app")

    __mapper_args__ = {
        'polymorphic_identity': 'paid_app',
    }

    # ПЕРЕВИЗНАЧЕННЯ: Download для платних додатків
    def download_app(self):
        print(f"💳 Processing payment of {self.price} {self.currency} for {self.title}...")
        print(f"✅ Download started for {self.title}.")

    def verify_license(self, user: User) -> bool:
        print(f"Verifying license for {user.email}...")
        return True

# --- ДОДАТКОВІ СУТНОСТІ ---

class AppVersion(Base):
    __tablename__ = 'app_versions'
    version_id = Column(Integer, primary_key=True)
    version_tag = Column(String)
    release_notes = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    app_id = Column(String, ForeignKey('applications.app_id'))
    application = relationship("Application", back_populates="versions")

class Review(Base):
    __tablename__ = 'reviews'
    review_id = Column(Integer, primary_key=True)
    stars = Column(Integer)
    comment = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    app_id = Column(String, ForeignKey('applications.app_id'))
    application = relationship("Application", back_populates="reviews")

    customer_id = Column(Integer, ForeignKey('customers.user_id'))
    customer = relationship("Customer", back_populates="reviews")

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(String, primary_key=True)
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String)

    customer_id = Column(Integer, ForeignKey('customers.user_id'))
    paid_app_id = Column(String, ForeignKey('paid_applications.app_id'))

    customer = relationship("Customer", back_populates="transactions")
    paid_app = relationship("PaidApplication", back_populates="transactions")

# from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
# from sqlalchemy.orm import DeclarativeBase, relationship
# from datetime import datetime

# # Стандартний базовий клас SQLAlchemy (без ABC, щоб не було конфліктів)
# class Base(DeclarativeBase):
#     pass

# # --- МОДЕЛІ КОРИСТУВАЧІВ (Згідно з діаграмою) ---

# class User(Base):
#     __tablename__ = 'users'
    
#     user_id = Column(Integer, primary_key=True)
#     email = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     user_type = Column(String(20)) # Дискримінатор для успадкування

#     __mapper_args__ = {
#         'polymorphic_identity': 'user',
#         'polymorphic_on': user_type
#     }

#     # Методи поведінки з твоєї діаграми
#     def login(self) -> bool:
#         print(f"Користувач {self.email} увійшов.")
#         return True

#     def logout(self):
#         print(f"Користувач {self.email} вийшов.")

#     def get_role(self) -> str:
#         return self.user_type

# class Developer(User):
#     __tablename__ = 'developers'
#     user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
#     company_name = Column(String)
#     dev_key = Column(String)

#     applications = relationship("Application", back_populates="developer")

#     __mapper_args__ = {
#         'polymorphic_identity': 'developer',
#     }

#     # Методи розробника з діаграми
#     def upload_app(self, app):
#         print(f"Завантаження додатка: {app.title}")

#     def manage_releases(self, app):
#         pass

# class Customer(User):
#     __tablename__ = 'customers'
#     user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
#     payment_method = Column(String)
#     wallet_balance = Column(Float, default=0.0)

#     transactions = relationship("Transaction", back_populates="customer")
#     reviews = relationship("Review", back_populates="customer")

#     __mapper_args__ = {
#         'polymorphic_identity': 'customer',
#     }

#     # Методи клієнта з діаграми
#     def purchase_app(self, app):
#         print(f"Покупка додатка: {app.title}")

#     def install_app(self, app):
#         print(f"Встановлення: {app.title}")

#     def rate_app(self, app, stars: int):
#         print(f"Оцінка {app.title}: {stars} зірок.")

# # --- МОДЕЛІ КОНТЕНТУ ---

# class Category(Base):
#     __tablename__ = 'categories'
    
#     category_id = Column(Integer, primary_key=True)
#     name = Column(String, unique=True)
#     applications = relationship("Application", back_populates="category")

#     # Метод пошуку з діаграми
#     def search(self, query: str):
#         print(f"Пошук '{query}' у категорії: {self.name}")

# class Application(Base):
#     __tablename__ = 'applications'
    
#     app_id = Column(String, primary_key=True)
#     title = Column(String, nullable=False)
#     average_rating = Column(Float, default=0.0)
#     current_version = Column(String)
#     app_type = Column(String(20))

#     developer_id = Column(Integer, ForeignKey('developers.user_id'))
#     category_id = Column(Integer, ForeignKey('categories.category_id'))

#     developer = relationship("Developer", back_populates="applications")
#     category = relationship("Category", back_populates="applications")
#     versions = relationship("AppVersion", back_populates="application", cascade="all, delete-orphan")
#     reviews = relationship("Review", back_populates="application", cascade="all, delete-orphan")

#     __mapper_args__ = {
#         'polymorphic_identity': 'application',
#         'polymorphic_on': app_type
#     }

#     # Методи додатка з діаграми
#     def get_metadata(self) -> str:
#         return f"{self.title} (версія: {self.current_version})"

#     def download_app(self):
#         print(f"Завантаження: {self.title}")

#     def search(self, query: str):
#         print(f"Пошук '{query}' у додатку: {self.title}")

# class FreeApplication(Application):
#     __tablename__ = 'free_applications'
#     app_id = Column(String, ForeignKey('applications.app_id'), primary_key=True)
#     contains_ads = Column(Boolean, default=True)

#     __mapper_args__ = {
#         'polymorphic_identity': 'free_app',
#     }

# class PaidApplication(Application):
#     __tablename__ = 'paid_applications'
#     app_id = Column(String, ForeignKey('applications.app_id'), primary_key=True)
#     price = Column(Float)
#     currency = Column(String, default='USD')

#     transactions = relationship("Transaction", back_populates="paid_app")

#     __mapper_args__ = {
#         'polymorphic_identity': 'paid_app',
#     }

#     # Специфічний метод для платних додатків
#     def verify_license(self, user: User) -> bool:
#         return True

# # --- ДОДОМАТКОВІ СУТНОСТІ ---

# class AppVersion(Base):
#     __tablename__ = 'app_versions'
    
#     version_id = Column(Integer, primary_key=True)
#     version_tag = Column(String)
#     release_notes = Column(String)
#     upload_date = Column(DateTime, default=datetime.utcnow)
    
#     app_id = Column(String, ForeignKey('applications.app_id'))
#     application = relationship("Application", back_populates="versions")

# class Review(Base):
#     __tablename__ = 'reviews'
    
#     review_id = Column(Integer, primary_key=True)
#     stars = Column(Integer)
#     comment = Column(String)
#     date = Column(DateTime, default=datetime.utcnow)

#     app_id = Column(String, ForeignKey('applications.app_id'))
#     application = relationship("Application", back_populates="reviews")

#     customer_id = Column(Integer, ForeignKey('customers.user_id'))
#     customer = relationship("Customer", back_populates="reviews")

# class Transaction(Base):
#     __tablename__ = 'transactions'
    
#     transaction_id = Column(String, primary_key=True)
#     amount = Column(Float)
#     date = Column(DateTime, default=datetime.utcnow)
#     status = Column(String)

#     customer_id = Column(Integer, ForeignKey('customers.user_id'))
#     paid_app_id = Column(String, ForeignKey('paid_applications.app_id'))

#     customer = relationship("Customer", back_populates="transactions")
#     paid_app = relationship("PaidApplication", back_populates="transactions")

# # from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Table
# # from sqlalchemy.orm import DeclarativeBase, relationship
# # from datetime import datetime

# # # Базовий клас для всіх моделей
# # class Base(DeclarativeBase):
# #     pass

# # # Проміжна таблиця для зв'язку "багато-до-багатьох" (якщо Category та Application так зв'язані)
# # # Але згідно з твоєю діаграмою, там 1 до * (Aggregation)

# # class User(Base):
# #     __tablename__ = 'users'
    
# #     user_id = Column(Integer, primary_key=True)
# #     email = Column(String, unique=True, nullable=False)
# #     password = Column(String, nullable=False)
# #     user_type = Column(String(20)) # Для ідентифікації типу в БД

# #     # Налаштування успадкування (Joined Table Inheritance)
# #     __mapper_args__ = {
# #         'polymorphic_identity': 'user',
# #         'polymorphic_on': user_type
# #     }

# # class Developer(User):
# #     __tablename__ = 'developers'
# #     user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
# #     company_name = Column(String)
# #     dev_key = Column(String)

# #     # Зв'язок 1 до * з додатками
# #     applications = relationship("Application", back_populates="developer")

# #     __mapper_args__ = {
# #         'polymorphic_identity': 'developer',
# #     }

# # class Customer(User):
# #     __tablename__ = 'customers'
# #     user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
# #     payment_method = Column(String)
# #     wallet_balance = Column(Float, default=0.0)

# #     # Зв'язок з транзакціями
# #     transactions = relationship("Transaction", back_populates="customer")
    
# #     # ДОДАНО: Зв'язок із відгуками
# #     reviews = relationship("Review", back_populates="customer")

# #     __mapper_args__ = {
# #         'polymorphic_identity': 'customer',
# #     }

# # class Category(Base):
# #     __tablename__ = 'categories'
    
# #     category_id = Column(Integer, primary_key=True)
# #     name = Column(String, unique=True)

# #     # Агрегація 1 до *
# #     applications = relationship("Application", back_populates="category")

# # class Application(Base):
# #     __tablename__ = 'applications'
    
# #     app_id = Column(String, primary_key=True)
# #     title = Column(String, nullable=False)
# #     average_rating = Column(Float, default=0.0)
# #     current_version = Column(String)
# #     app_type = Column(String(20))

# #     # Зовнішні ключі
# #     developer_id = Column(Integer, ForeignKey('developers.user_id'))
# #     category_id = Column(Integer, ForeignKey('categories.category_id'))

# #     # Зв'язки
# #     developer = relationship("Developer", back_populates="applications")
# #     category = relationship("Category", back_populates="applications")
# #     versions = relationship("AppVersion", back_populates="application", cascade="all, delete-orphan")
# #     reviews = relationship("Review", back_populates="application", cascade="all, delete-orphan")

# #     __mapper_args__ = {
# #         'polymorphic_identity': 'application',
# #         'polymorphic_on': app_type
# #     }

# # class FreeApplication(Application):
# #     __tablename__ = 'free_applications'
# #     app_id = Column(String, ForeignKey('applications.app_id'), primary_key=True)
# #     contains_ads = Column(Boolean, default=True)

# #     __mapper_args__ = {
# #         'polymorphic_identity': 'free_app',
# #     }

# # class PaidApplication(Application):
# #     __tablename__ = 'paid_applications'
# #     app_id = Column(String, ForeignKey('applications.app_id'), primary_key=True)
# #     price = Column(Float)
# #     currency = Column(String, default='USD')

# #     transactions = relationship("Transaction", back_populates="paid_app")

# #     __mapper_args__ = {
# #         'polymorphic_identity': 'paid_app',
# #     }

# # class AppVersion(Base):
# #     __tablename__ = 'app_versions'
    
# #     version_id = Column(Integer, primary_key=True)
# #     version_tag = Column(String)
# #     release_notes = Column(String)
# #     upload_date = Column(DateTime, default=datetime.utcnow)
    
# #     app_id = Column(String, ForeignKey('applications.app_id'))
# #     application = relationship("Application", back_populates="versions")


# # class Review(Base):
# #     __tablename__ = 'reviews'
    
# #     review_id = Column(Integer, primary_key=True)
# #     stars = Column(Integer)
# #     comment = Column(String)
# #     date = Column(DateTime, default=datetime.utcnow)

# #     # Зв'язок із додатком
# #     app_id = Column(String, ForeignKey('applications.app_id'))
# #     application = relationship("Application", back_populates="reviews")

# #     # ДОДАНО: Зв'язок із клієнтом
# #     customer_id = Column(Integer, ForeignKey('customers.user_id'))
# #     customer = relationship("Customer", back_populates="reviews")

# # class Transaction(Base):
# #     __tablename__ = 'transactions'
    
# #     transaction_id = Column(String, primary_key=True)
# #     amount = Column(Float)
# #     date = Column(DateTime, default=datetime.utcnow)
# #     status = Column(String)

# #     customer_id = Column(Integer, ForeignKey('customers.user_id'))
# #     paid_app_id = Column(String, ForeignKey('paid_applications.app_id'))

# #     customer = relationship("Customer", back_populates="transactions")
# #     paid_app = relationship("PaidApplication", back_populates="transactions")