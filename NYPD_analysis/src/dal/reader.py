import csv
import os

class NYPDDataReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_incidents(self, limit=100):
        incidents = []
        if not os.path.exists(self.file_path):
            print(f"❌ Помилка: Файл {self.file_path} не знайдено!")
            return []

        try:
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= limit: break
                    
                    incidents.append({
                        "id": row.get('INCIDENT_KEY'),
                        "date": row.get('OCCUR_DATE'),
                        "time": row.get('OCCUR_TIME'),
                        "boro": row.get('BORO'),
                        "precinct": row.get('PRECINCT'),
                        "coords": {
                            "lat": row.get('Latitude'),
                            "lon": row.get('Longitude')
                        }
                    })
            return incidents
        except Exception as e:
            print(f"❌ Помилка при читанні CSV: {e}")
            return []