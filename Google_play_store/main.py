from src.dal.repository import SqlAlchemyRepository
from src.bll.services import GooglePlayService
from src.core.config import Config 

def main():
    repository = SqlAlchemyRepository()
    service = GooglePlayService(repository=repository)

    csv_file = Config.CSV_DATA_PATH 
    
    print(f"🚀 Запуск процесу імпорту з {csv_file}...")
    service.import_data_from_csv(csv_file)
    
    print(service.get_statistics())

if __name__ == "__main__":
    main()