from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IDataRepository(ABC):
    """
    Інтерфейс рівня доступу до даних (DAL).
    Визначає методи для взаємодії з персистентним сховищем та зовнішніми файлами.
    """

    @abstractmethod
    def read_raw_data_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Зчитує дані з зовнішнього CSV-файлу.
        """
        pass

    @abstractmethod
    def save_entities(self, entities: List[Any]) -> None:
        """
        Виконує операції запису (Create/Update) для переліку об'єктів у базі даних.
        """
        pass

    @abstractmethod
    def delete_entity(self, entity: Any) -> None:
        """
        Видаляє вказаний екземпляр сутності з бази даних.
        """
        pass

    @abstractmethod
    def get_all_applications(self) -> List[Any]:
        """
        Повертає повний перелік об'єктів типу Application із бази даних.
        """
        pass

    @abstractmethod
    def get_all_developers(self) -> List[Any]:
        """
        Запитує та повертає всі об'єкти типу Developer. 
        """
        pass

    @abstractmethod
    def get_all_categories(self) -> List[Any]:
        """
        Запитує та повертає всі об'єкти типу Category.
        """
        pass

    @abstractmethod
    def clear_database(self) -> None:
        """
        Виконує повне очищення таблиць бази даних (Drop/Create).
        """
        pass