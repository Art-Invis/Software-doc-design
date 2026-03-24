import json
import os
from src.bll.strategies import ConsoleStrategy, KafkaStrategy, RedisStrategy, FileOutputStrategy, FirebaseStrategy

class ExporterFactory:
    @staticmethod
    def create_strategy():
        config_path = 'config.json'
        if not os.path.exists(config_path):
            print("WARNING: config.json не знайдено, використовується Console.")
            return ConsoleStrategy()

        with open(config_path, 'r', encoding='utf-8') as f:
            conf = json.load(f)
        
        mode = conf.get('export_mode', 'console').lower()
        
        if mode == 'kafka':
            k = conf['kafka_settings']
            return KafkaStrategy(k['bootstrap_servers'], k['topic'])
        elif mode == 'redis':
            r = conf['redis_settings']
            return RedisStrategy(r['host'], r['port'])
        elif mode == 'file':
            f_settings = conf['file_settings']
            return FileOutputStrategy(f_settings['output_file'])
        elif mode == 'firebase':
            f_conf = conf['firebase_settings']
            return FirebaseStrategy(f_conf['db_url'])
        else:
            return ConsoleStrategy()