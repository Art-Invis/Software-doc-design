from src.bll.strategies import ExportStrategy

class NYPDExporter:
    """
    Контекст який використовує обрану стратегію для експорту.
    """
    def __init__(self, strategy: ExportStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ExportStrategy):
        """
        Метод для динамічної зміни стратегії під час виконання (Runtime).
        """
        print(f" [Context] Зміна стратегії на {type(strategy).__name__}...")
        self._strategy = strategy

    def execute_export(self, data: list):
        """
        Основна бізнес-логіка: підготовка та виклик методу стратегії.
        """
        if not data:
            print(" [Context] Дані порожні. Експорт скасовано.")
            return

        print("🚀 [Context] Початок процесу експорту...")
        
        self._strategy.send(data)
        
        print("✅ [Context] Експорт завершено успішно.")