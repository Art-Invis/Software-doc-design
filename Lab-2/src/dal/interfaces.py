from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IDataRepository(ABC):
    """
    Інтерфейс рівня доступу до даних (DAL).
    Визначає методи для роботи з CSV та базою даних через ORM.
    """

    @abstractmethod
    def read_raw_data_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Зчитує дані з .csv файлу і повертає їх у вигляді списку словників.
        Це перша частина вимоги лаби.
        """
        pass

    @abstractmethod
    def save_entities(self, entities: List[Any]) -> None:
        """
        Зберігає список об'єктів (моделей SQLAlchemy) у базу даних.
        Реалізує логіку транзакцій ORM.
        """
        pass

    @abstractmethod
    def get_all_applications(self) -> List[Any]:
        """
        Повертає всі додатки з бази даних для презентаційного рівня.
        """
        pass

    @abstractmethod
    def clear_database(self) -> None:
        """
        Очищає таблиці перед завантаженням нових даних (опціонально для зручності).
        """
        pass