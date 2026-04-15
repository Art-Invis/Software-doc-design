import csv
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload, with_polymorphic
from src.dal.interfaces import IDataRepository
from src.dal.models import Base, Application, Developer, Category, Transaction, Review, Customer
from src.core.config import Config

class SqlAlchemyRepository(IDataRepository):
    def __init__(self, db_url: str = Config.DATABASE_URL):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def save_entities(self, entities: List[Any]) -> None:
        """Зберігає об'єкти через add_all. Без магії merge."""
        session = self.Session()
        try:
            session.add_all(entities) 
            session.commit()
            print(f"✅ Операція з БД успішна: додано/оновлено {len(entities)} об'єктів.")
        except Exception as e:
            session.rollback()
            print(f"❌ Помилка при збереженні в БД: {e}")
            raise e 
        finally:
            session.close()

    def delete_entity(self, entity: Any) -> None:
        """Видалення через завантаження об'єкта в поточну сесію."""
        session = self.Session()
        try:
            obj_id = self._get_primary_key(entity)
            if obj_id:
                local_entity = session.get(entity.__class__, obj_id)
                if local_entity:
                    session.delete(local_entity)
                    session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Помилка при видаленні: {e}")
        finally:
            session.close()

    def _get_primary_key(self, entity: Any):
        """Допоміжний метод для отримання PK об'єкта."""
        from sqlalchemy import inspect
        ins = inspect(entity.__class__)
        return getattr(entity, ins.primary_key[0].name)

    def get_all_applications(self) -> List[Application]:
        session = self.Session()
        try:
            poly = with_polymorphic(Application, "*")
            return session.query(poly).options(
                joinedload(poly.category),
                joinedload(poly.developer)
            ).all()
        finally:
            session.close()

    def get_app_by_id(self, app_id: str) -> Optional[Application]:
        session = self.Session()
        try:
            poly = with_polymorphic(Application, "*")
            return session.query(poly).options(
                joinedload(poly.category),
                joinedload(poly.developer),
                joinedload(poly.versions),
                joinedload(poly.reviews).joinedload(Review.customer)
            ).filter(poly.app_id == app_id).first()
        finally:
            session.close()

    def get_all_developers(self) -> List[Developer]:
        session = self.Session()
        try:
            return session.query(Developer).options(
                joinedload(Developer.applications).joinedload(Application.category)
            ).all()
        finally:
            session.close()

    def get_all_categories(self) -> List[Category]:
        session = self.Session()
        try:
            return session.query(Category).options(joinedload(Category.applications)).all()
        finally:
            session.close()

    def get_all_customers(self) -> List[Customer]:
        session = self.Session()
        try:
            return session.query(Customer).all()
        finally:
            session.close()

    def get_all_transactions(self) -> List[Transaction]:
        session = self.Session()
        try:
            return session.query(Transaction).options(
                joinedload(Transaction.customer),
                joinedload(Transaction.paid_app)
            ).all()
        finally:
            session.close()

    def read_raw_data_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        raw_data = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_data.append(row)
            return raw_data
        except FileNotFoundError:
            return []

    def clear_database(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)