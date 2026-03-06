from abc import ABC, abstractmethod
from typing import List, Any

class IView(ABC):
    """
    Інтерфейс презентаційного рівня (PL).
    Визначає методи взаємодії з користувачем без реалізації логіки.
    """

    @abstractmethod
    def display_message(self, message: str) -> None:
        """Показує текстове повідомлення (успіх/помилка)."""
        pass

    @abstractmethod
    def render_app_list(self, apps: List[Any]) -> None:
        """Відображає список додатків, отриманих від BLL."""
        pass

    @abstractmethod
    def render_statistics(self, stats: str) -> None:
        """Відображає аналітичні дані, підготовлені сервісом."""
        pass

    @abstractmethod
    def show_import_progress(self, current: int, total: int) -> None:
        """Відображає прогрес обробки 1000+ рядків CSV."""
        pass

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        """Отримує ввід від користувача (шлях до файлу, запит для пошуку)."""
        pass