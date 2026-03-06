import csv
from typing import List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.dal.interfaces import IDataRepository
from src.dal.models import Base, Application, Developer, Category # Імпортуємо моделі
from src.core.config import Config

    
class SqlAlchemyRepository(IDataRepository):
    """
    Реалізація репозиторію з використанням SQLAlchemy та стандартного модуля csv.
    """

    def __init__(self, db_url: str = Config.DATABASE_URL):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
        Base.metadata.create_all(self.engine)

    def read_raw_data_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Зчитує дані з CSV у список словників."""
        raw_data = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_data.append(row)
            return raw_data
        except FileNotFoundError:
            print(f"❌ Файл {file_path} не знайдено!")
            return []

    def save_entities(self, entities: List[Any]) -> None:
        """Зберігає об'єкти в базу даних за допомогою сесії ORM."""
        session = self.Session()
        try:
            session.add_all(entities)
            session.commit()
            print(f"✅ Успішно збережено {len(entities)} об'єктів у БД.")
        except Exception as e:
            session.rollback()
            print(f"❌ Помилка при збереженні в БД: {e}")
        finally:
            session.close()

    def get_all_applications(self) -> List[Application]:
        """Повертає всі додатки для презентаційного шару."""
        session = self.Session()
        apps = session.query(Application).all()
        session.close()
        return apps

    def clear_database(self) -> None:
        """Повне очищення бази даних для повторного завантаження."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        print("🧹 Базу даних очищено.")