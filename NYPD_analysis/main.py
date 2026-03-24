import json
import os
from src.dal.reader import NYPDDataReader
from src.bll.exporter import NYPDExporter
from src.core.factory import ExporterFactory
from src.bll.strategies import (
    ConsoleStrategy, 
    KafkaStrategy, 
    RedisStrategy, 
    FileOutputStrategy, 
    FirebaseStrategy
)

def main():
    print("\n" + "="*50)
    print("NYPD INCIDENT ANALYSIS TOOL | LAB 4 (STRATEGY)")
    print("="*50)
    
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(" ERROR: config.json не знайдено!")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        conf = json.load(f)
    
    reader = NYPDDataReader(conf['data_path'])
    data = reader.read_incidents(limit=10)
    
    if not data:
        print(" WARNING: Дані не зчитано.")
        return
    print(f"✅ OK: Зчитано інцидентів: {len(data)}")

    print("\n--- Оберіть режим експорту ---")
    print("1. Console (Вивід у термінал)")
    print("2. File (Запис у JSON файл)")
    print("3. Kafka (Стрімінг у брокер)")
    print("4. Redis (Кешування)")
    print("5. Firebase (Хмарна Realtime DB)")
    print("6. Авто (З конфіг-файлу)")
    
    choice = input("\nВведіть номер (1-6): ")

    if choice == '1':
        strategy = ConsoleStrategy()
        mode_name = "CONSOLE"
    elif choice == '2':
        strategy = FileOutputStrategy(conf['file_settings']['output_file'])
        mode_name = "FILE"
    elif choice == '3':
        k = conf['kafka_settings']
        strategy = KafkaStrategy(k['bootstrap_servers'], k['topic'])
        mode_name = "KAFKA"
    elif choice == '4':
        r = conf['redis_settings']
        strategy = RedisStrategy(r['host'], r['port'])
        mode_name = "REDIS"
    elif choice == '5':
        f_conf = conf['firebase_settings']
        strategy = FirebaseStrategy(f_conf['db_url'])
        mode_name = "FIREBASE"
    elif choice == '6':
        strategy = ExporterFactory.create_strategy()
        mode_name = f"{conf.get('export_mode', 'console').upper()} (AUTO)"
    else:
        print("Невірний вибір, використовується Console за замовчуванням.")
        strategy = ConsoleStrategy()
        mode_name = "CONSOLE (DEFAULT)"

    exporter = NYPDExporter(strategy)
    print(f"\n ACTIVE MODE: [{mode_name}]")
    print("-" * 50)
    
    exporter.execute_export(data)
    
    strategy.terminate()
    
    print("-" * 50)
    print("DONE: Процес завершено.\n")

if __name__ == "__main__":
    main()
