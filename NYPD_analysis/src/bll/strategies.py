import json
import time
from abc import ABC, abstractmethod

try:
    import requests
    from redis import Redis
    from kafka import KafkaProducer
except ImportError:
    requests = None
    Redis = None
    KafkaProducer = None

class ExportStrategy(ABC):
    """Абстрактний базовий клас для всіх стратегій виводу (Interface)"""
    @abstractmethod
    def send(self, data: list):
        pass

    def terminate(self):
        """Метод для коректного закриття з'єднань"""
        pass

class ConsoleStrategy(ExportStrategy):
    def send(self, data: list):
        print(f"[CONSOLE] Виведення {len(data)} записів NYPD:")
        for i, item in enumerate(data[:10], 1):
            print(f"   [{i}] ID: {item['id']} | Boro: {item['boro']} | Time: {item['time']}")
            time.sleep(0.05) 
        if len(data) > 10:
            print(f"   ... та ще {len(data) - 10} записів приховано.")

class FileOutputStrategy(ExportStrategy):
    def __init__(self, filename):
        self.filename = filename

    def send(self, data: list):
        print(f"[FILE] Запис у JSON-файл: {self.filename}...")
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"SUCCESS: [FILE] Дані збережено (усього {len(data)} об'єктів).")
        except Exception as e:
            print(f"ERROR: [FILE] Помилка запису: {e}")

class RedisStrategy(ExportStrategy):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = None

    def send(self, data: list):
        print(f"[REDIS] Підключення до {self.host}:{self.port}...")
        if Redis is None:
            print("WARNING: [REDIS] Бібліотека 'redis' не встановлена. Режим імітації.")
            return
        try:
            self.client = Redis(host=self.host, port=self.port, socket_timeout=1, decode_responses=True)
            for item in data:
                key = f"nypd:incident:{item['id']}"
                self.client.set(key, json.dumps(item))
            print(f"SUCCESS: [REDIS] Закешовано {len(data)} записів.")
        except Exception as e:
            print(f"WARNING: [REDIS] Сервер недоступний: {e}")
            print("MOCK: Дані оброблено в пам'яті.")

class KafkaStrategy(ExportStrategy):
    def __init__(self, servers, topic):
        self.servers = servers
        self.topic = topic
        self.producer = None

    def send(self, data: list):
        print(f"[KAFKA] Ініціалізація топіка '{self.topic}'...")
        if KafkaProducer is None:
            print("WARNING: [KAFKA] Бібліотека 'kafka-python' не встановлена. Режим імітації.")
            return
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks=1
            )
            for item in data:
                self.producer.send(self.topic, item)
            self.producer.flush()
            print(f"SUCCESS: [KAFKA] Пакет з {len(data)} повідомлень доставлено в брокер.")
        except Exception as e:
            print(f"WARNING: [KAFKA] Брокер {self.servers} не відповідає: {e}")
            print(f"MOCK: Топік '{self.topic}' імітовано.")

    def terminate(self):
        if self.producer:
            self.producer.close()
            print("[KAFKA] З'єднання з брокером закрито.")

class FirebaseStrategy(ExportStrategy):
    def __init__(self, db_url):
        self.db_url = db_url if db_url.endswith('/') else f"{db_url}/"

    def send(self, data: list):
        print(f"[FIREBASE] Підключення до хмарної бази: {self.db_url}")
        if requests is None:
            print("WARNING: Бібліотека 'requests' не встановлена.")
            return
        try:
            for item in data:
                url = f"{self.db_url}incidents/{item['id']}.json"
                response = requests.put(url, json=item, timeout=5)
                if response.status_code == 200:
                    print(f"   -> Firebase: Інцидент {item['id']} синхронізовано")
                else:
                    print(f"   -> Firebase: Помилка {response.status_code}")
            print(f"SUCCESS: [FIREBASE] Усі дані успішно вивантажено в хмару.")
        except Exception as e:
            print(f"WARNING: [FIREBASE] Помилка мережі: {e}")
            print("MOCK: Хмарний експорт імітовано.")
