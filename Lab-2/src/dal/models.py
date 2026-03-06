from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

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

    def purchase_app(self, app):
        print(f"Customer purchasing app: {app.title} via {self.payment_method}")

    def install_app(self, app):
        print(f"Installing {app.title} on device...")

    def rate_app(self, app, stars: int):
        print(f"Rated {app.title}: {stars}/5 stars.")


class Category(Base):
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    applications = relationship("Application", back_populates="category")

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

    def get_metadata(self) -> str:
        return f"App: {self.title}, Version: {self.current_version}"

    def download_app(self):
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

    def download_app(self):
        print(f"💳 Processing payment of {self.price} {self.currency} for {self.title}...")
        print(f"✅ Download started for {self.title}.")

    def verify_license(self, user: User) -> bool:
        print(f"Verifying license for {user.email}...")
        return True

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
